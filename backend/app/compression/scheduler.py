"""
NFM-X Auto-Compression Scheduler
Background job for automatic memory compression.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass, field

from backend.app.config import get_config, NFM_COMPRESSION_ENABLED, NFM_CORS_METHODS, NFM_CORS_HEADERS, NFM_COMPRESSION_INTERVAL, CompressionConfig
from backend.app.compression.engine import MemoryCompressionEngine
from backend.app.storage.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


class CompressionInterval(Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class CompressionRun:
    run_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    memories_compressed: int = 0
    memories_archived: int = 0
    memories_skipped: int = 0
    total_bytes_saved: int = 0
    status: str = "completed"
    error: Optional[str] = None


class CompressionJob:
    def __init__(self, job_id, interval, retention_days=365, batch_size=100, enabled=True):
        self.job_id = job_id
        self.interval = interval
        self.retention_days = retention_days
        self.batch_size = batch_size
        self.enabled = enabled
        self.last_run = None
        self.next_run = None
    
    def calculate_next_run(self):
        now = datetime.now(timezone.utc)
        if self.interval == CompressionInterval.HOURLY:
            return now + timedelta(hours=1)
        elif self.interval == CompressionInterval.DAILY:
            return now + timedelta(days=1)
        elif self.interval == CompressionInterval.WEEKLY:
            return now + timedelta(weeks=1)
        else:
            return now + timedelta(days=30)
    
    def is_due(self):
        if not self.enabled:
            return False
        if self.next_run is None:
            return True
        return datetime.now(timezone.utc) >= self.next_run


class CompressionScheduler:
    def __init__(self):
        self.jobs = {}
        self.running = False
        self._current_run: Optional[CompressionRun] = None
        self._runs: List[CompressionRun] = []
        self._engine = MemoryCompressionEngine()
    
    async def initialize(self):
        if NFM_COMPRESSION_ENABLED:
            interval_str = NFM_COMPRESSION_INTERVAL.lower()
            try:
                # Strip ending 'h', 'd' etc. if present
                if interval_str.endswith("h"):
                    interval = CompressionInterval.HOURLY
                elif interval_str.endswith("d"):
                    interval = CompressionInterval.DAILY
                else:
                    interval = CompressionInterval(interval_str)
            except ValueError:
                interval = CompressionInterval.DAILY
            default_job = CompressionJob(
                job_id="default",
                interval=interval,
                retention_days=365,
                batch_size=100,
                enabled=True
            )
            self.jobs["default"] = default_job
            logger.info("Initialized compression scheduler")
    
    async def run_job(self, job):
        start_time = datetime.now(timezone.utc)
        job.last_run = datetime.now(timezone.utc)
        job.next_run = job.calculate_next_run()

        # Run actual compression
        run = await self.run_compression()

        return {
            'job_id': job.job_id,
            'status': run.status if run else 'completed',
            'compressed_count': run.memories_compressed if run else 0,
            'next_run': job.next_run.isoformat()
        }
    
    async def run_due_jobs(self):
        results = []
        for job_id, job in self.jobs.items():
            if job.is_due():
                result = await self.run_job(job)
                results.append(result)
        return results
    
    async def start(self):
        if self.running:
            return
        self.running = True
        logger.info("Starting compression scheduler")
        while self.running:
            try:
                await self.run_due_jobs()
                await asyncio.sleep(60)
            except Exception as e:
                logger.error("Error in scheduler: " + str(e))
                await asyncio.sleep(300)
    
    async def stop(self):
        self.running = False
        logger.info("Stopped compression scheduler")

    def get_config(self) -> CompressionConfig:
        return get_config().compression

    def update_config(self, **kwargs) -> CompressionConfig:
        cfg = get_config().compression
        for k, v in kwargs.items():
            if hasattr(cfg, k):
                setattr(cfg, k, v)
        return cfg

    async def run_compression(self) -> Optional[CompressionRun]:
        if not get_config().compression.enabled:
            return None

        run_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc)
        self._current_run = CompressionRun(
            run_id=run_id,
            started_at=started_at,
            status="running"
        )
        self._runs.append(self._current_run)

        try:
            async with AsyncSessionLocal() as session:
                # Compress old memories via engine
                compressible = await self._engine.find_compressible_memories(session)
                memories_archived = len(compressible)
                for mem in compressible:
                    mem.status = "ARCHIVED"

                # Deduplicate near duplicates
                dedup_result = await self._engine.deduplicate_semantic(session)
                memories_compressed = dedup_result.get("duplicates_found", 0)

                await session.commit()

                self._current_run.status = "completed"
                self._current_run.memories_archived = memories_archived
                self._current_run.memories_compressed = memories_compressed
                self._current_run.completed_at = datetime.now(timezone.utc)
                self._current_run.total_bytes_saved = (memories_archived + memories_compressed) * 128
        except Exception as e:
            logger.error(f"Compression run failed: {e}")
            self._current_run.status = "failed"
            self._current_run.error = str(e)
            self._current_run.completed_at = datetime.now(timezone.utc)

        run = self._current_run
        self._current_run = None
        return run

    def get_run_history(self, limit: int = 100) -> List[CompressionRun]:
        return self._runs[-limit:]

    def get_current_run(self) -> Optional[CompressionRun]:
        return self._current_run


compression_scheduler = CompressionScheduler()


async def initialize_compression_scheduler():
    await compression_scheduler.initialize()
    asyncio.create_task(compression_scheduler.start())
    return compression_scheduler
