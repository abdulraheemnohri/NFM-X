"""
Search API for NFM-X
"""
from typing import Optional, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from ..storage.database import get_db_session
from ..retrieval.engine import HybridRetrievalEngine, RetrievalQuery, SearchMode
from .memory import MemoryResponse


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=1000)
    search_mode: SearchMode = SearchMode.HYBRID


class SearchResponse(BaseModel):
    query: str
    results: List[MemoryResponse]
    scores: List[float]
    total: int
    search_mode: str
    execution_time_ms: float


router = APIRouter(prefix="/memory", tags=["Search"])


@router.post("/search", response_model=SearchResponse)
async def search_memories(request: SearchRequest, db_session: AsyncSession = Depends(get_db_session)) -> SearchResponse:
    import time
    start_time = time.time()
    retrieval_query = RetrievalQuery(query=request.query, limit=request.limit, search_mode=request.search_mode)
    engine = HybridRetrievalEngine()
    results = await engine.search(db_session, retrieval_query)
    from .memory import _memory_to_response
    return SearchResponse(query=request.query, results=[_memory_to_response(r.memory) for r in results], scores=[r.score for r in results], total=len(results), search_mode=request.search_mode.value, execution_time_ms=round((time.time() - start_time) * 1000, 2))
