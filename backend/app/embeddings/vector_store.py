"""
NFM-X Vector Store
FAISS-based vector store for semantic search
"""
from typing import List, Optional, Tuple, Dict, Any
import logging
import numpy as np
from pathlib import Path

from ..config import settings
from .models import embedding_model

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self):
        self._index = None
        self._id_to_index = {}
        self._index_to_id = []
        self._embeddings = {}
        self._index_path = Path(settings.faiss_index_path)
        self._is_loaded = False
    
    def load(self):
        if self._is_loaded:
            return
        
        try:
            import faiss
            if not self._index_path.exists():
                dimension = embedding_model.dimension
                self._index = faiss.IndexFlatIP(dimension)
                logger.info(f"Created new FAISS index (dimension: {dimension})")
                self._is_loaded = True
                return
            
            self._index = faiss.read_index(str(self._index_path))
            logger.info(f"Loaded FAISS index from {self._index_path}")
            self._is_loaded = True
        except ImportError:
            logger.warning("FAISS not installed. Vector search will not be available.")
            self._index = None
            self._is_loaded = True
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            self._index = None
            self._is_loaded = True
    
    def save(self):
        if self._index is None:
            logger.warning("No FAISS index to save")
            return
        
        try:
            import faiss
            self._index_path.parent.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self._index, str(self._index_path))
            logger.info(f"Saved FAISS index to {self._index_path}")
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")
    
    @property
    def count(self) -> int:
        if self._index is None:
            return 0
        return self._index.ntotal
    
    @property
    def is_available(self) -> bool:
        return self._index is not None and self._is_loaded
    
    def add_vector(self, memory_id: str, embedding: List[float]) -> bool:
        if not self.is_available:
            return False
        
        try:
            vector = np.array([embedding], dtype=np.float32)
            self._index.add(vector)
            index = self._index.ntotal - 1
            self._id_to_index[memory_id] = index
            self._index_to_id.append(memory_id)
            self._embeddings[memory_id] = embedding
            return True
        except Exception as e:
            logger.error(f"Failed to add vector for {memory_id}: {e}")
            return False
    
    def search(self, query_embedding: List[float], k: int = 10) -> List[Tuple[str, float]]:
        if not self.is_available:
            return []
        
        try:
            import faiss
            query_vector = np.array([query_embedding], dtype=np.float32)
            faiss.normalize_L2(query_vector)
            distances, indices = self._index.search(query_vector, k)
            
            results = []
            for i in range(min(k, len(indices[0]))):
                idx = indices[0][i]
                if idx >= len(self._index_to_id):
                    continue
                memory_id = self._index_to_id[idx]
                score = float(distances[0][i])
                results.append((memory_id, score))
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_embedding(self, memory_id: str) -> Optional[List[float]]:
        return self._embeddings.get(memory_id)
    
    def update_vector(self, memory_id: str, new_embedding: List[float]) -> bool:
        if not self.is_available:
            return False
        self.remove_vector(memory_id)
        return self.add_vector(memory_id, new_embedding)
    
    def remove_vector(self, memory_id: str) -> bool:
        if not self.is_available:
            return False
        try:
            if memory_id in self._id_to_index:
                del self._id_to_index[memory_id]
            if memory_id in self._embeddings:
                del self._embeddings[memory_id]
            return True
        except Exception as e:
            logger.error(f"Failed to remove vector: {e}")
            return False
    
    def rebuild_index(self):
        if not self.is_available:
            return False
        try:
            import faiss
            dimension = embedding_model.dimension
            new_index = faiss.IndexFlatIP(dimension)
            for memory_id, embedding in self._embeddings.items():
                vector = np.array([embedding], dtype=np.float32)
                new_index.add(vector)
                index = new_index.ntotal - 1
                self._id_to_index[memory_id] = index
                self._index_to_id[index] = memory_id
            self._index = new_index
            return True
        except Exception as e:
            logger.error(f"Failed to rebuild index: {e}")
            return False


vector_store = VectorStore()
vector_store.load()