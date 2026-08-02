"""NFM-X V4 Health Check API - Detailed health monitoring endpoints"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime

from backend.app.health import HealthChecker, HealthCheckResult
from backend.app.config import get_config

router = APIRouter(prefix="/health", tags=["Health Check"])


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    uptime_seconds: float
    version: str
    environment: str
    subsystems: List[Dict[str, Any]]


class SimpleHealthResponse(BaseModel):
    status: str


health_checker = HealthChecker()


@router.get("/", response_model=SimpleHealthResponse)
async def simple_health():
    return SimpleHealthResponse(status="healthy")


@router.get("/detailed", response_model=HealthResponse)
async def detailed_health():
    config = get_config()
    result = await health_checker.check_all(config.health_check.timeout_seconds)
    
    return HealthResponse(
        status=result.status,
        timestamp=result.timestamp.isoformat(),
        uptime_seconds=result.uptime_seconds,
        version=result.version,
        environment=result.environment,
        subsystems=[s.to_dict() for s in result.subsystems]
    )


@router.get("/subsystems", response_model=List[Dict[str, Any]])
async def check_subsystems():
    config = get_config()
    result = await health_checker.check_all(config.health_check.timeout_seconds)
    return [s.to_dict() for s in result.subsystems]


@router.get("/subsystems/{subsystem_name}", response_model=Dict[str, Any])
async def check_subsystem(subsystem_name: str):
    config = get_config()
    result = await health_checker.check_all(config.health_check.timeout_seconds)
    
    for subsystem in result.subsystems:
        if subsystem.name == subsystem_name:
            return subsystem.to_dict()
    
    return {"error": f"Subsystem {subsystem_name} not found or not enabled"}


@router.get("/uptime")
async def get_uptime():
    uptime = health_checker.get_uptime()
    return {"uptime_seconds": uptime, "uptime_human": format_uptime(uptime)}


@router.get("/last-check")
async def get_last_check():
    last_check = health_checker.get_last_check_time()
    if last_check:
        return {"last_check": last_check.isoformat()}
    return {"last_check": None, "message": "No health check performed yet"}


@router.get("/status")
async def get_status():
    config = get_config()
    result = await health_checker.check_all(config.health_check.timeout_seconds)
    return {"status": result.status}


def format_uptime(seconds: float) -> str:
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return " ".join(parts)