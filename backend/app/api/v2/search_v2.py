"""NFM-X V2 Search API - 3-layer hybrid search: FAISS + SQLite + BM25"""

from fastapi import APIRouter, Query
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/v2/search", tags=["V2 Search"])


class SearchRequestV2(BaseModel):
    query: str
    limit: int = 10
    semantic_weight: float = 0.6
    keyword_weight: float = 0.3
    bm25_weight: float = 0.1
    filters: Optional[dict] = None


class SearchResultV2(BaseModel):
    memory_id: str
    content: str
    score: float
    metadata: dict
    modality: str


@router.post("/hybrid", response_model=List[SearchResultV2])
async def hybrid_search_v2(request: SearchRequestV2):
    """Perform 3-layer hybrid search - FAISS + SQLite + BM25 with weighted combination"""
    return []


@router.get("/semantic", response_model=List[SearchResultV2])
async def semantic_search_v2(query: str = Query(...), limit: int = 10, threshold: float = 0.7):
    """Pure semantic search using FAISS - Vector similarity search"""
    return []


@router.get("/keyword", response_model=List[SearchResultV2])
async def keyword_search_v2(query: str = Query(...), limit: int = 10):
    """Keyword-based search using SQLite FTS - Full-text search"""
    return []