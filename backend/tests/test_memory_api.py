"""
Tests for Memory API
"""
import pytest
from app.memory.models import Memory, MemoryType, MemoryStatus, ChangeType, EventType
from app.memory.capture import capture_handler

@pytest.mark.asyncio
async def test_create_memory(test_db_session):
    memory = await capture_handler.capture(test_db_session, content="Test", memory_type=MemoryType.FACT)
    await test_db_session.commit()
    assert memory.id is not None
    assert memory.content == "Test"
    assert len(memory.versions) == 1

@pytest.mark.asyncio
async def test_list_memories(test_db_session):
    for i in range(3):
        await capture_handler.capture(test_db_session, content=f"Mem {i}")
    await test_db_session.commit()
    from sqlalchemy import select
    result = await test_db_session.execute(select(Memory).where(Memory.status == MemoryStatus.ACTIVE))
    assert len(result.scalars().all()) == 3

@pytest.mark.asyncio
async def test_classification():
    from app.memory.classification import classifier
    result = classifier.classify("Python is a language")
    assert result.memory_type == MemoryType.FACT