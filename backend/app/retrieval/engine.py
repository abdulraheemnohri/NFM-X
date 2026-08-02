"""
Hybrid retrieval engine for NFM-X
"""
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func
from ..memory.models import Memory, MemoryStatus, MemoryType
from ..embeddings.models import embedding_model
from ..embeddings.vector_store import vector_store

class SearchMode(str, Enum):
    HYBRID = "hybrid"; SEMANTIC = "semantic"; KEYWORD = "keyword"

@dataclass
class RetrievalQuery:
    query: str
    limit: int = 10
    search_mode: SearchMode = SearchMode.HYBRID
    memory_types: Optional[List[MemoryType]] = None
    status: Optional[MemoryStatus] = None
    tags: Optional[List[str]] = None
    author_id: Optional[str] = None
    min_confidence: Optional[float] = None
    min_importance: Optional[float] = None
    semantic_weight: float = 0.7
    keyword_weight: float = 0.3

@dataclass
class RetrievalResult:
    memory: Memory
    score: float
    semantic_score: Optional[float] = None
    keyword_score: Optional[float] = None

class HybridRetrievalEngine:
    def __init__(self, semantic_weight=0.7, keyword_weight=0.3):
        total = semantic_weight + keyword_weight
        self.semantic_weight = semantic_weight / total if total > 0 else 0.7
        self.keyword_weight = keyword_weight / total if total > 0 else 0.3

    async def search(self, db_session, query: RetrievalQuery):
        if query.search_mode == SearchMode.SEMANTIC:
            return await self._semantic_search(db_session, query, query.limit)
        if query.search_mode == SearchMode.KEYWORD:
            return await self._keyword_search(db_session, query, query.limit)
        return await self._hybrid_search(db_session, query, query.limit)

    async def _semantic_search(self, db_session, query: RetrievalQuery, limit):
        query_embedding = embedding_model.encode(query.query)
        vector_ids, vector_scores = vector_store.search(query_embedding, k=limit * 2)
        memory_ids = [vector_store.get_metadata_by_id(vid).get("memory_id") for vid in vector_ids if vector_store.get_metadata_by_id(vid)]
        if memory_ids:
            stmt = select(Memory).where(Memory.id.in_(memory_ids))
            stmt = self._apply_filters(stmt, query)
            db_result = await db_session.execute(stmt)
            memories = db_result.scalars().all()
            memory_map = {m.id: m for m in memories}
            results = []
            for vid, score in zip(vector_ids, vector_scores):
                meta = vector_store.get_metadata_by_id(vid)
                if meta and "memory_id" in meta and meta["memory_id"] in memory_map:
                    results.append(RetrievalResult(memory=memory_map[meta["memory_id"]], score=float(score), semantic_score=float(score), keyword_score=0.0))
                    if len(results) >= limit:
                        break
            return results
        return []

    async def _keyword_search(self, db_session, query: RetrievalQuery, limit):
        terms = query.query.lower().split()
        conditions = [Memory.content.ilike(f"%{t}%") for t in terms if len(t) > 2]
        if not conditions:
            return []
        stmt = select(Memory).where(or_(*conditions))
        stmt = self._apply_filters(stmt, query).limit(limit)
        db_result = await db_session.execute(stmt)
        memories = db_result.scalars().all()
        results = []
        for memory in memories:
            score = sum(1.0 for t in terms if len(t) > 2 and t in memory.content.lower()) / max(len(terms), 1)
            results.append(RetrievalResult(memory=memory, score=score, semantic_score=0.0, keyword_score=score))
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]

    async def _hybrid_search(self, db_session, query: RetrievalQuery, limit):
        semantic_results = await self._semantic_search(db_session, query, limit * 2)
        keyword_results = await self._keyword_search(db_session, query, limit * 2)
        combined = {}
        for r in semantic_results:
            combined[r.memory.id] = {"memory": r.memory, "semantic_score": r.semantic_score or 0.0, "keyword_score": 0.0}
        for r in keyword_results:
            if r.memory.id not in combined:
                combined[r.memory.id] = {"memory": r.memory, "semantic_score": 0.0, "keyword_score": r.keyword_score or 0.0}
            else:
                combined[r.memory.id]["keyword_score"] = r.keyword_score or 0.0
        final_results = []
        for data in combined.values():
            score = (data["semantic_score"] * self.semantic_weight) + (data["keyword_score"] * self.keyword_weight)
            final_results.append(RetrievalResult(memory=data["memory"], score=score, semantic_score=data["semantic_score"], keyword_score=data["keyword_score"]))
        final_results.sort(key=lambda x: x.score, reverse=True)
        return final_results[:limit]

    def _apply_filters(self, stmt, query: RetrievalQuery):
        conditions = []
        if query.status:
            conditions.append(Memory.status == query.status)
        else:
            conditions.append(Memory.status == MemoryStatus.ACTIVE)
        if query.memory_types:
            conditions.append(Memory.memory_type.in_(query.memory_types))
        if query.author_id:
            conditions.append(Memory.author_id == query.author_id)
        if query.tags:
            for tag in query.tags:
                conditions.append(Memory.tags.contains([tag]))
        if query.min_confidence is not None:
            conditions.append(Memory.confidence >= query.min_confidence)
        if query.min_importance is not None:
            conditions.append(Memory.importance >= query.min_importance)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        return stmt

retrieval_engine = HybridRetrievalEngine()