"""
NFM-X Background Jobs
"""
from typing import List
import logging
from datetime import datetime, timezone, timedelta

from ..memory.models import Memory, MemoryStatus
from ..storage.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def run_all_consolidation_jobs():
    """Run all consolidation jobs"""
    logger.info("Running consolidation jobs...")
    
    await consolidate_old_memories()
    await optimize_embeddings()
    await cleanup_temp_data()
    
    logger.info("Consolidation jobs completed")


async def consolidate_old_memories():
    """Consolidate memories that haven't been accessed in a while"""
    logger.info("Consolidating old memories...")
    
    async with AsyncSessionLocal() as session:
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        result = await session.execute(
            Memory.__table__.update()
            .where(Memory.access_count < 5)
            .where(Memory.updated_at < thirty_days_ago)
            .where(Memory.status == MemoryStatus.ACTIVE)
            .values(status=MemoryStatus.ARCHIVED, archived_at=datetime.now(timezone.utc))
        )
        
        logger.info(f"Archived {result.rowcount} old memories")
        await session.commit()


async def optimize_embeddings():
    """Optimize embedding storage"""
    logger.info("Optimizing embeddings...")
    try:
        from ..embeddings.vector_store import vector_store
        if vector_store.is_available:
            vector_store.rebuild_index()
            logger.info("Embeddings optimized")
    except Exception as e:
        logger.error(f"Failed to optimize embeddings: {e}")


async def cleanup_temp_data():
    """Clean up temporary data"""
    logger.info("Cleaning up temporary data...")
    pass