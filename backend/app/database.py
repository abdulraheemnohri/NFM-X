"""
NFM-X Database Configuration Unification
Unifies and proxies database components to backend.app.storage.database
"""

import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

# Proxy core components from storage.database
from backend.app.storage.database import (
    Base,
    engine,
    AsyncSessionLocal,
    get_db,
    init_db,
    close_db,
    reset_database as drop_all_tables
)

logger = logging.getLogger(__name__)


async def get_db_connection():
    """
    Get a direct database connection for raw SQL queries.
    """
    async with engine.connect() as conn:
        return conn


# Import all models to ensure they are registered with Base.metadata
from backend.app.models.conflict import Conflict
from backend.app.models.document import UploadedDocument, OCRJob
from backend.app.models.pattern import SearchPattern
from backend.app.models.skill import Skill, SkillExecution
from backend.app.models.mcp import APIKey

# Additional models
try:
    from backend.app.memory.models import Memory, MemoryVersion, MemoryEvent, MemoryRelationship, MemoryConflict
    from backend.app.models.user import User, UserSession
except ImportError:
    pass

logger.info("Database module loaded and unified successfully")
