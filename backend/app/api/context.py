"""
NFM-X Context API
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from ..memory.retrieval import get_retrieval_engine

router = APIRouter(prefix="/memory", tags=["Context"])

class ContextRequest(BaseModel):
    agent_id: str
    query: str
    task: Optional[str] = None
    max_memories: Optional[int] = 20

class ContextResponse(BaseModel):
    task: str
    current_state: Dict[str, Any]
    relevant_memories: List[Dict[str, Any]]
    important_history: List[Dict[str, Any]]
    preferences: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]
    decisions: List[Dict[str, Any]]
    skills: List[Dict[str, Any]]
    known_failures: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    uncertainties: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]

@router.post("/context")
async def build_context(request: ContextRequest, retrieval_engine=Depends(get_retrieval_engine)):
    context_pack = await retrieval_engine.build_context(agent_id=request.agent_id, query=request.query, task=request.task, max_memories=request.max_memories or 20)
    return ContextResponse(**context_pack)