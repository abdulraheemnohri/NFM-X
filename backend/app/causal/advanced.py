from typing import List, Dict, Any, Optional, Set
from collections import deque
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..memory.models import Memory, MemoryType, MemoryStatus, MemoryRelationship

class AdvancedCausalEngine:
    """Multi-hop causal chain reasoning and counterfactual queries."""

    async def find_causal_chain(self, db_session: AsyncSession, cause: str, effect: str,
                                 max_hops: int = 5) -> Optional[List[Dict[str, Any]]]:
        """Find causal chain from cause to effect through multiple hops."""
        # BFS through causal relationships
        stmt = select(Memory).where(Memory.type == MemoryType.CAUSAL, Memory.status == MemoryStatus.ACTIVE)
        result = await db_session.execute(stmt)
        causal_memories = result.scalars().all()

        # Build adjacency list
        graph = {}
        for mem in causal_memories:
            meta = mem.metadata or {}
            c = meta.get("cause", "").lower()
            e = meta.get("effect", "").lower()
            if c and e:
                if c not in graph:
                    graph[c] = []
                graph[c].append({"effect": e, "memory_id": mem.id, "relationship_type": meta.get("relationship_type", "causes")})

        # BFS
        queue = deque([(cause.lower(), [])])
        visited = set()
        while queue:
            current, path = queue.popleft()
            if current == effect.lower():
                return path
            if current in visited or len(path) >= max_hops:
                continue
            visited.add(current)
            for edge in graph.get(current, []):
                if edge["effect"] not in visited:
                    new_path = path + [{"cause": current, **edge}]
                    queue.append((edge["effect"], new_path))
        return None

    async def counterfactual_query(self, db_session: AsyncSession, hypothetical_remove: str,
                                   agent_id: Optional[str] = None) -> Dict[str, Any]:
        """What would be different if 'hypothetical_remove' had not happened?"""
        # Find all memories that mention the removed event
        stmt = select(Memory).where(
            Memory.content.ilike(f"%{hypothetical_remove}%"),
            Memory.status == MemoryStatus.ACTIVE
        )
        if agent_id:
            stmt = stmt.where(Memory.agent_id == agent_id)
        result = await db_session.execute(stmt)
        removed_memories = result.scalars().all()

        # Find downstream effects (memories that reference these)
        downstream = []
        for mem in removed_memories:
            stmt2 = select(MemoryRelationship).where(MemoryRelationship.memory_id == mem.id)
            result2 = await db_session.execute(stmt2)
            rels = result2.scalars().all()
            for rel in rels:
                mem_result = await db_session.execute(select(Memory).where(Memory.id == rel.related_id))
                related = mem_result.scalar_one_or_none()
                if related:
                    downstream.append({
                        "removed_memory_id": mem.id,
                        "removed_content": mem.content[:100],
                        "affected_memory_id": related.id,
                        "affected_content": related.content[:100],
                        "relationship": rel.relationship_type
                    })

        return {
            "hypothetical_remove": hypothetical_remove,
            "removed_memory_count": len(removed_memories),
            "downstream_effects": downstream,
            "affected_count": len(downstream),
            "note": "Counterfactual: These effects would potentially not exist"
        }
