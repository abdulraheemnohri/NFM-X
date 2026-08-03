"""
NFM-X Simulation Database Models
SQLAlchemy models for simulation persistence
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Enum, func, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum
import uuid

from ..storage.database import Base


class SimulationStatus(str, PyEnum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PAUSED = "PAUSED"


class SimulationAction(str, PyEnum):
    INJECT = "inject"
    REMOVE = "remove"
    MODIFY = "modify"
    QUERY = "query"


class MemorySimulation(Base):
    __tablename__ = "memory_simulations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    simulation_id = Column(String(50), unique=True, index=True)  # Human-readable ID
    name = Column(String(500), index=True)
    description = Column(Text)
    status = Column(Enum(SimulationStatus), default=SimulationStatus.ACTIVE)
    original_memory_ids = Column(JSON, default=[])  # List of original memory IDs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)
    metadata = Column(JSON, default={})
    
    # Relationships
    actions = relationship("SimulationActionLog", back_populates="simulation", cascade="all, delete-orphan")
    injected_memories = relationship("SimulatedMemory", back_populates="simulation", cascade="all, delete-orphan")


class SimulatedMemory(Base):
    __tablename__ = "simulated_memories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    simulation_id = Column(String(36), ForeignKey("memory_simulations.id", ondelete="CASCADE"), index=True)
    memory_id = Column(String(36), index=True)  # Original memory ID or simulated ID
    content = Column(Text, nullable=False)
    memory_type = Column(String(100), default="TEXT")
    title = Column(String(500))
    source = Column(String(1000))
    tags = Column(JSON, default=[])
    categories = Column(JSON, default=[])
    metadata = Column(JSON, default={})
    is_injected = Column(Boolean, default=False)  # True if this is an injected memory
    is_modified = Column(Boolean, default=False)  # True if original memory was modified
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))
    
    simulation = relationship("MemorySimulation", back_populates="injected_memories")


class SimulationActionLog(Base):
    __tablename__ = "simulation_action_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    simulation_id = Column(String(36), ForeignKey("memory_simulations.id", ondelete="CASCADE"), index=True)
    action = Column(Enum(SimulationAction), index=True)
    memory_id = Column(String(36), index=True)  # Memory ID affected by the action
    details = Column(JSON, default={})  # Additional details about the action
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    simulation = relationship("MemorySimulation", back_populates="actions")


# Define python properties dynamically for metadata attributes
def _metadata_get(self):
    return self.meta if hasattr(self, 'meta') else {}

def _metadata_set(self, value):
    if hasattr(self, 'meta'):
        self.meta = value
    else:
        self.metadata = value

MemorySimulation.metadata = property(_metadata_get, _metadata_set)
SimulatedMemory.metadata = property(_metadata_get, _metadata_set)