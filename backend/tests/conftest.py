"""
Pytest configuration for backend tests
"""
import pytest
import tempfile
import asyncio
from pathlib import Path
import httpx

from backend.app.config import NFMXConfig
from backend.app.storage.database import Base


@pytest.fixture(scope="session")
def test_settings():
    with tempfile.TemporaryDirectory() as tmpdir:
        settings = NFMXConfig(
            database_url=f"sqlite+aiosqlite:///{Path(tmpdir) / 'test.db'}",
            vector_store_dir=str(Path(tmpdir) / "test_faiss"),
            debug=True
        )
        yield settings


@pytest.fixture(scope="session", autouse=True)
async def test_db_engine(test_settings):
    import backend.app.config
    backend.app.config.settings = test_settings

    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text

    # Ensure all models are registered
    import backend.app.database

    engine = create_async_engine(test_settings.database_url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        if engine.dialect.name == "sqlite":
            await conn.execute(text("PRAGMA journal_mode=WAL"))

    yield engine
    await engine.dispose()


@pytest.fixture()
async def db_session(test_db_engine):
    from sqlalchemy.ext.asyncio import AsyncSession
    async with AsyncSession(test_db_engine, expire_on_commit=False) as session:
        yield session
        await session.rollback()


@pytest.fixture()
async def async_test_client():
    from backend.app.main import app
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
