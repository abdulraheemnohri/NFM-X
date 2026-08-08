"""
NFM-X Pattern Search & Management API
Search memories using regex patterns and manage saved search patterns.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from backend.app.database import get_db_connection

router = APIRouter(prefix="", tags=["patterns"])


class PatternCreate(BaseModel):
    name: str
    pattern: str
    description: Optional[str] = None
    case_sensitive: bool = False
    enabled: bool = True
    tags: List[str] = Field(default_factory=list)


class PatternUpdate(BaseModel):
    name: Optional[str] = None
    pattern: Optional[str] = None
    description: Optional[str] = None
    case_sensitive: Optional[bool] = None
    enabled: Optional[bool] = None
    tags: Optional[List[str]] = None


class PatternResponse(PatternCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime] = None
    usage_count: int = 0


class PatternSearchRequest(BaseModel):
    pattern: str
    case_sensitive: bool = False
    limit: int = 100
    offset: int = 0
    include_metadata: bool = False


class PatternSearchResult(BaseModel):
    memory_id: int
    content: str
    matched_text: str
    match_position: int
    metadata: Optional[Dict[str, Any]] = None


class PatternMatch(BaseModel):
    memory_id: int
    matched_text: str
    positions: List[int]


@router.get("/", response_model=List[PatternResponse])
async def list_patterns(
    enabled: Optional[bool] = None,
    tag: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """List all saved search patterns."""
    db = await get_db_connection()
    query = "SELECT * FROM search_patterns"
    params = []
    
    conditions = []
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
    
    patterns = []
    for row in rows:
        patterns.append(PatternResponse(
            id=row[0],
            name=row[1],
            pattern=row[2],
            description=row[3],
            case_sensitive=bool(row[4]),
            enabled=bool(row[5]),
            tags=row[6].split(",") if row[6] else [],
            created_at=datetime.fromisoformat(row[7]),
            updated_at=datetime.fromisoformat(row[8]),
            last_used_at=datetime.fromisoformat(row[9]) if row[9] else None,
            usage_count=row[10]
        ))
    
    return patterns


@router.get("/{pattern_id}", response_model=PatternResponse)
async def get_pattern(pattern_id: int):
    """Get a specific pattern by ID."""
    db = await get_db_connection()
    async with db.execute(
        "SELECT * FROM search_patterns WHERE id = ?", (pattern_id,)
    ) as cursor:
        row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Pattern not found")
    
    return PatternResponse(
        id=row[0],
        name=row[1],
        pattern=row[2],
        description=row[3],
        case_sensitive=bool(row[4]),
        enabled=bool(row[5]),
        tags=row[6].split(",") if row[6] else [],
        created_at=datetime.fromisoformat(row[7]),
        updated_at=datetime.fromisoformat(row[8]),
        last_used_at=datetime.fromisoformat(row[9]) if row[9] else None,
        usage_count=row[10]
    )


@router.post("/", response_model=PatternResponse, status_code=201)
async def create_pattern(pattern: PatternCreate):
    """Create a new search pattern."""
    db = await get_db_connection()
    
    async with db.execute(
        """INSERT INTO search_patterns (name, pattern, description, case_sensitive, enabled, tags)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            pattern.name,
            pattern.pattern,
            pattern.description,
            pattern.case_sensitive,
            pattern.enabled,
            ",".join(pattern.tags)
        )
    ) as cursor:
        pattern_id = cursor.lastrowid
    
    await db.commit()
    
    return PatternResponse(
        id=pattern_id,
        **pattern.dict(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        usage_count=0
    )


@router.put("/{pattern_id}", response_model=PatternResponse)
async def update_pattern(pattern_id: int, pattern: PatternUpdate):
    """Update an existing pattern."""
    db = await get_db_connection()
    
    async with db.execute(
        "SELECT * FROM search_patterns WHERE id = ?", (pattern_id,)
    ) as cursor:
        row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Pattern not found")
    
    updates = []
    params = []
    
    if pattern.name is not None:
        updates.append("name = ?")
        params.append(pattern.name)
    if pattern.pattern is not None:
        updates.append("pattern = ?")
        params.append(pattern.pattern)
    if pattern.description is not None:
        updates.append("description = ?")
        params.append(pattern.description)
    if pattern.case_sensitive is not None:
        updates.append("case_sensitive = ?")
        params.append(pattern.case_sensitive)
    if pattern.enabled is not None:
        updates.append("enabled = ?")
        params.append(pattern.enabled)
    if pattern.tags is not None:
        updates.append("tags = ?")
        params.append(",".join(pattern.tags))
    
    if updates:
        updates.append("updated_at = ?")
        params.append(datetime.now(timezone.utc).isoformat())
        params.append(pattern_id)
        
        query = "UPDATE search_patterns SET " + ", ".join(updates) + " WHERE id = ?"
        async with db.execute(query, params):
            pass
        await db.commit()
    
    async with db.execute(
        "SELECT * FROM search_patterns WHERE id = ?", (pattern_id,)
    ) as cursor:
        row = await cursor.fetchone()
    
    return PatternResponse(
        id=row[0],
        name=row[1],
        pattern=row[2],
        description=row[3],
        case_sensitive=bool(row[4]),
        enabled=bool(row[5]),
        tags=row[6].split(",") if row[6] else [],
        created_at=datetime.fromisoformat(row[7]),
        updated_at=datetime.fromisoformat(row[8]),
        last_used_at=datetime.fromisoformat(row[9]) if row[9] else None,
        usage_count=row[10]
    )


@router.delete("/{pattern_id}", status_code=204)
async def delete_pattern(pattern_id: int):
    """Delete a pattern."""
    db = await get_db_connection()
    
    async with db.execute(
        "DELETE FROM search_patterns WHERE id = ?", (pattern_id,)
    ) as cursor:
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Pattern not found")
    
    await db.commit()


@router.post("/search", response_model=List[PatternSearchResult])
async def search_with_pattern(request: PatternSearchRequest):
    """Search memories using a regex pattern."""
    import re
    
    db = await get_db_connection()
    
    flags = 0 if request.case_sensitive else re.IGNORECASE
    
    try:
        compiled_pattern = re.compile(request.pattern, flags)
    except re.error as e:
        raise HTTPException(status_code=400, detail=f"Invalid regex pattern: {e}")
    
    async with db.execute("SELECT id, content, metadata FROM memories") as cursor:
        rows = await cursor.fetchall()
    
    results = []
    for row in rows:
        memory_id = row[0]
        content = row[1]
        metadata = row[2]
        
        matches = list(compiled_pattern.finditer(content))
        if matches:
            for match in matches:
                results.append(PatternSearchResult(
                    memory_id=memory_id,
                    content=content,
                    matched_text=match.group(0),
                    match_position=match.start(),
                    metadata=metadata if request.include_metadata else None
                ))
        
        if len(results) >= request.limit:
            break
    
    return results[:request.limit]


@router.post("/{pattern_id}/search", response_model=List[PatternSearchResult])
async def search_with_saved_pattern(
    pattern_id: int,
    limit: int = 100,
    offset: int = 0,
    include_metadata: bool = False
):
    """Search memories using a saved pattern."""
    db = await get_db_connection()
    
    async with db.execute(
        "SELECT pattern, case_sensitive FROM search_patterns WHERE id = ?", (pattern_id,)
    ) as cursor:
        row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Pattern not found")
    
    pattern_data = row[0]
    case_sensitive = bool(row[1])
    
    async with db.execute(
        "UPDATE search_patterns SET last_used_at = ?, usage_count = usage_count + 1 WHERE id = ?",
        (datetime.now(timezone.utc).isoformat(), pattern_id)
    ):
        pass
    await db.commit()
    
    request = PatternSearchRequest(
        pattern=pattern_data,
        case_sensitive=case_sensitive,
        limit=limit,
        offset=offset,
        include_metadata=include_metadata
    )
    
    return await search_with_pattern(request)


@router.post("/validate", response_model=Dict[str, Any])
async def validate_pattern(pattern: str):
    """Validate a regex pattern."""
    import re
    
    try:
        re.compile(pattern)
        return {"valid": True, "message": "Pattern is valid"}
    except re.error as e:
        return {"valid": False, "message": str(e)}
