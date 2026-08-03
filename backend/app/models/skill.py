"""
NFM-X Skill Database Models
SQLAlchemy models for skill execution tracking.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.sql import func
from backend.app.database import Base


class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    skill_type = Column(String, index=True)  # extraction, analysis, summarization, translation, classification, custom
    handler = Column(String)  # Python module path
    config = Column(JSON, default={})
    version = Column(String, default="1.0.0")
    author = Column(String)
    enabled = Column(Boolean, default=True)
    tags = Column(String, default="")  # Comma-separated
    status = Column(String, default="available")  # available, running, disabled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_executed_at = Column(DateTime(timezone=True))
    execution_count = Column(Integer, default=0)


class SkillExecution(Base):
    __tablename__ = "skill_executions"
    
    execution_id = Column(String, primary_key=True, index=True)
    skill_id = Column(Integer, index=True)
    skill_name = Column(String)
    input_data = Column(JSON, default={})
    output_data = Column(JSON)
    error = Column(Text)
    status = Column(String, index=True)  # running, completed, failed
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    execution_time_ms = Column(Float)
