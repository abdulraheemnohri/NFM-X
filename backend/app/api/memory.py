"""
Memory CRUD API for NFM-X
Handles memory creation, retrieval, update, and deletion
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid
import hashlib

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from ..storage.database import get_db_session
from ..memory.models import Memory, MemoryVersion, MemoryEvent, MemoryType, MemoryStatus, EventType, ChangeType
from ..memory.capture import capture_handler


class MemoryCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=100000)
    memory_type: Optional[MemoryType] = None
    source: Optional[str] = None
    source_type: Optional[str] = None
    author_id: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    importance: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    parent_memory_id: Optional[str] = None


class MemoryUpdateRequest(BaseModel):
    content: str = Field(..., min_length=1)
    change_type: ChangeType = Field(...)
    change_reason: str = Field(..., min_length=1)
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    importance: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None


class MemoryStatusUpdateRequest(BaseModel):
    status: MemoryStatus = Field(...)
    reason: Optional[str] = None


class MemoryVersionResponse(BaseModel):
    id: str
    memory_id: str
    version_number: int
    content: str
    change_type: ChangeType
    change_reason: Optional[str]
    confidence: float
    importance: float
    status: MemoryStatus
    actor_id: Optional[str]
    actor_type: Optional[str]
    created_at: datetime


class MemoryResponse(BaseModel):
    id: str
    content: str
    content_hash: str
    memory_type: MemoryType
    confidence: float
    importance: float
    status: MemoryStatus
    source: Optional[str]
    source_type: Optional[str]
    author_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    tags: List[str]
    current_version: Optional[MemoryVersionResponse] = None
    version_count: int = 0
    event_count: int = 0


class MemoryListResponse(BaseModel):
    memories: List[MemoryResponse]
    total: int
    limit: int
    offset: int


router = APIRouter(prefix="/memory", tags=["Memory"])


def _memory_to_response(memory: Memory) -> MemoryResponse:
    current_version = None
    for version in memory.versions:
        if version.status == MemoryStatus.ACTIVE:
            current_version = MemoryVersionResponse(
                id=version.id, memory_id=version.memory_id, version_number=version.version_number,
                content=version.content, change_type=version.change_type, change_reason=version.change_reason,
                confidence=version.confidence, importance=version.importance, status=version.status,
                actor_id=version.actor_id, actor_type=version.actor_type, created_at=version.created_at
            )
            break
    return MemoryResponse(
        id=memory.id, content=memory.content, content_hash=memory.content_hash, memory_type=memory.memory_type,
        confidence=memory.confidence, importance=memory.importance, status=memory.status, source=memory.source,
        source_type=memory.source_type, author_id=memory.author_id, created_at=memory.created_at,
        updated_at=memory.updated_at, metadata=memory.metadata or {}, tags=memory.tags or [],
        current_version=current_version, version_count=len(memory.versions), event_count=len(memory.events)
    )


@router.post("/", response_model=MemoryResponse, status_code=201)
async def create_memory(request: MemoryCreateRequest, db_session: AsyncSession = Depends(get_db_session)) -> MemoryResponse:
    memory = await capture_handler.capture(
        db_session=db_session, content=request.content, memory_type=request.memory_type, source=request.source,
        source_type=request.source_type, author_id=request.author_id, confidence=request.confidence,
        importance=request.importance, metadata=request.metadata, tags=request.tags, parent_memory_id=request.parent_memory_id
    )
    await db_session.commit()
    await db_session.refresh(memory)
    return _memory_to_response(memory)


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(memory_id: str, db_session: AsyncSession = Depends(get_db_session)) -> MemoryResponse:
    result = await db_session.execute(select(Memory).where(Memory.id == memory_id))
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=404, detail=f"Memory {memory_id} not found")
    return _memory_to_response(memory)


@router.get("/", response_model=MemoryListResponse)
async def list_memories(
    limit: int = Query(default=50, ge=1, le=1000), offset: int = Query(default=0, ge=0),
    memory_type: Optional[MemoryType] = Query(default=None), status: Optional[MemoryStatus] = Query(default=None),
    author_id: Optional[str] = Query(default=None), tag: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None), db_session: AsyncSession = Depends(get_db_session)
) -> MemoryListResponse:
    conditions = []
    if status:
        conditions.append(Memory.status == status)
    else:
        conditions.append(Memory.status == MemoryStatus.ACTIVE)
    if memory_type:
        conditions.append(Memory.memory_type == memory_type)
    if author_id:
        conditions.append(Memory.author_id == author_id)
    if tag:
        conditions.append(Memory.tags.contains([tag]))
    if search:
        terms = search.lower().split()
        search_conds = [Memory.content.ilike(f"%{t}%") for t in terms if len(t) > 2]
        if search_conds:
            conditions.append(or_(*search_conds))
    count_stmt = select(func.count(Memory.id)).where(and_(*conditions))
    count_result = await db_session.execute(count_stmt)
    total = count_result.scalar()
    stmt = select(Memory).where(and_(*conditions)).order_by(Memory.created_at.desc()).limit(limit).offset(offset)
    result = await db_session.execute(stmt)
    return MemoryListResponse(memories=[_memory_to_response(m) for m in result.scalars().all()], total=total, limit=limit, offset=offset)


@router.get("/{memory_id}/history")
async def get_memory_history(memory_id: str, db_session: AsyncSession = Depends(get_db_session)) -> Dict[str, Any]:
    result = await db_session.execute(select(Memory).where(Memory.id == memory_id))
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=404)
    versions = [{
        "id": v.id, "version_number": v.version_number, "content": v.content, "change_type": v.change_type.value,
        "change_reason": v.change_reason, "confidence": v.confidence, "importance": v.importance,
        "status": v.status.value, "created_at": v.created_at.isoformat()
    } for v in memory.versions]
    events = [{
        "id": e.id, "event_type": e.event_type.value, "description": e.description, "actor_id": e.actor_id,
        "actor_type": e.actor_type, "metadata": e.metadata, "created_at": e.created_at.isoformat()
    } for e in memory.events]
    return {"memory_id": memory_id, "versions": versions, "events": events, "total_versions": len(versions), "total_events": len(events)}


@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(memory_id: str, request: MemoryUpdateRequest, db_session: AsyncSession = Depends(get_db_session)) -> MemoryResponse:
    result = await db_session.execute(select(Memory).where(Memory.id == memory_id))
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=404)
    current_version = next((v for v in memory.versions if v.status == MemoryStatus.ACTIVE), None)
    if not current_version:
        raise HTTPException(status_code=400, detail="No active version")
    now = datetime.now(timezone.utc)
    new_version = MemoryVersion(
        id=str(uuid.uuid4()), memory_id=memory_id, content=request.content,
        content_hash=hashlib.sha256(request.content.encode("utf-8")).hexdigest(),
        version_number=current_version.version_number + 1, change_type=request.change_type,
        change_reason=request.change_reason, confidence=request.confidence or memory.confidence,
        importance=request.importance or memory.importance, status=MemoryStatus.ACTIVE,
        actor_id="user", actor_type="user", parent_version_id=current_version.id, created_at=now
    )
    db_session.add(new_version)
    current_version.status = MemoryStatus.ARCHIVED
    memory.content = request.content
    memory.content_hash = new_version.content_hash
    memory.confidence = new_version.confidence
    memory.importance = new_version.importance
    memory.updated_at = now
    if request.metadata:
        memory.metadata = {**memory.metadata, **request.metadata}
    event = MemoryEvent(
        id=str(uuid.uuid4()), memory_id=memory_id, version_id=new_version.id,
        event_type=EventType.VERSIONED, description=f"Updated: {request.change_reason}",
        actor_id="user", actor_type="user", metadata={}, created_at=now
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(memory)
    return _memory_to_response(memory)


@router.patch("/{memory_id}/status", response_model=MemoryResponse)
async def update_memory_status(memory_id: str, request: MemoryStatusUpdateRequest, db_session: AsyncSession = Depends(get_db_session)) -> MemoryResponse:
    result = await db_session.execute(select(Memory).where(Memory.id == memory_id))
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=404)
    old_status = memory.status
    memory.status = request.status
    memory.updated_at = datetime.now(timezone.utc)
    event = MemoryEvent(
        id=str(uuid.uuid4()), memory_id=memory_id,
        event_type=EventType.DELETED if request.status == MemoryStatus.DELETED else EventType.ARCHIVED,
        description=f"Status: {old_status.value} -> {request.status.value}", actor_id="user", actor_type="user",
        metadata={}, created_at=memory.updated_at
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(memory)
    return _memory_to_response(memory)


@router.delete("/{memory_id}", status_code=204)
async def delete_memory(memory_id: str, db_session: AsyncSession = Depends(get_db_session)) -> None:
    result = await db_session.execute(select(Memory).where(Memory.id == memory_id))
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=404)
    if memory.status == MemoryStatus.DELETED:
        raise HTTPException(status_code=400, detail="Already deleted")
    memory.status = MemoryStatus.DELETED
    memory.updated_at = datetime.now(timezone.utc)
    event = MemoryEvent(
        id=str(uuid.uuid4()), memory_id=memory_id, event_type=EventType.DELETED,
        description="Soft-deleted", actor_id="user", actor_type="user", metadata={}, created_at=memory.updated_at
    )
    db_session.add(event)
    await db_session.commit()