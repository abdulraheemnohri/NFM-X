import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.app.memory.models import Base

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(autouse=True)
def clean_vector_store(tmp_path):
    import backend.app.embeddings.vector_store as vs_module
    old_store = vs_module._vector_store
    vs_module._vector_store = vs_module.FAISSVectorStore(dimension=384, index_path=str(tmp_path / "vectors"))
    yield vs_module._vector_store
    vs_module._vector_store = old_store

@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

    await engine.dispose()
