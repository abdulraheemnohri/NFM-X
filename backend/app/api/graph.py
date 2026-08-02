from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy import select

from backend.app.storage.database import get_db_session
from backend.app.memory.models import Memory, MemoryRelationship

router = APIRouter()

class RelatedMemoryResponse(BaseModel):
    relationship_type: str
    confidence: Optional[float] = None
    memory: Dict[str, Any]

@router.get("/memory/{memory_id}/related")
async def get_related_memories(
    memory_id: str,
    relationship_type: Optional[str] = None,
    db_session=Depends(get_db_session)
):
    stmt = select(MemoryRelationship).where(MemoryRelationship.memory_id == memory_id)
    if relationship_type:
        stmt = stmt.where(MemoryRelationship.relationship_type == relationship_type)
    result = await db_session.execute(stmt)
    relationships = result.scalars().all()

    related = []
    for rel in relationships:
        mem_result = await db_session.execute(
            select(Memory).where(Memory.id == rel.related_id)
        )
        mem = mem_result.scalar_one_or_none()
        if mem:
            related.append(RelatedMemoryResponse(
                relationship_type=rel.relationship_type,
                confidence=rel.confidence,
                memory={
                    "id": mem.id,
                    "type": mem.type.value,
                    "content": mem.content,
                    "confidence": mem.confidence,
                    "status": mem.status.value
                }
            ))
    return {"memory_id": memory_id, "related": related}

@router.post("/memory/{memory_id}/relate/{related_id}")
async def create_relationship(
    memory_id: str,
    related_id: str,
    relationship_type: str,
    confidence: Optional[float] = 0.7,
    db_session=Depends(get_db_session)
):
    rel = MemoryRelationship(
        memory_id=memory_id,
        related_id=related_id,
        relationship_type=relationship_type,
        confidence=confidence
    )
    db_session.add(rel)
    await db_session.commit()
    return {"id": rel.id, "relationship_type": relationship_type, "created": True}
