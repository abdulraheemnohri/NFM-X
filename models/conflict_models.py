""" Pydantic models for Conflict objects """

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ConflictStatus(str, Enum):
    UNRESOLVED = "unresolved"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class ConflictType(str, Enum):
    FACTUAL = "factual"
    TEMPORAL = "temporal"
    CONTEXTUAL = "contextual"
    INTERPRETATION = "interpretation"


class ConflictCreate(BaseModel):
    memory_ids: List[str]
    type: ConflictType
    status: ConflictStatus = ConflictStatus.UNRESOLVED
    resolution: Optional[str] = None


class Conflict(ConflictCreate):
    id: str
    detected_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True