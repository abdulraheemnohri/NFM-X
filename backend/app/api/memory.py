"""
NFM-X Memory API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from ..memory.models import Memory, MemoryStatus, MemoryType
from ..memory.capture import capture
from ..storage.database import get_db

router = APIRouter(prefix="/memory", tags=["Memory"])

class MemoryCreateRequest(BaseModel):
    content: str
    title: Optional[str] = None
    memory_type: Optional[MemoryType] = None
    source: Optional[str] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    parent_id: Optional[str] = None

class MemoryResponse(BaseModel):
    id: str
    content: str
    title: Optional[str]
    memory_type: MemoryType
    status: MemoryStatus
    version: int
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/", response_model=MemoryResponse, status_code=201)
async def create_memory(request: MemoryCreateRequest, db=Depends(get_db)):
    memory = await capture.capture(
        content=request.content,
        title=request.title,
        memory_type=request.memory_type,
        source=request.source or "api",
        author=request.author or "user",
        tags=request.tags,
        categories=request.categories,
        parent_id=request.parent_id
    )
    return memory

@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(memory_id: str, db=Depends(get_db)):
    result = await db.execute(select(Memory).where(Memory.id == memory_id))
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory

@router.get("/", response_model=List[MemoryResponse])
async def list_memories(db=Depends(get_db)):
    result = await db.execute(select(Memory).where(Memory.status == MemoryStatus.ACTIVE))
    return result.scalars().all()

from sqlalchemy import select