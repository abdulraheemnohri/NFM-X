"""NFM-X V3 World Model Entity Merge
Merges two entities in the world model with their relationships and metadata"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MergeStrategy(str, Enum):
    COMBINE = "combine"           # Combine all attributes and relationships
    PREFER_SOURCE = "prefer_source" # Prefer source entity attributes
    PREFER_TARGET = "prefer_target" # Prefer target entity attributes



@dataclass
class Entity:
    """Represents an entity in the world model"""
    entity_id: str
    name: str
    entity_type: str
    attributes: Dict[str, any] = field(default_factory=dict)
    relationships: Dict[str, List[str]] = field(default_factory=dict)  # {relation_type: [target_ids]}
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, any] = field(default_factory=dict)
    
    def get_relationship_targets(self, relationship_type: str) -> Set[str]:
        """Get all targets for a specific relationship type"""
        return set(self.relationships.get(relationship_type, []))


@dataclass
class MergeResult:
    """Result of a merge operation"""
    success: bool
    merged_entity_id: str
    source_entity_id: str
    target_entity_id: str
    strategy_used: MergeStrategy
    attributes_merged: Dict[str, any]
    relationships_merged: Dict[str, List[str]]
    conflicts_resolved: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "merged_entity_id": self.merged_entity_id,
            "source_entity_id": self.source_entity_id,
            "target_entity_id": self.target_entity_id,
            "strategy_used": self.strategy_used.value,
            "attributes_merged": self.attributes_merged,
            "relationships_merged": {k: v for k, v in self.relationships_merged.items()},
            "conflicts_resolved": self.conflicts_resolved,
            "timestamp": self.timestamp.isoformat()
        }


class WorldModelMerger:
    """Handles merging of entities in the world model"""
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.merge_history: List[MergeResult] = []
    
    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the world model"""
        self.entities[entity.entity_id] = entity
        logger.info(f"Added entity: {entity.entity_id} ({entity.entity_type})")
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by ID"""
        return self.entities.get(entity_id)
    
    def merge_entities(
        self,
        source_id: str,
        target_id: str,
        strategy: MergeStrategy = MergeStrategy.COMBINE
    ) -> MergeResult:
        """
        Merge two entities using the specified strategy
        
        Args:
            source_id: ID of the source entity (will be removed)
            target_id: ID of the target entity (will be updated)
            strategy: How to resolve conflicts
            
        Returns:
            MergeResult with details of the merge operation
        """
        source = self.entities.get(source_id)
        target = self.entities.get(target_id)
        
        if not source:
            raise ValueError(f"Source entity {source_id} not found")
        if not target:
            raise ValueError(f"Target entity {target_id} not found")
        
        conflicts_resolved = []
        merged_attributes = {}
        merged_relationships = {}
        
        # Merge attributes based on strategy
        all_keys = set(source.attributes.keys()) | set(target.attributes.keys())
        for key in all_keys:
            source_val = source.attributes.get(key)
            target_val = target.attributes.get(key)
            
            if key not in target.attributes:
                # Key only in source, add to target
                merged_attributes[key] = source_val
                conflicts_resolved.append(f"Added attribute: {key}")
            elif key not in source.attributes:
                # Key only in target, keep target value
                merged_attributes[key] = target_val
            else:
                # Key in both, resolve conflict
                if strategy == MergeStrategy.PREFER_SOURCE:
                    merged_attributes[key] = source_val
                    conflicts_resolved.append(f"Conflict resolved: {key} -> source value")
                elif strategy == MergeStrategy.PREFER_TARGET:
                    merged_attributes[key] = target_val
                    conflicts_resolved.append(f"Conflict resolved: {key} -> target value")
                else:  # COMBINE
                    # For combine, create a list of both values
                    merged_attributes[key] = [target_val, source_val]
                    conflicts_resolved.append(f"Conflict resolved: {key} -> combined")
        
        # Merge relationships
        all_rel_types = set(source.relationships.keys()) | set(target.relationships.keys())
        for rel_type in all_rel_types:
            source_targets = set(source.relationships.get(rel_type, []))
            target_targets = set(target.relationships.get(rel_type, []))
            
            # Union of all relationships
            merged_targets = list(source_targets | target_targets)
            merged_relationships[rel_type] = merged_targets
            
            # Update the inverse relationships in connected entities
            for target_id in merged_targets:
                if target_id in self.entities:
                    target_entity = self.entities[target_id]
                    # Add inverse relationship if it does not exist
                    inverse_type = self._get_inverse_relationship(rel_type)
                    if inverse_type:
                        current = set(target_entity.relationships.get(inverse_type, []))
                        current.add(target.entity_id)  # Will be merged entity
                        target_entity.relationships[inverse_type] = list(current)
        
        # Update target entity
        target.attributes = merged_attributes
        target.relationships = merged_relationships
        target.updated_at = datetime.utcnow()
        
        # Remove source entity
        del self.entities[source_id]
        
        # Create merge result
        result = MergeResult(
            success=True,
            merged_entity_id=target_id,
            source_entity_id=source_id,
            target_entity_id=target_id,
            strategy_used=strategy,
            attributes_merged=merged_attributes,
            relationships_merged=merged_relationships,
            conflicts_resolved=conflicts_resolved
        )
        
        self.merge_history.append(result)
        logger.info(f"Merged {source_id} into {target_id} using {strategy.value}")
        
        return result
    
    def _get_inverse_relationship(self, relationship_type: str) -> Optional[str]:
        """Get the inverse of a relationship type"""
        inverses = {
            "parent_of": "child_of",
            "child_of": "parent_of",
            "part_of": "has_part",
            "has_part": "part_of",
            "connected_to": "connected_to",
            "depends_on": "required_by",
            "required_by": "depends_on",
            "similar_to": "similar_to",
            "opposite_of": "opposite_of"
        }
        return inverses.get(relationship_type)
    
    def get_merge_history(self, limit: int = 100) -> List[MergeResult]:
        """Get the history of merge operations"""
        return self.merge_history[-limit:]
    
    def list_entities(self, entity_type: Optional[str] = None) -> List[Entity]:
        """List all entities, optionally filtered by type"""
        if entity_type:
            return [e for e in self.entities.values() if e.entity_type == entity_type]
        return list(self.entities.values())