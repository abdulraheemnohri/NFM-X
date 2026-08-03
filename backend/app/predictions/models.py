"""
NFM-X Predictions Database Models
SQLAlchemy models for predictions persistence
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Enum, func, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum
import uuid

from ..storage.database import Base


class PredictionStatus(str, PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class PredictionPattern(Base):
    __tablename__ = "prediction_patterns"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pattern_id = Column(String(36), unique=True, index=True)  # External ID for API compatibility
    name = Column(String(500), index=True)
    description = Column(Text)
    pattern_type = Column(String(100), index=True)  # e.g., "temporal", "causal", "semantic"
    pattern_data = Column(JSON, default={})  # The actual pattern data
    confidence = Column(Float, default=0.8)
    accuracy_history = Column(JSON, default=[])  # List of accuracy scores for variance calculation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))
    metadata = Column(JSON, default={})
    
    # Relationships
    predictions = relationship("Prediction", back_populates="pattern", cascade="all, delete-orphan")


class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prediction_id = Column(String(36), unique=True, index=True)  # External ID for API compatibility
    query = Column(Text, index=True)
    prediction_value = Column(JSON)  # Can store any type of prediction result
    base_confidence = Column(Float, default=0.5)
    confidence = Column(Float, default=0.0)
    confidence_lower = Column(Float, default=0.0)
    confidence_upper = Column(Float, default=1.0)
    pattern_variance = Column(Float, default=0.0)
    patterns_used = Column(JSON, default=[])  # List of pattern IDs used
    status = Column(Enum(PredictionStatus), default=PredictionStatus.PENDING)
    pattern_id = Column(String(36), ForeignKey("prediction_patterns.pattern_id"), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))
    metadata = Column(JSON, default={})
    
    pattern = relationship("PredictionPattern", back_populates="predictions")


# Define python properties dynamically for metadata attributes
def _metadata_get(self):
    return self.metadata if hasattr(self, 'metadata') else {}

def _metadata_set(self, value):
    if hasattr(self, 'metadata'):
        self.metadata = value

PredictionPattern.metadata = property(_metadata_get, _metadata_set)
Prediction.metadata = property(_metadata_get, _metadata_set)