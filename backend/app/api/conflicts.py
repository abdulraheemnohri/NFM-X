from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy import select

from backend.app.storage.database import get_db_session
from backend.app.memory.models import MemoryConflict
from backend.app.memory.conflicts import ConflictDetector

router = APIRouter()

class ConflictResponse(BaseModel):
    id: str
    memory_a_id: str
    memory_b_id: str
    conflict_type: str
    description: Optional[str] = None
    severity: float
    status: str
    created_at: str

@router.get("/conflicts", response_model=List[ConflictResponse])
async def list_conflicts(
    status: Optional[str] = None,
    db_session=Depends(get_db_session)
):
    stmt = select(MemoryConflict)
    if status:
        stmt = stmt.where(MemoryConflict.status == status)
    stmt = stmt.order_by(MemoryConflict.created_at.desc())
    result = await db_session.execute(stmt)
    conflicts = result.scalars().all()
    return [
        ConflictResponse(
            id=c.id,
            memory_a_id=c.memory_a_id,
            memory_b_id=c.memory_b_id,
            conflict_type=c.conflict_type,
            description=c.description,
            severity=c.severity,
            status=c.status,
            created_at=c.created_at.isoformat() if c.created_at else None
        )
        for c in conflicts
    ]

@router.post("/memory/{memory_id}/scan-conflicts")
async def scan_memory_conflicts(memory_id: str, db_session=Depends(get_db_session)):
    detector = ConflictDetector()
    conflicts = await detector.scan_for_conflicts(db_session, memory_id)
    created = []
    for c in conflicts:
        record = await detector.create_conflict_record(
            db_session=db_session,
            memory_a_id=c["memory_a_id"],
            memory_b_id=c["memory_b_id"],
            conflict_type=c["conflict_type"],
            description=c["description"],
            severity=c["severity"]
        )
        created.append(record.id)
    return {"scanned": True, "conflicts_found": len(conflicts), "conflict_ids": created}
