"""
NFM-X Evolution API
Endpoints for memory evolution operations
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy import select

from ..storage.database import get_db_session
from ..memory.models import Memory, MemoryVersion, MemoryEvent, ChangeType
from ..memory.evolution import get_evolution_engine

router = APIRouter(prefix="/memory", tags=["Evolution"])


class EvolveRequest(BaseModel):
    memory_id: str
    new_content: Optional[str] = None
    change_type: Optional[str] = None
    change_reason: Optional[str] = None
    evidence: Optional[List[Dict[str, Any]]] = None
    agent_id: Optional[str] = None


class ConfirmRequest(BaseModel):
    memory_id: str
    agent_id: Optional[str] = None
    confidence_boost: Optional[float] = 0.1


class ContradictRequest(BaseModel):
    memory_id: str
    contradiction: str
    evidence: Optional[List[Dict[str, Any]]] = None
    agent_id: Optional[str] = None


@router.post("/evolve")
async def evolve_memory(
    request: EvolveRequest,
    evolution_engine=Depends(get_evolution_engine),
    db_session=Depends(get_db_session)
):
    """Evolve a memory based on new information"""
    async with db_session.begin():
        stmt = select(Memory).where(Memory.id == request.memory_id)
        result = await db_session.execute(stmt)
        memory = result.scalar_one_or_none()
        if memory is None:
            raise HTTPException(status_code=404, detail="Memory not found")
        new_version = await evolution_engine.evolve(
            session=db_session,
            memory=memory,
            new_content=request.new_content,
            change_type=request.change_type,
            change_reason=request.change_reason,
            evidence=request.evidence,
            agent_id=request.agent_id or memory.agent_id
        )
        return {
            "message": "Memory evolved successfully",
            "memory_id": request.memory_id,
            "new_version": new_version.version,
            "change_type": new_version.change_type.value
        }