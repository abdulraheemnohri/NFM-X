from typing import List, Dict, Any, Optional
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import uuid
import numpy as np

from ..memory.models import Memory, MemoryPattern, MemoryType, MemoryStatus
from ..embeddings.models import get_embedding_model

class PatternDiscoveryEngine:
    def __init__(self):
        self.embedding_model = get_embedding_model()
        self.min_cluster_size = 3
        self.similarity_threshold = 0.75

    async def discover_patterns(self, db_session: AsyncSession, agent_id: Optional[str] = None,
                                 memory_type: Optional[MemoryType] = None) -> List[MemoryPattern]:
        stmt = select(Memory).where(Memory.status == MemoryStatus.ACTIVE)
        if agent_id:
            stmt = stmt.where(Memory.agent_id == agent_id)
        if memory_type:
            stmt = stmt.where(Memory.type == memory_type)
        result = await db_session.execute(stmt)
        memories = result.scalars().all()
        if len(memories) < self.min_cluster_size:
            return []
        clusters = self._cluster_memories(memories)
        patterns = []
        for cluster in clusters:
            if len(cluster) >= self.min_cluster_size:
                pattern = await self._create_pattern(db_session, cluster)
                patterns.append(pattern)
        return patterns

    def _cluster_memories(self, memories: List[Memory]) -> List[List[Memory]]:
        if not memories:
            return []
        embeddings = {mem.id: self.embedding_model.embed(mem.content) for mem in memories}
        clusters, used = [], set()
        for mem in memories:
            if mem.id in used:
                continue
            cluster, used_add = [mem], {mem.id}
            mem_emb = embeddings[mem.id]
            for other in memories:
                if other.id in used or other.id in used_add:
                    continue
                sim = self._cosine_similarity(mem_emb, embeddings[other.id])
                if sim >= self.similarity_threshold:
                    cluster.append(other)
                    used_add.add(other.id)
            if len(cluster) >= self.min_cluster_size:
                clusters.append(cluster)
                used.update(used_add)
        return clusters

    async def _create_pattern(self, db_session, cluster):
        all_words = []
        for mem in cluster:
            all_words.extend(mem.content.lower().split())
        word_freq = defaultdict(int)
        for w in all_words:
            if len(w) > 3:
                word_freq[w] += 1
        common = [w for w, freq in word_freq.items() if freq >= len(cluster) * 0.5]
        pattern = MemoryPattern(
            id=str(uuid.uuid4()), pattern_type="semantic_cluster",
            name=f"Pattern: {' '.join(common[:5])}",
            description=f"Pattern across {len(cluster)} memories",
            supporting_memories=[m.id for m in cluster],
            pattern_data={"common_terms": common[:10], "memory_count": len(cluster),
                          "types": list(set(m.type.value for m in cluster))},
            confidence=0.7, strength=min(1.0, len(cluster) / 10.0),
            discovered_at=datetime.now(timezone.utc)
        )
        db_session.add(pattern)
        await db_session.commit()
        return pattern

    def _cosine_similarity(self, a, b):
        a_arr, b_arr = np.array(a), np.array(b)
        dot = np.dot(a_arr, b_arr)
        na, nb = np.linalg.norm(a_arr), np.linalg.norm(b_arr)
        return 0.0 if na == 0 or nb == 0 else float(dot / (na * nb))
