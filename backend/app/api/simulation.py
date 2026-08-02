from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import select

from ..storage.database import get_db_session
from ..memory.models import Memory, MemoryStatus
from ..simulation.engine import MemorySandbox

router = APIRouter()

# In-memory sandbox storage (resets on server restart)
_sandboxes: dict = {}

class CreateSandboxRequest(BaseModel):
    agent_id: Optional[str] = None

class InjectMemoryRequest(BaseModel):
    simulation_id: str
    memory: dict

class ModifyMemoryRequest(BaseModel):
    simulation_id: str
    memory_id: str
    new_content: str

@router.post("/simulation/create")
async def create_sandbox(request: CreateSandboxRequest, db_session=Depends(get_db_session)):
    stmt = select(Memory).where(Memory.status == MemoryStatus.ACTIVE)
    if request.agent_id:
        stmt = stmt.where(Memory.agent_id == request.agent_id)
    result = await db_session.execute(stmt)
    memories = result.scalars().all()

    mem_dicts = [
        {"id": m.id, "type": m.type.value, "content": m.content,
         "confidence": m.confidence, "importance": m.importance,
         "created_at": m.created_at.isoformat() if m.created_at else None}
        for m in memories
    ]

    sandbox = MemorySandbox(mem_dicts)
    _sandboxes[sandbox.simulation_id] = sandbox
    return {"simulation_id": sandbox.simulation_id, "state": sandbox.get_state()}

@router.post("/simulation/inject")
async def inject_memory(request: InjectMemoryRequest):
    sandbox = _sandboxes.get(request.simulation_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="Simulation not found")
    injected = sandbox.inject_memory(request.memory)
    return {"injected": injected, "state": sandbox.get_state()}

@router.post("/simulation/modify")
async def modify_memory(request: ModifyMemoryRequest):
    sandbox = _sandboxes.get(request.simulation_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="Simulation not found")
    modified = sandbox.modify_memory(request.memory_id, request.new_content)
    return {"modified": modified, "state": sandbox.get_state()}

@router.get("/simulation/{simulation_id}/query")
async def query_sandbox(simulation_id: str, q: str):
    sandbox = _sandboxes.get(simulation_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="Simulation not found")
    results = sandbox.query_simulation(q)
    return {"query": q, "results": results, "state": sandbox.get_state()}

@router.get("/simulation/{simulation_id}/state")
async def get_sandbox_state(simulation_id: str):
    sandbox = _sandboxes.get(simulation_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sandbox.get_state()
