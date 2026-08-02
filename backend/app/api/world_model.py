from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from ..storage.database import get_db_session
from ..world_model.engine import WorldModel

router = APIRouter()

_world_model_cache = None

async def _get_world_model(db_session):
    global _world_model_cache
    if _world_model_cache is None:
        _world_model_cache = WorldModel()
        await _world_model_cache.build_from_memories(db_session)
    return _world_model_cache

@router.get("/world-model/entity/{entity_name}")
async def get_entity(entity_name: str, db_session=Depends(get_db_session)):
    wm = await _get_world_model(db_session)
    result = wm.query_entity(entity_name.lower())
    if not result:
        raise HTTPException(status_code=404, detail="Entity not found in world model")
    return result

@router.get("/world-model/path")
async def find_entity_path(source: str, target: str, max_hops: int = 3, db_session=Depends(get_db_session)):
    wm = await _get_world_model(db_session)
    path = wm.find_path(source.lower(), target.lower(), max_hops)
    if not path:
        return {"source": source, "target": target, "path": None, "connected": False}
    return {"source": source, "target": target, "path": path, "hops": len(path) - 1, "connected": True}

@router.get("/world-model/central")
async def get_central_entities(top_n: int = 10, db_session=Depends(get_db_session)):
    wm = await _get_world_model(db_session)
    return {"entities": wm.get_central_entities(top_n)}

@router.post("/world-model/rebuild")
async def rebuild_world_model(db_session=Depends(get_db_session)):
    global _world_model_cache
    _world_model_cache = None
    wm = await _get_world_model(db_session)
    return {"status": "rebuilt", "entity_count": len(wm.graph.nodes), "relationship_count": len(wm.graph.edges)}
