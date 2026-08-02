"""
NFM-X Database Module
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import os

class Base(DeclarativeBase):
    pass

engine = create_async_engine(os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./nfm.db"))

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    pass

async def close_db():
    await engine.dispose()