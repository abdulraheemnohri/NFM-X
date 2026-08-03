"""
NFM-X World Model Database Models
SQLAlchemy models for world model entity persistence
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Enum, func, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum
import uuid

from ..storage.database import Base


# World Model Enums

class EntityType(str, PyEnum):
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    CONCEPT = "concept"
    EVENT = "event"
    OBJECT = "object"
    TIME = "time"
    OTHER = "other"


class MergeStrategy(str, PyEnum):
    COMBINE = "combine"
    PREFER_SOURCE = "prefer_source"
    PREFER_TARGET = "prefer_target"


class RelationshipDirection(str, PyEnum):
    UNIDIRECTIONAL = "unidirectional"
    BIDIRECTIONAL = "bidirectional"


# World Model Models

class WorldEntity(Base):
    __tablename__ = "world_entities"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id = Column(String(36), unique=True, index=True)  # External ID for API compatibility
    name = Column(String(500), index=True)
    entity_type = Column(Enum(EntityType), index=True)
    attributes = Column(JSON, default={})
    relationships = Column(JSON, default={})  # {relation_type: [target_ids]}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))
    metadata = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    
    # Relationships
    merge_history_as_source = relationship("EntityMerge", foreign_keys="EntityMerge.source_id", back_populates="source_entity")
    merge_history_as_target = relationship("EntityMerge", foreign_keys="EntityMerge.target_id", back_populates="target_entity")


class EntityMerge(Base):
    __tablename__ = "entity_merges"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String(36), ForeignKey("world_entities.entity_id"), index=True, nullable=False)
    target_id = Column(String(36), ForeignKey("world_entities.entity_id"), index=True, nullable=False)
    strategy_used = Column(Enum(MergeStrategy), index=True)
    attributes_merged = Column(JSON, default={})
    relationships_merged = Column(JSON, default={})
    conflicts_resolved = Column(JSON, default=[])
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    success = Column(Boolean, default=True)
    
    source_entity = relationship("WorldEntity", foreign_keys=[source_id], back_populates="merge_history_as_source")
    target_entity = relationship("WorldEntity", foreign_keys=[target_id], back_populates="merge_history_as_target")
    
    __table_args__ = (
        {"unique_constraints": [("source_id", "target_id")]},
    )


# Define python properties dynamically for metadata attributes
Memory.metadata = property(lambda self: self.meta, lambda self, value: setattr(self, 'meta', value))
WorldEntity.metadata = property(lambda self: self.meta, lambda self, value: setattr(self, 'meta', value))