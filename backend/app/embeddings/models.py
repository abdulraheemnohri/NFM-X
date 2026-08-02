"""
NFM-X Embedding Models
"""
from ..config import settings
import numpy as np

class EmbeddingModel:
    def __init__(self):
        self.model_name = settings.embedding_model_name
        self.dimension = settings.embedding_dimension
        self._model = None
    
    def encode_single(self, text: str) -> list:
        return [0.1] * self.dimension
    
    @property
    def is_available(self) -> bool:
        return True

embedding_model = EmbeddingModel()