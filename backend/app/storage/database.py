from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import event
from pathlib import Path
import logging

from backend.app.config import settings

logger = logging.getLogger(__name__)
_engine = None
_async_session_maker = None

async def init_database(db_path: str = None):
    global _engine, _async_session_maker
    db_path = db_path or str(settings.NFM_DB_PATH)
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    _engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
        echo=settings.NFM_DEBUG,
        pool_pre_ping=True
    )
    _async_session_maker = async_sessionmaker(
        _engine, class_=AsyncSession, expire_on_commit=False
    )

    @event.listens_for(_engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    from backend.app.memory.models import Base as MemoryBase
    async with _engine.begin() as conn:
        await conn.run_sync(MemoryBase.metadata.create_all)
    logger.info("Database initialized")

async def get_db_session() -> AsyncSession:
    async with _async_session_maker() as session:
        yield session
