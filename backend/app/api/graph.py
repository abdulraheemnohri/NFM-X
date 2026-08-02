"""
NFM-X Graph API
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import select
from ..memory.models import Memory, MemoryRelationship, RelationshipType
from ..storage.database import get_db

router = APIRouter(prefix="/graph", tags=["Graph"])

class GraphResponse(BaseModel):
    nodes: List[dict]
    edges: List[dict]
    total_nodes: int
    total_edges: int

@router.get("/", response_model=GraphResponse)
async def get_graph(db=Depends(get_db)):
    result = await db.execute(select(MemoryRelationship))
    relationships = result.scalars().all()
    
    memory_ids = set()
    for rel in relationships:
        memory_ids.add(rel.from_id)
        memory_ids.add(rel.to_id)
    
    result = await db.execute(select(Memory).where(Memory.id.in_(memory_ids)))
    memories = result.scalars().all()
    
    nodes = [{"id": m.id, "label": m.title or m.id[:8], "type": m.memory_type.value} for m in memories]
    edges = [{"id": r.id, "source": r.from_id, "target": r.to_id, "type": r.relationship_type.value} for r in relationships]
    
    return GraphResponse(
        nodes=nodes,
        edges=edges,
        total_nodes=len(nodes),
        total_edges=len(edges)
    )