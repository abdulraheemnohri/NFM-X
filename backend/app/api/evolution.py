"""
NFM-X Evolution API
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
async def evolve_memory(request: EvolveRequest, evolution_engine=Depends(get_evolution_engine), db_session=Depends(get_db_session)):
    async with db_session.begin():
        stmt = select(Memory).where(Memory.id == request.memory_id)
        result = await db_session.execute(stmt)
        memory = result.scalar_one_or_none()
        if memory is None: raise HTTPException(status_code=404, detail="Memory not found")
        new_version = await evolution_engine.evolve(session=db_session, memory=memory, new_content=request.new_content, change_type=request.change_type, change_reason=request.change_reason, evidence=request.evidence, agent_id=request.agent_id or memory.agent_id)
        return {"message": "Memory evolved successfully", "memory_id": request.memory_id, "new_version": new_version.version, "change_type": new_version.change_type.value}

@router.post("/confirm")
async def confirm_memory(request: ConfirmRequest, db_session=Depends(get_db_session)):
    async with db_session.begin():
        stmt = select(Memory).where(Memory.id == request.memory_id)
        result = await db_session.execute(stmt)
        memory = result.scalar_one_or_none()
        if memory is None: raise HTTPException(status_code=404, detail="Memory not found")
        new_confidence = min(1.0, memory.confidence + (request.confidence_boost or 0.1))
        memory.confidence = new_confidence
        new_version = MemoryVersion(id=str(uuid.uuid4()), memory_id=memory.id, version=memory.version + 1, content=memory.content, normalized_content=memory.normalized_content, content_hash=memory.content_hash, confidence=new_confidence, importance=memory.importance, status=memory.status, metadata=memory.metadata, change_type=ChangeType.REINFORCE, change_reason="Memory confirmed by agent", created_at=datetime.utcnow(), actor_id=request.agent_id or memory.agent_id, actor_type="agent")
        db_session.add(new_version)
        memory.version += 1
        event = MemoryEvent(id=str(uuid.uuid4()), memory_id=memory.id, event_type="confirm", details={"old_confidence": memory.confidence - (request.confidence_boost or 0.1), "new_confidence": new_confidence}, timestamp=datetime.utcnow(), agent_id=request.agent_id or memory.agent_id, actor_type="agent")
        db_session.add(event)
        return {"message": "Memory confirmed", "memory_id": request.memory_id, "new_confidence": new_confidence}

@router.post("/contradict")
async def contradict_memory(request: ContradictRequest, db_session=Depends(get_db_session)):
    async with db_session.begin():
        stmt = select(Memory).where(Memory.id == request.memory_id)
        result = await db_session.execute(stmt)
        memory = result.scalar_one_or_none()
        if memory is None: raise HTTPException(status_code=404, detail="Memory not found")
        from ..memory.models import MemoryConflict
        contradiction_memory = Memory(id=str(uuid.uuid4()), root_id=memory.root_id, version=1, type="conflict", content=request.contradiction, normalized_content=request.contradiction, content_hash=str(uuid.uuid4())[:16], agent_id=request.agent_id or memory.agent_id, source_id=memory.id, confidence=0.7, importance=0.8, status="active", created_at=datetime.utcnow(), observed_at=datetime.utcnow(), valid_from=datetime.utcnow(), parent_id=memory.id, metadata={"contradicts": memory.id, "evidence": request.evidence})
        db_session.add(contradiction_memory)
        event = MemoryEvent(id=str(uuid.uuid4()), memory_id=memory.id, event_type="contradict", details={"contradiction_id": contradiction_memory.id, "contradiction": request.contradiction}, timestamp=datetime.utcnow(), agent_id=request.agent_id or memory.agent_id, actor_type="agent")
        db_session.add(event)
        return {"message": "Contradiction created", "original_memory_id": request.memory_id, "contradiction_memory_id": contradiction_memory.id}