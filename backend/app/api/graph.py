"""
NFM-X Graph API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from ..memory.models import Memory, MemoryRelationship, RelationshipType
from ..storage.database import get_db

router = APIRouter(prefix="/graph", tags=["Graph"])


class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    memory_id: Optional[str]


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    type: str
    strength: float


class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    total_nodes: int
    total_edges: int


@router.get("/", response_model=GraphResponse)
async def get_graph(
    memory_id: Optional[str] = Query(None),
    depth: int = Query(default=2, ge=1, le=5),
    limit: int = Query(default=100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
) -> GraphResponse:
    result = await db.execute(select(MemoryRelationship))
    relationships = result.scalars().all()
    
    memory_ids = set()
    for rel in relationships:
        memory_ids.add(rel.from_id)
        memory_ids.add(rel.to_id)
    
    if memory_id:
        if memory_id not in memory_ids:
            memory_ids.add(memory_id)
    
    result = await db.execute(select(Memory).where(Memory.id.in_(memory_ids)))
    memories = result.scalars().all()
    memory_map = {m.id: m for m in memories}
    
    nodes = []
    for mem_id in memory_ids:
        memory = memory_map.get(mem_id)
        if memory:
            nodes.append(GraphNode(
                id=mem_id,
                label=memory.title or f"Memory {mem_id[:8]}",
                type=memory.memory_type.value if memory.memory_type else "TEXT",
                memory_id=mem_id
            ))
    
    edges = []
    for rel in relationships:
        if memory_id:
            if rel.from_id != memory_id and rel.to_id != memory_id:
                continue
        edges.append(GraphEdge(
            id=rel.id,
            source=rel.from_id,
            target=rel.to_id,
            type=rel.relationship_type.value,
            strength=rel.strength
        ))
    
    return GraphResponse(
        nodes=nodes,
        edges=edges,
        total_nodes=len(nodes),
        total_edges=len(edges)
    )


@router.get("/{memory_id}/relationships", response_model=List[dict])
async def get_memory_relationships(
    memory_id: str,
    relationship_type: Optional[RelationshipType] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> List[dict]:
    result = await db.execute(select(Memory).where(Memory.id == memory_id))
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=404, detail=f"Memory {memory_id} not found")
    
    query = select(MemoryRelationship).where(
        or_(
            MemoryRelationship.from_id == memory_id,
            MemoryRelationship.to_id == memory_id
        )
    )
    
    if relationship_type:
        query = query.where(MemoryRelationship.relationship_type == relationship_type)
    
    result = await db.execute(query)
    relationships = result.scalars().all()
    
    return [
        {
            "id": r.id,
            "from_id": r.from_id,
            "to_id": r.to_id,
            "type": r.relationship_type.value,
            "strength": r.strength,
            "created_at": r.created_at
        }
        for r in relationships
    ]


@router.post("/relationships", status_code=201)
async def create_relationship(
    from_id: str,
    to_id: str,
    relationship_type: RelationshipType,
    strength: float = 1.0,
    db: AsyncSession = Depends(get_db)
) -> dict:
    import uuid
    from datetime import timezone
    
    for mem_id in [from_id, to_id]:
        result = await db.execute(select(Memory).where(Memory.id == mem_id))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail=f"Memory {mem_id} not found")
    
    relationship = MemoryRelationship(
        id=str(uuid.uuid4()),
        from_id=from_id,
        to_id=to_id,
        relationship_type=relationship_type,
        strength=strength,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(relationship)
    await db.commit()
    await db.refresh(relationship)
    
    return {
        "id": relationship.id,
        "from_id": relationship.from_id,
        "to_id": relationship.to_id,
        "type": relationship.relationship_type.value,
        "strength": relationship.strength,
        "created_at": relationship.created_at
    }


@router.delete("/relationships/{relationship_id}", status_code=204)
async def delete_relationship(relationship_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MemoryRelationship).where(MemoryRelationship.id == relationship_id)
    )
    relationship = result.scalar_one_or_none()
    if not relationship:
        raise HTTPException(status_code=404, detail=f"Relationship {relationship_id} not found")
    
    await db.delete(relationship)
    await db.commit()


from datetime import datetime, timezone
import datetime