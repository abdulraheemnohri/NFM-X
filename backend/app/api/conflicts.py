"""
NFM-X Conflict Resolution API
Handles sync conflicts with automatic and manual resolution strategies using SQLAlchemy ORM.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models.conflict import Conflict

router = APIRouter(prefix="", tags=["conflicts"])


class ConflictStatus(str, Enum):
    PENDING = "pending"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class ConflictType(str, Enum):
    CONTENT = "content"
    METADATA = "metadata"
    DELETION = "deletion"


class ResolutionStrategy(str, Enum):
    KEEP_BOTH = "keep_both"
    KEEP_LOCAL = "keep_local"
    KEEP_REMOTE = "keep_remote"
    MERGE = "merge"
    LATEST = "latest"


class ConflictBase(BaseModel):
    memory_id: str
    local_content: str
    remote_content: str
    local_metadata: Dict[str, Any] = Field(default_factory=dict)
    remote_metadata: Dict[str, Any] = Field(default_factory=dict)
    conflict_type: ConflictType
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: ConflictStatus = ConflictStatus.PENDING


class ConflictCreate(ConflictBase):
    pass


class ConflictUpdate(BaseModel):
    status: Optional[ConflictStatus] = None
    resolution: Optional[ResolutionStrategy] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    notes: Optional[str] = None


class ConflictResponse(ConflictBase):
    id: int
    resolution: Optional[ResolutionStrategy] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime


class ConflictListResponse(BaseModel):
    id: int
    memory_id: str
    conflict_type: Conflict
Type
    status: ConflictStatus
    detected_at: datetime
    created_at: datetime


class AutoResolveRequest(BaseModel):
    strategy: ResolutionStrategy
    dry_run: bool = False


class BulkResolveRequest(BaseModel):
    strategy: ResolutionStrategy
    conflict_ids: List[int]
    dry_run: bool = False


@router.get("/", response_model=List[ConflictListResponse])
async def list_conflicts(
    status_filter: Optional[ConflictStatus] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List all conflicts with optional filtering."""
    query = select(Conflict)
    if status_filter:
        query = query.where(Conflict.status == status_filter.value)
    query = query.order_by(Conflict.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    conflicts = result.scalars().all()
    
    return [
        ConflictListResponse(
            id=c.id,
            memory_id=c.memory_id,
            conflict_type=ConflictType(c.conflict_type),
            status=ConflictStatus(c.status),
            detected_at=c.detected_at,
            created_at=c.created_at
        )
        for c in conflicts
    ]


@router.get("/{conflict_id}", response_model=ConflictResponse)
async def get_conflict(conflict_id: int, db: AsyncSession = Depends(get_db)):
    """Get details of a specific conflict."""
    result = await db.execute(select(Conflict).where(Conflict.id == conflict_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Conflict not found")
    
    return ConflictResponse(
        id=c.id,
        memory_id=c.memory_id,
        local_content=c.local_content,
        remote_content=c.remote_content,
        local_metadata=c.local_metadata or {},
        remote_metadata=c.remote_metadata or {},
        conflict_type=ConflictType(c.conflict_type),
        detected_at=c.detected_at,
        status=ConflictStatus(c.status),
        resolution=ResolutionS
trategy(c.resolution) if c.resolution else None,
        resolved_at=c.resolved_at,
        resolved_by=c.resolved_by,
        notes=c.notes,
        created_at=c.created_at
    )


@router.post("/", response_model=ConflictResponse, status_code=status.HTTP_201_CREATED)
async def create_conflict(conflict: ConflictCreate, db: AsyncSession = Depends(get_db)):
    """Create a new conflict record."""
    c = Conflict(
        memory_id=conflict.memory_id,
        local_content=conflict.local_content,
        remote_content=conflict.remote_content,
        local_metadata=conflict.local_metadata,
        remote_metadata=conflict.remote_metadata,
        conflict_type=conflict.conflict_type.value,
        detected_at=conflict.detected_at,
        status=conflict.status.value
    )
    db.add(c)
    await db.commit()
    await db.refresh(c)
    
    return ConflictResponse(
        id=c.id,
        memory_id=c.memory_id,
        local_content=c.local_content,
        remote_content=c.remote_content,
        local_metadata=c.local_metadata or {},
        remote_metadata=c.remote_metadata or {},
        conflict_type=ConflictType(c.conflict_type),
        detected_at=c.detected_at,
        status=ConflictStatus(c.status),
        resolution=ResolutionStrategy(c.resolution) if c.resolution else None,
        resolved_at=c.resolved_at,
        resolved_by=c.resolved_by,
        notes=c.notes,
        created_at=c.created_at
    )


@router.post("/{conflict_id}/resolve", response_model=ConflictResponse)
async def resolve_conflict(
    conflict_id: int,
    resolution: ConflictUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Resolve a conflict with a specific strategy."""
    result = await db.execute(select(Conflict).where(Conflict.id == conflict_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Conflict not found")
    
    applied_resolution = resolution.resolution or ResolutionStrategy.KEEP_BOTH
    
    if appl
ied_resolution == ResolutionStrategy.MERGE:
        merged_content = _merge_contents(c.local_content, c.remote_content)
        merged_metadata = _merge_metadata(c.local_metadata or {}, c.remote_metadata or {})
    elif applied_resolution == ResolutionStrategy.KEEP_LOCAL:
        merged_content = c.local_content
        merged_metadata = c.local_metadata or {}
    elif applied_resolution == ResolutionStrategy.KEEP_REMOTE:
        merged_content = c.remote_content
        merged_metadata = c.remote_metadata or {}
    else:
        merged_content = c.local_content
        merged_metadata = c.local_metadata or {}
    
    c.status = ConflictStatus.RESOLVED.value
    c.resolution = applied_resolution.value
    c.resolved_at = resolution.resolved_at or datetime.now(timezone.utc)
    c.resolved_by = resolution.resolved_by
    c.notes = resolution.notes
    
    db.add(c)
    await db.commit()
    await db.refresh(c)
    
    return ConflictResponse(
        id=c.id,
        memory_id=c.memory_id,
        local_content=c.local_content,
        remote_content=c.remote_content,
        local_metadata=c.local_metadata or {},
        remote_metadata=c.remote_metadata or {},
        conflict_type=ConflictType(c.conflict_type),
        detected_at=c.detected_at,
        status=ConflictStatus(c.status),
        resolution=applied_resolution,
        resolved_at=c.resolved_at,
        resolved_by=c.resolved_by,
        notes=c.notes,
        created_at=c.created_at
    )


@router.post("/auto-resolve", response_model=Dict[str, Any])
async def auto_resolve_conflicts(request: AutoResolveRequest, db: AsyncSession = Depends(get_db)):
    """Auto-resolve conflicts using a specified strategy."""
    result = await db.execute(select(Conflict).where(Conflict.status == ConflictStatus.PENDING.value))
    conflicts = result.scalars().all()
    
    resolved_count = 0
    failed_count = 0
    
    if not request.dry_run:
        for c in conflicts:
            try:
                resolution 
= ConflictUpdate(
                    status=ConflictStatus.RESOLVED,
                    resolution=request.strategy,
                    resolved_at=datetime.now(timezone.utc),
                    resolved_by="auto-resolver",
                    notes=f"Auto-resolved with {request.strategy.value} strategy"
                )
                applied_resolution = resolution.resolution or ResolutionStrategy.KEEP_BOTH
                c.status = ConflictStatus.RESOLVED.value
                c.resolution = applied_resolution.value
                c.resolved_at = resolution.resolved_at or datetime.now(timezone.utc)
                c.resolved_by = resolution.resolved_by
                c.notes = resolution.notes
                db.add(c)
                resolved_count += 1
            except Exception:
                failed_count += 1
        await db.commit()
    
    return {
        "total_conflicts": len(conflicts),
        "resolved_count": resolved_count if not request.dry_run else len(conflicts),
        "failed_count": failed_count,
        "dry_run": request.dry_run,
        "strategy": request.strategy.value
    }


@router.post("/bulk-resolve", response_model=Dict[str, Any])
async def bulk_resolve_conflicts(request: BulkResolveRequest, db: AsyncSession = Depends(get_db)):
    """Bulk resolve multiple conflicts."""
    resolved_count = 0
    failed_count = 0
    
    if not request.dry_run:
        for conflict_id in request.conflict_ids:
            try:
                result = await db.execute(select(Conflict).where(Conflict.id == conflict_id))
                c = result.scalar_one_or_none()
                if c:
                    resolution = ConflictUpdate(
                        status=ConflictStatus.RESOLVED,
                        resolution=request.strategy,
                        resolved_at=datetime.now(timezone.utc),
                        resolved_by="bulk-resolver",
                        notes=f"Bulk resolved with {request.strategy.value} s
trategy"
                    )
                    applied_resolution = resolution.resolution or ResolutionStrategy.KEEP_BOTH
                    c.status = ConflictStatus.RESOLVED.value
                    c.resolution = applied_resolution.value
                    c.resolved_at = resolution.resolved_at or datetime.now(timezone.utc)
                    c.resolved_by = resolution.resolved_by
                    c.notes = resolution.notes
                    db.add(c)
                    resolved_count += 1
            except Exception:
                failed_count += 1
        await db.commit()
    
    return {
        "total_requested": len(request.conflict_ids),
        "resolved_count": resolved_count if not request.dry_run else len(request.conflict_ids),
        "failed_count": failed_count,
        "dry_run": request.dry_run,
        "strategy": request.strategy.value
    }


@router.delete("/{conflict_id}", response_model=ConflictResponse)
async def dismiss_conflict(conflict_id: int, db: AsyncSession = Depends(get_db)):
    """Dismiss a conflict without resolution."""
    result = await db.execute(select(Conflict).where(Conflict.id == conflict_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Conflict not found")
    
    c.status = ConflictStatus.DISMISSED.value
    c.resolved_at = datetime.now(timezone.utc)
    db.add(c)
    await db.commit()
    await db.refresh(c)
    
    return ConflictResponse(
        id=c.id,
        memory_id=c.memory_id,
        local_content=c.local_content,
        remote_content=c.remote_content,
        local_metadata=c.local_metadata or {},
        remote_metadata=c.remote_metadata or {},
        conflict_type=ConflictType(c.conflict_type),
        detected_at=c.detected_at,
        status=ConflictStatus(c.status),
        resolution=ResolutionStrategy(c.resolution) if c.resolution else None,
        resolved_at=c.resolved_at,
        resolved_by=c.resolved_by,
        
notes=c.notes,
        created_at=c.created_at
    )


def _merge_contents(local: str, remote: str) -> str:
    """Merge two content versions."""
    if local == remote:
        return local
    return f"{local}\n\n---\n\n{remote}"


def _merge_metadata(local: Dict, remote: Dict) -> Dict:
    """Merge two metadata dictionaries."""
    merged = local.copy()
    for key, value in remote.items():
        if key not in merged or merged[key] != value:
            merged[key] = value
    return merged
