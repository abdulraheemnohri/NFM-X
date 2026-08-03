"""
NFM-X Sharing Database Models
SQLAlchemy models for sharing permissions persistence
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Enum, func, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum
import uuid

from ..storage.database import Base


class SharingPermission(str, PyEnum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class SharingBundle(Base):
    __tablename__ = "sharing_bundles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bundle_id = Column(String(36), unique=True, index=True)  # External ID for API compatibility
    name = Column(String(500), index=True)
    description = Column(Text)
    owner_id = Column(String(255), index=True)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))
    metadata = Column(JSON, default={})
    
    # Relationships
    permissions = relationship("SharingPermission", back_populates="bundle", cascade="all, delete-orphan")
    memory_associations = relationship("BundleMemory", back_populates="bundle", cascade="all, delete-orphan")


class SharingPermission(Base):
    __tablename__ = "sharing_permissions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bundle_id = Column(String(36), ForeignKey("sharing_bundles.bundle_id"), index=True, nullable=False)
    user_id = Column(String(255), index=True, nullable=False)
    read = Column(Boolean, default=False)
    write = Column(Boolean, default=False)
    admin = Column(Boolean, default=False)
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    granted_by = Column(String(255))
    
    bundle = relationship("SharingBundle", back_populates="permissions")
    
    __table_args__ = (
        {"unique_constraints": [("bundle_id", "user_id")]},
    )


class BundleMemory(Base):
    __tablename__ = "bundle_memories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bundle_id = Column(String(36), ForeignKey("sharing_bundles.bundle_id", ondelete="CASCADE"), index=True, nullable=False)
    memory_id = Column(String(36), index=True, nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    added_by = Column(String(255))
    
    bundle = relationship("SharingBundle", back_populates="memory_associations")
    
    __table_args__ = (
        {"unique_constraints": [("bundle_id", "memory_id")]},
    )


# Define python properties dynamically for metadata attributes
def _metadata_get(self):
    return self.metadata if hasattr(self, 'metadata') else {}

def _metadata_set(self, value):
    if hasattr(self, 'metadata'):
        self.metadata = value

SharingBundle.metadata = property(_metadata_get, _metadata_set)