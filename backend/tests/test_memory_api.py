"""
Tests for Memory API
"""
import pytest
from backend.app.storage.database import AsyncSessionLocal
from backend.app.memory.models import Memory, MemoryType, MemoryStatus, EventType
# Note: ChangeType and MemoryVersion are imported once they are defined in Step 2.
# We will define a local fallback or import them correctly once added.
from backend.app.memory.capture import capture as capture_handler

@pytest.mark.asyncio
async def test_create_memory(db_session):
    # Use db_session instead of test_db_session which matches root conftest fixture
    memory = await capture_handler.capture(content="Test", memory_type=MemoryType.TEXT, db_session=db_session)
    await db_session.commit()
    assert memory.id is not None
    assert memory.content == "Test"
    assert len(memory.versions) == 1

@pytest.mark.asyncio
async def test_list_memories(db_session):
    for i in range(3):
        await capture_handler.capture(content=f"Mem {i}", db_session=db_session)
    await db_session.commit()
    from sqlalchemy import select
    result = await db_session.execute(select(Memory).where(Memory.status == MemoryStatus.ACTIVE))
    assert len(result.scalars().all()) >= 3

@pytest.mark.asyncio
async def test_classification():
    from backend.app.memory.classification import classifier
    result = classifier.classify("Python is a language")
    assert result.memory_type == MemoryType.TEXT
