"""
NFM-X Embedding Models
Sentence transformer models for embedding generation
"""
from typing import List, Optional
import logging
import numpy as np

from ..config import settings

logger = logging.getLogger(__name__)


class EmbeddingModel:
    def __init__(self, model_name: str = None, dimension: int = None):
        self.model_name = model_name or settings.embedding_model_name
        self.dimension = dimension or settings.embedding_dimension
        self._model = None
        self._is_loaded = False
    
    def load(self):
        if self._is_loaded:
            return
        
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            test_embedding = self._model.encode(["test"])
            self.dimension = test_embedding.shape[1]
            self._is_loaded = True
            logger.info(f"Embedding model loaded (dimension: {self.dimension})")
        except ImportError:
            logger.warning("sentence-transformers not installed. Using mock embeddings.")
            self._model = None
            self._is_loaded = False
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self._model = None
            self._is_loaded = False
    
    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        if not self._is_loaded and self._model is None:
            self.load()
        
        if self._model is None:
            return self._generate_mock_embeddings(texts)
        
        try:
            embeddings = self._model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return self._generate_mock_embeddings(texts)
    
    def encode_single(self, text: str) -> List[float]:
        embeddings = self.encode([text])
        return embeddings[0].tolist()
    
    def _generate_mock_embeddings(self, texts: List[str]) -> np.ndarray:
        embeddings = []
        for text in texts:
            import hashlib
            hash_obj = hashlib.sha256(text.encode()).hexdigest()
            embedding = []
            for i in range(self.dimension):
                char_val = ord(hash_obj[i % len(hash_obj)]) / 255.0
                embedding.append((char_val * 2) - 1)
            embeddings.append(embedding)
        return np.array(embeddings)
    
    @property
    def is_available(self) -> bool:
        return self._is_loaded and self._model is not None


embedding_model = EmbeddingModel()
embedding_model.load()


def get_embedding_model() -> EmbeddingModel:
    return embedding_model