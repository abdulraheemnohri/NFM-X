from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from backend.app.storage.database import get_db_session
from backend.app.retrieval.engine import get_retrieval_engine

router = APIRouter()

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    agent_id: Optional[str] = None
    limit: Optional[int] = Field(20, ge=1, le=100)
    memory_types: Optional[List[str]] = None

class SearchResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    count: int

@router.post("/search", response_model=SearchResponse)
async def search_memories(
    request: SearchRequest,
    db_session=Depends(get_db_session),
    engine=Depends(get_retrieval_engine)
):
    results = await engine.retrieve(
        db_session=db_session,
        query=request.query,
        agent_id=request.agent_id,
        limit=request.limit or 20,
        memory_types=request.memory_types
    )
    return SearchResponse(
        query=request.query,
        results=results,
        count=len(results)
    )
