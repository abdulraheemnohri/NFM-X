from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import select
from datetime import datetime, timezone
import uuid

from ..storage.database import get_db_session
from ..memory.models import Memory, MemoryStatus, MemoryType
from ..sharing.protocol import MemoryBundle, SharePermission

router = APIRouter()

class ShareRequest(BaseModel):
    source_agent_id: str
    target_agent_id: str
    memory_ids: List[str]
    permissions: str = "read"  # read, write, admin
    note: Optional[str] = None

class ImportRequest(BaseModel):
    bundle: dict
    target_agent_id: str

@router.post("/sharing/export")
async def export_memories(request: ShareRequest, db_session=Depends(get_db_session)):
    """Export memories into a shareable bundle."""
    memories = []
    for mem_id in request.memory_ids:
        result = await db_session.execute(select(Memory).where(Memory.id == mem_id))
        mem = result.scalar_one_or_none()
        if mem:
            memories.append({
                "id": mem.id, "type": mem.type.value, "content": mem.content,
                "confidence": mem.confidence, "importance": mem.importance,
                "metadata": mem.metadata, "original_agent": mem.agent_id,
                "original_created_at": mem.created_at.isoformat() if mem.created_at else None
            })

    bundle = MemoryBundle(
        source_agent_id=request.source_agent_id,
        target_agent_id=request.target_agent_id,
        memories=memories,
        permissions=SharePermission(request.permissions)
    )
    bundle.status = "ready"

    return {"bundle": bundle.to_dict(), "export_count": len(memories)}

@router.post("/sharing/import")
async def import_memories(request: ImportRequest, db_session=Depends(get_db_session)):
    """Import memories from a bundle."""
    bundle_data = request.bundle
    bundle = MemoryBundle(
        source_agent_id=bundle_data["source_agent_id"],
        target_agent_id=request.target_agent_id,
        memories=bundle_data["memories"],
        permissions=SharePermission(bundle_data.get("permissions", "read"))
    )

    if not bundle.validate_bundle():
        raise HTTPException(status_code=400, detail="Invalid bundle")

    imported = []
    for mem_data in bundle.memories:
        new_mem = Memory(
            id=str(uuid.uuid4()),
            root_id=str(uuid.uuid4()),
            version=1,
            type=MemoryType(mem_data["type"]),
            content=mem_data["content"],
            normalized_content=mem_data["content"].lower().strip(),
            agent_id=request.target_agent_id,
            source_id=f"imported:{mem_data.get('original_agent', 'unknown')}",
            confidence=mem_data.get("confidence", 0.5),
            importance=mem_data.get("importance", 0.5),
            status=MemoryStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            observed_at=datetime.now(timezone.utc),
            valid_from=datetime.now(timezone.utc),
            metadata={
                **(mem_data.get("metadata") or {}),
                "imported_from": bundle.source_agent_id,
                "original_id": mem_data["id"],
                "imported_at": datetime.now(timezone.utc).isoformat()
            }
        )
        db_session.add(new_mem)
        imported.append(new_mem.id)

    await db_session.commit()
    return {"imported_count": len(imported), "imported_ids": imported, "source_agent": bundle.source_agent_id}
