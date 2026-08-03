"""
NFM-X MCP Database Models
SQLAlchemy models for MCP authentication.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from backend.app.database import Base


class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    hashed_secret = Column(String)
    permissions = Column(String, default="read,write")  # Comma-separated
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    last_used_at = Column(DateTime(timezone=True))
    usage_count = Column(Integer, default=0)
    rate_limit = Column(Integer, default=100)
