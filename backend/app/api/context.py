"""
NFM-X Context API
"""
from fastapi import APIRouter, Depends
from typing import Optional, List
from pydantic import BaseModel
from ..retrieval.engine import RetrievalEngine

router = APIRouter(prefix="/memory", tags=["Context"])

class ContextRequest(BaseModel):
    query: Optional[str] = None
    memory_ids: Optional[List[str]] = None
    max_tokens: int = 4000

class ContextResponse(BaseModel):
    context: str
    memory_count: int

@router.post("/context", response_model=ContextResponse)
async def build_context(request: ContextRequest):
    retrieval = RetrievalEngine()
    memories, scores = await retrieval.get_context_memories(
        query=request.query,
        memory_ids=request.memory_ids,
        limit=request.max_tokens
    )
    context = "\n".join([f"Memory {m.id}: {m.content}" for m in memories])
    return ContextResponse(context=context, memory_count=len(memories))