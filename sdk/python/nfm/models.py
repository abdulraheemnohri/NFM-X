"""
NFM-X Python SDK Models

Data models for the NFM-X Python SDK.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MemoryStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"
    PENDING = "PENDING"


class MemoryType(str, Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"
    DOCUMENT = "DOCUMENT"


class Memory(BaseModel):
    id: str
    content: str
    title: Optional[str] = None
    type: MemoryType = MemoryType.TEXT
    status: MemoryStatus = MemoryStatus.ACTIVE
    tags: List[str] = Field(default_factory=list)
    source: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    version: int = 1
    parent_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MemoryCreate(BaseModel):
    content: str
    title: Optional[str] = None
    type: MemoryType = MemoryType.TEXT
    tags: List[str] = Field(default_factory=list)
    source: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MemoryUpdate(BaseModel):
    content: Optional[str] = None
    title: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class SearchResult(BaseModel):
    memory_id: str
    title: Optional[str] = None
    content: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    items: List[SearchResult] = Field(default_factory=list)
    total: int = 0
    query: str
    semantic: bool = True
    keyword: bool = True


class Context(BaseModel):
    context: str
    memory_ids: List[str] = Field(default_factory=list)
    token_count: int = 0
    query: str


class MemoryStats(BaseModel):
    total_memories: int = 0
    active_memories: int = 0
    archived_memories: int = 0
    deleted_memories: int = 0
    total_versions: int = 0
    avg_memory_size: float = 0.0
    total_storage_size: int = 0
    last_updated: Optional[datetime] = None
    most_used_tags: Dict[str, int] = Field(default_factory=dict)


class ConflictType(str, Enum):
    DUPLICATE = "DUPLICATE"
    CONTRADICTION = "CONTRADICTION"
    AMBIGUITY = "AMBIGUITY"


class ConflictSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Conflict(BaseModel):
    id: str
    type: ConflictType
    severity: ConflictSeverity
    description: str
    memory_ids: List[str] = Field(default_factory=list)
    detected_at: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class GraphNode(BaseModel):
    id: str
    label: Optional[str] = None
    type: str


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str
    weight: float = 1.0


class GraphData(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
    node_count: int = 0
    edge_count: int = 0