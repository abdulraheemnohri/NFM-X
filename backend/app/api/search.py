"""
NFM-X Search API
Endpoints for memory search operations
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from ..memory.retrieval import get_retrieval_engine

router = APIRouter(prefix="/memory", tags=["Search"])


class SearchRequest(BaseModel):
    query: str
    agent_id: Optional[str] = None
    limit: Optional[int] = 20
    memory_types: Optional[List[str]] = None
    include_history: Optional[bool] = True
    include_contradictions: Optional[bool] = True


class SearchResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    count: int


@router.post("/search")
async def search_memories(
    request: SearchRequest,
    retrieval_engine=Depends(get_retrieval_engine)
):
    """Search memories using hybrid retrieval"""
    results = await retrieval_engine.retrieve(
        query=request.query,
        agent_id=request.agent_id,
        limit=request.limit or 20,
        memory_types=request.memory_types,
        include_history=request.include_history or True,
        include_contradictions=request.include_contradictions or True
    )
    return SearchResponse(query=request.query, results=results, count=len(results))