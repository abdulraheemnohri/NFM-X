from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select

from ..storage.database import get_db_session
from ..memory.models import Memory, MemoryEvent
from ..memory.evolution import EvolutionEngine

router = APIRouter()

class EvolutionTriggerRequest(BaseModel):
    memory_id: str

class EvolutionResult(BaseModel):
    memory_id: str
    action: str
    details: Dict[str, Any]
    timestamp: str

@router.post("/evolve")
async def trigger_evolution(request: EvolutionTriggerRequest, db_session=Depends(get_db_session)):
    result = await db_session.execute(select(Memory).where(Memory.id == request.memory_id))
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    engine = EvolutionEngine()
    evolution_result = await engine.evolve(db_session, memory)
    return EvolutionResult(
        memory_id=request.memory_id, action=evolution_result["action"],
        details=evolution_result["details"], timestamp=datetime.now(timezone.utc).isoformat()
    )

@router.get("/memory/{memory_id}/evolution")
async def get_evolution_history(memory_id: str, db_session=Depends(get_db_session)):
    stmt = select(MemoryEvent).where(
        MemoryEvent.memory_id == memory_id,
        MemoryEvent.event_type.in_(["reinforce", "refine", "expand", "contradicted", "duplicate_detected"])
    ).order_by(MemoryEvent.timestamp.desc())
    result = await db_session.execute(stmt)
    events = result.scalars().all()
    return {
        "memory_id": memory_id,
        "evolution_events": [{"event_type": e.event_type, "details": e.details,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None, "agent_id": e.agent_id} for e in events]
    }
