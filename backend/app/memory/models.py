# NFM-X Memory Models
SQLAlchemy models for memory storage and management

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Enum, func
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum
import uuid

from ..storage.database import Base


# ENUMS

class MemoryStatus(str, PyEnum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"
    MERGED = "MERGED"


class MemoryType(str, PyEnum):
    TEXT = "TEXT"
    CONVERSATION = "CONVERSATION"
    DOCUMENT = "DOCUMENT"
    CODE = "CODE"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"
    STRUCTURED = "STRUCTURED"


class MemoryPriority(str, PyEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EventType(str, PyEnum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    VERSIONED = "VERSIONED"
    DELETED = "DELETED"
    RESTORED = "RESTORED"
    MERGED = "MERGED"
    TAGGED = "TAGGED"
    CLASSIFIED = "CLASSIFIED"
    LINKED = "LINKED"
    UNLINKED = "UNLINKED"


class RelationshipType(str, PyEnum):
    REFERENCES = "REFERENCES"
    DEPENDS_ON = "DEPENDS_ON"
    SIMILAR_TO = "SIMILAR_TO"
    PART_OF = "PART_OF"
    SUPERSEDES = "SUPERSEDES"
    CONTRADICTS = "CONTRADICTS"
    EXTENDS = "EXTENDS"
    RELATED_TO = "RELATED_TO"


class ConflictResolution(str, PyEnum):
    MANUAL = "MANUAL"
    AUTO_MERGE = "AUTO_MERGE"
    AUTO_KEEP_BOTH = "AUTO_KEEP_BOTH"
    IGNORED = "IGNORED"


# MEMORY MODEL

class Memory(Base):
    __tablename__ = "memories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), index=True)
    title = Column(String(500), index=True)
    description = Column(String(2000))
    memory_type = Column(Enum(MemoryType), default=MemoryType.TEXT, index=True)
    status = Column(Enum(MemoryStatus), default=MemoryStatus.ACTIVE, index=True)
    version = Column(Integer, default=1)
    parent_id = Column(String(36), nullable=True, index=True)
    source = Column(String(1000))
    source_id = Column(String(36))
    author = Column(String(255))
    tags = Column(JSON, default=[])
    categories = Column(JSON, default=[])
    priority = Column(Enum(MemoryPriority), default=MemoryPriority.MEDIUM)
    embedding = Column(JSON, nullable=True)
    embedding_model = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    archived_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    access_count = Column(Integer, default=0)
    relevance_score = Column(Float, default=0.0)
    metadata = Column(JSON, default={})
    
    parent = relationship("Memory", remote_side=[parent_id], back_populates="children")
    children = relationship("Memory", remote_side=[id], back_populates="parent")
    events = relationship("MemoryEvent", back_populates="memory", cascade="all, delete-orphan")
    relationships_from = relationship("MemoryRelationship", foreign_keys="MemoryRelationship.from_id", back_populates="from_memory")
    relationships_to = relationship("MemoryRelationship", foreign_keys="MemoryRelationship.to_id", back_populates="to_memory")
    conflicts_as_a = relationship("MemoryConflict", foreign_keys="MemoryConflict.memory_a_id", back_populates="memory_a")
    conflicts_as_b = relationship("MemoryConflict", foreign_keys="MemoryConflict.memory_b_id", back_populates="memory_b")


# MEMORY EVENT MODEL

class MemoryEvent(Base):
    __tablename__ = "memory_events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = Column(String(36), index=True, nullable=False)
    event_type = Column(Enum(EventType), index=True)
    details = Column(JSON, default={})
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    memory = relationship("Memory", back_populates="events")


# MEMORY RELATIONSHIP MODEL

class MemoryRelationship(Base):
    __tablename__ = "memory_relationships"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    from_id = Column(String(36), index=True, nullable=False)
    to_id = Column(String(36), index=True, nullable=False)
    relationship_type = Column(Enum(RelationshipType), index=True)
    strength = Column(Float, default=1.0)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    from_memory = relationship("Memory", foreign_keys=[from_id], back_populates="relationships_from")
    to_memory = relationship("Memory", foreign_keys=[to_id], back_populates="relationships_to")
    
    __table_args__ = (
        {"unique_constraints": [("from_id", "to_id", "relationship_type")]},
    )


# MEMORY CONFLICT MODEL

class MemoryConflict(Base):
    __tablename__ = "memory_conflicts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_a_id = Column(String(36), index=True, nullable=False)
    memory_b_id = Column(String(36), index=True, nullable=False)
    conflict_type = Column(String(100), index=True)
    description = Column(Text)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution = Column(Enum(ConflictResolution), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    metadata = Column(JSON, default={})
    
    memory_a = relationship("Memory", foreign_keys=[memory_a_id], back_populates="conflicts_as_a")
    memory_b = relationship("Memory", foreign_keys=[memory_b_id], back_populates="conflicts_as_b")
    
    __table_args__ = (
        {"unique_constraints": [("memory_a_id", "memory_b_id")]},
    )


# SYSTEM STATISTICS MODEL

class SystemStat(Base):
    __tablename__ = "system_stats"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stat_name = Column(String(100), index=True, unique=True)
    stat_value = Column(JSON)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())