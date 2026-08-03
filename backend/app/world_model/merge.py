"""NFM-X V3 World Model Entity Merge
Merges entities in the world model with database persistence
"""

from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, update, delete

from ..storage.database import AsyncSessionLocal
from .models import WorldEntity, EntityMerge, EntityType, MergeStrategy

logger = logging.getLogger(__name__)


class WorldModelMerger:
    """Handles merging of entities in the world model with database persistence"""
    
    def __init__(self):
        self._session = None
    
    async def get_session(self) -> AsyncSession:
        """Get or create a database session"""
        if self._session is None or self._session.is_active is False:
            self._session = AsyncSessionLocal()
        return self._session
    
    async def close(self):
        """Close the database session"""
        if self._session:
            await self._session.close()
            self._session = None
    
    async def add_entity(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add an entity to the world model with database persistence"""
        session = await self.get_session()
        try:
            entity_id = entity_data.get('entity_id', str(uuid.uuid4()))
            
            entity = WorldEntity(
                entity_id=entity_id,
                id=str(uuid.uuid4()),
                name=entity_data.get('name', ''),
                entity_type=entity_data.get('entity_type', EntityType.OTHER),
                attributes=entity_data.get('attributes', {}),
                relationships=entity_data.get('relationships', {}),
                metadata=entity_data.get('metadata', {}),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                is_active=True
            )
            
            session.add(entity)
            await session.commit()
            await session.refresh(entity)
            
            logger.info(f"Added entity: {entity_id} ({entity.entity_type})")
            
            return {
                'entity_id': entity_id,
                'name': entity.name,
                'entity_type': entity.entity_type.value,
                'attributes': entity.attributes,
                'relationships': entity.relationships,
                'created_at': entity.created_at,
                'updated_at': entity.updated_at,
                'metadata': entity.metadata
            }
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to add entity: {e}")
            raise
    
    async def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get an entity by ID from database"""
        session = await self.get_session()
        try:
            result = await session.execute(
                select(WorldEntity).where(WorldEntity.entity_id == entity_id)
            )
            entity = result.scalar_one_or_none()
            
            if entity:
                return {
                    'entity_id': entity.entity_id,
                    'name': entity.name,
                    'entity_type': entity.entity_type.value,
                    'attributes': entity.attributes or {},
                    'relationships': entity.relationships or {},
                    'created_at': entity.created_at,
                    'updated_at': entity.updated_at,
                    'metadata': entity.metadata or {}
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get entity {entity_id}: {e}")
            return None
    
    async def merge_entities(
        self,
        source_id: str,
        target_id: str,
        strategy: str = "combine"
    ) -> Dict[str, Any]:
        """
        Merge two entities using the specified strategy with database persistence
        """
        session = await self.get_session()
        try:
            # Get source and target entities
            source_result = await session.execute(
                select(WorldEntity).where(WorldEntity.entity_id == source_id)
            )
            source = source_result.scalar_one_or_none()
            
            target_result = await session.execute(
                select(WorldEntity).where(WorldEntity.entity_id == target_id)
            )
            target = target_result.scalar_one_or_none()
            
            if not source:
                raise ValueError(f"Source entity {source_id} not found")
            if not target:
                raise ValueError(f"Target entity {target_id} not found")
            
            strategy_enum = MergeStrategy(strategy)
            conflicts_resolved = []
            merged_attributes = {}
            merged_relationships = {}
            
            # Merge attributes based on strategy
            all_keys = set(source.attributes.keys()) | set(target.attributes.keys())
            for key in all_keys:
                source_val = source.attributes.get(key)
                target_val = target.attributes.get(key)
                
                if key not in target.attributes:
                    merged_attributes[key] = source_val
                    conflicts_resolved.append(f"Added attribute: {key}")
                elif key not in source.attributes:
                    merged_attributes[key] = target_val
                else:
                    if strategy_enum == MergeStrategy.PREFER_SOURCE:
                        merged_attributes[key] = source_val
                        conflicts_resolved.append(f"Conflict resolved: {key} -> source value")
                    elif strategy_enum == MergeStrategy.PREFER_TARGET:
                        merged_attributes[key] = target_val
                        conflicts_resolved.append(f"Conflict resolved: {key} -> target value")
                    else:  # COMBINE
                        merged_attributes[key] = [target_val, source_val]
                        conflicts_resolved.append(f"Conflict resolved: {key} -> combined")
            
            # Merge relationships
            all_rel_types = set(source.relationships.keys()) | set(target.relationships.keys())
            for rel_type in all_rel_types:
                source_targets = set(source.relationships.get(rel_type, []))
                target_targets = set(target.relationships.get(rel_type, []))
                merged_targets = list(source_targets | target_targets)
                merged_relationships[rel_type] = merged_targets
            
            # Update target entity
            target.attributes = merged_attributes
            target.relationships = merged_relationships
            target.updated_at = datetime.now(timezone.utc)
            
            # Mark source as inactive instead of deleting (for history)
            source.is_active = False
            source.updated_at = datetime.now(timezone.utc)
            
            # Create merge record
            merge_record = EntityMerge(
                id=str(uuid.uuid4()),
                source_id=source_id,
                target_id=target_id,
                strategy_used=strategy_enum,
                attributes_merged=merged_attributes,
                relationships_merged=merged_relationships,
                conflicts_resolved=conflicts_resolved,
                timestamp=datetime.now(timezone.utc),
                success=True
            )
            
            session.add(merge_record)
            await session.commit()
            await session.refresh(target)
            await session.refresh(merge_record)
            
            logger.info(f"Merged {source_id} into {target_id} using {strategy}")
            
            return {
                'success': True,
                'merged_entity_id': target_id,
                'source_entity_id': source_id,
                'target_entity_id': target_id,
                'strategy_used': strategy,
                'attributes_merged': merged_attributes,
                'relationships_merged': merged_relationships,
                'conflicts_resolved': conflicts_resolved,
                'timestamp': merge_record.timestamp.isoformat()
            }
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to merge entities: {e}")
            raise
    
    async def get_merge_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get the history of merge operations from database"""
        session = await self.get_session()
        try:
            result = await session.execute(
                select(EntityMerge)
                .order_by(EntityMerge.timestamp.desc())
                .limit(limit)
            )
            merges = result.scalars().all()
            
            return [
                {
                    'success': merge.success,
                    'merged_entity_id': merge.target_id,
                    'source_entity_id': merge.source_id,
                    'target_entity_id': merge.target_id,
                    'strategy_used': merge.strategy_used.value,
                    'attributes_merged': merge.attributes_merged or {},
                    'relationships_merged': merge.relationships_merged or {},
                    'conflicts_resolved': merge.conflicts_resolved or [],
                    'timestamp': merge.timestamp.isoformat()
                }
                for merge in merges
            ]
        except Exception as e:
            logger.error(f"Failed to get merge history: {e}")
            return []
    
    async def list_entities(self, entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all entities from database, optionally filtered by type"""
        session = await self.get_session()
        try:
            if entity_type:
                result = await session.execute(
                    select(WorldEntity)
                    .where(WorldEntity.entity_type == entity_type)
                    .where(WorldEntity.is_active == True)
                )
            else:
                result = await session.execute(
                    select(WorldEntity)
                    .where(WorldEntity.is_active == True)
                )
            
            entities = result.scalars().all()
            
            return [
                {
                    'entity_id': entity.entity_id,
                    'name': entity.name,
                    'entity_type': entity.entity_type.value,
                    'attributes': entity.attributes or {},
                    'relationships': entity.relationships or {},
                    'created_at': entity.created_at,
                    'updated_at': entity.updated_at,
                    'metadata': entity.metadata or {}
                }
                for entity in entities
            ]
        except Exception as e:
            logger.error(f"Failed to list entities: {e}")
            return []
    
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


# Create a singleton instance for backward compatibility
world_model_merger = WorldModelMerger()