"""
NFM-X Agents API
Endpoints for agent management
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
async def create_agent(
    request: AgentCreateRequest,
    db_session=Depends(get_db_session)
):
    """Create a new agent"""
    agent_id = str(uuid.uuid4())
    agent = Agent(
        id=agent_id,
        name=request.name,
        agent_type=request.agent_type,
        description=request.description,
        configuration=request.configuration or {},
        memory_policy=request.memory_policy or {},
        is_active=True,
        created_at=datetime.utcnow(),
        last_active=None,
        metadata={}
    )
    async with db_session.begin():
        db_session.add(agent)
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        agent_type=agent.agent_type,
        description=agent.description,
        configuration=agent.configuration,
        memory_policy=agent.memory_policy,
        is_active=agent.is_active,
        created_at=agent.created_at.isoformat(),
        last_active=agent.last_active.isoformat() if agent.last_active else None
    )