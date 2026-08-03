"""
NFM-X V4 Detailed Health Check
Comprehensive health monitoring for all subsystems
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import logging
import os
import sqlite3

from backend.app.config import get_config

logger = logging.getLogger(__name__)


@dataclass
class SubsystemStatus:
    """Status of a single subsystem"""
    name: str
    healthy: bool
    latency_ms: Optional[float] = None
    last_check: Optional[datetime] = None
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "name": self.name,
            "healthy": self.healthy,
        }
        if self.latency_ms is not None:
            result["latency_ms"] = round(self.latency_ms, 2)
        if self.last_check:
            result["last_check"] = self.last_check.isoformat()
        if self.error:
            result["error"] = self.error
        if self.details:
            result["details"] = self.details
        return result


@dataclass
class HealthCheckResult:
    """Complete health check result"""
    status: str  # "healthy", "degraded", "unhealthy"
    uptime_seconds: float
    version: str
    environment: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    subsystems: List[SubsystemStatus] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "uptime_seconds": round(self.uptime_seconds, 2),
            "version": self.version,
            "environment": self.environment,
            "subsystems": [s.to_dict() for s in self.subsystems]
        }
    
    @property
    def is_healthy(self) -> bool:
        return self.status == "healthy"
    
    @property
    def is_degraded(self) -> bool:
        return self.status == "degraded"
    
    @property
    def is_unhealthy(self) -> bool:
        return self.status == "unhealthy"


class HealthChecker:
    """Performs comprehensive health checks"""
    
    def __init__(self):
        self._start_time = datetime.utcnow()
        self._last_check: Optional[datetime] = None
    
    async def check_all(self, timeout_seconds: int = 5) -> HealthCheckResult:
        """
        Check all subsystems
        """
        config = get_config()
        subsystems = []
        
        # Check database
        if config.health_check.check_db:
            db_status = await self._check_database(timeout_seconds)
            subsystems.append(db_status)
        
        # Check vector store
        if config.health_check.check_vector_store:
            vector_status = await self._check_vector_store(timeout_seconds)
            subsystems.append(vector_status)
        
        # Check OCR
        if config.health_check.check_ocr:
            ocr_status = await self._check_ocr(timeout_seconds)
            subsystems.append(ocr_status)
        
        # Check storage
        if config.health_check.check_storage:
            storage_status = await self._check_storage(timeout_seconds)
            subsystems.append(storage_status)
        
        # Calculate overall status
        status = self._calculate_overall_status(subsystems)
        uptime = (datetime.utcnow() - self._start_time).total_seconds()
        
        result = HealthCheckResult(
            status=status,
            uptime_seconds=uptime,
            subsystems=subsystems,
            version=config.version,
            environment=config.environment
        )
        
        self._last_check = datetime.utcnow()
        return result
    
    async def _check_database(self, timeout: int) -> SubsystemStatus:
        """Check database connectivity"""
        import asyncio
        config = get_config()
        
        try:
            start = datetime.utcnow()
            
            # Try to connect to database
            if config.database_url.startswith("sqlite"):
                # For SQLite, just check if file exists or can be created
                db_path = config.database_url.replace("sqlite+aiosqlite:///", "")
                db_path = db_path.replace("sqlite:///", "")
                if db_path.startswith("./"):
                    db_path = db_path[2:]
                
                # Check if directory exists
                db_dir = os.path.dirname(db_path)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)
                
                # Try to connect
                loop = asyncio.get_event_loop()
                await asyncio.wait_for(
                    self._test_sqlite_connection(config.database_url),
                    timeout=timeout
                )
            else:
                # For other databases, try a simple query
                await asyncio.wait_for(
                    self._test_async_db_connection(config.database_url),
                    timeout=timeout
                )
            
            latency = (datetime.utcnow() - start).total_seconds() * 1000
            return SubsystemStatus(
                name="database",
                healthy=True,
                latency_ms=latency,
                last_check=datetime.utcnow(),
                details={"url": config.database_url}
            )
        except Exception as e:
            return SubsystemStatus(
                name="database",
                healthy=False,
                error=str(e),
                last_check=datetime.utcnow()
            )
    
    async def _test_sqlite_connection(self, url: str):
        """Test SQLite connection"""
        import aiosqlite
        async with aiosqlite.connect(url.replace("sqlite+aiosqlite:///", "/")) as db:
            await db.execute("SELECT 1")
            await db.commit()
    
    async def _test_async_db_connection(self, url: str):
        """Test async database connection"""
        import sqlalchemy
        from sqlalchemy.ext.asyncio import create_async_engine
        
        engine = create_async_engine(url)
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
            await conn.commit()
        await engine.dispose()
    
    async def _check_vector_store(self, timeout: int) -> SubsystemStatus:
        """Check vector store connectivity"""
        config = get_config()
        
        try:
            start = datetime.utcnow()
            
            # Check if vector store directory exists
            if config.vector_store_dir and not os.path.exists(config.vector_store_dir):
                os.makedirs(config.vector_store_dir, exist_ok=True)
            
            # Try to load or create a simple FAISS index
            try:
                import faiss
                index = faiss.IndexFlatL2(10)  # Dummy index
                del index
            except ImportError:
                return SubsystemStatus(
                    name="vector_store",
                    healthy=False,
                    error="FAISS not installed",
                    last_check=datetime.utcnow()
                )
            
            latency = (datetime.utcnow() - start).total_seconds() * 1000
            return SubsystemStatus(
                name="vector_store",
                healthy=True,
                latency_ms=latency,
                last_check=datetime.utcnow(),
                details={"directory": config.vector_store_dir}
            )
        except Exception as e:
            return SubsystemStatus(
                name="vector_store",
                healthy=False,
                error=str(e),
                last_check=datetime.utcnow()
            )
    
    async def _check_ocr(self, timeout: int) -> SubsystemStatus:
        """Check OCR engine"""
        config = get_config()
        
        try:
            start = datetime.utcnow()
            
            if not config.ocr.enabled:
                return SubsystemStatus(
                    name="ocr",
                    healthy=True,
                    latency_ms=0,
                    last_check=datetime.utcnow(),
                    details={"enabled": False, "engine": config.ocr.engine}
                )
            
            # Test the configured OCR engine
            if config.ocr.engine == "easyocr":
                try:
                    import easyocr
                    reader = easyocr.Reader([config.ocr.languages[0]])
                    del reader
                except ImportError:
                    return SubsystemStatus(
                        name="ocr",
                        healthy=False,
                        error="EasyOCR not installed",
                        last_check=datetime.utcnow()
                    )
            elif config.ocr.engine == "tesseract":
                try:
                    import pytesseract
                    if config.ocr.tesseract_path:
                        pytesseract.pytesseract.tesseract_cmd = config.ocr.tesseract_path
                except ImportError:
                    return SubsystemStatus(
                        name="ocr",
                        healthy=False,
                        error="Tesseract not installed",
                        last_check=datetime.utcnow()
                    )
            elif config.ocr.engine in ["azure", "google"]:
                if not config.ocr.cloud_api_key:
                    return SubsystemStatus(
                        name="ocr",
                        healthy=False,
                        error="Cloud API key not configured",
                        last_check=datetime.utcnow()
                    )
            
            latency = (datetime.utcnow() - start).total_seconds() * 1000
            return SubsystemStatus(
                name="ocr",
                healthy=True,
                latency_ms=latency,
                last_check=datetime.utcnow(),
                details={
                    "engine": config.ocr.engine,
                    "languages": config.ocr.languages,
                    "table_extraction": config.ocr.table_extraction
                }
            )
        except Exception as e:
            return SubsystemStatus(
                name="ocr",
                healthy=False,
                error=str(e),
                last_check=datetime.utcnow()
            )
    
    async def _check_storage(self, timeout: int) -> SubsystemStatus:
        """Check storage directory"""
        config = get_config()
        
        try:
            start = datetime.utcnow()
            
            # Check if storage directory exists
            if config.storage_dir and not os.path.exists(config.storage_dir):
                os.makedirs(config.storage_dir, exist_ok=True)
            
            # Check disk space
            if config.storage_dir:
                stat = os.statvfs(config.storage_dir)
                free_space_mb = (stat.f_frsize * stat.f_bavail) / (1024 * 1024)
                total_space_mb = (stat.f_frsize * stat.f_blocks) / (1024 * 1024)
                used_percent = ((stat.f_blocks - stat.f_bavail) / stat.f_blocks) * 100
            else:
                free_space_mb = 0
                total_space_mb = 0
                used_percent = 0
            
            latency = (datetime.utcnow() - start).total_seconds() * 1000
            return SubsystemStatus(
                name="storage",
                healthy=used_percent < 90,  # Healthy if less than 90% used
                latency_ms=latency,
                last_check=datetime.utcnow(),
                details={
                    "directory": config.storage_dir,
                    "free_space_mb": round(free_space_mb, 2),
                    "total_space_mb": round(total_space_mb, 2),
                    "used_percent": round(used_percent, 2)
                }
            )
        except Exception as e:
            return SubsystemStatus(
                name="storage",
                healthy=False,
                error=str(e),
                last_check=datetime.utcnow()
            )
    
    def _calculate_overall_status(self, subsystems: List[SubsystemStatus]) -> str:
        """Calculate overall health status"""
        if not subsystems:
            return "healthy"
        
        unhealthy_count = sum(1 for s in subsystems if not s.healthy)
        total_count = len(subsystems)
        
        if unhealthy_count == 0:
            return "healthy"
        elif unhealthy_count < total_count:
            return "degraded"
        else:
            return "unhealthy"
    
    def get_last_check_time(self) -> Optional[datetime]:
        """Get the time of the last health check"""
        return self._last_check
    
    def get_uptime(self) -> float:
        """Get uptime in seconds"""
        return (datetime.utcnow() - self._start_time).total_seconds()