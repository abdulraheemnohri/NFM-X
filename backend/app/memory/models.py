"""
SQLAlchemy models for NFM-X memory layer
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON, Index, Enum, func
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from enum import Enum as PyEnum
from ..storage.database import Base

class MemoryType(str, PyEnum):
    FACT = "fact"; CONCEPT = "concept"; PROCEDURE = "procedure"; EXPERIENCE = "experience"; CAUSAL = "causal"; DECISION = "decision"; OBSERVATION = "observation"; HYPOTHESIS = "hypothesis"; GOAL = "goal"; PLAN = "plan"

class MemoryStatus(str, PyEnum):
    ACTIVE = "active"; ARCHIVED = "archived"; DELETED = "deleted"; WORKING = "working"

class EventType(str, PyEnum):
    CREATED = "created"; VERSIONED = "versioned"; DELETED = "deleted"; ARCHIVED = "archived"; TAGGED = "tagged"; RELATED = "related"; CONFLICT = "conflict"; CONSOLIDATED = "consolidated"

class RelationshipType(str, PyEnum):
    RELATED = "related"; SUBSUMES = "subsumes"; CONTRADICTS = "contradicts"; SUPPORTS = "supports"; EXTENDS = "extends"; CAUSES = "causes"; DEPENDS_ON = "depends_on"

class ChangeType(str, PyEnum):
    CORRECT = "correct"; REFINES = "refine"; EXPAND = "expand"; SUPERSEDE = "supersede"; CLARIFY = "clarify"; SIMPLIFY = "simplify"

class Memory(Base):
    __tablename__ = "memories"
    id: str = Column(String(36), primary_key=True, index=True)
    content: str = Column(Text, nullable=False)
    content_hash: str = Column(String(64), nullable=False, index=True)
    memory_type: MemoryType = Column(Enum(MemoryType), nullable=False, default=MemoryType.FACT)
    confidence: Float = Column(Float, nullable=False, default=0.8)
    importance: Float = Column(Float, nullable=False, default=0.5)
    status: MemoryStatus = Column(Enum(MemoryStatus), nullable=False, default=MemoryStatus.ACTIVE, index=True)
    source: str = Column(String(500), nullable=True)
    source_type: str = Column(String(50), nullable=True)
    author_id: str = Column(String(100), nullable=True, index=True)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    metadata: Dict[str, Any] = Column(JSON, nullable=False, default=dict)
    tags: List[str] = Column(JSON, nullable=False, default=list)

class MemoryVersion(Base):
    __tablename__ = "memory_versions"
    id: str = Column(String(36), primary_key=True, index=True)
    memory_id: str = Column(String(36), ForeignKey("memories.id", ondelete="CASCADE"), nullable=False, index=True)
    content: str = Column(Text, nullable=False)
    content_hash: str = Column(String(64), nullable=False)
    version_number: int = Column(Integer, nullable=False)
    change_type: ChangeType = Column(Enum(ChangeType), nullable=False)
    change_reason: str = Column(Text, nullable=True)
    confidence: Float = Column(Float, nullable=False)
    importance: Float = Column(Float, nullable=False)
    status: MemoryStatus = Column(Enum(MemoryStatus), nullable=False, default=MemoryStatus.ACTIVE)
    actor_id: str = Column(String(100), nullable=True)
    actor_type: str = Column(String(50), nullable=True)
    parent_version_id: Optional[str] = Column(String(36), nullable=True)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

class MemoryEvent(Base):
    __tablename__ = "memory_events"
    id: str = Column(String(36), primary_key=True, index=True)
    memory_id: str = Column(String(36), ForeignKey("memories.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id: Optional[str] = Column(String(36), ForeignKey("memory_versions.id", ondelete="SET NULL"), nullable=True)
    event_type: EventType = Column(Enum(EventType), nullable=False, index=True)
    description: str = Column(Text, nullable=True)
    actor_id: str = Column(String(100), nullable=True)
    actor_type: str = Column(String(50), nullable=True)
    metadata: Dict[str, Any] = Column(JSON, nullable=False, default=dict)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

class MemoryRelationship(Base):
    __tablename__ = "memory_relationships"
    id: str = Column(String(36), primary_key=True, index=True)
    source_id: str = Column(String(36), ForeignKey("memories.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id: str = Column(String(36), ForeignKey("memories.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship_type: RelationshipType = Column(Enum(RelationshipType), nullable=False, index=True)
    confidence: Float = Column(Float, nullable=False, default=1.0)
    description: str = Column(Text, nullable=True)
    metadata: Dict[str, Any] = Column(JSON, nullable=False, default=dict)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

class MemoryEmbedding(Base):
    __tablename__ = "memory_embeddings"
    id: str = Column(String(36), primary_key=True, index=True)
    memory_id: str = Column(String(36), ForeignKey("memories.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id: Optional[str] = Column(String(36), ForeignKey("memory_versions.id", ondelete="SET NULL"), nullable=True)
    embedding: List[Float] = Column(JSON, nullable=False)
    model_name: str = Column(String(100), nullable=False)
    dimension: int = Column(Integer, nullable=False)
    metadata: Dict[str, Any] = Column(JSON, nullable=False, default=dict)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)