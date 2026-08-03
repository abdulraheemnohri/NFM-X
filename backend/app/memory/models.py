# NFM-X Memory Models
# SQLAlchemy models for memory storage and management

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Enum, func, ForeignKey, UniqueConstraint
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
    INACTIVE = "INACTIVE"


class MemoryType(str, PyEnum):
    TEXT = "TEXT"
    CONVERSATION = "CONVERSATION"
    DOCUMENT = "DOCUMENT"
    CODE = "CODE"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"
    STRUCTURED = "STRUCTURED"
    PREFERENCE = "PREFERENCE"
    SEMANTIC = "SEMANTIC"
    CAUSAL = "CAUSAL"
    WORKING = "WORKING"


class ChangeType(str, PyEnum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    REFINE = "REFINE"
    EXPAND = "EXPAND"
    MERGE = "MERGE"
    DELETE = "DELETE"
    SYNC_UPDATE = "SYNC_UPDATE"


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
    root_id = Column(String(36), nullable=True, index=True)
    agent_id = Column(String(255), nullable=True, index=True)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), index=True)
    title = Column(String(500), index=True)
    description = Column(String(2000))
    memory_type = Column(Enum(MemoryType), default=MemoryType.TEXT, index=True)
    status = Column(Enum(MemoryStatus), default=MemoryStatus.ACTIVE, index=True)
    version = Column(Integer, default=1)
    parent_id = Column(String(36), ForeignKey("memories.id"), nullable=True, index=True)
    source = Column(String(1000))
    source_id = Column(String(36))
    author = Column(String(255))
    tags = Column(JSON, default=[])
    categories = Column(JSON, default=[])
    priority = Column(Enum(MemoryPriority), default=MemoryPriority.MEDIUM)
    embedding = Column(JSON, nullable=True)
    embedding_model = Column(String(100))
    confidence = Column(Float, default=0.7)
    importance = Column(Float, default=0.5)
    normalized_content = Column(Text, nullable=True)
    observed_at = Column(DateTime(timezone=True), nullable=True)
    valid_from = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))
    archived_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    access_count = Column(Integer, default=0)
    relevance_score = Column(Float, default=0.0)
    meta = Column("metadata", JSON, default={})
    
    parent = relationship("Memory", remote_side=[parent_id], back_populates="children")
    children = relationship("Memory", remote_side=[id], back_populates="parent")
    events = relationship("MemoryEvent", back_populates="memory", cascade="all, delete-orphan")
    versions = relationship("MemoryVersion", back_populates="memory_obj", cascade="all, delete-orphan")
    relationships_from = relationship("MemoryRelationship", foreign_keys="MemoryRelationship.from_id", back_populates="from_memory")
    relationships_to = relationship("MemoryRelationship", foreign_keys="MemoryRelationship.to_id", back_populates="to_memory")
    conflicts_as_a = relationship("MemoryConflict", foreign_keys="MemoryConflict.memory_a_id", back_populates="memory_a")
    conflicts_as_b = relationship("MemoryConflict", foreign_keys="MemoryConflict.memory_b_id", back_populates="memory_b")

    @property
    def type(self):
        return self.memory_type

    @type.setter
    def type(self, value):
        self.memory_type = value


class MemoryVersion(Base):
    __tablename__ = "memory_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = Column(String(36), ForeignKey("memories.id", ondelete="CASCADE"), index=True, nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    normalized_content = Column(Text)
    content_hash = Column(String(64))
    confidence = Column(Float, default=1.0)
    importance = Column(Float, default=0.5)
    status = Column(Enum(MemoryStatus), default=MemoryStatus.ACTIVE)
    change_type = Column(Enum(ChangeType), default=ChangeType.REFINE)
    change_reason = Column(String(1000))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    actor_id = Column(String(255), default="system")
    actor_type = Column(String(100), default="agent")

    memory_obj = relationship("Memory", back_populates="versions")


# MEMORY EVENT MODEL

class MemoryEvent(Base):
    __tablename__ = "memory_events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = Column(String(36), ForeignKey("memories.id", ondelete="CASCADE"), index=True, nullable=False)
    event_type = Column(Enum(EventType), index=True)
    details = Column(JSON, default={})
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    memory = relationship("Memory", back_populates="events")


# MEMORY RELATIONSHIP MODEL

class MemoryRelationship(Base):
    __tablename__ = "memory_relationships"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    from_id = Column(String(36), ForeignKey("memories.id", ondelete="CASCADE"), index=True, nullable=False)
    to_id = Column(String(36), ForeignKey("memories.id", ondelete="CASCADE"), index=True, nullable=False)
    relationship_type = Column(Enum(RelationshipType), index=True)
    strength = Column(Float, default=1.0)
    meta = Column("metadata", JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    from_memory = relationship("Memory", foreign_keys=[from_id], back_populates="relationships_from")
    to_memory = relationship("Memory", foreign_keys=[to_id], back_populates="relationships_to")
    

    agent_id = Column(String, index=True, default=None)
    importance = Column(Float, default=0.5)
    confidence = Column(Float, default=1.0)
    root_id = Column(String, index=True, default=None)
    normalized_content = Column(Text, default=None)
    observed_at = Column(DateTime(timezone=True), default=None)
    valid_from = Column(DateTime(timezone=True), default=None)
    __table_args__ = (
        UniqueConstraint("from_id", "to_id", name="uq_from_to_rel_type"),
    )


# MEMORY CONFLICT MODEL

class MemoryConflict(Base):
    __tablename__ = "memory_conflicts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_a_id = Column(String(36), ForeignKey("memories.id", ondelete="CASCADE"), index=True, nullable=False)
    memory_b_id = Column(String(36), ForeignKey("memories.id", ondelete="CASCADE"), index=True, nullable=False)
    conflict_type = Column(String(100), index=True)
    description = Column(Text)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution = Column(Enum(ConflictResolution), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    meta = Column("metadata", JSON, default={})
    
    memory_a = relationship("Memory", foreign_keys=[memory_a_id], back_populates="conflicts_as_a")
    memory_b = relationship("Memory", foreign_keys=[memory_b_id], back_populates="conflicts_as_b")
    
    __table_args__ = (
        UniqueConstraint("memory_a_id", "memory_b_id", name="uq_memory_a_b"),
    )


# SYSTEM STATISTICS MODEL

class SystemStat(Base):
    __tablename__ = "system_stats"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stat_name = Column(String(100), index=True, unique=True)
    stat_value = Column(JSON)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# Define python properties dynamically for metadata attributes to bypass SQLAlchemy 2.0 limitation
def _metadata_get(self):
    return self.meta

def _metadata_set(self, value):
    self.meta = value

Memory.metadata = property(_metadata_get, _metadata_set)
MemoryRelationship.metadata = property(_metadata_get, _metadata_set)
MemoryConflict.metadata = property(_metadata_get, _metadata_set)


class MemoryProcedure(Base):
    __tablename__ = "memory_procedures"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), index=True)
    description = Column(Text)
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    last_executed = Column(DateTime(timezone=True))
    meta = Column("metadata", JSON, default={})


MemoryProcedure.metadata = property(_metadata_get, _metadata_set)


class MemorySkill(Base):
    __tablename__ = "memory_skills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), index=True)
    description = Column(Text)
    source_procedure_ids = Column(JSON, default=[])
    success_rate = Column(Float, default=0.0)
    execution_count = Column(Integer, default=0)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MemoryCheckpoint(Base):
    __tablename__ = "memory_checkpoints"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    checkpoint_type = Column(String(100), default="full")
    merkle_root = Column(String(255))
    memory_count = Column(Integer, default=0)
    signature = Column(Text)
    public_key = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MemoryPattern(Base):
    __tablename__ = "memory_patterns"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pattern_type = Column(String(100), default="semantic_cluster")
    name = Column(String(500))
    description = Column(Text)
    supporting_memories = Column(JSON, default=[])
    pattern_data = Column(JSON, default={})
    confidence = Column(Float, default=0.7)
    strength = Column(Float, default=0.5)
    discovered_at = Column(DateTime(timezone=True), server_default=func.now())