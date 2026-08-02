from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any
from sqlalchemy import select, func

from backend.app.storage.database import get_db_session
from backend.app.memory.models import Memory, MemoryVersion, MemoryEvent, MemoryConflict, MemoryStatus

router = APIRouter()

class StatsResponse(BaseModel):
    total_memories: int
    active_memories: int
    historical_versions: int
    total_events: int
    unresolved_conflicts: int
    memories_by_type: Dict[str, int]
    avg_confidence: float
    avg_importance: float

@router.get("/stats", response_model=StatsResponse)
async def get_stats(db_session=Depends(get_db_session)):
    # Total memories
    total_result = await db_session.execute(select(func.count(Memory.id)))
    total = total_result.scalar() or 0

    # Active
    active_result = await db_session.execute(
        select(func.count(Memory.id)).where(Memory.status == MemoryStatus.ACTIVE)
    )
    active = active_result.scalar() or 0

    # Versions
    versions_result = await db_session.execute(select(func.count(MemoryVersion.id)))
    versions = versions_result.scalar() or 0

    # Events
    events_result = await db_session.execute(select(func.count(MemoryEvent.id)))
    events = events_result.scalar() or 0

    # Conflicts
    conflicts_result = await db_session.execute(
        select(func.count(MemoryConflict.id)).where(MemoryConflict.status == "unresolved")
    )
    conflicts = conflicts_result.scalar() or 0

    # By type
    type_result = await db_session.execute(
        select(Memory.type, func.count(Memory.id)).group_by(Memory.type)
    )
    by_type = {row[0].value if hasattr(row[0], 'value') else str(row[0]): row[1] for row in type_result}

    # Averages
    avg_conf_result = await db_session.execute(select(func.avg(Memory.confidence)))
    avg_conf = avg_conf_result.scalar() or 0.0

    avg_imp_result = await db_session.execute(select(func.avg(Memory.importance)))
    avg_imp = avg_imp_result.scalar() or 0.0

    return StatsResponse(
        total_memories=total,
        active_memories=active,
        historical_versions=versions,
        total_events=events,
        unresolved_conflicts=conflicts,
        memories_by_type=by_type,
        avg_confidence=round(float(avg_conf), 3),
        avg_importance=round(float(avg_imp), 3)
    )
