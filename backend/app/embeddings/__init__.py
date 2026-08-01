"""
NFM-X Embeddings Module
Vector embeddings and similarity search
"""

from .vector_store import VectorStore, init_vector_store, shutdown_vector_store
from .embedding_models import EmbeddingModel, get_embedding_model

__all__ = [
    "VectorStore",
    "init_vector_store", 
    "shutdown_vector_store",
    "EmbeddingModel",
    "get_embedding_model"
]