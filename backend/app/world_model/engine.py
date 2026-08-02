from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

import networkx as nx

from ..memory.models import Memory, MemoryType, MemoryStatus

class WorldModel:
    """Structured representation of entities, states, and transitions."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.entity_types = {"person", "organization", "technology", "location", "concept", "system"}

    async def build_from_memories(self, db_session: AsyncSession, agent_id: Optional[str] = None):
        """Build world model graph from semantic memories."""
        stmt = select(Memory).where(
            Memory.type == MemoryType.SEMANTIC,
            Memory.status == MemoryStatus.ACTIVE
        )
        if agent_id:
            stmt = stmt.where(Memory.agent_id == agent_id)
        result = await db_session.execute(stmt)
        memories = result.scalars().all()

        for mem in memories:
            self._extract_entities_from_memory(mem)

        # Build relationships between entities that co-occur
        for mem in memories:
            entities_in_mem = [n for n, data in self.graph.nodes(data=True)
                               if data.get("source_memory_id") == mem.id]
            for i, e1 in enumerate(entities_in_mem):
                for e2 in entities_in_mem[i + 1:]:
                    if not self.graph.has_edge(e1, e2):
                        self.graph.add_edge(e1, e2, relationship="co_occurs",
                                           strength=1, memories=[mem.id])
                    else:
                        self.graph[e1][e2]["strength"] += 1
                        self.graph[e1][e2]["memories"].append(mem.id)

    def _extract_entities_from_memory(self, memory: Memory):
        """Extract named entities from memory content. Simple NER using keyword lists."""
        content_lower = memory.content.lower()

        # Technology entities
        tech_keywords = ["python", "javascript", "react", "fastapi", "sqlalchemy",
                        "docker", "kubernetes", "aws", "azure", "gpt", "llm"]
        for tech in tech_keywords:
            if tech in content_lower:
                if tech not in self.graph:
                    self.graph.add_node(tech, entity_type="technology",
                                       first_seen=memory.created_at.isoformat() if memory.created_at else None,
                                       source_memory_id=memory.id,
                                       mentions=1)
                else:
                    self.graph.nodes[tech]["mentions"] += 1

        # Person entities (simple heuristic: capitalized words)
        import re
        persons = re.findall(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b", memory.content)
        for person in persons:
            person_lower = person.lower()
            if person_lower not in self.graph:
                self.graph.add_node(person_lower, entity_type="person",
                                   first_seen=memory.created_at.isoformat() if memory.created_at else None,
                                   source_memory_id=memory.id, mentions=1)
            else:
                self.graph.nodes[person_lower]["mentions"] += 1

    def query_entity(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """Query the current state of an entity in the world model."""
        if entity_name not in self.graph:
            return None

        node_data = dict(self.graph.nodes[entity_name])
        neighbors = []
        for neighbor in self.graph.neighbors(entity_name):
            edge_data = self.graph[entity_name][neighbor]
            neighbors.append({
                "entity": neighbor,
                "relationship": edge_data.get("relationship", "related"),
                "strength": edge_data.get("strength", 1),
                "entity_type": self.graph.nodes[neighbor].get("entity_type", "unknown")
            })

        return {
            "entity": entity_name,
            "entity_type": node_data.get("entity_type", "unknown"),
            "mentions": node_data.get("mentions", 0),
            "first_seen": node_data.get("first_seen"),
            "related_entities": neighbors,
            "related_count": len(neighbors)
        }

    def find_path(self, source: str, target: str, max_hops: int = 3) -> Optional[List[str]]:
        """Find connection path between two entities."""
        try:
            path = nx.shortest_path(self.graph, source, target)
            if len(path) - 1 <= max_hops:
                return path
            return None
        except nx.NetworkXNoPath:
            return None
        except Exception:
            return None

    def get_central_entities(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Get most central entities by degree centrality."""
        if not self.graph.nodes:
            return []
        centrality = nx.degree_centrality(self.graph)
        sorted_entities = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        return [
            {"entity": name, "centrality": round(score, 4),
             "entity_type": self.graph.nodes[name].get("entity_type", "unknown"),
             "mentions": self.graph.nodes[name].get("mentions", 0)}
            for name, score in sorted_entities[:top_n]
        ]
