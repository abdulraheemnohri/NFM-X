"""NFM-X V2 Relationships - Semantic memory connections"""

from typing import List, Dict, Optional, Set
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class RelationshipType(str, Enum):
    CAUSAL = "causal"           # Cause-effect relationship
    TEMPORAL = "temporal"       # Time-based relationship
    SEMANTIC = "semantic"       # Meaning-based relationship
    REFERENTIAL = "referential" # Reference/citation relationship
    HIERARCHICAL = "hierarchical" # Parent-child relationship


@dataclass
class MemoryRelationship:
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    weight: float = 1.0
    created_at: datetime = datetime.now()
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MemoryRelationshipManager:
    """Manages relationships between memories"""
    
    def __init__(self):
        self.relationships: Dict[str, List[MemoryRelationship]] = {}
        self.adjacency_list: Dict[str, Set[str]] = {}
    
    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType,
        weight: float = 1.0,
        metadata: Optional[Dict] = None
    ) -> MemoryRelationship:
        """Add a relationship between two memories"""
        relationship = MemoryRelationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            weight=weight,
            metadata=metadata or {}
        )
        
        # Add to relationships list
        if source_id not in self.relationships:
            self.relationships[source_id] = []
        self.relationships[source_id].append(relationship)
        
        # Update adjacency list for traversal
        if source_id not in self.adjacency_list:
            self.adjacency_list[source_id] = set()
        self.adjacency_list[source_id].add(target_id)
        
        if target_id not in self.adjacency_list:
            self.adjacency_list[target_id] = set()
        self.adjacency_list[target_id].add(source_id)  # Bidirectional
        
        return relationship
    
    def get_relationships(self, memory_id: str) -> List[MemoryRelationship]:
        """Get all relationships for a memory"""
        return self.relationships.get(memory_id, [])
    
    def get_connected_memories(self, memory_id: str) -> Set[str]:
        """Get all memories connected to this memory"""
        return self.adjacency_list.get(memory_id, set())
    
    def remove_relationship(self, source_id: str, target_id: str) -> bool:
        """Remove a relationship between two memories"""
        if source_id in self.relationships:
            self.relationships[source_id] = [
                r for r in self.relationships[source_id]
                if not (r.source_id == source_id and r.target_id == target_id)
            ]
            
            # Update adjacency list
            if source_id in self.adjacency_list and target_id in self.adjacency_list[source_id]:
                self.adjacency_list[source_id].remove(target_id)
            if target_id in self.adjacency_list and source_id in self.adjacency_list[target_id]:
                self.adjacency_list[target_id].remove(source_id)
            return True
        return False