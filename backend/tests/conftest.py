"""
Pytest configuration
"""
import pytest
import tempfile
from pathlib import Path
from app.config import Settings
from app.storage.database import Base

@pytest.fixture(scope="session")
def test_settings():
    with tempfile.TemporaryDirectory() as tmpdir:
        settings = Settings(database_url=f"sqlite+aiosqlite:///{Path(tmpdir) / 'test.db'}", faiss_index_path=str(Path(tmpdir) / "test_faiss"))
        yield settings

@pytest.fixture(scope="session", autouse=True)
async def test_db_engine(test_settings):
    import app.config
    app.config.settings = test_settings
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
    engine = create_async_engine(test_settings.database_url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        if engine.dialect.name == "sqlite":
            await conn.execute(text("PRAGMA journal_mode=WAL"))
    yield engine
    await engine.dispose()