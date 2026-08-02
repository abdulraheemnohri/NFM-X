from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..storage.database import get_db_session
from ..memory.models import MemoryStatus
from ..compression.engine import MemoryCompressionEngine

router = APIRouter()

class CompressRequest(BaseModel):
    agent_id: Optional[str] = None
    action: str = "archive_old"  # archive_old, summarize_cluster, deduplicate
    memory_ids: Optional[list] = None

@router.post("/compression/run")
async def run_compression(request: CompressRequest, db_session=Depends(get_db_session)):
    engine = MemoryCompressionEngine()

    if request.action == "archive_old":
        memories = await engine.find_compressible_memories(db_session, request.agent_id)
        for mem in memories:
            mem.status = MemoryStatus.ARCHIVED
            if mem.metadata is None:
                mem.metadata = {}
            mem.metadata["archived_reason"] = "old_and_low_importance"
        await db_session.commit()
        return {"action": "archive_old", "archived_count": len(memories)}

    elif request.action == "summarize_cluster":
        if not request.memory_ids or len(request.memory_ids) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 memory IDs for summarization")
        summary = await engine.summarize_memory_cluster(db_session, request.memory_ids)
        return {"action": "summarize_cluster", "summary_id": summary.id if summary else None}

    elif request.action == "deduplicate":
        result = await engine.deduplicate_semantic(db_session, request.agent_id)
        return {"action": "deduplicate", **result}

    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")
