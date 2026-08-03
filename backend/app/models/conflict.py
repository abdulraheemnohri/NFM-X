"""
NFM-X Conflict Database Models
SQLAlchemy models for conflict resolution.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Float, JSON
from sqlalchemy.sql import func
from backend.app.database import Base


class Conflict(Base):
    __tablename__ = "conflicts"
    
    id = Column(Integer, primary_key=True, index=True)
    memory_id = Column(String, index=True)
    local_content = Column(Text)
    remote_content = Column(Text)
    local_metadata = Column(JSON, default={})
    remote_metadata = Column(JSON, default={})
    conflict_type = Column(String, index=True)  # content, metadata, deletion
    detected_at = Column(DateTime(timezone=True), default=func.now())
    status = Column(String, default="pending")  # pending, resolved, dismissed
    resolution = Column(String)  # keep_both, keep_local, keep_remote, merge, latest
    resolved_at = Column(DateTime(timezone=True))
    resolved_by = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
