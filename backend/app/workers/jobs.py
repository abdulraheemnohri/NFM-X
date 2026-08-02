"""
NFM-X Background Jobs
"""
from typing import List
import logging
from ..memory.capture import capture

logger = logging.getLogger(__name__)

async def run_all_consolidation_jobs():
    logger.info("Running consolidation jobs")
    # Consolidation logic would go here
    pass

def add_scheduled_job(func, name: str, **kwargs):
    from .scheduler import scheduler
    scheduler.add_job(func, name, **kwargs)