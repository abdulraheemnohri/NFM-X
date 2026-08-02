"""
Embeddings module for NFM-X
"""
from .models import EmbeddingModel
from .vector_store import VectorStore, FAISSVectorStore

__all__ = ["EmbeddingModel", "VectorStore", "FAISSVectorStore"]