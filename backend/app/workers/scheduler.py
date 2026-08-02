"""
NFM-X Background Job Scheduler
"""
import asyncio
from typing import Callable, Any, Dict, List, Optional
import logging
from datetime import datetime, timezone, timedelta
import uuid

logger = logging.getLogger(__name__)


class ScheduledJob:
    def __init__(
        self,
        name: str,
        func: Callable,
        interval_seconds: float,
        args: tuple = (),
        kwargs: dict = None
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.func = func
        self.interval_seconds = interval_seconds
        self.args = args
        self.kwargs = kwargs or {}
        self.last_run = None
        self.next_run = datetime.now(timezone.utc)
        self.enabled = True


class Scheduler:
    def __init__(self):
        self._jobs: Dict[str, ScheduledJob] = {}
        self._running = False
        self._loop = None
        self._shutdown = False
    
    async def start(self):
        if self._running:
            return
        
        self._running = True
        self._shutdown = False
        logger.info("Background scheduler started")
        
        async def run_jobs():
            while not self._shutdown:
                now = datetime.now(timezone.utc)
                for job_name, job in self._jobs.items():
                    if job.enabled and job.next_run <= now:
                        try:
                            logger.debug(f"Running job: {job.name}")
                            if asyncio.iscoroutinefunction(job.func):
                                await job.func(*job.args, **job.kwargs)
                            else:
                                job.func(*job.args, **job.kwargs)
                            job.last_run = now
                            job.next_run = now + timedelta(seconds=job.interval_seconds)
                            logger.debug(f"Job completed: {job.name}")
                        except Exception as e:
                            logger.error(f"Job failed: {job.name}: {e}")
                
                await asyncio.sleep(1)
        
        self._loop = asyncio.create_task(run_jobs())
    
    async def stop(self):
        self._shutdown = True
        if self._loop:
            self._loop.cancel()
            try:
                await self._loop
            except asyncio.CancelledError:
                pass
        self._running = False
        logger.info("Background scheduler stopped")
    
    def add_job(
        self,
        func: Callable,
        name: str,
        seconds: Optional[float] = None,
        minutes: Optional[float] = None,
        hours: Optional[float] = None,
        days: Optional[float] = None,
        args: tuple = (),
        kwargs: dict = None
    ):
        interval = 0
        if seconds:
            interval += seconds
        if minutes:
            interval += minutes * 60
        if hours:
            interval += hours * 3600
        if days:
            interval += days * 86400
        
        if interval <= 0:
            interval = 3600  # Default to 1 hour
        
        job = ScheduledJob(
            name=name,
            func=func,
            interval_seconds=interval,
            args=args,
            kwargs=kwargs or {}
        )
        self._jobs[name] = job
        logger.info(f"Added job: {name} (interval: {interval}s)")
        return job
    
    def remove_job(self, name: str) -> bool:
        if name in self._jobs:
            del self._jobs[name]
            logger.info(f"Removed job: {name}")
            return True
        return False
    
    def list_jobs(self) -> List[dict]:
        return [
            {
                "name": job.name,
                "id": job.id,
                "enabled": job.enabled,
                "interval_seconds": job.interval_seconds,
                "last_run": job.last_run,
                "next_run": job.next_run
            }
            for job in self._jobs.values()
        ]


scheduler = Scheduler()


def add_scheduled_job(func: Callable, name: str, **kwargs):
    scheduler.add_job(func, name, **kwargs)