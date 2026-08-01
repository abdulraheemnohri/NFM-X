"""
NFM-X Graph API
Endpoints for knowledge graph operations
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func

from ..storage.database import get_db_session
from ..memory.models import Memory, MemoryRelationship

router = APIRouter(prefix="/graph", tags=["Graph"])


class GraphNodeResponse(BaseModel):
    id: str
    type: str
    label: str
    properties: Dict[str, Any]


class GraphEdgeResponse(BaseModel):
    source: str
    target: str
    type: str
    properties: Dict[str, Any]


class GraphResponse(BaseModel):
    nodes: List[GraphNodeResponse]
    edges: List[GraphEdgeResponse]


@router.get("/")
async def get_graph(
    agent_id: Optional[str] = None,
    memory_type: Optional[str] = None,
    limit: int = 100,
    db_session=Depends(get_db_session)
):
    """Get knowledge graph data"""
    nodes = []
    edges = []
    async with db_session.begin():
        stmt = select(Memory)
        if agent_id:
            stmt = stmt.where(Memory.agent_id == agent_id)
        if memory_type:
            stmt = stmt.where(Memory.type == memory_type)
        stmt = stmt.limit(limit)
        result = await db_session.execute(stmt)
        memories = result.scalars().all()
        for memory in memories:
            nodes.append(GraphNodeResponse(
                id=memory.id,
                type=memory.type.value,
                label=memory.content[:50] + "..." if len(memory.content) > 50 else memory.content,
                properties={"confidence": memory.confidence, "importance": memory.importance, "created_at": memory.created_at.isoformat()}
            ))
        memory_ids = [m.id for m in memories]
        if memory_ids:
            stmt = select(MemoryRelationship).where(
                MemoryRelationship.memory_id.in_(memory_ids) | MemoryRelationship.related_id.in_(memory_ids)
            )
            result = await db_session.execute(stmt)
            relationships = result.scalars().all()
            for rel in relationships:
                edges.append(GraphEdgeResponse(
                    source=rel.memory_id,
                    target=rel.related_id,
                    type=rel.relationship_type,
                    properties={"confidence": rel.confidence, "weight": rel.weight}
                ))
    return GraphResponse(nodes=nodes, edges=edges)