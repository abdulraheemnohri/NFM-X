"""
NFM-X Search API
"""
from fastapi import APIRouter, Depends, Query
from typing import List
from pydantic import BaseModel
from ..retrieval.engine import RetrievalEngine

router = APIRouter(prefix="/memory", tags=["Search"])

class SearchRequest(BaseModel):
    query: str
    limit: int = 10

class SearchResponse(BaseModel):
    query: str
    results: List[dict]
    total: int
    search_type: str

@router.get("/search", response_model=SearchResponse)
async def search_memories(query: str = Query(...), limit: int = 10):
    retrieval = RetrievalEngine()
    results, total = await retrieval.hybrid_search(query, limit)
    return SearchResponse(query=query, results=results, total=total, search_type="hybrid")