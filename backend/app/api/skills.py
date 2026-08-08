"""
NFM-X Skill Execution Tracking API
Track and manage skill executions, results, and performance.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import json
from enum import Enum

from backend.app.database import get_db_connection

router = APIRouter(prefix="", tags=["skills"])


class SkillStatus(str, Enum):
    AVAILABLE = "available"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DISABLED = "disabled"


class SkillType(str, Enum):
    EXTRACTION = "extraction"
    ANALYSIS = "analysis"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    CLASSIFICATION = "classification"
    CUSTOM = "custom"


class SkillBase(BaseModel):
    name: str
    description: str
    skill_type: SkillType
    version: str = "1.0.0"
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class SkillCreate(SkillBase):
    handler: str  # Python module path
    config: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    skill_type: Optional[SkillType] = None
    version: Optional[str] = None
    author: Optional[str] = None
    handler: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None
    tags: Optional[List[str]] = None


class SkillResponse(SkillBase):
    id: int
    handler: str
    config: Dict[str, Any]
    enabled: bool
    status: SkillStatus
    created_at: datetime
    updated_at: datetime
    last_executed_at: Optional[datetime] = None
    execution_count: int = 0


class SkillExecutionRequest(BaseModel):
    skill_id: int
    input_data: Dict[str, Any] = Field(default_factory=dict)
    async_execution: bool = False
    callback_url: Optional[str] = None


class SkillExecutionResponse(BaseModel):
    execution_id: str
    skill_id: int
    skill_name: str
    status: SkillStatus
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    execution_time_ms: Optional[float] = None


class SkillExecutionListResponse(BaseModel):
    execution_id: str
    skill_id: int
    skill_name: str
    status: SkillStatus
    started_at: datetime
    completed_at: Optional[datetime] = None


@router.get("/", response_model=List[SkillResponse])
async def list_skills(
    skill_type: Optional[SkillType] = None,
    enabled: Optional[bool] = None,
    tag: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """List all available skills."""
    db = await get_db_connection()
    query = "SELECT * FROM skills"
    params = []
    
    conditions = []
    if skill_type:
        conditions.append("skill_type = ?")
        params.append(skill_type.value)
    if enabled is not None:
        conditions.append("enabled = ?")
        params.append(enabled)
    if tag:
        conditions.append("tags LIKE ?")
        params.append(f"%{tag}%")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    async with db.execute(query, params) as cursor:
        rows = await cursor.fetchall()
    
    skills = []
    for row in rows:
        skills.append(SkillResponse(
            id=row[0],
            name=row[1],
            description=row[2],
            skill_type=SkillType(row[3]),
            handler=row[4],
            config=row[5] or {},
            version=row[6],
            author=row[7],
            enabled=bool(row[8]),
            tags=row[9].split(",") if row[9] else [],
            status=SkillStatus(row[10]),
            created_at=datetime.fromisoformat(row[11]),
            updated_at=datetime.fromisoformat(row[12]),
            last_executed_at=datetime.fromisoformat(row[13]) if row[13] else None,
            execution_count=row[14]
        ))
    
    return skills


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: int):
    """Get a specific skill by ID."""
    db = await get_db_connection()
    async with db.execute(
        "SELECT * FROM skills WHERE id = ?", (skill_id,)
    ) as cursor:
        row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    return SkillResponse(
        id=row[0],
        name=row[1],
        description=row[2],
        skill_type=SkillType(row[3]),
        handler=row[4],
        config=row[5] or {},
        version=row[6],
        author=row[7],
        enabled=bool(row[8]),
        tags=row[9].split(",") if row[9] else [],
        status=SkillStatus(row[10]),
        created_at=datetime.fromisoformat(row[11]),
        updated_at=datetime.fromisoformat(row[12]),
        last_executed_at=datetime.fromisoformat(row[13]) if row[13] else None,
        execution_count=row[14]
    )


@router.post("/", response_model=SkillResponse, status_code=201)
async def create_skill(skill: SkillCreate):
    """Register a new skill."""
    db = await get_db_connection()
    
    async with db.execute(
        """INSERT INTO skills (name, description, skill_type, handler, config, version, author, enabled, tags)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            skill.name,
            skill.description,
            skill.skill_type.value,
            skill.handler,
            json.dumps(skill.config),
            skill.version,
            skill.author,
            skill.enabled,
            ",".join(skill.tags)
        )
    ) as cursor:
        skill_id = cursor.lastrowid
    
    await db.commit()
    
    return SkillResponse(
        id=skill_id,
        **skill.dict(),
        status=SkillStatus.AVAILAB
LE,
       
 created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        execution_count=0
    )


@router.put("/{skill_id}", response_model=SkillResponse)
async def update_skill(skill_id: int, skill: SkillUpdate):
    """Update an existing skill."""
    db = await get_db_connection()
    
    async with db.execute(
        "SELECT * FROM skills WHERE id = ?", (skill_id,)
    ) as cursor:
        row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    updates = []
    params = []
    
    if skill.name is not None:
        updates.append("name = ?")
        params.append(skill.name)
    if skill.description is not None:
        updates.append("description = ?")
        params.append(skill.description)
    if skill.skill_type is not None:
        updates.append("skill_type = ?")
        params.append(skill.skill_type.value)
    if skill.version is not None:
        updates.append("version = ?")
        params.append(skill.version)
    if skill.author is not None:
        updates.append("author = ?")
        params.append(skill.author)
    if skill.handler is not None:
        updates.append("handler = ?")
        params.append(skill.handler)
    if skill.config is not None:
        updates.append("config = ?")
        params.append(json.dumps(skill.config))
    if skill.enabled is not None:
        updates.append("enabled = ?")
        params.append(skill.enabled)
    if skill.tags is not None:
        updates.append("tags = ?")
        params.append(",".join(skill.tags))
    
    if updates:
        updates.append("updated_at = ?")
        params.append(datetime.now(timezone.utc).isoformat())
        params.append(skill_id)
        
        query = "UPDATE skills SET " + ", ".join(updates) + " WHERE id = ?"
        async with db.execute(query, params):
            pass
        await db.commit()
    
    async with db.execute(
        "SELECT * FROM skills WHERE id = ?", (skill_id,)
    
) as curso
r:
        row = await cursor.fetchone()
    
    return SkillResponse(
        id=row[0],
        name=row[1],
        description=row[2],
        skill_type=SkillType(row[3]),
        handler=row[4],
        config=row[5] or {},
        version=row[6],
        author=row[7],
        enabled=bool(row[8]),
        tags=row[9].split(",") if row[9] else [],
        status=SkillStatus(row[10]),
        created_at=datetime.fromisoformat(row[11]),
        updated_at=datetime.fromisoformat(row[12]),
        last_executed_at=datetime.fromisoformat(row[13]) if row[13] else None,
        execution_count=row[14]
    )


@router.delete("/{skill_id}", status_code=204)
async def delete_skill(skill_id: int):
    """Delete a skill."""
    db = await get_db_connection()
    
    async with db.execute(
        "DELETE FROM skills WHERE id = ?", (skill_id,)
    ) as cursor:
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Skill not found")
    
    await db.commit()


@router.post("/{skill_id}/execute", response_model=SkillExecutionResponse)
async def execute_skill(
    skill_id: int,
    request: SkillExecutionRequest,
    background_tasks: BackgroundTasks = None
):
    """Execute a skill with the given input data."""
    db = await get_db_connection()
    
    async with db.execute(
        "SELECT name, handler, config FROM skills WHERE id = ?", (skill_id,)
    ) as cursor:
        row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    skill_name = row[0]
    handler_path = row[1]
    skill_config = row[2] or {}
    
    execution_id = f"exec_{skill_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
    started_at = datetime.now(timezone.utc)
    
    async with db.execute(
        """INSERT INTO skill_executions (execution_id, skill_id, skill_name, input_data, status, started_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (execution_id, skill_id, skill_name
, json.du
mps(request.input_data), SkillStatus.RUNNING.value, started_at.isoformat())
    ):
        pass
    
    async with db.execute(
        "UPDATE skills SET last_executed_at = ?, execution_count = execution_count + 1 WHERE id = ?",
        (started_at.isoformat(), skill_id)
    ):
        pass
    
    await db.commit()
    
    if request.async_execution:
        if background_tasks:
            background_tasks.add_task(_execute_skill_async, skill_id, execution_id, handler_path, skill_config, request.input_data)
        
        return SkillExecutionResponse(
            execution_id=execution_id,
            skill_id=skill_id,
            skill_name=skill_name,
            status=SkillStatus.RUNNING,
            input_data=request.input_data,
            started_at=started_at
        )
    else:
        try:
            result = await _execute_skill_sync(handler_path, skill_config, request.input_data)
            completed_at = datetime.now(timezone.utc)
            execution_time = (completed_at - started_at).total_seconds() * 1000
            
            async with db.execute(
                """UPDATE skill_executions SET status = ?, output_data = ?, completed_at = ?, 
                   execution_time_ms = ? WHERE execution_id = ?""",
                (SkillStatus.COMPLETED.value, json.dumps(result), completed_at.isoformat(), execution_time, execution_id)
            ):
                pass
            await db.commit()
            
            return SkillExecutionResponse(
                execution_id=execution_id,
                skill_id=skill_id,
                skill_name=skill_name,
                status=SkillStatus.COMPLETED,
                input_data=request.input_data,
                output_data=result,
                started_at=started_at,
                completed_at=completed_at,
                execution_time_ms=execution_time
            )
        except Exception as e:
            async with db.execute(
                """UPDATE skill_execut
ions SET
 status = ?, error = ?, completed_at = ? 
                   WHERE execution_id = ?""",
                (SkillStatus.FAILED.value, str(e), datetime.now(timezone.utc).isoformat(), execution_id)
            ):
                pass
            await db.commit()
            
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/executions", response_model=List[SkillExecutionListResponse])
async def list_executions(
    skill_id: Optional[int] = None,
    status: Optional[SkillStatus] = None,
    limit: int = 100,
    offset: int = 0
):
    """List skill executions with optional filtering."""
    db = await get_db_connection()
    query = "SELECT execution_id, skill_id, skill_name, status, started_at, completed_at FROM skill_executions"
    params = []
    
    conditions = []
    if skill_id is not None:
        conditions.append("skill_id = ?")
        params.append(skill_id)
    if status:
        conditions.append("status = ?")
        params.append(status.value)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY started_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    async with db.execute(query, params) as cursor:
        rows = await cursor.fetchall()
    
    executions = []
    for row in rows:
        executions.append(SkillExecutionListResponse(
            execution_id=row[0],
            skill_id=row[1],
            skill_name=row[2],
            status=SkillStatus(row[3]),
            started_at=datetime.fromisoformat(row[4]),
            completed_at=datetime.fromisoformat(row[5]) if row[5] else None
        ))
    
    return executions


@router.get("/{skill_id}/executions", response_model=List[SkillExecutionListResponse])
async def list_skill_executions(
    skill_id: int,
    limit: int = 100,
    offset: int = 0
):
    """List executions for a specific skill."""
    db = await get_db_connection()
    async with db.execute(
        "SELECT execution_id
, skill
_id, skill_name, status, started_at, completed_at FROM skill_executions WHERE skill_id = ? ORDER BY started_at DESC LIMIT ? OFFSET ?",
        (skill_id, limit, offset)
    ) as cursor:
        rows = await cursor.fetchall()
    
    executions = []
    for row in rows:
        executions.append(SkillExecutionListResponse(
            execution_id=row[0],
            skill_id=row[1],
            skill_name=row[2],
            status=SkillStatus(row[3]),
            started_at=datetime.fromisoformat(row[4]),
            completed_at=datetime.fromisoformat(row[5]) if row[5] else None
        ))
    
    return executions


@router.get("/executions/{execution_id}", response_model=SkillExecutionResponse)
async def get_execution(execution_id: str):
    """Get details of a specific skill execution."""
    db = await get_db_connection()
    async with db.execute(
        "SELECT * FROM skill_executions WHERE execution_id = ?", (execution_id,)
    ) as cursor:
        row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return SkillExecutionResponse(
        execution_id=row[0],
        skill_id=row[1],
        skill_name=row[2],
        status=SkillStatus(row[3]),
        input_data=row[4] or {},
        output_data=row[5] or None,
        error=row[6],
        started_at=datetime.fromisoformat(row[7]),
        completed_at=datetime.fromisoformat(row[8]) if row[8] else None,
        execution_time_ms=row[9]
    )


async def _execute_skill_sync(handler_path: str, config: Dict, input_data: Dict) -> Dict:
    """Execute a skill synchronously."""
    import importlib
    
    try:
        module_path, function_name = handler_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        handler = getattr(module, function_name)
        return await handler(input_data, config)
    except Exception as e:
        raise Exception(f"Failed to execute skill: {e}")


async def 
_execu
te_skill_async(skill_id: int, execution_id: str, handler_path: str, config: Dict, input_data: Dict):
    """Execute a skill asynchronously."""
    import importlib
    
    try:
        started_at = datetime.now(timezone.utc)
        db = await get_db_connection()
        
        module_path, function_name = handler_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        handler = getattr(module, function_name)
        
        result = await handler(input_data, config)
        completed_at = datetime.now(timezone.utc)
        execution_time = (completed_at - started_at).total_seconds() * 1000
        
        async with db.execute(
            """UPDATE skill_executions SET status = ?, output_data = ?, completed_at = ?, 
               execution_time_ms = ? WHERE execution_id = ?""",
            (SkillStatus.COMPLETED.value, json.dumps(result), completed_at.isoformat(), execution_time, execution_id)
        ):
            pass
        await db.commit()
        
    except Exception as e:
        async with db.execute(
            """UPDATE skill_executions SET status = ?, error = ?, completed_at = ? 
               WHERE execution_id = ?""",
            (SkillStatus.FAILED.value, str(e), datetime.now(timezone.utc).isoformat(), execution_id)
        ):
            pass
        await db.commit()


