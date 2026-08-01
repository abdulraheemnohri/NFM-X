""" Pydantic models for ProjectMemory objects """

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class ProjectMemoryCreate(BaseModel):
    name: str
    goals: List[str] = Field(default_factory=list)
    architecture: Any = None
    technology: List[str] = Field(default_factory=list)
    decisions: List[Any] = Field(default_factory=list)
    requirements: List[Any] = Field(default_factory=list)
    tasks: List[Any] = Field(default_factory=list)
    bugs: List[Any] = Field(default_factory=list)
    features: List[Any] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    files: List[str] = Field(default_factory=list)
    versions: List[Any] = Field(default_factory=list)
    milestones: List[Any] = Field(default_factory=list)


class ProjectMemory(ProjectMemoryCreate):
    id: str

    class Config:
        from_attributes = True