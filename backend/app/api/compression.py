"""NFM-X V3 Compression API
Manages automatic compression of memories"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from backend.app.compression.scheduler import CompressionScheduler, CompressionConfig

router = APIRouter(prefix="/api/v1/compression", tags=["Compression"])


class CompressionConfigRequest(BaseModel):
    enabled: Optional[bool] = None
    age_days: Optional[int] = None
    importance_threshold: Optional[float] = None
    run_interval_hours: Optional[int] = None
    max_memories_per_run: Optional[int] = None
    archive_enabled: Optional[bool] = None
    archive_age_days: Optional[int] = None


class CompressionRunResponse(BaseModel):
    run_id: str
    started_at: str
    completed_at: Optional[str] = None
    memories_compressed: int
    memories_archived: int
    memories_skipped: int
    total_bytes_saved: int
    status: str
    error: Optional[str] = None


# Initialize scheduler
compression_scheduler = CompressionScheduler()


@router.get("/config", response_model=Dict[str, Any])
async def get_config():
    """
    Get current compression configuration
    """
    config = compression_scheduler.get_config()
    return {
        "enabled": config.enabled,
        "age_days": config.age_days,
        "importance_threshold": config.importance_threshold,
        "run_interval_hours": config.run_interval_hours,
        "max_memories_per_run": config.max_memories_per_run,
        "archive_enabled": config.archive_enabled,
        "archive_age_days": config.archive_age_days
    }


@router.put("/config", response_model=Dict[str, Any])
async def update_config(request: CompressionConfigRequest):
    """
    Update compression configuration
    """
    config_dict = request.dict(exclude_unset=True)
    config = compression_scheduler.update_config(**config_dict)
    return {
        "message": "Configuration updated",
        "config": {
            "enabled": config.enabled,
            "age_days": config.age_days,
            "importance_threshold": config.importance_threshold,
            "run_interval_hours": config.run_interval_hours,
            "max_memories_per_run": config.max_memories_per_run,
            "archive_enabled": config.archive_enabled,
            "archive_age_days": config.archive_age_days
        }
    }


@router.post("/run", response_model=CompressionRunResponse, status_code=201)
async def run_compression():
    """
    Manually trigger a compression run
    """
    import asyncio
    
    run = await compression_scheduler.run_compression()
    if not run:
        raise HTTPException(status_code=400, detail="Compression is disabled")
    
    return CompressionRunResponse(
        run_id=run.run_id,
        started_at=run.started_at.isoformat(),
        completed_at=run.completed_at.isoformat() if run.completed_at else None,
        memories_compressed=run.memories_compressed,
        memories_archived=run.memories_archived,
        memories_skipped=run.memories_skipped,
        total_bytes_saved=run.total_bytes_saved,
        status=run.status,
        error=run.error
    )


@router.get("/runs", response_model=List[CompressionRunResponse])
async def list_runs(limit: int = 100):
    """
    List compression run history
    """
    runs = compression_scheduler.get_run_history(limit)
    return [
        CompressionRunResponse(
            run_id=r.run_id,
            started_at=r.started_at.isoformat(),
            completed_at=r.completed_at.isoformat() if r.completed_at else None,
            memories_compressed=r.memories_compressed,
            memories_archived=r.memories_archived,
            memories_skipped=r.memories_skipped,
            total_bytes_saved=r.total_bytes_saved,
            status=r.status,
            error=r.error
        )
        for r in runs
    ]


@router.get("/runs/current", response_model=Optional[CompressionRunResponse])
async def get_current_run():
    """
    Get the current running compression run
    """
    run = compression_scheduler.get_current_run()
    if not run:
        return None
    
    return CompressionRunResponse(
        run_id=run.run_id,
        started_at=run.started_at.isoformat(),
        completed_at=run.completed_at.isoformat() if run.completed_at else None,
        memories_compressed=run.memories_compressed,
        memories_archived=run.memories_archived,
        memories_skipped=run.memories_skipped,
        total_bytes_saved=run.total_bytes_saved,
        status=run.status,
        error=run.error
    )


@router.post("/start", status_code=200)
async def start_scheduler():
    """
    Start the compression scheduler (background task)
    """
    import asyncio
    asyncio.create_task(compression_scheduler.start())
    return {"message": "Compression scheduler started"}


@router.post("/stop", status_code=200)
async def stop_scheduler():
    """
    Stop the compression scheduler
    """
    await compression_scheduler.stop()
    return {"message": "Compression scheduler stopped"}