"""
NFM-X Memory Models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Enum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
import uuid
from ..storage.database import Base
from enum import Enum as PyEnum

class MemoryStatus(PyEnum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"
    MERGED = "MERGED"

class MemoryType(PyEnum):
    TEXT = "TEXT"
    CONVERSATION = "CONVERSATION"
    DOCUMENT = "DOCUMENT"
    CODE = "CODE"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"
    STRUCTURED = "STRUCTURED"

class MemoryPriority(PyEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

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