"""NFM-X V2 Retrieval Engine - Enhanced memory retrieval"""

from typing import List, Optional, Tuple
from .hybrid_search import HybridSearchEngine


class RetrievalEngineV2:
    """V2 retrieval engine with scoring and ranking"""
    
    def __init__(self):
        self.hybrid_search = HybridSearchEngine()
    
    def retrieve(
        self,
        query: str,
        limit: int = 10,
        semantic_weight: float = 0.6,
        keyword_weight: float = 0.3,
        bm25_weight: float = 0.1,
        filters: Optional[dict] = None
    ) -> List[Tuple[str, float]]:
        """
        Retrieve memories using hybrid search
        Returns list of (memory_id, score) tuples sorted by score
        """
        results = self.hybrid_search.search(
            query=query,
            limit=limit,
            semantic_weight=semantic_weight,
            keyword_weight=keyword_weight,
            bm25_weight=bm25_weight,
            filters=filters
        )
        return results
    
    def retrieve_similar(self, memory_id: str, limit: int = 5) -> List[Tuple[str, float]]:
        """Retrieve memories similar to the given memory"""
        return []