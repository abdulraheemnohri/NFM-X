from sqlalchemy import Column, String, Text, Float, Integer, DateTime, JSON, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
from enum import Enum as PyEnum
import uuid

Base = declarative_base()

def now_utc():
    return datetime.now(timezone.utc)

class MemoryType(PyEnum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    PREFERENCE = "preference"
    DECISION = "decision"
    FAILURE = "failure"
    SUCCESS = "success"
    TEMPORAL = "temporal"
    CAUSAL = "causal"
    HYPOTHESIS = "hypothesis"
    CONFLICT = "conflict"
    MULTIMODAL = "multimodal"

class MemoryStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    DELETED = "deleted"

class ChangeType(PyEnum):
    CREATE = "create"
    REINFORCE = "reinforce"
    REFINE = "refine"
    EXPAND = "expand"
    CORRECT = "correct"
    MERGE = "merge"
    SPLIT = "split"
    SUPERSEDE = "supersede"
    CONTRADICT = "contradict"
    RESTORE = "restore"

class Memory(Base):
    __tablename__ = "memories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    root_id = Column(String(36), nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1)
    type = Column(Enum(MemoryType), nullable=False, index=True)
    subtype = Column(String(50), nullable=True, index=True)
    content = Column(Text, nullable=False)
    normalized_content = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=True, index=True)
    agent_id = Column(String(36), nullable=True, index=True)
    source_id = Column(String(36), nullable=True, index=True)
    confidence = Column(Float, nullable=False, default=0.7)
    importance = Column(Float, nullable=False, default=0.5)
    status = Column(Enum(MemoryStatus), nullable=False, default=MemoryStatus.ACTIVE)
    created_at = Column(DateTime, nullable=False, default=now_utc)
    observed_at = Column(DateTime, nullable=True)
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    parent_id = Column(String(36), nullable=True, index=True)
    integrity_hash = Column(String(64), nullable=True)

    meta = Column("metadata", JSON, nullable=True, default=dict)

    versions = relationship("MemoryVersion", back_populates="memory", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_memory_type_status', 'type', 'status'),
        Index('idx_memory_agent', 'agent_id'),
        Index('idx_memory_root', 'root_id'),
    )

class MemoryVersion(Base):
    __tablename__ = "memory_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = Column(String(36), ForeignKey('memories.id'), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    normalized_content = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=True)
    confidence = Column(Float, nullable=False)
    importance = Column(Float, nullable=False)
    status = Column(Enum(MemoryStatus), nullable=False)
    change_type = Column(Enum(ChangeType), nullable=False)
    change_reason = Column(Text, nullable=True)

    meta = Column("metadata", JSON, nullable=True, default=dict)

    created_at = Column(DateTime, nullable=False, default=now_utc)
    actor_id = Column(String(36), nullable=True)
    actor_type = Column(String(20), nullable=True)

    memory = relationship("Memory", back_populates="versions")

    __table_args__ = (Index('idx_version_memory', 'memory_id', 'version'),)

class MemoryEvent(Base):
    __tablename__ = "memory_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = Column(String(36), nullable=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=now_utc)
    agent_id = Column(String(36), nullable=True)

    __table_args__ = (
        Index('idx_event_memory', 'memory_id'),
        Index('idx_event_type', 'event_type'),
        Index('idx_event_timestamp', 'timestamp'),
    )

class MemoryRelationship(Base):
    __tablename__ = "memory_relationships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = Column(String(36), ForeignKey('memories.id'), nullable=False, index=True)
    related_id = Column(String(36), ForeignKey('memories.id'), nullable=False, index=True)
    relationship_type = Column(String(50), nullable=False, index=True)
    confidence = Column(Float, nullable=True, default=0.7)

    meta = Column("metadata", JSON, nullable=True, default=dict)

    created_at = Column(DateTime, nullable=False, default=now_utc)

    __table_args__ = (
        Index('idx_rel_memory', 'memory_id'),
        Index('idx_rel_related', 'related_id'),
        Index('idx_rel_type', 'relationship_type'),
    )

class MemoryEmbedding(Base):
    __tablename__ = "memory_embeddings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = Column(String(36), ForeignKey('memories.id'), nullable=False, index=True, unique=True)
    vector = Column(JSON, nullable=False)  # Stored as list of floats
    model = Column(String(100), nullable=True)
    dimension = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=now_utc)

# Assign properties after class declarations to bypass SQLAlchemy reserved word checks
# while preserving property-like access for .metadata across all code.
Memory.metadata = property(lambda self: self.meta, lambda self, val: setattr(self, 'meta', val))
MemoryVersion.metadata = property(lambda self: self.meta, lambda self, val: setattr(self, 'meta', val))
MemoryRelationship.metadata = property(lambda self: self.meta, lambda self, val: setattr(self, 'meta', val))
