from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from ..storage.database import get_db_session
from ..memory.models import Memory, MemoryStatus, MemoryType
from ..memory.patterns import PatternDiscoveryEngine

logger = logging.getLogger(__name__)

async def run_consolidation_job():
    logger.info("Starting consolidation job...")
    # Since background jobs run outside request lifecycle, we get a session dynamically
    from ..storage.database import _async_session_maker
    if _async_session_maker is None:
        logger.warning("Database not initialized yet, skipping consolidation job.")
        return

    async with _async_session_maker() as session:
        try:
            pattern_engine = PatternDiscoveryEngine()
            patterns = await pattern_engine.discover_patterns(session)
            logger.info(f"Discovered {len(patterns)} patterns")
            await _recalculate_confidences(session)
            await _detect_stale_memories(session)
            await session.commit()
        except Exception as e:
            logger.error(f"Error in consolidation job: {e}")
            await session.rollback()
    logger.info("Consolidation job completed")

async def _recalculate_confidences(session: AsyncSession):
    stmt = select(Memory).where(Memory.status == MemoryStatus.ACTIVE)
    result = await session.execute(stmt)
    memories = result.scalars().all()
    now = datetime.now(timezone.utc)
    for mem in memories:
        if mem.created_at:
            age_days = (now - mem.created_at.replace(tzinfo=timezone.utc) if mem.created_at.tzinfo is None else now - mem.created_at).days
            if age_days > 90 and mem.confidence > 0.5:
                decay = min(0.1, age_days / 1000)
                mem.confidence = max(0.3, mem.confidence - decay)

async def _detect_stale_memories(session: AsyncSession):
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    stmt = select(Memory).where(Memory.type == MemoryType.WORKING, Memory.status == MemoryStatus.ACTIVE, Memory.created_at < cutoff)
    result = await session.execute(stmt)
    stale = result.scalars().all()
    for mem in stale:
        mem.status = MemoryStatus.ARCHIVED
        logger.info(f"Archived stale working memory: {mem.id}")
