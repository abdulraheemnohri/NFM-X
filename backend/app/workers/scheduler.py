"""
NFM-X Background Job Scheduler
"""
import asyncio
from typing import Callable, Any, Dict, List
import logging

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._running = False
        self._loop = None
    
    async def start(self):
        if self._running:
            return
        self._running = True
        logger.info("Background scheduler started")
    
    async def stop(self):
        self._running = False
        logger.info("Background scheduler stopped")
    
    def add_job(self, func: Callable, name: str, **kwargs):
        self._jobs[name] = {"func": func, "kwargs": kwargs}
    
    async def run_job(self, name: str):
        if name in self._jobs:
            job = self._jobs[name]
            await job["func"](**job["kwargs"])

scheduler = Scheduler()