"""
Pydantic models for Memory objects
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MemoryType(str, Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PREFERENCE = "preference"
    PROJECT = "project"
    DECISION = "decision"
    PROCEDURAL = "procedural"
    SKILL = "skill"
    FAILURE = "failure"
    SUCCESS = "success"
    TEMPORAL = "temporal"
    CAUSAL = "causal"
    HYPOTHESIS = "hypothesis"
    CONFLICT = "conflict"
    SOURCE = "source"


class MemoryStatus(str, Enum):
    ACTIVE = "active"
    HISTORICAL = "historical"
    SUPERSEDED = "superseded"
    INVALID = "invalid"


class MemoryBase(BaseModel):
    type: MemoryType
    content: str
    normalized_content: str = ""
    status: MemoryStatus = MemoryStatus.ACTIVE
    confidence: float = 0.0
    importance: float = 0.0
    agent_id: str
    source_id: Optional[str] = None
    parent_id: Optional[str] = None
    evidence_ids: List[str] = Field(default_factory=list)
    relationship_ids: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class MemoryCreate(MemoryBase):
    pass


class Memory(MemoryBase):
    id: str
    root_id: str
    version: int = 1
    created_at: datetime
    observed_at: datetime
    valid_from: datetime
    valid_until: Optional[datetime] = None
    content_hash: str
    integrity_hash: str

    class Config:
        from_attributes = True


class MemoryUpdate(BaseModel):
    content: Optional[str] = None
    normalized_content: Optional[str] = None
    status: Optional[MemoryStatus] = None
    confidence: Optional[float] = None
    importance: Optional[float] = None
    metadata: Optional[dict] = None


class ChangeType(str, Enum):
    CREATE = "CREATE"
    REINFORCE = "REINFORCE"
    REFINE = "REFINE"
    EXPAND = "EXPAND"
    CORRECT = "CORRECT"
    MERGE = "MERGE"
    SPLIT = "SPLIT"
    SUPERSEDE = "SUPERSEDE"
    CONTRADICT = "CONTRADICT"
    RESTORE = "RESTORE"
    DISCOVER = "DISCOVER"


class MemoryVersion(BaseModel):
    version: int
    memory_id: str
    content: str
    previous_version: Optional[int] = None
    change_type: ChangeType
    change_reason: str
    evidence: List[str] = Field(default_factory=list)
    confidence_change: float = 0.0
    actor: str
    timestamp: datetime


class MemoryGenome(BaseModel):
    memory_id: str
    identity: dict
    origin: dict
    parent: Optional[str] = None
    children: List[str] = Field(default_factory=list)
    versions: List[int] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    relationships: List[str] = Field(default_factory=list)
    confidence: float
    importance: float
    contradictions: List[str] = Field(default_factory=list)
    usage: dict = Field(default_factory=dict)
    temporal_validity: dict = Field(default_factory=dict)
    current_state: str