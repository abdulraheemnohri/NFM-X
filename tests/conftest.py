"""
NFM-X Test Configuration

Pytest fixtures and configuration for NFM-X tests.
"""

import asyncio
import os
import tempfile
from pathlib import Path
import pytest
from typing import AsyncGenerator

import httpx
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Setup session-scoped temporary directory for the test SQLite database
_temp_dir = tempfile.TemporaryDirectory()
_test_db_path = Path(_temp_dir.name) / "test_nfm.db"

os.environ["DEBUG"] = "true"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_test_db_path}"
os.environ["EMBEDDING_MODEL"] = "all-MiniLM-L6-v2"

from backend.app.main import app
from backend.app.config import settings
from backend.app.storage.database import get_db, Base
import backend.app.database  # Register all models on Base metadata


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    # Use the unified engine from the storage layer
    from backend.app.storage.database import engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    try:
        _temp_dir.cleanup()
    except Exception:
        pass


@pytest.fixture()
def test_client():
    with TestClient(app) as client:
        yield client


@pytest.fixture()
async def async_test_client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture()
async def db_session():
    from backend.app.storage.database import engine
    
    async with AsyncSession(engine) as session:
        yield session
        await session.rollback()


@pytest.fixture()
def test_memory_data():
    return {
        "content": "Test memory content",
        "title": "Test Memory",
        "tags": ["test", "sample"],
        "categories": ["personal"],
        "source": "test",
        "type": "TEXT",
    }


@pytest.fixture()
def test_search_query():
    return "test"
