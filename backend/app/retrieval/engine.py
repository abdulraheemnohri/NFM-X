"""
NFM-X Retrieval Engine
Combines semantic and keyword search for optimal retrieval
"""
from typing import List, Tuple, Optional, Dict, Any
import logging
import time

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc

from ..memory.models import Memory, MemoryStatus, MemoryType
from ..embeddings.models import embedding_model
from ..embeddings.vector_store import vector_store

logger = logging.getLogger(__name__)


class RetrievalEngine:
    def __init__(self):
        self.embedding_model = embedding_model
        self.vector_store = vector_store

    async def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        memory_type: Optional[MemoryType] = None,
        status: Optional[MemoryStatus] = None,
        tags: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
        db_session: Optional[AsyncSession] = None
    ) -> Tuple[List[Tuple[Memory, float]], int]:
        start_time = time.time()
        
        query_embedding = self.embedding_model.encode_single(query)
        
        semantic_results = []
        if self.vector_store.is_available:
            semantic_results = self.vector_store.search(query_embedding, k=limit * 2)
        
        keyword_results = await self._keyword_search(
            query=query,
            limit=limit * 2,
            memory_type=memory_type,
            status=status,
            tags=tags,
            categories=categories,
            db_session=db_session
        )
        
        combined_results = self._combine_results(
            semantic_results=semantic_results,
            keyword_results=keyword_results,
            semantic_weight=semantic_weight,
            keyword_weight=keyword_weight,
            limit=limit
        )
        
        logger.debug(f"Hybrid search completed in {time.time() - start_time:.3f}s")
        return combined_results, len(combined_results)

    async def semantic_search(
        self,
        query: str,
        limit: int = 10,
        memory_type: Optional[MemoryType] = None,
        status: Optional[MemoryStatus] = None,
        tags: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        db_session: Optional[AsyncSession] = None
    ) -> Tuple[List[Tuple[Memory, float]], int]:
        if not self.vector_store.is_available:
            return await self.keyword_search(
                query=query,
                limit=limit,
                memory_type=memory_type,
                status=status,
                tags=tags,
                categories=categories,
                db_session=db_session
            )
        
        query_embedding = self.embedding_model.encode_single(query)
        results = self.vector_store.search(query_embedding, k=limit * 2)
        
        filtered_results = []
        for memory_id, score in results:
            memory = await self._get_memory(memory_id, db_session)
            if memory and self._matches_filters(memory, memory_type, status, tags, categories):
                filtered_results.append((memory, score))
            if len(filtered_results) >= limit:
                break
        
        return filtered_results, len(filtered_results)

    async def keyword_search(
        self,
        query: str,
        limit: int = 10,
        memory_type: Optional[MemoryType] = None,
        status: Optional[MemoryStatus] = None,
        tags: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        db_session: Optional[AsyncSession] = None
    ) -> Tuple[List[Tuple[Memory, float]], int]:
        results = await self._keyword_search(
            query=query,
            limit=limit * 2,
            memory_type=memory_type,
            status=status,
            tags=tags,
            categories=categories,
            db_session=db_session
        )
        return results, len(results)

    async def _keyword_search(
        self,
        query: str,
        limit: int,
        memory_type: Optional[MemoryType],
        status: Optional[MemoryStatus],
        tags: Optional[List[str]],
        categories: Optional[List[str]],
        db_session: Optional[AsyncSession]
    ) -> List[Tuple[Memory, float]]:
        from ..storage.database import AsyncSessionLocal
        
        if db_session is None:
            db_session = AsyncSessionLocal()
        
        try:
            search_query = select(Memory)
            filters = []
            
            if status:
                filters.append(Memory.status == status)
            else:
                filters.append(Memory.status == MemoryStatus.ACTIVE)
            
            if memory_type:
                filters.append(Memory.memory_type == memory_type)
            
            if tags:
                for tag in tags:
                    filters.append(Memory.tags.contains([tag]))
            
            if categories:
                for category in categories:
                    filters.append(Memory.categories.contains([category]))
            
            if query:
                search_pattern = f"%{query}%"
                search_filters = [
                    Memory.content.ilike(search_pattern),
                    Memory.title.ilike(search_pattern),
                    Memory.description.ilike(search_pattern),
                ]
                search_filters.append(Memory.tags.contains([query]))
                search_filters.append(Memory.categories.contains([query]))
                filters.append(or_(*search_filters))
            
            if filters:
                search_query = search_query.where(and_(*filters))
            
            search_query = search_query.order_by(
                desc(Memory.relevance_score),
                desc(Memory.access_count)
            ).limit(limit * 2)
            
            result = await db_session.execute(search_query)
            memories = result.scalars().all()
            
            results = []
            for memory in memories:
                score = self._calculate_keyword_score(memory, query)
                results.append((memory, score))
            
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []

    def _calculate_keyword_score(self, memory: Memory, query: str) -> float:
        if not query:
            return 0.5
        
        content = (memory.content or "").lower()
        title = (memory.title or "").lower()
        description = (memory.description or "").lower()
        query_lower = query.lower()
        
        matches = 0
        
        if query_lower in content:
            matches += 2
        if query_lower in title:
            matches += 3
        if query_lower in description:
            matches += 2
        
        query_words = query_lower.split()
        for word in query_words:
            if word in content:
                matches += 0.5
            if word in title:
                matches += 1.0
            if word in description:
                matches += 0.5
        
        total_length = len(content) + len(title) + len(description) + 1
        score = min(matches / (total_length ** 0.5), 1.0)
        
        access_boost = min(memory.access_count / 100, 0.3)
        relevance_boost = memory.relevance_score * 0.2
        
        return min(score + access_boost + relevance_boost, 1.0)

    def _combine_results(
        self,
        semantic_results: List[Tuple[str, float]],
        keyword_results: List[Tuple[Memory, float]],
        semantic_weight: float,
        keyword_weight: float,
        limit: int
    ) -> List[Tuple[Memory, float]]:
        memory_scores = {}
        memory_id_to_memory = {}
        
        for memory_id, score in semantic_results:
            memory_scores[memory_id] = score * semantic_weight
        
        for memory, score in keyword_results:
            if memory.id in memory_scores:
                memory_scores[memory.id] += score * keyword_weight
            else:
                memory_scores[memory.id] = score * keyword_weight
            memory_id_to_memory[memory.id] = memory
        
        sorted_memory_ids = sorted(memory_scores.keys(), key=lambda x: memory_scores[x], reverse=True)
        
        results = []
        for memory_id in sorted_memory_ids[:limit]:
            if memory_id in memory_id_to_memory:
                memory = memory_id_to_memory[memory_id]
                combined_score = memory_scores[memory_id]
                results.append((memory, combined_score))
        
        return results

    async def find_similar(
        self,
        memory_id: str,
        limit: int = 10,
        db_session: Optional[AsyncSession] = None
    ) -> Tuple[List[Tuple[Memory, float]], int]:
        from ..storage.database import AsyncSessionLocal
        
        if db_session is None:
            db_session = AsyncSessionLocal()
        
        try:
            result = await db_session.execute(
                select(Memory).where(Memory.id == memory_id)
            )
            reference_memory = result.scalar_one_or_none()
            if not reference_memory:
                return [], 0
            
            embedding = self.vector_store.get_embedding(memory_id)
            if embedding is None:
                embedding = self.embedding_model.encode_single(reference_memory.content or "")
            
            results = self.vector_store.search(embedding, k=limit * 2)
            
            filtered_results = []
            for result_memory_id, score in results:
                if result_memory_id == memory_id:
                    continue
                
                similar_memory = await self._get_memory(result_memory_id, db_session)
                if similar_memory and similar_memory.status == MemoryStatus.ACTIVE:
                    filtered_results.append((similar_memory, score))
                
                if len(filtered_results) >= limit:
                    break
            
            return filtered_results, len(filtered_results)
            
        except Exception as e:
            logger.error(f"Failed to find similar memories: {e}")
            return [], 0

    async def get_context_memories(
        self,
        query: Optional[str] = None,
        memory_ids: Optional[List[str]] = None,
        limit: int = 10,
        memory_types: Optional[List[MemoryType]] = None,
        tags: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        min_relevance: float = 0.3,
        db_session: Optional[AsyncSession] = None
    ) -> Tuple[List[Memory], List[float]]:
        from ..storage.database import AsyncSessionLocal
        
        if db_session is None:
            db_session = AsyncSessionLocal()
        
        try:
            memories = []
            scores = []
            
            if memory_ids:
                for mem_id in memory_ids[:limit]:
                    memory = await self._get_memory(mem_id, db_session)
                    if memory and memory.status == MemoryStatus.ACTIVE:
                        memories.append(memory)
                        scores.append(1.0)
            elif query:
                results, _ = await self.hybrid_search(
                    query=query,
                    limit=limit * 2,
                    memory_type=memory_types[0] if memory_types and len(memory_types) == 1 else None,
                    tags=tags,
                    categories=categories,
                    db_session=db_session
                )
                
                for memory, score in results:
                    if score >= min_relevance:
                        memories.append(memory)
                        scores.append(score)
                    if len(memories) >= limit:
                        break
            else:
                result = await db_session.execute(
                    select(Memory)
                    .where(Memory.status == MemoryStatus.ACTIVE)
                    .order_by(desc(Memory.created_at))
                    .limit(limit)
                )
                memories = result.scalars().all()
                scores = [1.0] * len(memories)
            
            if memory_types and len(memory_types) > 1:
                filtered_pairs = [(m, s) for m, s in zip(memories, scores) if m.memory_type in memory_types]
                memories = [m for m, s in filtered_pairs]
                scores = [s for m, s in filtered_pairs]
            
            if tags:
                filtered_memories = []
                filtered_scores = []
                for memory, score in zip(memories, scores):
                    if memory.tags and any(tag in memory.tags for tag in tags):
                        filtered_memories.append(memory)
                        filtered_scores.append(score)
                memories = filtered_memories
                scores = filtered_scores
            
            if categories:
                filtered_memories = []
                filtered_scores = []
                for memory, score in zip(memories, scores):
                    if memory.categories and any(cat in memory.categories for cat in categories):
                        filtered_memories.append(memory)
                        filtered_scores.append(score)
                memories = filtered_memories
                scores = filtered_scores
            
            return memories[:limit], scores[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get context memories: {e}")
            return [], []

    async def get_context_summary(
        self,
        query: str,
        limit: int = 20,
        db_session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        from ..storage.database import AsyncSessionLocal
        
        if db_session is None:
            db_session = AsyncSessionLocal()
        
        try:
            results, _ = await self.hybrid_search(query=query, limit=limit, db_session=db_session)
            memories = [m for m, _ in results]
            total = len(memories)
            
            by_type = {}
            for memory in memories:
                type_name = memory.memory_type.value if memory.memory_type else "TEXT"
                by_type[type_name] = by_type.get(type_name, 0) + 1
            
            by_category = {}
            for memory in memories:
                for category in (memory.categories or []):
                    by_category[category] = by_category.get(category, 0) + 1
            
            by_tag = {}
            for memory in memories:
                for tag in (memory.tags or []):
                    by_tag[tag] = by_tag.get(tag, 0) + 1
            
            avg_relevance = sum(s for _, s in results) / len(results) if results else 0
            
            return {
                "total": total,
                "relevant": len(memories),
                "by_type": by_type,
                "by_category": by_category,
                "by_tag": by_tag,
                "avg_relevance": avg_relevance
            }
            
        except Exception as e:
            logger.error(f"Failed to get context summary: {e}")
            return {"total": 0, "relevant": 0, "by_type": {}, "by_category": {}, "by_tag": {}, "avg_relevance": 0}

    async def _get_memory(self, memory_id: str, db_session: AsyncSession) -> Optional[Memory]:
        result = await db_session.execute(
            select(Memory).where(Memory.id == memory_id)
        )
        return result.scalar_one_or_none()

    def _matches_filters(
        self,
        memory: Memory,
        memory_type: Optional[MemoryType],
        status: Optional[MemoryStatus],
        tags: Optional[List[str]],
        categories: Optional[List[str]]
    ) -> bool:
        if status and memory.status != status:
            return False
        if memory_type and memory.memory_type != memory_type:
            return False
        if tags:
            memory_tags = set(memory.tags or [])
            if not any(tag in memory_tags for tag in tags):
                return False
        if categories:
            memory_categories = set(memory.categories or [])
            if not any(cat in memory_categories for cat in categories):
                return False
        return True