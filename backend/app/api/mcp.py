"""
NFM-X MCP Authentication API
API key management and authentication for MCP (Model Context Protocol) integration.
"""

from fastapi import APIRouter, HTTPException, Depends, Header, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import secrets
import hashlib

from backend.app.database import get_db_connection
from backend.app.config import NFM_MCP_ENABLED

router = APIRouter(prefix="/api/v1/mcp", tags=["mcp"])

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class APIKeyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str] = Field(default_factory=lambda: ["read", "write"])
    expires_at: Optional[datetime] = None
    rate_limit: Optional[int] = None


class APIKeyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    enabled: Optional[bool] = None
    expires_at: Optional[datetime] = None
    rate_limit: Optional[int] = None


class APIKeyResponse(BaseModel):
    id: int
    key_id: str
    name: str
    description: Optional[str] = None
    permissions: List[str]
    enabled: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    usage_count: int = 0
    rate_limit: Optional[int] = None


class APIKeyWithSecret(APIKeyResponse):
    secret: str


class AuthenticateRequest(BaseModel):
    api_key: str


class AuthenticateResponse(BaseModel):
    authenticated: bool
    key_id: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
    expires_at: Optional[datetime] = None


class RateLimitInfo(BaseModel):
    remaining: int
    limit: int
    reset_at: datetime


class MCPConfig(BaseModel):
    enabled: bool
    require_authentication: bool
    default_permissions: List[str]
    rate_limit_default: int


@router.get("/config", response_model=MCPConfig)
async def get_mcp_config():
    """Get MCP configuration."""
    return MCPConfig(
        enabled=NFM_MCP_ENABLED,
        require_authentication=True,
        default_permissions=["read", "write"],
        rate_limit_default=100
    )


@router.post("/keys", response_model=APIKeyWithSecret, status_code=status.HTTP_201_CREATED)
async def create_api_key(key_data: APIKeyCreate):
    """Create a new API key."""
    if not NFM_MCP_ENABLED:
        raise HTTPException(status_code=403, detail="MCP is disabled")
    
    db = await get_db_connection()
    
    key_id = secrets.token_urlsafe(16)
    secret = secrets.token_urlsafe(32)
    hashed_secret = hashlib.sha256(secret.encode()).hexdigest()
    
    async with db.execute(
        """INSERT INTO api_keys (key_id, name, description, hashed_secret, permissions, enabled, expires_at, rate_limit)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            key_id,
            key_data.name,
            key_data.description,
            hashed_secret,
            ",".join(key_data.permissions),
            True,
            key_data.expires_at.isoformat() if key_data.expires_at else None,
            key_data.rate_limit
        )
    ) as cursor:
        key_id_row = cursor.lastrowid
    
    await db.commit()
    
    return APIKeyWithSecret(
        id=key_id_row,
        key_id=key_id,
        name=key_data.name,
        description=key_data.description,
        permissions=key_data.permissions,
        enabled=True,
        created_at=datetime.now(timezone.utc),
        expires_at=key_data.expires_at,
        usage_count=0,
        rate_limit=key_data.rate_limit,
        secret=secret
    )


@router.get("/keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    enabled: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0
):
    """List all API keys (without secrets)."""
    if not NFM_MCP_ENABLED:
        raise HTTPException(status_code=403, detail="MCP is disabled")
    
    db = await get_db_connection()
    query = "SELECT * FROM api_keys"
    params = []
    
    if enabled is not None:
        query += " WHERE enabled = ?"
        params.append(enabled)
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    async with db.execute(query, params) as cursor:
        rows = await cursor.fetchall()
    
    keys = []
    for row in rows:
        keys.append(APIKeyResponse(
            id=row[0],
            key_id=row[1],
            name=row[2],
            description=row[3],
            permissions=row[5].split(",") if row[5] else [],
            enabled=bool(row[6]),
            created_at=datetime.fromisoformat(row[7]) if isinstance(row[7], str) else row[7],
            expires_at=datetime.fromisoformat(row[8]) if row[8] and isinstance(row[8], str) else row[8],
            last_used_at=datetime.fromisoformat(row[9]) if row[9] and isinstance(row[9], str) else row[9],
            usage_count=row[10],
            rate_limit=row[11]
        ))
    
    return keys


@router.get("/keys/{key_id}", response_model=APIKeyResponse)
async def get_api_key(key_id: str):
    """Get a specific API key by ID."""
    if not NFM_MCP_ENABLED:
        raise HTTPException(status_code=403, detail="MCP is disabled")
    
    db = await get_db_connection()
    async with db.execute(
        "SELECT * FROM api_keys WHERE key_id = ?", (key_id,)
    ) as cursor:
        row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="API key not found")
    
    return APIKeyResponse(
        id=row[0],
        key_id=row[1],
        name=row[2],
        description=row[3],
        permissions=row[5].split(",") if row[5] else [],
        enabled=bool(row[6]),
        created_at=datetime.fromisoformat(row[7]) if isinstance(row[7], str) else row[7],
        expires_at=datetime.fromisoformat(row[8]) if row[8] and isinstance(row[8], str) else row[8],
        last_used_at=datetime.fromisoformat(row[9]) if row[9] and isinstance(row[9], str) else row[9],
        usage_count=row[10],
        rate_limit=row[11]
    )


@router.put("/keys/{key_id}", response_model=APIKeyResponse)
async def update_api_key(key_id: str, key_data: APIKeyUpdate):
    """Update an API key."""
    if not NFM_MCP_ENABLED:
        raise HTTPException(status_code=403, detail="MCP is disabled")
    
    db = await get_db_connection()
    
    async with db.execute(
        "SELECT * FROM api_keys WHERE key_id = ?", (key_id,)
    ) as cursor:
        row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="API key not found")
    
    updates = []
    params = []
    
    if key_data.name is not None:
        updates.append("name = ?")
        params.append(key_data.name)
    if key_data.description is not None:
        updates.append("description = ?")
        params.append(key_data.description)
    if key_data.permissions is not None:
        updates.append("permissions = ?")
        params.append(",".join(key_data.permissions))
    if key_data.enabled is not None:
        updates.append("enabled = ?")
        params.append(key_data.enabled)
    if key_data.expires_at is not None:
        updates.append("expires_at = ?")
        params.append(key_data.expires_at.isoformat())
    if key_data.rate_limit is not None:
        updates.append("rate_limit = ?")
        params.append(key_data.rate_limit)
    
    if updates:
        params.append(key_id)
        query = "UPDATE api_keys SET " + ", ".join(updates) + " WHERE key_id = ?"
        async with db.execute(query, params):
            pass
        await db.commit()
    
    async with db.execute(
        "SELECT * FROM api_keys WHERE key_id = ?", (key_id,)
    ) as cursor:
        row = await cursor.fetchone()
    
    return APIKeyResponse(
        id=row[0],
        key_id=row[1],
        name=row[2],
        description=row[3],
        permissions=row[5].split(",") if row[5] else [],
        enabled=bool(row[6]),
        created_at=datetime.fromisoformat(row[7]) if isinstance(row[7], str) else row[7],
        expires_at=datetime.fromisoformat(row[8]) if row[8] and isinstance(row[8], str) else row[8],
        last_used_at=datetime.fromisoformat(row[9]) if row[9] and isinstance(row[9], str) else row[9],
        usage_count=row[10],
        rate_limit=row[11]
    )


@router.delete("/keys/{key_id}", status_code=204)
async def delete_api_key(key_id: str):
    """Revoke an API key."""
    if not NFM_MCP_ENABLED:
        raise HTTPException(status_code=403, detail="MCP is disabled")
    
    db = await get_db_connection()
    
    async with db.execute(
        "DELETE FROM api_keys WHERE key_id = ?", (key_id,)
    ) as cursor:
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="API key not found")
    
    await db.commit()


@router.post("/authenticate", response_model=AuthenticateResponse)
async def authenticate(request: AuthenticateRequest):
    """Authenticate using an API key."""
    if not NFM_MCP_ENABLED:
        raise HTTPException(status_code=403, detail="MCP is disabled")
    
    db = await get_db_connection()
    async with db.execute(
        "SELECT key_id, permissions, enabled, expires_at, hashed_secret FROM api_keys"
    ) as cursor:
        rows = await cursor.fetchall()
    
    current_time = datetime.now(timezone.utc)
    
    for row in rows:
        key_id, permissions, enabled, expires_at, hashed_secret = row
        if not enabled:
            continue
        if expires_at:
            expires_dt = datetime.fromisoformat(expires_at) if isinstance(expires_at, str) else expires_at
            if expires_dt < current_time:
                continue
        
        input_hashed = hashlib.sha256(request.api_key.encode()).hexdigest()
        if secrets.compare_digest(input_hashed, hashed_secret):
            async with db.execute(
                "UPDATE api_keys SET last_used_at = ?, usage_count = usage_count + 1 WHERE key_id = ?",
                (current_time.isoformat(), key_id)
            ):
                pass
            await db.commit()
            
            expires_result = datetime.fromisoformat(expires_at) if expires_at and isinstance(expires_at, str) else expires_at
            return AuthenticateResponse(
                authenticated=True,
                key_id=key_id,
                permissions=permissions.split(",") if permissions else [],
                expires_at=expires_result
            )
    
    raise HTTPException(status_code=401, detail="Invalid API key")


@router.get("/rate-limit", response_model=RateLimitInfo)
async def get_rate_limit_info(api_key: str = Depends(api_key_header)):
    """Get rate limit information for the current API key."""
    if not NFM_MCP_ENABLED:
        raise HTTPException(status_code=403, detail="MCP is disabled")
    
    db = await get_db_connection()
    
    input_hashed = hashlib.sha256(api_key.encode()).hexdigest()
    
    async with db.execute(
        "SELECT rate_limit, last_used_at, usage_count FROM api_keys WHERE hashed_secret = ?",
        (input_hashed,)
    ) as cursor:
        row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    rate_limit = row[0] or 100
    last_used = datetime.fromisoformat(row[1]) if row[1] and isinstance(row[1], str) else row[1]
    if last_used is None:
        last_used = current_time
    usage_count = row[2] or 0
    
    reset_at = last_used + timedelta(minutes=1)
    remaining = rate_limit - (usage_count % rate_limit)
    
    return RateLimitInfo(
        remaining=remaining,
        limit=rate_limit,
        reset_at=reset_at
    )


async def verify_api_key(api_key: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Dependency to verify API key and return key info."""
    if not NFM_MCP_ENABLED:
        return None
    
    if not api_key:
        return None
    
    db = await get_db_connection()
    current_time = datetime.now(timezone.utc)
    
    async with db.execute(
        "SELECT key_id, permissions, enabled, expires_at FROM api_keys"
    ) as cursor:
        rows = await cursor.fetchall()
    
    for row in rows:
        key_id, permissions, enabled, expires_at = row
        if not enabled:
            continue
        if expires_at:
            expires_dt = datetime.fromisoformat(expires_at) if isinstance(expires_at, str) else expires_at
            if expires_dt < current_time:
                continue
        
        input_hashed = hashlib.sha256(api_key.encode()).hexdigest()
        async with db.execute(
            "SELECT hashed_secret FROM api_keys WHERE key_id = ?", (key_id,)
        ) as cursor2:
            secret_row = await cursor2.fetchone()
        
        if secret_row and secrets.compare_digest(input_hashed, secret_row[0]):
            async with db.execute(
                "UPDATE api_keys SET last_used_at = ?, usage_count = usage_count + 1 WHERE key_id = ?",
                (current_time.isoformat(), key_id)
            ):
                pass
            await db.commit()
            
            expires_result = datetime.fromisoformat(expires_at) if expires_at and isinstance(expires_at, str) else expires_at
            return {
                "key_id": key_id,
                "permissions": permissions.split(",") if permissions else [],
                "expires_at": expires_result
            }
    
    return None


async def check_permission(required_permission: str, api_key_info: Optional[Dict] = Depends(verify_api_key)):
    """Dependency to check if API key has required permission."""
    if not NFM_MCP_ENABLED:
        return
    
    if not api_key_info:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if required_permission not in api_key_info.get("permissions", []):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    if api_key_info.get("expires_at") and api_key_info["expires_at"] < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="API key expired")
    
    return api_key_info