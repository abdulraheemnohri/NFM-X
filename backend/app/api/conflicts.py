"""
NFM-X Conflict Resolution API
Handles sync conflicts with automatic and manual resolution strategies.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from backend.app.database import get_db_connection
from backend.app.models.conflict import Conflict, ConflictResolution

router = APIRouter(prefix="/api/v1/conflicts", tags=["conflicts"])


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
    detected_at: datetime = Field(default_factory=datetime.utcnow)
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
    conflict_type: ConflictType
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
    offset: int = 0
):
    """List all conflicts with optional filtering."""
    db = await get_db_connection()
    query = "SELECT id, memory_id, conflict_type, status, detected_at, created_at FROM conflicts"
    params = []
    
    if status_filter:
        query += " WHERE status = ?"
        params.append(status_filter.value)
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    async with db.execute(query, params) as cursor:
        rows = await cursor.fetchall()
    
    conflicts = []
    for row in rows:
        conflicts.append(ConflictListResponse(
            id=row[0],
            memory_id=row[1],
            conflict_type=ConflictType(row[2]),
            status=ConflictStatus(row[3]),
            detected_at=datetime.fromisoformat(row[4]),
            created_at=datetime.fromisoformat(row[5])
        ))
    
    return conflicts


@router.get("/{conflict_id}", response_model=ConflictResponse)
async def get_conflict(conflict_id: int):
    """Get details of a specific conflict."""
    db = await get_db_connection()
    async with db.execute(
        "SELECT * FROM conflicts WHERE id = ?", (conflict_id,)
    ) as cursor:
        row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Conflict not found")
    
    return ConflictResponse(
        id=row[0],
        memory_id=row[1],
        local_content=row[2],
        remote_content=row[3],
        local_metadata=row[4] or {},
        remote_metadata=row[5] or {},
        conflict_type=ConflictType(row[6]),
        detected_at=datetime.fromisoformat(row[7]),
        status=ConflictStatus(row[8]),
        resolution=ResolutionStrategy(row[9]) if row[9] else None,
        resolved_at=datetime.fromisoformat(row[10]) if row[10] else None,
        resolved_by=row[11],
        notes=row[12],
        created_at=datetime.fromisoformat(row[13])
    )


@router.post("/", response_model=ConflictResponse, status_code=status.HTTP_201_CREATED)
async def create_conflict(conflict: ConflictCreate):
    """Create a new conflict record."""
    db = await get_db_connection()
    
    async with db.execute(
        """INSERT INTO conflicts (memory_id, local_content, remote_content, 
           local_metadata, remote_metadata, conflict_type, detected_at, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            conflict.memory_id,
            conflict.local_content,
            conflict.remote_content,
            json.dumps(conflict.local_metadata),
            json.dumps(conflict.remote_metadata),
            conflict.conflict_type.value,
            conflict.detected_at.isoformat(),
            conflict.status.value
        )
    ) as cursor:
        conflict_id = cursor.lastrowid
    
    await db.commit()
    
    return ConflictResponse(
        id=conflict_id,
        **conflict.dict(),
        created_at=datetime.utcnow()
    )


@router.post("/{conflict_id}/resolve", response_model=ConflictResponse)
async def resolve_conflict(
    conflict_id: int,
    resolution: ConflictUpdate
):
    """Resolve a conflict with a specific strategy."""
    db = await get_db_connection()
    
    async with db.execute(
        "SELECT * FROM conflicts WHERE id = ?", (conflict_id,)
    ) as cursor:
        row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Conflict not found")
    
    applied_resolution = resolution.resolution or ResolutionStrategy.KEEP_BOTH
    
    if applied_resolution == ResolutionStrategy.MERGE:
        merged_content = self._merge_contents(row[2], row[3])
        merged_metadata = self._merge_metadata(row[4] or {}, row[5] or {})
    elif applied_resolution == ResolutionStrategy.KEEP_LOCAL:
        merged_content = row[2]
        merged_metadata = row[4] or {}
    elif applied_resolution == ResolutionStrategy.KEEP_REMOTE:
        merged_content = row[3]
        merged_metadata = row[5] or {}
    else:
        merged_content = row[2]
        merged_metadata = row[4] or {}
    
    resolved_at = resolution.resolved_at or datetime.utcnow()
    
    async with db.execute(
        """UPDATE conflicts SET status = ?, resolution = ?, resolved_at = ?, 
           resolved_by = ?, notes = ? WHERE id = ?""",
        (
            ConflictStatus.RESOLVED.value,
            applied_resolution.value,
            resolved_at.isoformat(),
            resolution.resolved_by,
            resolution.notes,
            conflict_id
        )
    ):
        pass
    
    await db.commit()
    
    return ConflictResponse(
        id=row[0],
        memory_id=row[1],
        local_content=row[2],
        remote_content=row[3],
        local_metadata=row[4] or {},
        remote_metadata=row[5] or {},
        conflict_type=ConflictType(row[6]),
        detected_at=datetime.fromisoformat(row[7]),
        status=ConflictStatus.RESOLVED,
        resolution=applied_resolution,
        resolved_at=resolved_at,
        resolved_by=resolution.resolved_by,
        notes=resolution.notes,
        created_at=datetime.fromisoformat(row[13])
    )


@router.post("/auto-resolve", response_model=Dict[str, Any])
async def auto_resolve_conflicts(request: AutoResolveRequest):
    """Auto-resolve conflicts using a specified strategy."""
    db = await get_db_connection()
    
    async with db.execute(
        "SELECT id FROM conflicts WHERE status = ?", (ConflictStatus.PENDING.value,)
    ) as cursor:
        rows = await cursor.fetchall()
    
    conflict_ids = [row[0] for row in rows]
    resolved_count = 0
    failed_count = 0
    
    if not request.dry_run:
        for conflict_id in conflict_ids:
            try:
                resolution = ConflictUpdate(
                    status=ConflictStatus.RESOLVED,
                    resolution=request.strategy,
                    resolved_at=datetime.utcnow(),
                    resolved_by="auto-resolver",
                    notes=f"Auto-resolved with {request.strategy.value} strategy"
                )
                await resolve_conflict(conflict_id, resolution)
                resolved_count += 1
            except Exception:
                failed_count += 1
    
    return {
        "total_conflicts": len(conflict_ids),
        "resolved_count": resolved_count,
        "failed_count": failed_count,
        "dry_run": request.dry_run,
        "strategy": request.strategy.value
    }


@router.post("/bulk-resolve", response_model=Dict[str, Any])
async def bulk_resolve_conflicts(request: BulkResolveRequest):
    """Bulk resolve multiple conflicts."""
    resolved_count = 0
    failed_count = 0
    
    if not request.dry_run:
        for conflict_id in request.conflict_ids:
            try:
                resolution = ConflictUpdate(
                    status=ConflictStatus.RESOLVED,
                    resolution=request.strategy,
                    resolved_at=datetime.utcnow(),
                    resolved_by="bulk-resolver",
                    notes=f"Bulk resolved with {request.strategy.value} strategy"
                )
                await resolve_conflict(conflict_id, resolution)
                resolved_count += 1
            except Exception:
                failed_count += 1
    
    return {
        "total_requested": len(request.conflict_ids),
        "resolved_count": resolved_count,
        "failed_count": failed_count,
        "dry_run": request.dry_run,
        "strategy": request.strategy.value
    }


@router.delete("/{conflict_id}", response_model=ConflictResponse)
async def dismiss_conflict(conflict_id: int):
    """Dismiss a conflict without resolution."""
    db = await get_db_connection()
    
    async with db.execute(
        "SELECT * FROM conflicts WHERE id = ?", (conflict_id,)
    ) as cursor:
        row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Conflict not found")
    
    async with db.execute(
        "UPDATE conflicts SET status = ?, resolved_at = ? WHERE id = ?",
        (ConflictStatus.DISMISSED.value, datetime.utcnow().isoformat(), conflict_id)
    ):
        pass
    
    await db.commit()
    
    return ConflictResponse(
        id=row[0],
        memory_id=row[1],
        local_content=row[2],
        remote_content=row[3],
        local_metadata=row[4] or {},
        remote_metadata=row[5] or {},
        conflict_type=ConflictType(row[6]),
        detected_at=datetime.fromisoformat(row[7]),
        status=ConflictStatus.DISMISSED,
        resolved_at=datetime.utcnow(),
        created_at=datetime.fromisoformat(row[13])
    )


def _merge_contents(self, local: str, remote: str) -> str:
    """Merge two content versions."""
    if local == remote:
        return local
    return f"{local}

---

{remote}"


def _merge_metadata(self, local: Dict, remote: Dict) -> Dict:
    """Merge two metadata dictionaries."""
    merged = local.copy()
    for key, value in remote.items():
        if key not in merged or merged[key] != value:
            merged[key] = value
    return merged


import json
