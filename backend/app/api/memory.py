"""
NFM-X Memory API
FastAPI endpoints for memory CRUD operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc

from ..memory.models import Memory, MemoryStatus, MemoryType, MemoryEvent, EventType
from ..memory.capture import capture
from ..storage.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Memory"])


class MemoryCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=100000, description="Main content of the memory")
    title: Optional[str] = Field(None, description="Title for the memory")
    description: Optional[str] = Field(None, description="Description of the memory")
    memory_type: Optional[MemoryType] = Field(None, description="Type of memory")
    source: Optional[str] = Field(None, description="Source of the memory")
    source_id: Optional[str] = Field(None, description="ID of the source")
    author: Optional[str] = Field(None, description="Author of the memory")
    tags: Optional[List[str]] = Field(None, description="List of tags")
    categories: Optional[List[str]] = Field(None, description="List of categories")
    metadata: Optional[dict] = Field(None, description="Additional metadata")
    parent_id: Optional[str] = Field(None, description="Parent memory ID for versioning")


class MemoryUpdateRequest(BaseModel):
    content: Optional[str] = Field(None, description="New content")
    title: Optional[str] = Field(None, description="New title")
    description: Optional[str] = Field(None, description="New description")
    tags: Optional[List[str]] = Field(None, description="New tags")
    categories: Optional[List[str]] = Field(None, description="New categories")
    metadata: Optional[dict] = Field(None, description="New metadata")


class MemoryResponse(BaseModel):
    id: str
    content: str
    content_hash: str
    title: Optional[str]
    description: Optional[str]
    memory_type: MemoryType
    status: MemoryStatus
    version: int
    parent_id: Optional[str]
    source: Optional[str]
    source_id: Optional[str]
    author: Optional[str]
    tags: List[str]
    categories: List[str]
    priority: str
    embedding: Optional[list]
    embedding_model: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None
    archived_at: Optional[datetime]
    deleted_at: Optional[datetime]
    access_count: int
    relevance_score: float
    metadata: dict
    
    class Config:
        from_attributes = True


@router.post("/", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(
    request: MemoryCreateRequest,
    db: AsyncSession = Depends(get_db)
) -> MemoryResponse:
    memory = await capture.capture(
        content=request.content,
        title=request.title,
        description=request.description,
        memory_type=request.memory_type,
        source=request.source or "api",
        source_id=request.source_id,
        author=request.author or "api_user",
        tags=request.tags,
        categories=request.categories,
        metadata=request.metadata,
        parent_id=request.parent_id,
        db_session=db
    )

    # Generate embedding and add to vector store
    try:
        from backend.app.embeddings.models import get_embedding_model
        from backend.app.embeddings.vector_store import get_vector_store

        emb_model = get_embedding_model()
        memory.embedding = emb_model.encode_single(memory.content)

        v_store = get_vector_store()
        v_store.add(memory.id, memory.content, memory.embedding)
        v_store.save()
    except Exception as e:
        logger.error(f"Failed to index memory embedding: {e}")

    memory.access_count += 1
    await db.commit()
    await db.refresh(memory)
    return MemoryResponse.model_validate(memory)


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(memory_id: str, db: AsyncSession = Depends(get_db)) -> MemoryResponse:
    result = await db.execute(select(Memory).where(Memory.id == memory_id))
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Memory {memory_id} not found")
    memory.access_count += 1
    await db.commit()
    await db.refresh(memory)
    return MemoryResponse.model_validate(memory)


@router.get("/", response_model=List[MemoryResponse])
async def list_memories(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=1000),
    status_filter: Optional[MemoryStatus] = Query(None),
    type_filter: Optional[MemoryType] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> List[MemoryResponse]:
    query = select(Memory)
    filters = []
    
    if status_filter:
        filters.append(Memory.status == status_filter)
    else:
        filters.append(Memory.status == MemoryStatus.ACTIVE)
    
    if type_filter:
        filters.append(Memory.memory_type == type_filter)
    
    if search:
        search_pattern = f"%{search}%"
        filters.append(or_(
            Memory.content.ilike(search_pattern),
            Memory.title.ilike(search_pattern),
            Memory.description.ilike(search_pattern)
        ))
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(desc(Memory.created_at)).offset((page-1)*page_size).limit(page_size)
    result = await db.execute(query)
    memories = result.scalars().all()
    
    for memory in memories:
        memory.access_count += 1
    await db.commit()
    
    return [MemoryResponse.model_validate(m) for m in memories]


@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: str,
    request: MemoryUpdateRequest,
    db: AsyncSession = Depends(get_db)
) -> MemoryResponse:
    memory = await capture.update_memory(
        memory_id=memory_id,
        content=request.content,
        title=request.title,
        description=request.description,
        tags=request.tags,
        categories=request.categories,
        metadata=request.metadata,
        db_session=db
    )

    # Update embedding and vector store
    try:
        from backend.app.embeddings.models import get_embedding_model
        from backend.app.embeddings.vector_store import get_vector_store

        emb_model = get_embedding_model()
        memory.embedding = emb_model.encode_single(memory.content)

        v_store = get_vector_store()
        v_store.add(memory.id, memory.content, memory.embedding)
        v_store.save()
    except Exception as e:
        logger.error(f"Failed to update indexed memory embedding: {e}")

    return MemoryResponse.model_validate(memory)


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: str,
    hard_delete: bool = Query(default=False),
    db: AsyncSession = Depends(get_db)
) -> None:
    success = await capture.delete_memory(
        memory_id=memory_id,
        hard_delete=hard_delete,
        db_session=db
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Memory {memory_id} not found")


@router.post("/{memory_id}/restore", response_model=MemoryResponse)
async def restore_memory(memory_id: str, db: AsyncSession = Depends(get_db)) -> MemoryResponse:
    result = await db.execute(select(Memory).where(Memory.id == memory_id))
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Memory {memory_id} not found")
    if memory.status == MemoryStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Memory is already active")
    
    memory.status = MemoryStatus.ACTIVE
    memory.archived_at = None
    memory.deleted_at = None
    memory.updated_at = datetime.now()
    
    restore_event = MemoryEvent(
        memory_id=memory_id,
        event_type=EventType.RESTORED,
        details={"previous_status": memory.status.value}
    )
    db.add(restore_event)
    
    await db.commit()
    await db.refresh(memory)
    return MemoryResponse.model_validate(memory)


@router.get("/{memory_id}/versions", response_model=List[MemoryResponse])
async def get_memory_versions(memory_id: str, db: AsyncSession = Depends(get_db)) -> List[MemoryResponse]:
    result = await db.execute(select(Memory).where(Memory.id == memory_id))
    base_memory = result.scalar_one_or_none()
    if not base_memory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Memory {memory_id} not found")
    
    version_ids = set()
    current = base_memory
    while current:
        version_ids.add(current.id)
        current = current.parent
    
    result = await db.execute(select(Memory).where(Memory.parent_id.in_(version_ids)))
    children = result.scalars().all()
    for child in children:
        version_ids.add(child.id)
    
    result = await db.execute(select(Memory).where(Memory.id.in_(version_ids)).order_by(Memory.version))
    versions = result.scalars().all()
    
    for version in versions:
        version.access_count += 1
    await db.commit()
    
    return [MemoryResponse.model_validate(v) for v in versions]


@router.get("/{memory_id}/events")
async def get_memory_events(memory_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Memory).where(Memory.id == memory_id))
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Memory {memory_id} not found")
    
    result = await db.execute(select(MemoryEvent).where(MemoryEvent.memory_id == memory_id).order_by(desc(MemoryEvent.timestamp)))
    events = result.scalars().all()
    return [{"id": e.id, "memory_id": e.memory_id, "event_type": e.event_type, "details": e.details, "timestamp": e.timestamp} for e in events]


from datetime import timezone