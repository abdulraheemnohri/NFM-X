""" Pydantic models for Preference objects """

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class PreferenceCreate(BaseModel):
    key: str
    value: Any
    confidence: float = 0.5
    evidence: List[str] = Field(default_factory=list)
    current_status: str = "active"
    evolution_history: List[Any] = Field(default_factory=list)


class Preference(PreferenceCreate):
    id: str
    last_confirmed: datetime

    class Config:
        from_attributes = True