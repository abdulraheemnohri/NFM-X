from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
import uuid
import hashlib

from backend.app.storage.database import get_db_session
from backend.app.memory.models import Memory, MemoryVersion, MemoryEvent, MemoryType, MemoryStatus, ChangeType
from backend.app.memory.capture import get_capture_engine
from backend.app.config import settings

class MemoryCreateRequest(BaseModel):
    type: str = Field(..., description="Memory type: episodic, semantic, preference, etc.")
    content: str = Field(..., min_length=1)
    subtype: Optional[str] = None
    agent_id: Optional[str] = None
    source_id: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    importance: Optional[float] = Field(None, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None

    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        valid = {"working","episodic","semantic","procedural","preference",
                 "decision","failure","success","temporal","causal",
                 "hypothesis","conflict","multimodal"}
        if v not in valid:
            raise ValueError(f"Invalid memory type: {v}. Must be one of {valid}")
        return v

class MemoryResponse(BaseModel):
    id: str
    root_id: str
    version: int
    type: str
    content: str
    normalized_content: Optional[str] = None
    agent_id: Optional[str] = None
    source_id: Optional[str] = None
    confidence: float
    importance: float
    status: str
    created_at: str
    observed_at: Optional[str] = None
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    parent_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class MemoryListResponse(BaseModel):
    memories: List[MemoryResponse]
    total: int
    limit: int
    offset: int

class LearnRequest(BaseModel):
    agent_id: str
    user_input: str
    ai_output: str
    metadata: Optional[Dict[str, Any]] = None

router = APIRouter()

def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def _memory_to_response(memory: Memory) -> MemoryResponse:
    return MemoryResponse(
        id=memory.id,
        root_id=memory.root_id,
        version=memory.version,
        type=memory.type.value,
        content=memory.content,
        normalized_content=memory.normalized_content,
        agent_id=memory.agent_id,
        source_id=memory.source_id,
        confidence=memory.confidence,
        importance=memory.importance,
        status=memory.status.value,
        created_at=memory.created_at.isoformat() if memory.created_at else None,
        observed_at=memory.observed_at.isoformat() if memory.observed_at else None,
        valid_from=memory.valid_from.isoformat() if memory.valid_from else None,
        valid_until=memory.valid_until.isoformat() if memory.valid_until else None,
        parent_id=memory.parent_id,
        metadata=memory.metadata or {}
    )

@router.post("/", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(request: MemoryCreateRequest, db_session=Depends(get_db_session)):
    memory_id = str(uuid.uuid4())
    content_hash = _sha256(request.content)
    now = datetime.now(timezone.utc)

    memory = Memory(
        id=memory_id,
        root_id=memory_id,
        version=1,
        type=MemoryType(request.type),
        subtype=request.subtype,
        content=request.content,
        normalized_content=request.content.lower().strip(),
        content_hash=content_hash,
        agent_id=request.agent_id,
        source_id=request.source_id,
        confidence=request.confidence or settings.NFM_DEFAULT_CONFIDENCE,
        importance=request.importance or 0.5,
        status=MemoryStatus.ACTIVE,
        created_at=now,
        observed_at=now,
        valid_from=now,
        metadata=request.metadata or {}
    )

    version = MemoryVersion(
        id=str(uuid.uuid4()),
        memory_id=memory_id,
        version=1,
        content=request.content,
        normalized_content=memory.normalized_content,
        content_hash=content_hash,
        confidence=memory.confidence,
        importance=memory.importance,
        status=MemoryStatus.ACTIVE,
        change_type=ChangeType.CREATE,
        change_reason="Initial creation",
        created_at=now,
        actor_id=request.agent_id or "system",
        actor_type="agent"
    )

    event = MemoryEvent(
        id=str(uuid.uuid4()),
        memory_id=memory_id,
        event_type="create",
        details={"type": request.type, "content_length": len(request.content)},
        timestamp=now,
        agent_id=request.agent_id or "system"
    )

    db_session.add(memory)
    db_session.add(version)
    db_session.add(event)
    await db_session.commit()

    return _memory_to_response(memory)

@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(memory_id: str, db_session=Depends(get_db_session)):
    result = await db_session.execute(select(Memory).where(Memory.id == memory_id))
    memory = result.scalar_one_or_none()
    if memory is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    return _memory_to_response(memory)

@router.get("/", response_model=MemoryListResponse)
async def list_memories(
    agent_id: Optional[str] = None,
    memory_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db_session=Depends(get_db_session)
):
    stmt = select(Memory)
    conditions = []
    if agent_id:
        conditions.append(Memory.agent_id == agent_id)
    if memory_type:
        try:
            conditions.append(Memory.type == MemoryType(memory_type))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid memory type: {memory_type}")
    if conditions:
        stmt = stmt.where(*conditions)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db_session.execute(count_stmt)
    total = count_result.scalar() or 0

    stmt = stmt.order_by(Memory.created_at.desc()).limit(limit).offset(offset)
    result = await db_session.execute(stmt)
    memories = result.scalars().all()

    return MemoryListResponse(
        memories=[_memory_to_response(m) for m in memories],
        total=total,
        limit=limit,
        offset=offset
    )

@router.get("/{memory_id}/history")
async def get_memory_history(memory_id: str, db_session=Depends(get_db_session)):
    stmt = select(MemoryVersion).where(MemoryVersion.memory_id == memory_id).order_by(MemoryVersion.version)
    result = await db_session.execute(stmt)
    versions = result.scalars().all()
    if not versions:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {
        "memory_id": memory_id,
        "versions": [{
            "version": v.version,
            "content": v.content,
            "confidence": v.confidence,
            "importance": v.importance,
            "status": v.status.value,
            "change_type": v.change_type.value,
            "change_reason": v.change_reason,
            "created_at": v.created_at.isoformat() if v.created_at else None,
            "actor_id": v.actor_id,
            "actor_type": v.actor_type
        } for v in versions]
    }

@router.post("/learn")
async def learn_interaction(request: LearnRequest, db_session=Depends(get_db_session), capture_engine=Depends(get_capture_engine)):
    # Simple rule-based logic to capture from interaction
    user_mem = await capture_engine.capture(
        db_session=db_session,
        content=request.user_input,
        agent_id=request.agent_id,
        metadata=request.metadata
    )
    ai_mem = await capture_engine.capture(
        db_session=db_session,
        content=request.ai_output,
        agent_id=request.agent_id,
        metadata=request.metadata
    )
    await db_session.commit()
    return {
        "message": "Learned from interaction",
        "memory_ids": [user_mem.id, ai_mem.id]
    }
