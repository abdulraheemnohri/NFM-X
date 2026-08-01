""" Pydantic models for Pattern objects """

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PatternCreate(BaseModel):
    name: str
    description: str
    supporting_memories: List[str] = Field(default_factory=list)
    confidence: float = 0.5


class Pattern(PatternCreate):
    id: str
    discovered_at: datetime
    validated_at: Optional[datetime] = None

    class Config:
        from_attributes = True