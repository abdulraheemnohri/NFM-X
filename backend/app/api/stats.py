"""
NFM-X Stats API
"""
from fastapi import APIRouter, Depends
from typing import Dict
from pydantic import BaseModel
from sqlalchemy import select, func
from ..memory.models import Memory, MemoryStatus
from ..storage.database import get_db

router = APIRouter(prefix="/stats", tags=["Stats"])

class StatsResponse(BaseModel):
    total_memories: int
    active_memories: int
    by_type: Dict[str, int]
    by_status: Dict[str, int]

@router.get("/", response_model=StatsResponse)
async def get_stats(db=Depends(get_db)):
    result = await db.execute(select(func.count(Memory.id)))
    total = result.scalar() or 0
    
    result = await db.execute(
        select(Memory.status, func.count(Memory.id)).group_by(Memory.status)
    )
    by_status = {k.value: v for k, v in result.all()}
    
    result = await db.execute(
        select(Memory.memory_type, func.count(Memory.id)).group_by(Memory.memory_type)
    )
    by_type = {k.value: v for k, v in result.all()}
    
    return StatsResponse(
        total_memories=total,
        active_memories=by_status.get("ACTIVE", 0),
        by_type=by_type,
        by_status=by_status
    )