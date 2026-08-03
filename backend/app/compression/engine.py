from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from ..memory.models import Memory, MemoryStatus, MemoryType

class MemoryCompressionEngine:
    """Summarize old memories, archive low-importance, semantic deduplication."""

    def __init__(self):
        self.archive_age_days = 90
        self.archive_importance_threshold = 0.3
        self.min_confidence_for_summary = 0.6

    async def find_compressible_memories(self, db_session: AsyncSession,
                                          agent_id: Optional[str] = None) -> List[Memory]:
        """Find memories that can be compressed or archived."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.archive_age_days)
        stmt = select(Memory).where(
            Memory.status == MemoryStatus.ACTIVE,
            Memory.created_at < cutoff,
            Memory.importance < self.archive_importance_threshold
        )
        if agent_id:
            stmt = stmt.where(Memory.agent_id == agent_id)
        result = await db_session.execute(stmt)
        return result.scalars().all()

    async def summarize_memory_cluster(self, db_session: AsyncSession,
                                        memory_ids: List[str]) -> Optional[Memory]:
        """Create a summary memory from a cluster of related memories."""
        stmt = select(Memory).where(Memory.id.in_(memory_ids))
        result = await db_session.execute(stmt)
        memories = result.scalars().all()
        if len(memories) < 2:
            return None

        # Simple extraction-based summary
        all_content = " ".join([m.content for m in memories])
        words = all_content.lower().split()
        word_freq = {}
        for w in words:
            if len(w) > 3:
                word_freq[w] = word_freq.get(w, 0) + 1
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        summary_text = f"Summary of {len(memories)} memories: " + ", ".join([w for w, _ in top_words])

        summary = Memory(
            id=str(uuid.uuid4()),
            root_id=str(uuid.uuid4()),
            version=1,
            type=MemoryType.SEMANTIC,
            content=summary_text,
            normalized_content=summary_text.lower(),
            agent_id=memories[0].agent_id,
            source_id="compression_engine",
            confidence=min(0.8, sum(m.confidence for m in memories) / len(memories)),
            importance=max(m.importance for m in memories),
            status=MemoryStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            observed_at=datetime.now(timezone.utc),
            valid_from=datetime.now(timezone.utc),
            metadata={
                "summarized_memory_ids": [m.id for m in memories],
                "summarized_count": len(memories),
                "compression_type": "cluster_summary",
                "original_date_range": {
                    "oldest": min(m.created_at.isoformat() for m in memories if m.created_at),
                    "newest": max(m.created_at.isoformat() for m in memories if m.created_at)
                }
            }
        )
        db_session.add(summary)

        # Archive original memories
        for mem in memories:
            mem.status = MemoryStatus.ARCHIVED
            if mem.metadata is None:
                mem.metadata = {}
            mem.metadata["archived_reason"] = "compressed_into_summary"
            mem.metadata["summary_memory_id"] = summary.id

        await db_session.commit()
        return summary

    async def deduplicate_semantic(self, db_session: AsyncSession,
                                    agent_id: Optional[str] = None,
                                    similarity_threshold: float = 0.95) -> Dict[str, Any]:
        """Find and merge near-duplicate memories."""
        from ..embeddings.models import get_embedding_model
        from ..embeddings.vector_store import get_vector_store

        embedding_model = get_embedding_model()
        vector_store = get_vector_store()

        stmt = select(Memory).where(Memory.status == MemoryStatus.ACTIVE)
        if agent_id:
            stmt = stmt.where(Memory.agent_id == agent_id)
        result = await db_session.execute(stmt)
        memories = result.scalars().all()

        duplicates_found = []
        processed = set()

        for i, mem_a in enumerate(memories):
            if mem_a.id in processed:
                continue
            emb_a = embedding_model.embed(mem_a.content)

            for mem_b in memories[i + 1:]:
                if mem_b.id in processed:
                    continue
                emb_b = embedding_model.embed(mem_b.content)
                similarity = self._cosine_similarity(emb_a, emb_b)

                if similarity >= similarity_threshold:
                    # Mark B as duplicate of A
                    mem_b.status = MemoryStatus.ARCHIVED
                    mem_b.metadata = {**(mem_b.metadata or {}),
                                      "duplicate_of": mem_a.id, "similarity": round(similarity, 4)}
                    mem_a.confidence = min(0.99, mem_a.confidence + 0.02)
                    processed.add(mem_b.id)
                    duplicates_found.append({
                        "kept": mem_a.id,
                        "removed": mem_b.id,
                        "similarity": round(similarity, 4)
                    })

        await db_session.commit()
        return {"duplicates_found": len(duplicates_found), "details": duplicates_found}

    def _cosine_similarity(self, a, b):
        import numpy as np
        a_arr, b_arr = np.array(a), np.array(b)
        dot = np.dot(a_arr, b_arr)
        na, nb = np.linalg.norm(a_arr), np.linalg.norm(b_arr)
        return 0.0 if na == 0 or nb == 0 else float(dot / (na * nb))