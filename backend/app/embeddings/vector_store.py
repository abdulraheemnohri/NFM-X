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


class SearchResultDict(dict):
    """Custom dict that supports both dict key lookup and tuple-like unpacking/indexing"""
    def __init__(self, memory_id: str, score: float):
        super().__init__(memory_id=memory_id, score=score)
        self.memory_id = memory_id
        self.score = score

    def __getitem__(self, key):
        if isinstance(key, int):
            if key == 0:
                return self.memory_id
            if key == 1:
                return self.score
            raise IndexError("Index out of range")
        return super().__getitem__(key)

    def __iter__(self):
        yield self.memory_id
        yield self.score


class VectorStore:
    def __init__(self, dimension: Optional[int] = None, index_path: Optional[str] = None):
        self._index = None
        self._id_to_index = {}
        self._index_to_id = []
        self._embeddings = {}
        self._metadata = {}
        self._id_map = {}

        self.dimension = dimension or (embedding_model.dimension if embedding_model else 384)
        if index_path:
            self._index_path = Path(index_path) / "index.faiss"
            self._meta_path = Path(index_path) / "meta.json"
        else:
            self._index_path = Path(settings.vector_store_dir) / "faiss_index"
            self._meta_path = Path(settings.vector_store_dir) / "meta.json"

        self._is_loaded = False
        self.load()
    

    def _save_mappings(self):
        """Save mappings to disk."""
        if not self._index_path:
            return
        
        try:
            import json
            mappings_path = self._index_path.parent / "mappings.json"
            mappings_data = {
                "id_to_index": self._id_to_index,
                "index_to_id": self._index_to_id,
                "embeddings": {k: v for k, v in self._embeddings.items()}
            }
            with open(mappings_path, 'w') as f:
                json.dump(mappings_data, f)
        except Exception as e:
            logger.error(f"Failed to save mappings: {e}")
    
    def _load_mappings(self):
        """Load mappings from disk."""
        if not self._index_path:
            return
        
        try:
            import json
            mappings_path = self._index_path.parent / "mappings.json"
            if mappings_path.exists():
                with open(mappings_path, 'r') as f:
                    mappings_data = json.load(f)
                    self._id_to_index = mappings_data.get("id_to_index", {})
                    self._index_to_id = mappings_data.get("index_to_id", [])
                    self._embeddings = mappings_data.get("embeddings", {})
        except Exception as e:
            logger.error(f"Failed to load mappings: {e}")


    def load(self):
        if self._is_loaded:
            return
        
        try:
            import faiss
            if not self._index_path.exists():
                self._index = faiss.IndexFlatIP(self.dimension)
                self._is_loaded = True
                return
            
  
          self._index = faiss.read_index(str(self._index_path))
            logger.info(f"Loaded FAISS index from {self._index_path}")

            # Load metadata and index mappings
            import json
            if self._meta_path.exists():
                with open(self._meta_path, "r") as f:
                    meta_data = json.load(f)
                    self._metadata = meta_data.get("metadata", {})
                    self._id_to_index = meta_data.get("id_to_index", {})
                    self._index_to_id = meta_data.get("index_to_id", [])
                    self._embeddings = meta_data.get("embeddings", {})
                    # Safely rebuild id_map
                    id_map_raw = meta_data.get("id_map", {})
                    self._id_map = {int(k): v for k, v in id_map_raw.items()}

            self._is_loaded = True
        except ImportError:
            logger.warning("FAISS not installed. Vector search will not be available.")
            self._index = None
            self._is_loaded = True
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            self._index = None
            self._is_loaded = True
        self._load_mappings()
    
    def save(self):
        if self._index is None:
            logger.warning("No FAISS index to save")
            return
        
        try:
            import faiss
            self._index_path.parent.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self._index, str(self._index_path))

            # Save metadata and index mappings
            import json
            meta_data = {
                "metadata": self._metadata,
                "id_to_index": self._id_to_index,
                "index_to_id": self._index_to_id,
                "embeddings": self._embeddings,
                "id_map": {str(k): v for k, v in self._id_map.items()}
            }
            with open(self._meta_path, "w") as f:
                json.dump(meta_data, f)
            logger.info(f"Saved 
FAISS index to {self._index_path}")
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")
    
    @property
    def count(self) -> int:
        if self._index is None:
            return 0
        return self._index.ntotal

    @property
    def _count(self) -> int:
        return self.count
    
    @property
    def is_available(self) -> bool:
        return self._index is not None and self._is_loaded
    
    def add_vector(self, memory_id: str, embedding: List[float]) -> bool:
        if not self.is_available:
            return False
        
        try:
            import faiss
            vector = np.array([embedding], dtype=np.float32)
            faiss.normalize_L2(vector)  # Normalized inner product = Cosine similarity
            self._index.add(vector)
            index = self._index.ntotal - 1
            self._id_to_index[memory_id] = index
            self._index_to_id.append(memory_id)
            self._id_map[index] = memory_id
            self._embeddings[memory_id] = embedding
            return True
        except Exception as e:
            logger.error(f"Failed to add vector for {memory_id}: {e}")
            return False

    def add(self, memory_id: str, content: str, embedding: List[float], metadata: Optional[Dict] = None) -> bool:
        """Compatibility wrapper for testing"""
        self._metadata[memory_id] = {**(metadata or {}), "content": content, "_deleted": False}
        return self.add_vector(memory_id, embedding)
    
    def search(self, query_embedding: List[float], k: int = 10) -> List[SearchResultDict]:
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
                if idx < 0 or idx >= len(self._index_to_id):
                    continue
                memory_id = self._index_to_id[idx]
                if memory_id is None:
                    continue

                # Check if soft deleted in test metadata
                if self._metadata.get(memory_id, {}).get("_deleted"):
                    continue

                score = float(distances[0][i])
                results.append(SearchResultDict(memory_id, score))
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
                index = self._id_to_index[memory_id]
                del self._id_to_index[memory_id]
                
                if index < len(self._index_to_id):
                    self._index_to_id[index] = None
                
                if memory_id in self._embeddings:
                    del self._embeddings[memory_id]
                
                self._rebuild_index_after_removal()
            return True
        except Exception as e:
            logger.error(f"Failed to remove vector: {e}")
            return False

    def delete(self, memory_id: str) -> bool:
        """Soft delete compatibility wrapper for testing"""
        if memory_id in self._metadata:
            self._metadata[memory_id]["_deleted"] = True
            return True
        return False
    
    def rebuild_index(se
lf) -> bool:
        if not self.is_available:
            return False
        try:
            import faiss
            new_index = faiss.IndexFlatIP(self.dimension)
            self._id_to_index = {}
            self._index_to_id = []
            self._id_map = {}
            for memory_id, embedding in self._embeddings.items():
                vector = np.array([embedding], dtype=np.float32)
                faiss.normalize_L2(vector)
                new_index.add(vector)
                index = new_index.ntotal - 1
                self._id_to_index[memory_id] = index
                self._index_to_id.append(memory_id)
                self._id_map[index] = memory_id
            self._index = new_index
            return True
        except Exception as e:
            logger.error(f"Failed to rebuild index: {e}")
            return False

    def _rebuild_index_after_removal(self):
        """Rebuild the FAISS index after removing vectors."""
        self.rebuild_index()


def get_vector_store() -> VectorStore:
    return vector_store


vector_store = VectorStore()
vector_store.load()

# Alias for backward compatibility with backend/tests/
FAISSVectorStore = VectorStore
