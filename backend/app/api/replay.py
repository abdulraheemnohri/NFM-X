from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from typing import List, Dict, Any

from ..storage.database import get_db_session
from ..memory.models import Memory, MemoryVersion, MemoryEvent, MemoryConflict

router = APIRouter()

@router.get("/memory/{memory_id}/replay")
async def replay_memory_evolution(memory_id: str, db_session=Depends(get_db_session)):
    """Replay complete evolution of a memory."""
    result = await db_session.execute(select(Memory).where(Memory.id == memory_id))
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    # Get all versions
    versions_result = await db_session.execute(
        select(MemoryVersion).where(MemoryVersion.memory_id == memory_id).order_by(MemoryVersion.version)
    )
    versions = versions_result.scalars().all()

    # Get all events
    events_result = await db_session.execute(
        select(MemoryEvent).where(MemoryEvent.memory_id == memory_id).order_by(MemoryEvent.timestamp)
    )
    events = events_result.scalars().all()

    # Get conflicts
    conflicts_result = await db_session.execute(
        select(MemoryConflict).where(
            (MemoryConflict.memory_a_id == memory_id) | (MemoryConflict.memory_b_id == memory_id)
        )
    )
    conflicts = conflicts_result.scalars().all()

    timeline = []
    for v in versions:
        timeline.append({
            "type": "version", "version": v.version, "content": v.content,
            "change_type": v.change_type.value, "change_reason": v.change_reason,
            "confidence": v.confidence, "created_at": v.created_at.isoformat() if v.created_at else None
        })
    for e in events:
        timeline.append({
            "type": "event", "event_type": e.event_type, "details": e.details,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None, "agent_id": e.agent_id
        })
    for c in conflicts:
        timeline.append({
            "type": "conflict", "conflict_id": c.id, "conflict_type": c.conflict_type,
            "severity": c.severity, "status": c.status, "created_at": c.created_at.isoformat() if c.created_at else None
        })

    timeline.sort(key=lambda x: x.get("created_at") or x.get("timestamp") or "")

    return {
        "memory_id": memory_id,
        "current_content": memory.content,
        "current_confidence": memory.confidence,
        "total_versions": len(versions),
        "total_events": len(events),
        "total_conflicts": len(conflicts),
        "timeline": timeline
    }
