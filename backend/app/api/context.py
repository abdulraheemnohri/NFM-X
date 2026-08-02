"""
Context API for NFM-X
Builds context for LLM prompts from relevant memories
"""
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..storage.database import get_db_session
from ..retrieval.engine import HybridRetrievalEngine, RetrievalQuery, SearchMode
from ..memory.models import MemoryType, MemoryStatus
from .memory import MemoryResponse


# REQUEST MODELS
class ContextRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=100)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    memory_types: Optional[List[MemoryType]] = None
    exclude_types: Optional[List[MemoryType]] = None
    min_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    min_importance: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    include_metadata: bool = False
    format: str = "text"


class ContextResponse(BaseModel):
    query: str
    context: str
    memories: List[MemoryResponse]
    total_memories: int
    total_tokens_estimated: int
    execution_time_ms: float


# ROUTER
router = APIRouter(prefix="/memory", tags=["Context"])


@router.post("/context", response_model=ContextResponse)
async def build_context(request: ContextRequest, db_session: AsyncSession = Depends(get_db_session)) -> ContextResponse:
    import time
    start_time = time.time()
    retrieval_query = RetrievalQuery(query=request.query, limit=request.limit * 2, search_mode=SearchMode.HYBRID)
    engine = HybridRetrievalEngine()
    results = await engine.search(db_session, retrieval_query)
    context = "\n\n---\n\n".join([r.memory.content for r in results[:request.limit]])
    execution_time = (time.time() - start_time) * 1000
    from .memory import _memory_to_response
    return ContextResponse(query=request.query, context=context, memories=[_memory_to_response(r.memory) for r in results[:request.limit]], total_memories=len(results), total_tokens_estimated=sum(len(m.content) // 4 for m in [r.memory for r in results[:request.limit]]), execution_time_ms=round(execution_time, 2))


@router.post("/context/for-prompt")
async def build_prompt_context(request: ContextRequest, db_session: AsyncSession = Depends(get_db_session)) -> Dict[str, Any]:
    import time
    start_time = time.time()
    context_response = await build_context(request, db_session)
    prompt_context = f"Relevant Context:\n{context_response.context}\n\n---\n"
    return {"prompt": prompt_context, "context": context_response.context, "memories_used": context_response.total_memories, "tokens_estimated": context_response.total_tokens_estimated, "execution_time_ms": round((time.time() - start_time) * 1000, 2)}
