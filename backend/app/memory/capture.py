from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import uuid
import hashlib

from backend.app.memory.models import Memory, MemoryVersion, MemoryEvent, MemoryType, MemoryStatus, ChangeType
from backend.app.memory.classification import MemoryClassifier
from backend.app.config import settings

class MemoryCaptureEngine:
    def __init__(self):
        self.classifier = MemoryClassifier()

    def _sha256(self, content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    async def capture(
        self,
        db_session: AsyncSession,
        content: str,
        type: str = None,
        subtype: str = None,
        agent_id: str = None,
        source_id: str = None,
        confidence: float = None,
        importance: float = None,
        metadata: dict = None
    ) -> Memory:
        # 1. Classification
        classification = self.classifier.classify(content)
        final_type = type or classification["type"]
        final_confidence = confidence or classification["confidence"]
        final_importance = importance or classification["importance"]

        memory_id = str(uuid.uuid4())
        content_hash = self._sha256(content)
        now = datetime.now(timezone.utc)

        # 2. Create models
        memory = Memory(
            id=memory_id,
            root_id=memory_id,
            version=1,
            type=MemoryType(final_type),
            subtype=subtype,
            content=content,
            normalized_content=content.lower().strip(),
            content_hash=content_hash,
            agent_id=agent_id,
            source_id=source_id,
            confidence=final_confidence,
            importance=final_importance,
            status=MemoryStatus.ACTIVE,
            created_at=now,
            observed_at=now,
            valid_from=now,
            metadata=metadata or {}
        )

        version = MemoryVersion(
            id=str(uuid.uuid4()),
            memory_id=memory_id,
            version=1,
            content=content,
            normalized_content=memory.normalized_content,
            content_hash=content_hash,
            confidence=final_confidence,
            importance=final_importance,
            status=MemoryStatus.ACTIVE,
            change_type=ChangeType.CREATE,
            change_reason="Initial capture",
            metadata=metadata or {},
            created_at=now,
            actor_id=agent_id or "system",
            actor_type="agent"
        )

        event = MemoryEvent(
            id=str(uuid.uuid4()),
            memory_id=memory_id,
            event_type="create",
            details={"type": final_type, "content_length": len(content)},
            timestamp=now,
            agent_id=agent_id or "system"
        )

        db_session.add(memory)
        db_session.add(version)
        db_session.add(event)

        return memory

# Singleton or factory
def get_capture_engine() -> MemoryCaptureEngine:
    return MemoryCaptureEngine()
