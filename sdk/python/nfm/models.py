"""
Data models for NFM-X SDK
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class MemoryType(str, Enum):
    FACT = "fact"; CONCEPT = "concept"; PROCEDURE = "procedure"; EXPERIENCE = "experience"; CAUSAL = "causal"; DECISION = "decision"; OBSERVATION = "observation"; HYPOTHESIS = "hypothesis"; GOAL = "goal"; PLAN = "plan"

class MemoryStatus(str, Enum):
    ACTIVE = "active"; ARCHIVED = "archived"; DELETED = "deleted"; WORKING = "working"

class ChangeType(str, Enum):
    CORRECT = "correct"; REFINES = "refine"; EXPAND = "expand"; SUPERSEDE = "supersede"; CLARIFY = "clarify"; SIMPLIFY = "simplify"

class MemoryCreateRequest(BaseModel):
    content: str = Field(..., min_length=1)
    memory_type: Optional[MemoryType] = None
    source: Optional[str] = None
    author_id: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    importance: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class MemoryUpdateRequest(BaseModel):
    content: str = Field(..., min_length=1)
    change_type: ChangeType = Field(...)
    change_reason: str = Field(..., min_length=1)
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    importance: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None

class MemoryVersion(BaseModel):
    id: str; memory_id: str; version_number: int; content: str
    change_type: ChangeType; change_reason: Optional[str]
    confidence: float; importance: float; status: MemoryStatus
    actor_id: Optional[str]; actor_type: Optional[str]; created_at: datetime

class Memory(BaseModel):
    id: str; content: str; content_hash: str; memory_type: MemoryType
    confidence: float; importance: float; status: MemoryStatus
    source: Optional[str]; source_type: Optional[str]; author_id: Optional[str]
    created_at: datetime; updated_at: datetime
    metadata: Dict[str, Any]; tags: List[str]
    current_version: Optional[MemoryVersion] = None
    version_count: int = 0; event_count: int = 0

class MemoryListResponse(BaseModel):
    memories: List[Memory]; total: int; limit: int; offset: int

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=1000)
    memory_types: Optional[List[MemoryType]] = None
    status: Optional[MemoryStatus] = None

class SearchResponse(BaseModel):
    query: str; results: List[Memory]; scores: List[float]
    total: int; search_mode: str; execution_time_ms: float

class ContextRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=100)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    memory_types: Optional[List[MemoryType]] = None
    format: str = "text"

class ContextResponse(BaseModel):
    query: str; context: str; memories: List[Memory]
    total_memories: int; total_tokens_estimated: int; execution_time_ms: float