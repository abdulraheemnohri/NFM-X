""" Pydantic models for Source objects """

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SourceType(str, Enum):
    USER = "user"
    DOCUMENT = "document"
    API = "api"
    WEB = "web"
    SYSTEM = "system"
    OCR = "ocr"


class SourceCreate(BaseModel):
    type: SourceType
    reference: str
    reliability: float = 1.0
    metadata: dict = Field(default_factory=dict)


class Source(SourceCreate):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True