"""
NFM-X Auto-Compression Scheduler
Background job for automatic memory compression.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from enum import Enum

from backend.app.config import NFM_COMPRESSION_ENABLED, NFM_COMPRESSION_INTERVAL

logger = logging.getLogger(__name__)


class CompressionInterval(Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


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
        now = datetime.utcnow()
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
        return datetime.utcnow() >= self.next_run


class CompressionScheduler:
    def __init__(self):
        self.jobs = {}
        self.running = False
    
    async def initialize(self):
        if NFM_COMPRESSION_ENABLED:
            interval_str = NFM_COMPRESSION_INTERVAL.lower()
            try:
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
        start_time = datetime.utcnow()
        compressed_count = 0
        job.last_run = datetime.utcnow()
        job.next_run = job.calculate_next_run()
        return {
            'job_id': job.job_id,
            'status': 'completed',
            'compressed_count': compressed_count,
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


compression_scheduler = CompressionScheduler()


async def initialize_compression_scheduler():
    await compression_scheduler.initialize()
    asyncio.create_task(compression_scheduler.start())
    return compression_scheduler
