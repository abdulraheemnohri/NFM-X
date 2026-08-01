from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class MemoryCreate(BaseModel):
    type: str
    content: str
    subtype: Optional[str] = None
    agent_id: Optional[str] = None
    source_id: Optional[str] = None
    confidence: Optional[float] = None
    importance: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class MemoryUpdate(BaseModel):
    content: Optional[str] = None
    confidence: Optional[float] = None
    importance: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class SearchQuery(BaseModel):
    query: str
    agent_id: Optional[str] = None
    limit: Optional[int] = 20
    memory_types: Optional[List[str]] = None

class ContextQuery(BaseModel):
    agent_id: str
    query: str
    memory_types: Optional[List[str]] = None
    max_memories: Optional[int] = None
