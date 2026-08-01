"""
NFM-X Graph API
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
async def get_graph(agent_id: Optional[str] = None, memory_type: Optional[str] = None, limit: int = 100, db_session=Depends(get_db_session)):
    nodes = []
    edges = []
    async with db_session.begin():
        stmt = select(Memory)
        if agent_id: stmt = stmt.where(Memory.agent_id == agent_id)
        if memory_type: stmt = stmt.where(Memory.type == memory_type)
        stmt = stmt.limit(limit)
        result = await db_session.execute(stmt)
        memories = result.scalars().all()
        for memory in memories:
            nodes.append(GraphNodeResponse(id=memory.id, type=memory.type.value, label=memory.content[:50] + "..." if len(memory.content) > 50 else memory.content, properties={"confidence": memory.confidence, "importance": memory.importance, "created_at": memory.created_at.isoformat()}))
        memory_ids = [m.id for m in memories]
        if memory_ids:
            stmt = select(MemoryRelationship).where(MemoryRelationship.memory_id.in_(memory_ids) | MemoryRelationship.related_id.in_(memory_ids))
            result = await db_session.execute(stmt)
            relationships = result.scalars().all()
            for rel in relationships:
                edges.append(GraphEdgeResponse(source=rel.memory_id, target=rel.related_id, type=rel.relationship_type, properties={"confidence": rel.confidence, "weight": rel.weight}))
    return GraphResponse(nodes=nodes, edges=edges)

@router.get("/stats")
async def get_graph_stats(agent_id: Optional[str] = None, db_session=Depends(get_db_session)):
    async with db_session.begin():
        node_stmt = select(Memory)
        if agent_id: node_stmt = node_stmt.where(Memory.agent_id == agent_id)
        node_result = await db_session.execute(node_stmt)
        node_count = len(node_result.scalars().all())
        edge_stmt = select(MemoryRelationship)
        edge_result = await db_session.execute(edge_stmt)
        edge_count = len(edge_result.scalars().all())
        type_counts = {}
        type_stmt = select(Memory.type, func.count(Memory.id)).group_by(Memory.type)
        if agent_id: type_stmt = type_stmt.where(Memory.agent_id == agent_id)
        type_result = await db_session.execute(type_stmt)
        for row in type_result: type_counts[row.type.value] = row.count
        return {"node_count": node_count, "edge_count": edge_count, "type_counts": type_counts, "density": edge_count / max(node_count, 1)}