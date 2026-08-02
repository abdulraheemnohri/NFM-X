import logging
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.memory.conflicts import ConflictDetector

logger = logging.getLogger(__name__)

async def scan_memory_background(db_session: AsyncSession, memory_id: str):
    """Scan memory for conflicts in a background task."""
    try:
        detector = ConflictDetector()
        conflicts = await detector.scan_for_conflicts(db_session, memory_id)
        for c in conflicts:
            await detector.create_conflict_record(
                db_session=db_session,
                memory_a_id=c["memory_a_id"],
                memory_b_id=c["memory_b_id"],
                conflict_type=c["conflict_type"],
                description=c["description"],
                severity=c["severity"]
            )
        logger.info(f"Background conflict scan complete for {memory_id}: {len(conflicts)} found.")
    except Exception as e:
        logger.error(f"Failed to scan conflicts in background: {e}")
