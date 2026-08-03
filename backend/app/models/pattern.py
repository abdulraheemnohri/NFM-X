"""
NFM-X Pattern Database Models
SQLAlchemy models for pattern search.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from backend.app.database import Base


class SearchPattern(Base):
    __tablename__ = "search_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    key_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    pattern = Column(Text)
    description = Column(Text)
    case_sensitive = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)
    tags = Column(String, default="")  # Comma-separated
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_used_at = Column(DateTime(timezone=True))
    usage_count = Column(Integer, default=0)
