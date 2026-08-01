"""
NFM-X Agents API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy import select, func
from ..storage.database import get_db_session
from ..memory.models import Agent

router = APIRouter(prefix="/agents", tags=["Agents"])

class AgentCreateRequest(BaseModel):
    name: str
    agent_type: str = "assistant"
    description: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    memory_policy: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    id: str
    name: str
    agent_type: str
    description: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    memory_policy: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: str
    last_active: Optional[str] = None

class AgentListResponse(BaseModel):
    agents: List[AgentResponse]
    total: int

@router.post("/")
async def create_agent(request: AgentCreateRequest, db_session=Depends(get_db_session)):
    agent_id = str(uuid.uuid4())
    agent = Agent(id=agent_id, name=request.name, agent_type=request.agent_type, description=request.description, configuration=request.configuration or {}, memory_policy=request.memory_policy or {}, is_active=True, created_at=datetime.utcnow(), last_active=None, metadata={})
    async with db_session.begin(): db_session.add(agent)
    return AgentResponse(id=agent.id, name=agent.name, agent_type=agent.agent_type, description=agent.description, configuration=agent.configuration, memory_policy=agent.memory_policy, is_active=agent.is_active, created_at=agent.created_at.isoformat(), last_active=agent.last_active.isoformat() if agent.last_active else None)

@router.get("/{agent_id}")
async def get_agent(agent_id: str, db_session=Depends(get_db_session)):
    async with db_session.begin():
        stmt = select(Agent).where(Agent.id == agent_id)
        result = await db_session.execute(stmt)
        agent = result.scalar_one_or_none()
        if agent is None: raise HTTPException(status_code=404, detail="Agent not found")
        return AgentResponse(id=agent.id, name=agent.name, agent_type=agent.agent_type, description=agent.description, configuration=agent.configuration, memory_policy=agent.memory_policy, is_active=agent.is_active, created_at=agent.created_at.isoformat(), last_active=agent.last_active.isoformat() if agent.last_active else None)

@router.get("/")
async def list_agents(agent_type: Optional[str] = None, is_active: Optional[bool] = None, limit: int = 50, offset: int = 0, db_session=Depends(get_db_session)):
    async with db_session.begin():
        stmt = select(Agent)
        if agent_type: stmt = stmt.where(Agent.agent_type == agent_type)
        if is_active is not None: stmt = stmt.where(Agent.is_active == is_active)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await db_session.execute(count_stmt)
        total = count_result.scalar()
        stmt = stmt.order_by(Agent.created_at.desc()).limit(limit).offset(offset)
        result = await db_session.execute(stmt)
        agents = result.scalars().all()
        return AgentListResponse(agents=[AgentResponse(id=a.id, name=a.name, agent_type=a.agent_type, description=a.description, configuration=a.configuration, memory_policy=a.memory_policy, is_active=a.is_active, created_at=a.created_at.isoformat(), last_active=a.last_active.isoformat() if a.last_active else None) for a in agents], total=total)