"""NFM-X V3 Sync API
Synchronization with conflict auto-resolution"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from backend.app.sync.auto_resolve import SyncConflictResolver, ConflictResolutionStrategy

router = APIRouter(prefix="/api/v1/sync", tags=["Sync"])


class ConflictResolutionStrategyModel(str, Enum):
    TIMESTAMP = "timestamp"
    VERSION = "version"
    MANUAL = "manual"
    MERGE = "merge"
    PREFER_SOURCE = "prefer_source"
    PREFER_SERVER = "prefer_server"


class SyncConflictRequest(BaseModel):
    memory_id: str
    local_version: str
    remote_version: str
    local_timestamp: datetime
    remote_timestamp: datetime
    local_content: Dict[str, Any]
    remote_content: Dict[str, Any]
    device_id: str


class AutoResolveRequest(BaseModel):
    strategy: Optional[ConflictResolutionStrategyModel] = None
    dry_run: Optional[bool] = False


class ConflictResponse(BaseModel):
    conflict_id: str
    memory_id: str
    local_version: str
    remote_version: str
    detected_at: datetime
    resolved: bool
    resolution_strategy: Optional[str] = None


class ResolutionResponse(BaseModel):
    conflict_id: str
    success: bool
    resolution_strategy: str
    resolved_content: Dict[str, Any]
    notes: str
    resolved_at: datetime


# Initialize conflict resolver
sync_resolver = SyncConflictResolver()


@router.post("/conflicts", response_model=ConflictResponse, status_code=201)
async def detect_conflict(request: SyncConflictRequest):
    """
    Detect and register a synchronization conflict
    """
    conflict = sync_resolver.detect_conflict(
        memory_id=request.memory_id,
        local_version=request.local_version,
        remote_version=request.remote_version,
        local_timestamp=request.local_timestamp,
        remote_timestamp=request.remote_timestamp,
        local_content=request.local_content,
        remote_content=request.remote_content,
        device_id=request.device_id
    )
    
    return ConflictResponse(
        conflict_id=conflict.conflict_id,
        memory_id=conflict.memory_id,
        local_version=conflict.local_version,
        remote_version=conflict.remote_version,
        detected_at=conflict.detected_at,
        resolved=conflict.resolved,
        resolution_strategy=conflict.resolution_strategy.value if conflict.resolution_strategy else None
    )


@router.get("/conflicts", response_model=List[ConflictResponse])
async def list_conflicts(resolved: Optional[bool] = None):
    """
    List all synchronization conflicts
    """
    conflicts = sync_resolver.list_conflicts(resolved)
    return [
        ConflictResponse(
            conflict_id=c.conflict_id,
            memory_id=c.memory_id,
            local_version=c.local_version,
            remote_version=c.remote_version,
            detected_at=c.detected_at,
            resolved=c.resolved,
            resolution_strategy=c.resolution_strategy.value if c.resolution_strategy else None
        )
        for c in conflicts
    ]


@router.post("/conflicts/{conflict_id}/resolve", response_model=ResolutionResponse)
async def resolve_conflict(conflict_id: str, request: AutoResolveRequest):
    """
    Auto-resolve a specific conflict
    """
    strategy = None
    if request.strategy:
        strategy = ConflictResolutionStrategy(request.strategy.value)
    
    try:
        result = sync_resolver.auto_resolve(conflict_id, strategy)
        return ResolutionResponse(
            conflict_id=result.conflict_id,
            success=result.success,
            resolution_strategy=result.resolution_strategy.value,
            resolved_content=result.resolved_content,
            notes=result.notes,
            resolved_at=result.resolved_at
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/auto-resolve", response_model=Dict[str, Any])
async def auto_resolve_all(request: AutoResolveRequest):
    """
    Auto-resolve all unresolved conflicts
    """
    strategy = None
    if request.strategy:
        strategy = ConflictResolutionStrategy(request.strategy.value)
    
    result = sync_resolver.auto_resolve_all(strategy)
    return result


@router.post("/strategy/{memory_id}", status_code=200)
async def set_resolution_strategy(
    memory_id: str,
    strategy: ConflictResolutionStrategyModel
):
    """
    Set default resolution strategy for a specific memory
    """
    sync_resolver.set_strategy_for_memory(
        memory_id,
        ConflictResolutionStrategy(strategy.value)
    )
    return {"message": f"Strategy set for {memory_id}: {strategy.value}"}


@router.get("/conflicts/history", response_model=List[ResolutionResponse])
async def get_resolution_history(limit: int = 100):
    """
    Get history of conflict resolutions
    """
    history = sync_resolver.get_resolution_history(limit)
    return [
        ResolutionResponse(
            conflict_id=r.conflict_id,
            success=r.success,
            resolution_strategy=r.resolution_strategy.value,
            resolved_content=r.resolved_content,
            notes=r.notes,
            resolved_at=r.resolved_at
        )
        for r in history
    ]