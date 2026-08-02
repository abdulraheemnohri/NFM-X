"""NFM-X V2 Memory Models - Versioned memory data structures"""

from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum


class MemoryStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"


class MemoryModality(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    MULTIMODAL = "multimodal"


class MemoryV2(BaseModel):
    id: str = Field(default_factory=lambda: f"mem_v2_{datetime.now().isoformat()}")
    content: str
    version: int = 1
    previous_version_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict = {}
    tags: List[str] = []
    status: MemoryStatus = MemoryStatus.ACTIVE
    modality: MemoryModality = MemoryModality.TEXT
    source: Optional[str] = None
    relationships: List[str] = []
    
    class Config:
        from_attributes = True


class MemoryVersion(BaseModel):
    version_id: str
    memory_id: str
    content: str
    version_number: int
    created_at: datetime
    metadata: Dict
    changes: Dict = {}