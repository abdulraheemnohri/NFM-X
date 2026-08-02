"""
NFM-X Conflicts API
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import select
from ..memory.models import Memory
from ..storage.database import get_db

router = APIRouter(prefix="/conflicts", tags=["Conflicts"])

class ConflictResponse(BaseModel):
    id: str
    memory_a_id: str
    memory_b_id: str
    conflict_type: str
    status: str
    description: Optional[str]

class ConflictListResponse(BaseModel):
    conflicts: List[ConflictResponse]
    total: int

@router.get("/", response_model=ConflictListResponse)
async def list_conflicts(db=Depends(get_db)):
    result = await db.execute(
        select(Memory).where(Memory.metadata["is_conflict"].as_boolean() == True)
    )
    conflicts = result.scalars().all()
    
    conflict_responses = []
    for mem in conflicts:
        metadata = mem.metadata or {}
        conflict_responses.append(ConflictResponse(
            id=metadata.get("conflict_id", mem.id),
            memory_a_id=metadata.get("memory_a_id", ""),
            memory_b_id=metadata.get("memory_b_id", ""),
            conflict_type=metadata.get("conflict_type", "unknown"),
            status=metadata.get("status", "detected"),
            description=mem.content
        ))
    
    return ConflictListResponse(conflicts=conflict_responses, total=len(conflict_responses))