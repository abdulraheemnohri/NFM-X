"""
NFM-X Memory Database Models
Core memory storage models.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.sql import func
from backend.app.database import Base


class Memory(Base):
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    subtype = Column(String, index=True, default="text")  # text, table, key_value, entity, etc.
    metadata = Column(JSON, default={})
    confidence = Column(Float, default=1.0)
    compressed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes for faster queries
    __table_args__ = (
        ("idx_memories_subtype", "subtype"),
        ("idx_memories_created_at", "created_at"),
        ("idx_memories_confidence", "confidence"),
    )
