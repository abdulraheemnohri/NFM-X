"""
NFM-X Memory Capture
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import hashlib
import uuid
from .models import Memory, MemoryStatus, MemoryType
from ..storage.database import AsyncSessionLocal

class MemoryCapture:
    async def capture(self, content: str, title: Optional[str] = None, **kwargs) -> Memory:
        memory = Memory(
            id=str(uuid.uuid4()),
            content=content,
            content_hash=hashlib.sha256(content.encode()).hexdigest(),
            title=title or content[:100],
            **kwargs
        )
        async with AsyncSessionLocal() as session:
            session.add(memory)
            await session.commit()
            await session.refresh(memory)
        return memory