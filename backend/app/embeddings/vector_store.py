import faiss
import numpy as np
import json
from typing import List, Optional, Dict, Any
from pathlib import Path

class FAISSVectorStore:
    def __init__(self, dimension: int = 384, index_path: str = "./storage/vectors"):
        self.dimension = dimension
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.index = faiss.IndexFlatIP(dimension)
        self._id_map = {}      # faiss_idx -> memory_id
        self._reverse_map = {} # memory_id -> faiss_idx
        self._metadata = {}    # memory_id -> metadata
        self._texts = {}       # memory_id -> text
        self._count = 0

    def _normalize(self, vector: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    def add(self, memory_id: str, text: str, vector: List[float], metadata: Optional[Dict] = None):
        vec = np.array([vector], dtype=np.float32)
        vec = self._normalize(vec)
        idx = self._count
        self.index.add(vec)
        self._id_map[idx] = memory_id
        self._reverse_map[memory_id] = idx
        self._metadata[memory_id] = metadata or {}
        self._texts[memory_id] = text
        self._count += 1

    def search(self, query_vector: List[float], k: int = 10) -> List[Dict[str, Any]]:
        if self._count == 0:
            return []
        vec = np.array([query_vector], dtype=np.float32)
        vec = self._normalize(vec)
        k = min(k, self._count)
        scores, indices = self.index.search(vec, k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            memory_id = self._id_map.get(int(idx))
            if memory_id:
                results.append({
                    "memory_id": memory_id,
                    "text": self._texts.get(memory_id, ""),
                    "score": float(score),
                    "metadata": self._metadata.get(memory_id, {})
                })
        return results

    def delete(self, memory_id: str) -> bool:
        if memory_id in self._metadata:
            self._metadata[memory_id]["_deleted"] = True
            return True
        return False

    def save(self):
        faiss.write_index(self.index, str(self.index_path / "index.faiss"))
        with open(self.index_path / "meta.json", "w") as f:
            json.dump({
                "id_map": {str(k): v for k, v in self._id_map.items()},
                "reverse_map": self._reverse_map,
                "metadata": self._metadata,
                "texts": self._texts,
                "count": self._count,
                "dimension": self.dimension
            }, f)

    def load(self):
        index_file = self.index_path / "index.faiss"
        meta_file = self.index_path / "meta.json"
        if index_file.exists() and meta_file.exists():
            self.index = faiss.read_index(str(index_file))
            with open(meta_file, "r") as f:
                data = json.load(f)
            self._id_map = {int(k): v for k, v in data["id_map"].items()}
            self._reverse_map = data["reverse_map"]
            self._metadata = data["metadata"]
            self._texts = data["texts"]
            self._count = data["count"]
            self.dimension = data["dimension"]

# Singleton
_vector_store = None

def get_vector_store() -> FAISSVectorStore:
    global _vector_store
    if _vector_store is None:
        from backend.app.config import settings
        _vector_store = FAISSVectorStore(
            dimension=settings.NFM_EMBEDDING_DIM,
            index_path=str(settings.NFM_VECTOR_PATH)
        )
        _vector_store.load()
    return _vector_store
