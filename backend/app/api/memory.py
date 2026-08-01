"""
NFM-X Memory API
Endpoints for memory operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from sqlalchemy import select, func

from ..config import settings
from ..storage.database import get_db_session
from ..memory.models import Memory, MemoryVersion, MemoryEvent
from ..memory.capture import get_capture_engine

router = APIRouter(prefix="/memory", tags=["Memory"])


class MemoryCreateRequest(BaseModel):
    type: str
    content: str
    subtype: Optional[str] = None
    agent_id: Optional[str] = None
    source_id: Optional[str] = None
    confidence: Optional[float] = None
    importance: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


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


@router.post("/")
async def create_memory(request: MemoryCreateRequest, db_session=Depends(get_db_session)):
    memory_id = str(uuid.uuid4())
    root_id = memory_id
    memory = Memory(
        id=memory_id, root_id=root_id, version=1, type=request.type,
        subtype=request.subtype, content=request.content,
        normalized_content=request.content, content_hash=str(uuid.uuid4())[:16],
        agent_id=request.agent_id, source_id=request.source_id,
        confidence=request.confidence or settings.NFM_DEFAULT_CONFIDENCE,
        importance=request.importance or 0.5, status="active",
        created_at=datetime.utcnow(), observed_at=datetime.utcnow(),
        valid_from=datetime.utcnow(), parent_id=None, metadata=request.metadata or {}
    )
    async with db_session.begin():
        db_session.add(memory)
        version = MemoryVersion(
            id=str(uuid.uuid4()), memory_id=memory_id, version=1,
            content=request.content, normalized_content=request.content,
            content_hash=memory.content_hash, confidence=memory.confidence,
            importance=memory.importance, status="active",
            metadata=request.metadata or {}, change_type="create",
            change_reason="Initial creation", created_at=datetime.utcnow(),
            actor_id=request.agent_id or "system", actor_type="agent"
        )
        db_session.add(version)
        event = MemoryEvent(
            id=str(uuid.uuid4()), memory_id=memory_id, event_type="create",
            details={"type": request.type, "content_length": len(request.content)},
            timestamp=datetime.utcnow(), agent_id=request.agent_id or "system",
            actor_type="agent"
        )
        db_session.add(event)
    return MemoryResponse(
        id=memory.id, root_id=memory.root_id, version=memory.version,
        type=memory.type.value, content=memory.content,
        normalized_content=memory.normalized_content, agent_id=memory.agent_id,
        source_id=memory.source_id, confidence=memory.confidence,
        importance=memory.importance, status=memory.status.value,
        created_at=memory.created_at.isoformat(),
        observed_at=memory.observed_at.isoformat() if memory.observed_at else None,
        valid_from=memory.valid_from.isoformat() if memory.valid_from else None,
        valid_until=memory.valid_until.isoformat() if memory.valid_until else None,
        parent_id=memory.parent_id, metadata=memory.metadata
    )


@router.get("/{memory_id}")
async def get_memory(memory_id: str, db_session=Depends(get_db_session)):
    async with db_session.begin():
        stmt = select(Memory).where(Memory.id == memory_id)
        result = await db_session.execute(stmt)
        memory = result.scalar_one_or_none()
        if memory is None:
            raise HTTPException(status_code=404, detail="Memory not found")
        return MemoryResponse(
            id=memory.id, root_id=memory.root_id, version=memory.version,
            type=memory.type.value, content=memory.content,
            normalized_content=memory.normalized_content, agent_id=memory.agent_id,
            source_id=memory.source_id, confidence=memory.confidence,
            importance=memory.importance, status=memory.status.value,
            created_at=memory.created_at.isoformat(),
            observed_at=memory.observed_at.isoformat() if memory.observed_at else None,
            valid_from=memory.valid_from.isoformat() if memory.valid_from else None,
            valid_until=memory.valid_until.isoformat() if memory.valid_until else None,
            parent_id=memory.parent_id, metadata=memory.metadata
        )


@router.get("/")
async def list_memories(agent_id: Optional[str] = None, memory_type: Optional[str] = None, limit: int = 50, offset: int = 0, db_session=Depends(get_db_session)):
    async with db_session.begin():
        stmt = select(Memory)
        conditions = []
        if agent_id: conditions.append(Memory.agent_id == agent_id)
        if memory_type: conditions.append(Memory.type == memory_type)
        if conditions: stmt = stmt.where(*conditions)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await db_session.execute(count_stmt)
        total = count_result.scalar()
        stmt = stmt.order_by(Memory.created_at.desc()).limit(limit).offset(offset)
        result = await db_session.execute(stmt)
        memories = result.scalars().all()
        return MemoryListResponse(
            memories=[MemoryResponse(
                id=m.id, root_id=m.root_id, version=m.version, type=m.type.value,
                content=m.content, normalized_content=m.normalized_content,
                agent_id=m.agent_id, source_id=m.source_id, confidence=m.confidence,
                importance=m.importance, status=m.status.value,
                created_at=m.created_at.isoformat(),
                observed_at=m.observed_at.isoformat() if m.observed_at else None,
                valid_from=m.valid_from.isoformat() if m.valid_from else None,
                valid_until=m.valid_until.isoformat() if m.valid_until else None,
                parent_id=m.parent_id, metadata=m.metadata
            ) for m in memories],
            total=total, limit=limit, offset=offset
        )


@router.post("/learn")
async def learn(request: LearnRequest, capture_engine=Depends(get_capture_engine)):
    memories = await capture_engine.learn(
        agent_id=request.agent_id,
        user_input=request.user_input,
        ai_output=request.ai_output,
        metadata=request.metadata
    )
    return {"message": "Learned from interaction", "memory_ids": [m.id for m in memories]}


@router.get("/{memory_id}/history")
async def get_memory_history(memory_id: str, db_session=Depends(get_db_session)):
    async with db_session.begin():
        stmt = select(MemoryVersion).where(MemoryVersion.memory_id == memory_id).order_by(MemoryVersion.version)
        result = await db_session.execute(stmt)
        versions = result.scalars().all()
        if not versions:
            raise HTTPException(status_code=404, detail="Memory not found")
        return {
            "memory_id": memory_id,
            "versions": [{
                "version": v.version, "content": v.content, "confidence": v.confidence,
                "importance": v.importance, "status": v.status.value,
                "change_type": v.change_type.value, "change_reason": v.change_reason,
                "created_at": v.created_at.isoformat(), "actor_id": v.actor_id,
                "actor_type": v.actor_type
            } for v in versions]
        }