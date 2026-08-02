"""
NFM-X Test Configuration

Pytest fixtures and configuration for NFM-X tests.
"""

import asyncio
import os
import pytest
from pathlib import Path
from typing import AsyncGenerator

import httpx
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

os.environ["DEBUG"] = "true"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["EMBEDDING_MODEL"] = "all-MiniLM-L6-v2"

from backend.app.main import app
from backend.app.config import settings
from backend.app.storage.database import get_db, Base


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    engine = create_async_engine(settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "sqlite+aiosqlite:///:memory:"))
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
def test_client():
    with TestClient(app) as client:
        yield client


@pytest.fixture()
async def async_test_client():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture()
async def db_session():
    engine = create_async_engine(settings.DATABASE_URL)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as session:
        yield session
        await session.rollback()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
def test_memory_data():
    return {
        "content": "Test memory content",
        "title": "Test Memory",
        "tags": ["test", "sample"],
        "source": "test",
        "type": "TEXT",
    }


@pytest.fixture()
def test_search_query():
    return "test"