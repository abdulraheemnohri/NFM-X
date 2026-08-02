from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from typing import Dict, Any

from ..storage.database import get_db_session
from ..memory.models import Memory, MemoryEvent, MemoryRelationship

router = APIRouter()

@router.get("/memory/{memory_id}/debug")
async def debug_memory(memory_id: str, db_session=Depends(get_db_session)):
    """Debug inspector for a memory."""
    result = await db_session.execute(select(Memory).where(Memory.id == memory_id))
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    # Event counts
    events_result = await db_session.execute(
        select(MemoryEvent.event_type, func.count(MemoryEvent.id))
        .where(MemoryEvent.memory_id == memory_id)
        .group_by(MemoryEvent.event_type)
    )
    event_counts = {row[0]: row[1] for row in events_result}

    # Relationship counts
    rel_result = await db_session.execute(
        select(func.count(MemoryRelationship.id)).where(MemoryRelationship.memory_id == memory_id)
    )
    outgoing_rels = rel_result.scalar() or 0

    rel_result2 = await db_session.execute(
        select(func.count(MemoryRelationship.id)).where(MemoryRelationship.related_id == memory_id)
    )
    incoming_rels = rel_result2.scalar() or 0

    return {
        "memory_id": memory_id,
        "type": memory.type.value,
        "content_preview": memory.content[:200],
        "confidence": memory.confidence,
        "importance": memory.importance,
        "status": memory.status.value,
        "version": memory.version,
        "event_summary": event_counts,
        "relationships": {"outgoing": outgoing_rels, "incoming": incoming_rels},
        "created_at": memory.created_at.isoformat() if memory.created_at else None,
        "last_observed": memory.observed_at.isoformat() if memory.observed_at else None,
        "metadata": memory.metadata
    }
