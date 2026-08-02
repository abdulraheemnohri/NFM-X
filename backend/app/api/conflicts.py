"""
NFM-X Conflicts API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..memory.models import Memory, MemoryStatus
from ..memory.conflicts import ConflictDetector, ConflictType, ConflictStatus
from ..storage.database import get_db

router = APIRouter(prefix="/conflicts", tags=["Conflicts"])


class ConflictResponse(BaseModel):
    id: str
    memory_a_id: str
    memory_b_id: str
    conflict_type: str
    status: str
    description: Optional[str]
    detected_at: datetime
    resolved_at: Optional[datetime]
    resolution: Optional[str]
    resolution_notes: Optional[str]
    
    class Config:
        from_attributes = True


class ConflictListResponse(BaseModel):
    conflicts: List[ConflictResponse]
    total: int
    new_count: int
    resolved_count: int


class ConflictResolveRequest(BaseModel):
    resolution: str
    resolution_notes: Optional[str] = None


@router.get("/", response_model=ConflictListResponse)
async def list_conflicts(
    status: Optional[str] = None,
    conflict_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
) -> ConflictListResponse:
    result = await db.execute(
        select(Memory).where(Memory.metadata["is_conflict"].as_boolean() == True)
    )
    conflict_memories = result.scalars().all()
    
    conflicts = []
    for mem in conflict_memories:
        metadata = mem.metadata or {}
        if metadata.get("is_conflict"):
            if status and metadata.get("status") != status:
                continue
            if conflict_type and metadata.get("conflict_type") != conflict_type:
                continue
            conflicts.append(ConflictResponse(
                id=metadata.get("conflict_id", mem.id),
                memory_a_id=metadata.get("memory_a_id", ""),
                memory_b_id=metadata.get("memory_b_id", ""),
                conflict_type=metadata.get("conflict_type", "unknown"),
                status=metadata.get("status", "detected"),
                description=mem.content,
                detected_at=mem.created_at,
                resolved_at=datetime.fromisoformat(metadata.get("resolved_at")) if metadata.get("resolved_at") else None,
                resolution=metadata.get("resolution"),
                resolution_notes=metadata.get("resolution_notes")
            ))
    
    return ConflictListResponse(
        conflicts=conflicts[offset:offset+limit],
        total=len(conflicts),
        new_count=len([c for c in conflicts if c.status == "detected"]),
        resolved_count=len([c for c in conflicts if c.status == "resolved"])
    )


@router.get("/{conflict_id}", response_model=ConflictResponse)
async def get_conflict(conflict_id: str, db: AsyncSession = Depends(get_db)) -> ConflictResponse:
    detector = ConflictDetector()
    conflict = await detector.get_conflict(db, conflict_id)
    if not conflict:
        raise HTTPException(status_code=404, detail=f"Conflict {conflict_id} not found")
    return ConflictResponse(
        id=conflict.id,
        memory_a_id=conflict.memory_a_id,
        memory_b_id=conflict.memory_b_id,
        conflict_type=conflict.conflict_type.value,
        status=conflict.status.value,
        description=conflict.description,
        detected_at=conflict.detected_at,
        resolved_at=conflict.resolved_at,
        resolution=conflict.resolution.value if conflict.resolution else None,
        resolution_notes=conflict.resolution_notes
    )


@router.post("/detect")
async def detect_conflicts(
    memory_id: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    detector = ConflictDetector()
    result = await detector.detect_conflicts(db_session=db, memory_id=memory_id, limit=limit)
    return {
        "total": result.total_conflicts,
        "new": result.new_conflicts,
        "resolved": result.resolved_conflicts,
        "conflicts": [
            {
                "id": c.id,
                "type": c.conflict_type.value,
                "status": c.status.value,
                "memory_a": c.memory_a_id,
                "memory_b": c.memory_b_id,
                "description": c.description,
                "severity": c.severity,
                "detected_at": c.detected_at.isoformat()
            }
            for c in result.conflicts
        ]
    }