""" Pydantic models for Skill objects """

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class SkillCreate(BaseModel):
    name: str
    description: str
    procedure: Any
    conditions: Any = None


class Skill(SkillCreate):
    id: str
    success_count: int = 0
    failure_count: int = 0
    learned_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True