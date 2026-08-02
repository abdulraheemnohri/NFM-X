"""
NFM-X Python SDK Models
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel

class MemoryType(str, Enum):
    TEXT = "TEXT"
    CONVERSATION = "CONVERSATION"
    DOCUMENT = "DOCUMENT"
    CODE = "CODE"

class MemoryStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"

class Memory(BaseModel):
    id: str
    content: str
    title: Optional[str] = None
    memory_type: MemoryType = MemoryType.TEXT
    status: MemoryStatus = MemoryStatus.ACTIVE
    version: int = 1
    created_at: datetime
    class Config:
        from_attributes = True