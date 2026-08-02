"""
Embeddings module
"""
from .models import EmbeddingModel
from .vector_store import FAISSVectorStore

__all__ = ["EmbeddingModel", "FAISSVectorStore"]