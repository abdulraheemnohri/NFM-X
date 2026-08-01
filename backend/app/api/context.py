from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from backend.app.storage.database import get_db_session
from backend.app.retrieval.engine import get_retrieval_engine
from backend.app.config import settings

router = APIRouter()

class ContextRequest(BaseModel):
    agent_id: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    memory_types: Optional[List[str]] = None
    max_memories: Optional[int] = Field(None, ge=1, le=100)

class ContextResponse(BaseModel):
    agent_id: str
    query: str
    memories: List[Dict[str, Any]]
    total_tokens_estimate: int

@router.post("/context", response_model=ContextResponse)
async def build_context(
    request: ContextRequest,
    db_session=Depends(get_db_session),
    engine=Depends(get_retrieval_engine)
):
    limit = request.max_memories or settings.NFM_MAX_CONTEXT_MEMORIES

    results = await engine.retrieve(
        db_session=db_session,
        query=request.query,
        agent_id=request.agent_id,
        limit=limit,
        memory_types=request.memory_types
    )

    total_chars = sum(len(r["content"]) for r in results)
    token_estimate = total_chars // 4

    return ContextResponse(
        agent_id=request.agent_id,
        query=request.query,
        memories=results,
        total_tokens_estimate=token_estimate
    )
