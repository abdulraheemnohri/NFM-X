from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ..storage.database import get_db_session
from ..sync.engine import SyncEngine

router = APIRouter()

class SyncPullRequest(BaseModel):
    device_id: str
    last_sync: Optional[str] = None

class SyncPushRequest(BaseModel):
    device_id: str
    payload: dict

@router.post("/sync/pull")
async def sync_pull(request: SyncPullRequest, db_session=Depends(get_db_session)):
    engine = SyncEngine()
    last_sync = datetime.fromisoformat(request.last_sync.replace("Z", "+00:00")) if request.last_sync else None
    payload = await engine.generate_sync_payload(db_session, request.device_id, last_sync)
    return payload

@router.post("/sync/push")
async def sync_push(request: SyncPushRequest, db_session=Depends(get_db_session)):
    engine = SyncEngine()
    result = await engine.apply_sync_payload(db_session, request.payload, request.device_id)
    return result
