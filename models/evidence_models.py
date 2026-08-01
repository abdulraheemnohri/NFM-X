""" Pydantic models for Evidence objects """

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class EvidenceCreate(BaseModel):
    source_id: str
    memory_id: str
    data: dict
    confidence: float = 1.0


class Evidence(EvidenceCreate):
    id: str
    timestamp: datetime

    class Config:
        from_attributes = True