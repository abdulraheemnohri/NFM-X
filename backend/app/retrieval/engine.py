from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import re

from backend.app.memory.models import Memory, MemoryStatus, MemoryType
from backend.app.embeddings.models import get_embedding_model
from backend.app.embeddings.vector_store import get_vector_store
from backend.app.config import settings

class RetrievalEngine:
    def __init__(self):
        self.embedding_model = get_embedding_model()
        self.vector_store = get_vector_store()

    def _keyword_score(self, query: str, content: str) -> float:
        query_words = set(re.findall(r'\w+', query.lower()))
        content_words = set(re.findall(r'\w+', content.lower()))
        if not query_words:
            return 0.0
        overlap = len(query_words & content_words)
        return overlap / len(query_words)

    async def retrieve(
        self,
        db_session: AsyncSession,
        query: str,
        agent_id: Optional[str] = None,
        limit: int = 20,
        memory_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        # 1. Semantic search via FAISS
        query_embedding = self.embedding_model.embed(query)
        semantic_results = self.vector_store.search(query_embedding, k=limit * 2)
        semantic_ids = {r["memory_id"]: r["score"] for r in semantic_results
                        if not r["metadata"].get("_deleted")}

        # 2. Keyword search via SQLite
        stmt = select(Memory).where(Memory.status == MemoryStatus.ACTIVE)
        if agent_id:
            stmt = stmt.where(Memory.agent_id == agent_id)
        if memory_types:
            stmt = stmt.where(Memory.type.in_([MemoryType(t) for t in memory_types]))

        result = await db_session.execute(stmt)
        memories = result.scalars().all()

        # 3. Hybrid scoring
        scored = []
        for mem in memories:
            sem_score = semantic_ids.get(mem.id, 0.0)
            kw_score = self._keyword_score(query, mem.content)

            final_score = (
                settings.NFM_SEMANTIC_WEIGHT * sem_score +
                settings.NFM_KEYWORD_WEIGHT * kw_score
            )

            final_score *= (0.5 + 0.5 * mem.confidence)
            final_score *= (0.5 + 0.5 * mem.importance)

            scored.append({
                "memory": mem,
                "score": final_score,
                "semantic_score": sem_score,
                "keyword_score": kw_score
            })

        scored.sort(key=lambda x: x["score"], reverse=True)

        results = []
        for item in scored[:limit]:
            mem = item["memory"]
            results.append({
                "id": mem.id,
                "type": mem.type.value,
                "content": mem.content,
                "confidence": mem.confidence,
                "importance": mem.importance,
                "score": round(item["score"], 4),
                "semantic_score": round(item["semantic_score"], 4),
                "keyword_score": round(item["keyword_score"], 4),
                "created_at": mem.created_at.isoformat() if mem.created_at else None
            })
        return results

def get_retrieval_engine() -> RetrievalEngine:
    return RetrievalEngine()
