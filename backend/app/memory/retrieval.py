#!/usr/bin/env python3
"""
NFM-X Memory Retrieval Engine
============================

Handles retrieval of memories using multiple strategies:
- Semantic search
- Keyword search
- Temporal search
- Graph-based retrieval
- Hybrid search (combination of above)

Urdu: Yadashthon ko alag alag tareeqon se talash karne ka engine
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pydantic import BaseModel
import numpy as np

from .models import Memory, MemoryVersion, MemoryType


class RetrievalQuery(BaseModel):
    query: str
    memory_types: Optional[List[str]] = None
    time_range: Optional[Tuple[datetime, datetime]] = None
    confidence_threshold: Optional[float] = None
    limit: int = 10
    strategy: str = "hybrid"
    metadata_filters: Optional[Dict[str, Any]] = None


class RetrievalResult(BaseModel):
    memory_id: str
    version_id: str
    content: str
    memory_type: str
    confidence: float
    timestamp: datetime
    similarity_score: float
    metadata: Dict[str, Any]


class MemoryRetriever:
    def __init__(self, vector_store=None, graph_engine=None):
        self.vector_store = vector_store
        self.graph_engine = graph_engine
        self._memories = []
        self._embeddings = {}
    
    def add_memory(self, memory: Memory, embedding: Optional[np.ndarray] = None):
        self._memories.append(memory)
        if embedding is not None:
            self._embeddings[memory.id] = embedding
    
    def retrieve(self, query: RetrievalQuery) -> List[RetrievalResult]:
        if query.strategy == "semantic":
            return self._semantic_search(query)
        elif query.strategy == "keyword":
            return self._keyword_search(query)
        elif query.strategy == "temporal":
            return self._temporal_search(query)
        elif query.strategy == "graph":
            return self._graph_search(query)
        else:
            return self._hybrid_search(query)
    
    def _semantic_search(self, query: RetrievalQuery) -> List[RetrievalResult]:
        results = []
        for memory in self._memories:
            similarity = self._text_similarity(query.query, memory.content)
            if similarity > 0.1:
                results.append(RetrievalResult(
                    memory_id=memory.id, version_id=memory.current_version_id,
                    content=memory.content, memory_type=memory.memory_type,
                    confidence=memory.metadata.get('confidence', 0.8),
                    timestamp=memory.created_at, similarity_score=similarity,
                    metadata=memory.metadata or {}
                ))
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:query.limit]
    
    def _keyword_search(self, query: RetrievalQuery) -> List[RetrievalResult]:
        query_keywords = self._extract_keywords(query.query)
        results = []
        for memory in self._memories:
            memory_keywords = self._extract_keywords(memory.content)
            common_keywords = set(query_keywords) & set(memory_keywords)
            if common_keywords:
                score = len(common_keywords) / max(len(query_keywords), 1)
                results.append(RetrievalResult(
                    memory_id=memory.id, version_id=memory.current_version_id,
                    content=memory.content, memory_type=memory.memory_type,
                    confidence=memory.metadata.get('confidence', 0.8),
                    timestamp=memory.created_at, similarity_score=score,
                    metadata=memory.metadata or {}
                ))
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:query.limit]
    
    def _temporal_search(self, query: RetrievalQuery) -> List[RetrievalResult]:
        results = []
        for memory in self._memories:
            if query.time_range:
                start_time, end_time = query.time_range
                if start_time <= memory.created_at <= end_time:
                    results.append(RetrievalResult(
                        memory_id=memory.id, version_id=memory.current_version_id,
                        content=memory.content, memory_type=memory.memory_type,
                        confidence=memory.metadata.get('confidence', 0.8),
                        timestamp=memory.created_at, similarity_score=1.0,
                        metadata=memory.metadata or {}
                    ))
            else:
                time_diff = datetime.utcnow() - memory.created_at
                score = 1.0 / (1.0 + time_diff.total_seconds() / 3600)
                results.append(RetrievalResult(
                    memory_id=memory.id, version_id=memory.current_version_id,
                    content=memory.content, memory_type=memory.memory_type,
                    confidence=memory.metadata.get('confidence', 0.8),
                    timestamp=memory.created_at, similarity_score=score,
                    metadata=memory.metadata or {}
                ))
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:query.limit]
    
    def _graph_search(self, query: RetrievalQuery) -> List[RetrievalResult]:
        return []
    
    def _hybrid_search(self, query: RetrievalQuery) -> List[RetrievalResult]:
        semantic_results = self._semantic_search(query)
        keyword_results = self._keyword_search(query)
        temporal_results = self._temporal_search(query)
        
        all_results = semantic_results + keyword_results + temporal_results
        unique_results = {}
        for result in all_results:
            if result.memory_id not in unique_results:
                unique_results[result.memory_id] = result
            else:
                if result.similarity_score > unique_results[result.memory_id].similarity_score:
                    unique_results[result.memory_id] = result
        
        combined_results = list(unique_results.values())
        combined_results.sort(key=lambda x: x.similarity_score, reverse=True)
        return combined_results[:query.limit]
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        common = words1 & words2
        return len(common) / max(len(words1 | words2), 1)
    
    def _extract_keywords(self, text: str) -> List[str]:
        words = text.lower().split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        return [word for word in words if word not in stop_words and len(word) > 2]


# Urdu: NFM-X memory retrieval engine - Yadashthon ko talash karne ke liye