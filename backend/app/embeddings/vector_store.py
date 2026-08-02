"""
FAISS vector store for NFM-X
"""
from typing import Optional, Dict, Any, List, Tuple
import numpy as np
import faiss
import pickle
import os
import logging
from ..config import settings
from .models import embedding_model

logger = logging.getLogger(__name__)

class FAISSVectorStore:
    def __init__(self, dimension=settings.embedding_dimension, index_path=None):
        self.dimension = dimension
        self.index_path = index_path or settings.faiss_index_path
        self.metadata_path = f"{self.index_path}.meta.pkl"
        self.index = None
        self.metadata = []
        self.id_to_index = {}
        self._initialize_index()

    def _initialize_index(self):
        self.index = faiss.IndexFlatIP(self.dimension)

    def add(self, vectors, metadata):
        if self.index is None:
            self._initialize_index()
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"Vector dimension mismatch")
        ids = [str(i + len(self.metadata)) for i in range(len(vectors))]
        if len(vectors) > 0:
            self.index.add(vectors)
        for i, meta in enumerate(metadata):
            idx = len(self.metadata) + i
            self.metadata.append({**meta, "_vector_id": ids[i], "_index": idx})
            self.id_to_index[ids[i]] = idx
        return ids

    def search(self, query_vector, k=10):
        if self.index is None or self.index.ntotal == 0:
            return [], []
        query_vector = query_vector.reshape(1, -1)
        faiss.normalize_L2(query_vector)
        distances, indices = self.index.search(query_vector, k)
        scores = distances[0].tolist()
        result_indices = indices[0].tolist()
        ids = [self.metadata[idx].get("_vector_id", str(idx)) for idx in result_indices if 0 <= idx < len(self.metadata)]
        return ids, scores

    def get_metadata_by_id(self, vector_id):
        return self.metadata[self.id_to_index[vector_id]] if vector_id in self.id_to_index else None

    def save(self, path=None):
        save_path = path or self.index_path
        meta_path = path or self.metadata_path
        if self.index is not None:
            faiss.write_index(self.index, save_path)
            with open(meta_path, 'wb') as f:
                pickle.dump({"metadata": self.metadata, "id_to_index": self.id_to_index}, f)

    def load(self, path=None):
        load_path = path or self.index_path
        meta_path = path or self.metadata_path
        try:
            self.index = faiss.read_index(load_path)
            self.dimension = self.index.d
            if os.path.exists(meta_path):
                with open(meta_path, 'rb') as f:
                    data = pickle.load(f)
                    self.metadata = data.get("metadata", [])
                    self.id_to_index = data.get("id_to_index", {})
        except Exception:
            self._initialize_index()

    def clear(self):
        self.index = None
        self.metadata = []
        self.id_to_index = {}
        self._initialize_index()

    @property
    def count(self):
        return self.index.ntotal if self.index is not None else 0

vector_store = FAISSVectorStore()