#!/usr/bin/env python3
"""
NFM-X Models
============

Data models for NFM-X SDK.
Defines all the data structures used in API communication.

Urdu: NFM-X SDK پالئے کے لئے داتا ۞ډلز
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


# Memory Types
class MemoryType(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    PREFERENCE = "preference"
    DECISION = "decision"
    FAILURE = "failure"
    SUCCESS = "success"
    TEMPORAL = "temporal"
    CAUSAL = "causal"
    HYPOTHESIS = "hypothesis"
    CONFLICT = "conflict"
    MULTIMODAL = "multimodal"


class BaseMemoryModel(BaseModel):
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Memory(BaseMemoryModel):
    content: str = Field(..., description="Memory content")
    memory_type: MemoryType = Field(..., description="Type of memory")
    source: Optional[str] = Field(None, description="Source of the memory")
    tags: List[str] = Field(default_factory=list)
    current_version_id: str = Field(..., description="ID of current version")
    version_count: int = Field(default=1)
    confidence: float = Field(default=0.8)
    checksum: str = Field(..., description="Content checksum")


class MemoryVersion(BaseMemoryModel):
    memory_id: str = Field(..., description="Parent memory ID")
    content: str = Field(..., description="Version content")
    memory_type: MemoryType = Field(..., description="Type of memory")
    version_number: int = Field(..., description="Version number")
    is_current: bool = Field(default=True)
    confidence: float = Field(default=0.8)
    checksum: str = Field(..., description="Content checksum")
    source: Optional[str] = Field(None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)