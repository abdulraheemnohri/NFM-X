""" Pydantic models for Relationship objects """

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class RelationshipType(str, Enum):
    RELATED = "related"
    CAUSES = "causes"
    DEPENDS_ON = "depends_on"
    USES = "uses"
    PART_OF = "part_of"
    SIMILAR_TO = "similar_to"
    OPPOSES = "opposes"


class RelationshipCreate(BaseModel):
    source_id: str
    target_id: str
    type: RelationshipType
    confidence: float = 1.0
    source: str = ""
    evidence: List[str] = Field(default_factory=list)
    valid_from: datetime
    valid_until: Optional[datetime] = None


class Relationship(RelationshipCreate):
    id: str
    timestamp: datetime

    class Config:
        from_attributes = True