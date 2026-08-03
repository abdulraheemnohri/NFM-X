"""
NFM-X Database Configuration
SQLite database setup with SQLAlchemy 2.0 async support.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import event
import os
import logging
from typing import AsyncGenerator

from backend.app.config import (
    NFM_DATABASE_URL,
    NFM_DATABASE_ECHO,
    NFM_DATABASE_POOL_SIZE,
    NFM_DATABASE_MAX_OVERFLOW
)

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    NFM_DATABASE_URL,
    echo=NFM_DATABASE_ECHO,
    pool_size=NFM_DATABASE_POOL_SIZE,
    max_overflow=NFM_DATABASE_MAX_OVERFLOW,
    future=True
)

# Enable foreign keys for SQLite
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get async database session.
    Use this in FastAPI route dependencies.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            await session.close()


async def get_db_connection():
    """
    Get a direct database connection for raw SQL queries.
    """
    async with engine.connect() as conn:
        return conn


async def init_db():
    """
    Initialize database tables.
    Create all tables defined in models.
    """
    logger.info("Initializing database tables...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables initialized successfully")


async def drop_all_tables():
    """
    Drop all database tables (DANGEROUS - use only in development).
    """
    logger.warning("Dropping all database tables...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    logger.warning("All database tables dropped")


# Import all models to ensure they are registered with Base.metadata
from backend.app.models.conflict import Conflict
from backend.app.models.document import UploadedDocument, OCRJob
from backend.app.models.pattern import SearchPattern
from backend.app.models.skill import Skill, SkillExecution
from backend.app.models.mcp import APIKey

# Additional models that might exist
try:
    from backend.app.models.memory import Memory
    from backend.app.models.user import User
except ImportError:
    pass

logger.info("Database module loaded successfully")
