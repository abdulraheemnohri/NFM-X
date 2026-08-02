"""NFM-X V3 World Model API
Entity management and merging endpoints"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

from backend.app.world_model.merge import WorldModelMerger, MergeStrategy, MergeResult

router = APIRouter(prefix="/api/v1/world-model", tags=["World Model"])


class EntityType(str, Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    CONCEPT = "concept"
    EVENT = "event"
    OBJECT = "object"
    TIME = "time"
    OTHER = "other"


class EntityCreate(BaseModel):
    name: str
    entity_type: EntityType
    attributes: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


class EntityResponse(BaseModel):
    entity_id: str
    name: str
    entity_type: str
    attributes: Dict[str, Any]
    relationships: Dict[str, List[str]]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]


class MergeRequest(BaseModel):
    source_entity_id: str
    target_entity_id: str
    strategy: str = "combine"  # combine, prefer_source, prefer_target


class MergeResponse(BaseModel):
    success: bool
    merged_entity_id: str
    source_entity_id: str
    target_entity_id: str
    strategy_used: str
    attributes_merged: Dict[str, Any]
    relationships_merged: Dict[str, List[str]]
    conflicts_resolved: List[str]
    timestamp: datetime


# Initialize world model merger
world_model_merger = WorldModelMerger()


@router.post("/entities", response_model=EntityResponse, status_code=201)
async def create_entity(entity: EntityCreate):
    """
    Create a new entity in the world model
    """
    from backend.app.world_model.merge import Entity
    import uuid
    
    entity_obj = Entity(
        entity_id=str(uuid.uuid4()),
        name=entity.name,
        entity_type=entity.entity_type.value,
        attributes=entity.attributes,
        metadata=entity.metadata
    )
    
    world_model_merger.add_entity(entity_obj)
    
    return EntityResponse(
        entity_id=entity_obj.entity_id,
        name=entity_obj.name,
        entity_type=entity_obj.entity_type,
        attributes=entity_obj.attributes,
        relationships=entity_obj.relationships,
        created_at=entity_obj.created_at,
        updated_at=entity_obj.updated_at,
        metadata=entity_obj.metadata
    )


@router.get("/entities", response_model=List[EntityResponse])
async def list_entities(entity_type: Optional[str] = None):
    """
    List all entities in the world model
    """
    entities = world_model_merger.list_entities(entity_type)
    return [
        EntityResponse(
            entity_id=e.entity_id,
            name=e.name,
            entity_type=e.entity_type,
            attributes=e.attributes,
            relationships=e.relationships,
            created_at=e.created_at,
            updated_at=e.updated_at,
            metadata=e.metadata
        )
        for e in entities
    ]


@router.post("/merge", response_model=MergeResponse)
async def merge_entities(request: MergeRequest):
    """
    Merge two entities in the world model
    
    Request body:
    - source_entity_id: The entity to merge (will be removed)
    - target_entity_id: The entity to keep (will be updated)
    - strategy: Merge strategy (combine, prefer_source, prefer_target)
    """
    try:
        strategy = MergeStrategy(request.strategy)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid strategy. Use: combine, prefer_source, prefer_target")
    
    try:
        result = world_model_merger.merge_entities(
            source_id=request.source_entity_id,
            target_id=request.target_entity_id,
            strategy=strategy
        )
        
        return MergeResponse(
            success=result.success,
            merged_entity_id=result.merged_entity_id,
            source_entity_id=result.source_entity_id,
            target_entity_id=result.target_entity_id,
            strategy_used=result.strategy_used.value,
            attributes_merged=result.attributes_merged,
            relationships_merged={k: v for k, v in result.relationships_merged.items()},
            conflicts_resolved=result.conflicts_resolved,
            timestamp=result.timestamp
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/merge/history", response_model=List[MergeResponse])
async def get_merge_history(limit: int = 100):
    """
    Get the history of merge operations
    """
    history = world_model_merger.get_merge_history(limit)
    return [
        MergeResponse(
            success=r.success,
            merged_entity_id=r.merged_entity_id,
            source_entity_id=r.source_entity_id,
            target_entity_id=r.target_entity_id,
            strategy_used=r.strategy_used.value,
            attributes_merged=r.attributes_merged,
            relationships_merged={k: list(v) for k, v in r.relationships_merged.items()},
            conflicts_resolved=r.conflicts_resolved,
            timestamp=r.timestamp
        )
        for r in history
    ]