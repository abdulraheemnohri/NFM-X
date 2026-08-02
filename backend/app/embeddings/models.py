"""
Embedding model wrapper for NFM-X
"""
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum
import numpy as np
from ..config import settings

class EmbeddingBackend(str, Enum):
    SENTENCE_TRANSFORMERS = "sentence_transformers"

@dataclass
class EmbeddingConfig:
    model_name: str = settings.embedding_model
    backend: EmbeddingBackend = EmbeddingBackend.SENTENCE_TRANSFORMERS
    device: str = "cpu"
    batch_size: int = 32
    normalize: bool = True

class EmbeddingModel:
    def __init__(self, config=None):
        self.config = config or EmbeddingConfig()
        self._model = None
        self._is_loaded = False

    def _load_model(self):
        if self._is_loaded:
            return
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.config.model_name)
            self._is_loaded = True
        except ImportError:
            raise ImportError("sentence-transformers not installed")

    def encode(self, text: str):
        self._load_model()
        return self._model.encode(text, normalize_embeddings=self.config.normalize)

    def encode_batch(self, texts: List[str]):
        self._load_model()
        return self._model.encode(texts, batch_size=self.config.batch_size, normalize_embeddings=self.config.normalize)

    @property
    def dimension(self):
        self._load_model()
        return self._model.get_sentence_embedding_dimension()

embedding_model = EmbeddingModel()