"""
NFM-X Memory Models
SQLAlchemy models for all memory types and versions
"""

from sqlalchemy import Column, String, Text, Float, Integer, Boolean, DateTime, JSON
from sqlalchemy import ForeignKey, Enum, Index
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum as PyEnum
import uuid

Base = declarative_base()


# Enums for memory types and statuses
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
    SOURCE = "source"
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
    DISCOVER = "discover"
    RESTORE = "restore"


class MemoryPermission(PyEnum):
    PRIVATE = "private"
    PROJECT = "project"
    TEAM = "team"
    AGENT = "agent"
    SYSTEM = "system"
    SHARED = "shared"


class AccessPermission(PyEnum):
    READ = "read"
    WRITE = "write"
    EVOLVE = "evolve"
    CONFIRM = "confirm"
    EXPORT = "export"
    ADMIN = "admin"


# Main Memory Model
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
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    observed_at = Column(DateTime, nullable=True)
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    parent_id = Column(String(36), nullable=True, index=True)
    integrity_hash = Column(String(64), nullable=True)
    parent = relationship("Memory", remote_side=[id], backref="children")
    versions = relationship("MemoryVersion", backref="memory", cascade="all, delete-orphan")
    evidence = relationship("MemoryEvidence", backref="memory")
    relationships = relationship("MemoryRelationship", foreign_keys="MemoryRelationship.memory_id", backref="source_memory")
    related_memories = relationship("MemoryRelationship", foreign_keys="MemoryRelationship.related_id", backref="target_memory")
    sources = relationship("MemorySource", backref="memory")
    metadata = Column(JSON, nullable=True, default={})
    __table_args__ = (
        Index('idx_memory_type_status', 'type', 'status'),
        Index('idx_memory_agent', 'agent_id'),
        Index('idx_memory_root', 'root_id'),
        Index('idx_memory_content_hash', 'content_hash'),
    )
    
    def __repr__(self):
        return f"<Memory(id={self.id}, type={self.type}, version={self.version}, confidence={self.confidence})>"


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
    metadata = Column(JSON, nullable=True, default={})
    change_type = Column(Enum(ChangeType), nullable=False)
    change_reason = Column(Text, nullable=True)
    change_evidence = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    actor_id = Column(String(36), nullable=True)
    actor_type = Column(String(20), nullable=True)
    previous_version_hash = Column(String(64), nullable=True)
    current_hash = Column(String(64), nullable=True)
    __table_args__ = (Index('idx_version_memory', 'memory_id', 'version'),)


class MemoryEvent(Base):
    __tablename__ = "memory_events"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = Column(String(36), nullable=True, index=True)
    version_id = Column(String(36), nullable=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    agent_id = Column(String(36), nullable=True)
    actor_type = Column(String(20), nullable=True)
    metadata = Column(JSON, nullable=True, default={})
    __table_args__ = (
        Index('idx_event_memory', 'memory_id'),
        Index('idx_event_type', 'event_type'),
        Index('idx_event_timestamp', 'timestamp'),
    )


class MemoryEvidence(Base):
    __tablename__ = "memory_evidence"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = Column(String(36), ForeignKey('memories.id'), nullable=False, index=True)
    content = Column(Text, nullable=False)
    content_type = Column(String(50), nullable=True)
    source_id = Column(String(36), nullable=True)
    source_type = Column(String(50), nullable=True)
    quality_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    metadata = Column(JSON, nullable=True, default={})


class MemorySource(Base):
    __tablename__ = "memory_sources"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = Column(String(36), ForeignKey('memories.id'), nullable=True, index=True)
    source_type = Column(String(50), nullable=False)
    source_id = Column(String(100), nullable=True)
    source_name = Column(String(200), nullable=True)
    url = Column(String(500), nullable=True)
    file_path = Column(String(500), nullable=True)
    reliability = Column(Float, nullable=True, default=0.8)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    accessed_at = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True, default={})


class MemoryRelationship(Base):
    __tablename__ = "memory_relationships"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = Column(String(36), ForeignKey('memories.id'), nullable=False, index=True)
    related_id = Column(String(36), ForeignKey('memories.id'), nullable=False, index=True)
    relationship_type = Column(String(50), nullable=False, index=True)
    confidence = Column(Float, nullable=True, default=0.7)
    weight = Column(Float, nullable=True, default=1.0)
    is_directed = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    evidence_id = Column(String(36), nullable=True)
    metadata = Column(JSON, nullable=True, default={})
    __table_args__ = (
        Index('idx_relationship_memory', 'memory_id'),
        Index('idx_relationship_related', 'related_id'),
        Index('idx_relationship_type', 'relationship_type'),
    )


class MemoryEntity(Base):
    __tablename__ = "memory_entities"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type = Column(String(50), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    normalized_name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    properties = Column(JSON, nullable=True, default={})
    first_seen = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_seen = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True, default={})
    __table_args__ = (Index('idx_entity_type_name', 'entity_type', 'name'),)


class MemoryConflict(Base):
    __tablename__ = "memory_conflicts"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_a_id = Column(String(36), ForeignKey('memories.id'), nullable=False, index=True)
    memory_b_id = Column(String(36), ForeignKey('memories.id'), nullable=False, index=True)
    conflict_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(Float, nullable=True, default=0.5)
    status = Column(String(20), nullable=False, default="unresolved")
    resolution = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(36), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    metadata = Column(JSON, nullable=True, default={})
    __table_args__ = (
        Index('idx_conflict_memories', 'memory_a_id', 'memory_b_id'),
        Index('idx_conflict_status', 'status'),
    )


class MemoryHypothesis(Base):
    __tablename__ = "memory_hypotheses"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = Column(String(36), ForeignKey('memories.id'), nullable=True, index=True)
    statement = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="unverified")
    confidence = Column(Float, nullable=True, default=0.3)
    supporting_evidence = Column(JSON, nullable=True, default=[])
    contradicting_evidence = Column(JSON, nullable=True, default=[])
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True, default={})


class MemoryPattern(Base):
    __tablename__ = "memory_patterns"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pattern_type = Column(String(50), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    supporting_memories = Column(JSON, nullable=True, default=[])
    pattern_data = Column(JSON, nullable=True, default={})
    confidence = Column(Float, nullable=True, default=0.7)
    strength = Column(Float, nullable=True, default=0.5)
    discovered_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_updated = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True, default={})


class MemoryProcedure(Base):
    __tablename__ = "memory_procedures"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = Column(String(36), ForeignKey('memories.id'), nullable=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    steps = Column(JSON, nullable=True, default=[])
    execution_count = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    failure_count = Column(Integer, nullable=False, default=0)
    success_rate = Column(Float, nullable=True, default=0.0)
    confidence = Column(Float, nullable=True, default=0.7)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_executed = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True, default={})


class MemoryPreference(Base):
    __tablename__ = "memory_preferences"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = Column(String(36), ForeignKey('memories.id'), nullable=True, index=True)
    preference_type = Column(String(50), nullable=False, index=True)
    key = Column(String(200), nullable=False)
    value = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True, default=0.7)
    importance = Column(Float, nullable=True, default=0.5)
    status = Column(String(20), nullable=False, default="active")
    first_observed = Column(DateTime, nullable=True)
    last_confirmed = Column(DateTime, nullable=True)
    evolution_history = Column(JSON, nullable=True, default=[])
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    metadata = Column(JSON, nullable=True, default={})
    __table_args__ = (Index('idx_preference_type_key', 'preference_type', 'key'),)


class MemoryEmbedding(Base):
    __tablename__ = "memory_embeddings"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = Column(String(36), ForeignKey('memories.id'), nullable=False, index=True, unique=True)
    vector = Column(JSON, nullable=False)
    model = Column(String(100), nullable=True)
    dimension = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    __table_args__ = (Index('idx_embedding_memory', 'memory_id'),)


class MemoryUsage(Base):
    __tablename__ = "memory_usage"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = Column(String(36), ForeignKey('memories.id'), nullable=False, index=True)
    usage_type = Column(String(50), nullable=False, index=True)
    agent_id = Column(String(36), nullable=True)
    query = Column(Text, nullable=True)
    success = Column(Boolean, nullable=True)
    score = Column(Float, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    metadata = Column(JSON, nullable=True, default={})
    __table_args__ = (
        Index('idx_usage_memory', 'memory_id'),
        Index('idx_usage_type', 'usage_type'),
        Index('idx_usage_timestamp', 'timestamp'),
    )


class MemoryCheckpoint(Base):
    __tablename__ = "memory_checkpoints"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    checkpoint_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    memory_count = Column(Integer, nullable=False)
    version_count = Column(Integer, nullable=False)
    state_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    metadata = Column(JSON, nullable=True, default={})


class MemorySnapshot(Base):
    __tablename__ = "memory_snapshots"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    metadata = Column(JSON, nullable=True, default={})


class Agent(Base):
    __tablename__ = "agents"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    agent_type = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    configuration = Column(JSON, nullable=True, default={})
    memory_policy = Column(JSON, nullable=True, default={})
    permissions = Column(JSON, nullable=True, default=[])
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_active = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True, default={})


class AgentMemoryPolicy(Base):
    __tablename__ = "agent_memory_policies"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey('agents.id'), nullable=False, index=True)
    policy_type = Column(String(50), nullable=False, index=True)
    rules = Column(JSON, nullable=True, default=[])
    priority = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True, default={})


async def create_all_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)