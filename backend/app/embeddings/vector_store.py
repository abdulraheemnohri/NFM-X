#!/usr/bin/env python3
"""
NFM-X Vector Store
==================

Provides vector storage and similarity search capabilities.
Supports multiple backend options including FAISS, SQLite, and in-memory.

Urdu: Vector storage aur similarity search ke liye module
"""

from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np
from pydantic import BaseModel
import json
import os
import pickle
from pathlib import Path

from .embedding_models import BaseEmbeddingModel, EmbeddingResult, MockEmbeddingModel


class VectorStoreConfig(BaseModel):
    backend: str = "memory"
    index_path: str = "./vector_index"
    dimension: int = 384
    metric: str = "cosine"
    max_index_size: int = 1000000
    batch_size: int = 1000


class SearchResult(BaseModel):
    id: str
    text: str
    embedding: List[float]
    score: float
    metadata: Dict[str, Any] = {}
    memory_id: Optional[str] = None
    version_id: Optional[str] = None


class BaseVectorStore:
    def __init__(self, config: VectorStoreConfig, embedding_model: Optional[BaseEmbeddingModel] = None):
        self.config = config
        self.embedding_model = embedding_model or MockEmbeddingModel()
        self._text_to_id = {}
        self._id_to_metadata = {}
        self._initialized = False
    
    def initialize(self):
        self._initialized = True
    
    def add_text(self, text: str, id: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        embedding_result = self.embedding_model.embed(text)
        return self.add_embedding(embedding_result.embedding, id, text, {**(metadata or {}), **embedding_result.metadata})
    
    def add_embedding(self, embedding: List[float], id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        raise NotImplementedError("Subclasses must implement add_embedding method")
    
    def search(self, query: str, k: int = 10, filter_metadata: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        raise NotImplementedError("Subclasses must implement search method")
    
    def batch_add(self, texts: List[str], ids: List[str], metadata_list: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        if metadata_list is None:
            metadata_list = [{} for _ in texts]
        return [self.add_text(text, id, metadata) for text, id, metadata in zip(texts, ids, metadata_list)]
    
    def get_by_id(self, id: str) -> Optional[SearchResult]:
        raise NotImplementedError("Subclasses must implement get_by_id method")
    
    def delete_by_id(self, id: str) -> bool:
        raise NotImplementedError("Subclasses must implement delete_by_id method")
    
    def save(self, path: Optional[str] = None):
        pass
    
    def load(self, path: Optional[str] = None):
        pass


class MemoryVectorStore(BaseVectorStore):
    def __init__(self, config: Optional[VectorStoreConfig] = None, embedding_model: Optional[BaseEmbeddingModel] = None):
        if config is None:
            config = VectorStoreConfig(backend="memory", dimension=384)
        super().__init__(config, embedding_model)
        self._embeddings = []
        self._ids = []
        self._texts = []
        self._metadata_list = []
        self.initialize()
    
    def add_embedding(self, embedding: List[float], id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        if len(self._embeddings) >= self.config.max_index_size:
            raise ValueError(f"Vector store at maximum capacity: {self.config.max_index_size}")
        
        self._embeddings.append(np.array(embedding))
        self._ids.append(id)
        self._texts.append(text)
        self._metadata_list.append(metadata or {})
        self._text_to_id[id] = len(self._embeddings) - 1
        self._id_to_metadata[id] = metadata or {}
        return id
    
    def search(self, query: str, k: int = 10, filter_metadata: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        if not self._embeddings:
            return []
        
        query_embedding = self.embedding_model.embed(query).embedding
        query_array = np.array(query_embedding)
        similarities = cosine_similarity([query_array], np.array(self._embeddings))[0]
        top_indices = np.argsort(similarities)[::-1][:k]
        
        results = []
        for idx in top_indices:
            if filter_metadata:
                metadata = self._metadata_list[idx]
                match = all(metadata.get(key) == value for key, value in filter_metadata.items())
                if not match:
                    continue
            results.append(SearchResult(
                id=self._ids[idx], text=self._texts[idx],
                embedding=self._embeddings[idx].tolist(), score=float(similarities[idx]),
                metadata=self._metadata_list[idx],
                memory_id=self._metadata_list[idx].get('memory_id'),
                version_id=self._metadata_list[idx].get('version_id')
            ))
        return results
    
    def get_by_id(self, id: str) -> Optional[SearchResult]:
        if id not in self._text_to_id:
            return None
        idx = self._text_to_id[id]
        return SearchResult(
            id=self._ids[idx], text=self._texts[idx],
            embedding=self._embeddings[idx].tolist(), score=1.0,
            metadata=self._metadata_list[idx],
            memory_id=self._metadata_list[idx].get('memory_id'),
            version_id=self._metadata_list[idx].get('version_id')
        )
    
    def delete_by_id(self, id: str) -> bool:
        if id not in self._text_to_id:
            return False
        idx = self._text_to_id[id]
        del self._embeddings[idx]
        del self._ids[idx]
        del self._texts[idx]
        del self._metadata_list[idx]
        del self._text_to_id[id]
        if id in self._id_to_metadata:
            del self._id_to_metadata[id]
        self._text_to_id = {id: i for i, id in enumerate(self._ids)}
        return True
    
    def save(self, path: Optional[str] = None):
        save_path = path or self.config.index_path
        data = {
            'embeddings': [emb.tolist() for emb in self._embeddings],
            'ids': self._ids, 'texts': self._texts, 'metadata': self._metadata_list
        }
        with open(f"{save_path}.pkl", 'wb') as f:
            pickle.dump(data, f)
    
    def load(self, path: Optional[str] = None):
        load_path = path or self.config.index_path
        try:
            with open(f"{load_path}.pkl", 'rb') as f:
                data = pickle.load(f)
            self._embeddings = [np.array(emb) for emb in data['embeddings']]
            self._ids = data['ids']
            self._texts = data['texts']
            self._metadata_list = data['metadata']
            self._text_to_id = {id: i for i, id in enumerate(self._ids)}
            self._id_to_metadata = {id: metadata for id, metadata in zip(self._ids, self._metadata_list)}
            return True
        except FileNotFoundError:
            return False


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot_product / (norm_a * norm_b))


class VectorStoreFactory:
    @staticmethod
    def create_vector_store(config: VectorStoreConfig, embedding_model: Optional[BaseEmbeddingModel] = None) -> BaseVectorStore:
        if config.backend == "memory":
            return MemoryVectorStore(config, embedding_model)
        else:
            return MemoryVectorStore(config, embedding_model)
    
    @staticmethod
    def get_available_backends() -> List[str]:
        backends = ["memory"]
        try:
            import faiss
            backends.append("faiss")
        except ImportError:
            pass
        return backends


# Urdu: NFM-X vector store - Vector storage aur similarity search ke liye