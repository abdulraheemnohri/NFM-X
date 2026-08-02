"""NFM-X V2 Python SDK Models"""

from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class MemoryV2(BaseModel):
    id: str
    content: str
    version: int
    previous_version_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metadata: Dict = {}
    tags: List[str] = []
    status: str = "ACTIVE"
    modality: str = "text"
    source: Optional[str] = None
    relationships: List[str] = []


class SearchRequestV2(BaseModel):
    query: str
    limit: int = 10
    semantic_weight: float = 0.6
    keyword_weight: float = 0.3
    bm25_weight: float = 0.1
    filters: Optional[Dict] = None


class SearchResultV2(BaseModel):
    memory_id: str
    content: str
    score: float
    metadata: Dict
    modality: str