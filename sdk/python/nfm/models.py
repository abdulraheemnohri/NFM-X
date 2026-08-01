#!/usr/bin/env python3
"""
NFM-X Models
============

Data models for NFM-X SDK.
Defines all the data structures used in API communication.

Urdu: NFM-X SDK ke liye data models
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


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
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class Memory(BaseMemoryModel):
    content: str = Field(..., description="Memory content")
    memory_type: MemoryType = Field(..., description="Type of memory")
    source: Optional[str] = Field(None, description="Source of the memory")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    current_version_id: str = Field(..., description="ID of current version")
    version_count: int = Field(default=1, description="Total number of versions")
    confidence: float = Field(default=0.8, description="Confidence score (0-1)")
    checksum: str = Field(..., description="Content checksum for integrity")


class MemoryVersion(BaseMemoryModel):
    memory_id: str = Field(..., description="Parent memory ID")
    content: str = Field(..., description="Version content")
    memory_type: MemoryType = Field(..., description="Type of memory")
    version_number: int = Field(..., description="Version number")
    is_current: bool = Field(default=True, description="Whether this is the current version")
    confidence: float = Field(default=0.8, description="Confidence score (0-1)")
    checksum: str = Field(..., description="Content checksum")
    source: Optional[str] = Field(None, description="Source of this version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Version timestamp")


class MemoryCreate(BaseModel):
    content: str = Field(..., description="Memory content")
    memory_type: Optional[MemoryType] = Field(None, description="Type of memory")
    source: Optional[str] = Field(None, description="Source of the memory")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    confidence: Optional[float] = Field(None, description="Initial confidence score")


class MemoryUpdate(BaseModel):
    content: Optional[str] = Field(None, description="Updated content")
    memory_type: Optional[MemoryType] = Field(None, description="Updated memory type")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")
    tags: Optional[List[str]] = Field(None, description="Updated tags")
    confidence: Optional[float] = Field(None, description="Updated confidence score")


class SearchQuery(BaseModel):
    query: str = Field(..., description="Search query text")
    memory_types: Optional[List[MemoryType]] = Field(None, description="Filter by memory types")
    time_range: Optional[tuple] = Field(None, description="Time range filter")
    confidence_threshold: Optional[float] = Field(None, description="Minimum confidence threshold")
    limit: int = Field(default=10, description="Maximum number of results")
    strategy: str = Field(default="hybrid", description="Search strategy")
    metadata_filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")


class SearchResult(BaseModel):
    memory_id: str = Field(..., description="Memory ID")
    version_id: str = Field(..., description="Version ID")
    content: str = Field(..., description="Memory content")
    memory_type: MemoryType = Field(..., description="Type of memory")
    confidence: float = Field(..., description="Confidence score")
    timestamp: datetime = Field(..., description="Memory timestamp")
    similarity_score: float = Field(..., description="Similarity score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Memory metadata")


class ContextQuery(BaseModel):
    query: str = Field(..., description="Context query text")
    memory_types: Optional[List[MemoryType]] = Field(None, description="Memory types to include")
    time_window: Optional[str] = Field(None, description="Time window")
    max_memories: int = Field(default=20, description="Maximum number of memories")
    include_relationships: bool = Field(default=True, description="Include relationships")


class ContextResult(BaseModel):
    query: str = Field(..., description="Original query")
    memories: List[Memory] = Field(default_factory=list, description="Relevant memories")
    relationships: List[Dict[str, Any]] = Field(default_factory=list, description="Relationships")
    summary: str = Field(default="", description="Context summary")
    temporal_context: Dict[str, Any] = Field(default_factory=dict, description="Temporal context")
    confidence: float = Field(default=0.0, description="Overall context confidence")


class EvolutionQuery(BaseModel):
    memory_id: str = Field(..., description="Memory ID to evolve")
    new_content: str = Field(..., description="New content to incorporate")
    evolution_type: str = Field(default="update", description="Type of evolution")
    preserve_original: bool = Field(default=True, description="Preserve original version")
    conflict_resolution: Optional[str] = Field(None, description="Conflict resolution strategy")


class EvolutionResult(BaseModel):
    original_memory_id: str = Field(..., description="Original memory ID")
    new_memory_id: str = Field(..., description="New memory ID")
    new_version_id: str = Field(..., description="New version ID")
    evolution_type: str = Field(..., description="Type of evolution performed")
    changes: Dict[str, Any] = Field(default_factory=dict, description="Changes made")
    conflicts: List[Dict[str, Any]] = Field(default_factory=list, description="Conflicts detected")
    confidence: float = Field(..., description="Confidence in the evolution")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Evolution timestamp")


class GraphQuery(BaseModel):
    query_type: str = Field(..., description="Type of graph query")
    node_id: Optional[str] = Field(None, description="Node ID for queries")
    relationship_type: Optional[str] = Field(None, description="Relationship type")
    max_depth: int = Field(default=2, description="Maximum depth for traversal")
    max_results: int = Field(default=50, description="Maximum number of results")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")


class GraphNode(BaseModel):
    id: str = Field(..., description="Node ID")
    label: str = Field(..., description="Node label")
    node_type: str = Field(..., description="Type of node")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Node properties")
    memory_id: Optional[str] = Field(None, description="Associated memory ID")
    version_id: Optional[str] = Field(None, description="Associated version ID")


class GraphEdge(BaseModel):
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    relationship: str = Field(..., description="Relationship type")
    weight: float = Field(default=1.0, description="Edge weight")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Edge properties")


class GraphResult(BaseModel):
    query_type: str = Field(..., description="Type of query performed")
    nodes: List[GraphNode] = Field(default_factory=list, description="Matching nodes")
    edges: List[GraphEdge] = Field(default_factory=list, description="Matching edges")
    paths: List[List[str]] = Field(default_factory=list, description="Found paths")
    statistics: Dict[str, Any] = Field(default_factory=dict, description="Graph statistics")


class AgentQuery(BaseModel):
    agent_type: str = Field(..., description="Type of agent to use")
    task: str = Field(..., description="Task for the agent")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    memory_ids: Optional[List[str]] = Field(None, description="Specific memory IDs")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Agent parameters")


class AgentResult(BaseModel):
    agent_type: str = Field(..., description="Type of agent used")
    task: str = Field(..., description="Task that was performed")
    result: Any = Field(..., description="Result of the operation")
    confidence: float = Field(..., description="Confidence in the result")
    steps: List[Dict[str, Any]] = Field(default_factory=list, description="Steps taken")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Operation timestamp")