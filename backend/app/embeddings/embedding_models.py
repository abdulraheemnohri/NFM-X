#!/usr/bin/env python3
"""
NFM-X Embedding Models
======================

Provides embedding generation for different types of content.
Supports multiple embedding models and providers.

Urdu: Alag alag qism ke content ke liye embeddings banane ka module
"""

from typing import Dict, Any, List, Optional, Union
import numpy as np
from pydantic import BaseModel
import hashlib
import json


class EmbeddingConfig(BaseModel):
    model_name: str = "all-MiniLM-L6-v2"
    dimension: int = 384
    provider: str = "sentence-transformers"
    batch_size: int = 32
    normalize: bool = True
    device: str = "cpu"


class EmbeddingResult(BaseModel):
    text: str
    embedding: List[float]
    model: str
    dimension: int
    checksum: str
    metadata: Dict[str, Any] = {}


class BaseEmbeddingModel:
    def __init__(self, config: EmbeddingConfig):
        self.config = config
    
    def embed(self, text: str) -> EmbeddingResult:
        raise NotImplementedError("Subclasses must implement embed method")
    
    def batch_embed(self, texts: List[str]) -> List[EmbeddingResult]:
        return [self.embed(text) for text in texts]
    
    def _generate_checksum(self, text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def _normalize_embedding(self, embedding: np.ndarray) -> np.ndarray:
        if self.config.normalize:
            norm = np.linalg.norm(embedding)
            if norm > 0:
                return embedding / norm
        return embedding


class MockEmbeddingModel(BaseEmbeddingModel):
    def __init__(self, config: Optional[EmbeddingConfig] = None):
        if config is None:
            config = EmbeddingConfig(dimension=384)
        super().__init__(config)
    
    def embed(self, text: str) -> EmbeddingResult:
        checksum = self._generate_checksum(text)
        hash_int = int(checksum[:16], 16)
        np.random.seed(hash_int % (2**32))
        
        embedding = np.random.randn(self.config.dimension).tolist()
        embedding_array = np.array(embedding)
        normalized_embedding = self._normalize_embedding(embedding_array)
        
        return EmbeddingResult(
            text=text, embedding=normalized_embedding.tolist(),
            model=self.config.model_name, dimension=self.config.dimension,
            checksum=checksum, metadata={"provider": "mock", "deterministic": True}
        )


class SentenceTransformerEmbeddingModel(BaseEmbeddingModel):
    def __init__(self, config: Optional[EmbeddingConfig] = None):
        if config is None:
            config = EmbeddingConfig(
                model_name="all-MiniLM-L6-v2", dimension=384, provider="sentence-transformers"
            )
        super().__init__(config)
        self._model = None
    
    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.config.model_name, device=self.config.device)
        except ImportError:
            raise ImportError("sentence-transformers library is required")
    
    def embed(self, text: str) -> EmbeddingResult:
        if self._model is None:
            self._load_model()
        
        embedding = self._model.encode(text, convert_to_tensor=False)
        embedding_array = np.array(embedding)
        normalized_embedding = self._normalize_embedding(embedding_array)
        checksum = self._generate_checksum(text)
        
        return EmbeddingResult(
            text=text, embedding=normalized_embedding.tolist(),
            model=self.config.model_name, dimension=len(embedding),
            checksum=checksum, metadata={"provider": "sentence-transformers", "model": self.config.model_name}
        )
    
    def batch_embed(self, texts: List[str]) -> List[EmbeddingResult]:
        if self._model is None:
            self._load_model()
        
        embeddings = self._model.encode(texts, convert_to_tensor=False, batch_size=self.config.batch_size)
        
        results = []
        for i, text in enumerate(texts):
            embedding_array = np.array(embeddings[i])
            normalized_embedding = self._normalize_embedding(embedding_array)
            checksum = self._generate_checksum(text)
            
            results.append(EmbeddingResult(
                text=text, embedding=normalized_embedding.tolist(),
                model=self.config.model_name, dimension=len(embeddings[i]),
                checksum=checksum, metadata={"provider": "sentence-transformers", "model": self.config.model_name, "batch": True}
            ))
        return results


class EmbeddingModelFactory:
    @staticmethod
    def create_model(config: EmbeddingConfig) -> BaseEmbeddingModel:
        if config.provider == "sentence-transformers":
            return SentenceTransformerEmbeddingModel(config)
        elif config.provider == "mock":
            return MockEmbeddingModel(config)
        else:
            return MockEmbeddingModel(config)
    
    @staticmethod
    def get_available_models() -> List[str]:
        return ["sentence-transformers", "mock"]


# Urdu: NFM-X embedding models - Content ke liye embeddings banane ke liye