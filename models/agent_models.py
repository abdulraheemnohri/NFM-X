""" Pydantic models for Agent objects """

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AgentCreate(BaseModel):
    name: str
    description: str = ""


class Agent(AgentCreate):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True