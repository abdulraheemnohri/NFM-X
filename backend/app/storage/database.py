"""
NFM-X Database Module
SQLite database setup and session management
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import event
from contextlib import asynccontextmanager
import logging
from pathlib import Path
from typing import AsyncGenerator, Optional

from ..config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

_engine = None
_async_session_maker = None


class AsyncEngine:
    pass


async def init_database(db_path = None):
    global _engine, _async_session_maker
    if db_path is None:
        db_path = str(settings.NFM_DB_PATH)
    db_dir = Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Initializing database at {db_path}")
    _engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
        echo=settings.NFM_DEBUG,
        pool_size=settings.NFM_DB_POOL_SIZE,
        max_overflow=settings.NFM_DB_MAX_OVERFLOW,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    _async_session_maker = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    @event.listens_for(_engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    from ..memory.models import Base as MemoryBase
    async with _engine.begin() as conn:
        await conn.run_sync(MemoryBase.metadata.create_all)
    logger.info("Database initialized successfully")
    return _engine