"""
Memory capture logic for NFM-X
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import hashlib
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Memory, MemoryVersion, MemoryEvent, MemoryType, MemoryStatus, EventType, ChangeType, MemoryRelationship, RelationshipType
from .classification import classifier
from ..config import settings

class MemoryCapture:
    def _generate_id(self):
        return str(uuid.uuid4())

    def _compute_hash(self, content):
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _get_classification(self, content, memory_type=None):
        if memory_type:
            return memory_type, 1.0, "Explicit"
        result = classifier.classify(content)
        return result.memory_type, result.confidence, result.reason

    async def capture(self, db_session, content, memory_type=None, source=None, source_type=None, author_id=None, confidence=None, importance=None, metadata=None, tags=None, parent_memory_id=None):
        if not content or not content.strip():
            raise ValueError("Content cannot be empty")
        clean_content = content.strip()
        content_hash = self._compute_hash(clean_content)
        mem_type, _, _ = self._get_classification(clean_content, memory_type)
        final_confidence = confidence if confidence is not None else settings.default_confidence
        final_importance = importance if importance is not None else settings.default_importance
        final_confidence = max(0.0, min(1.0, final_confidence))
        final_importance = max(0.0, min(1.0, final_importance))
        now = datetime.now(timezone.utc)
        memory_id = self._generate_id()
        memory = Memory(id=memory_id, content=clean_content, content_hash=content_hash, memory_type=mem_type, confidence=final_confidence, importance=final_importance, status=MemoryStatus.ACTIVE, source=source, source_type=source_type, author_id=author_id, created_at=now, updated_at=now, metadata=metadata or {}, tags=tags or [])
        db_session.add(memory)
        await db_session.flush()
        version = MemoryVersion(id=self._generate_id(), memory_id=memory_id, content=clean_content, content_hash=content_hash, version_number=1, change_type=ChangeType.EXPAND, change_reason="Initial capture", confidence=final_confidence, importance=final_importance, status=MemoryStatus.ACTIVE, actor_id=author_id, actor_type=source_type or "user", parent_version_id=None, created_at=now)
        db_session.add(version)
        await db_session.flush()
        event = MemoryEvent(id=self._generate_id(), memory_id=memory_id, version_id=version.id, event_type=EventType.CREATED, description=f"Created with type: {mem_type.value}", actor_id=author_id, actor_type=source_type or "user", metadata={"classification": mem_type.value}, created_at=now)
        db_session.add(event)
        if parent_memory_id:
            relationship = MemoryRelationship(id=self._generate_id(), source_id=parent_memory_id, target_id=memory_id, relationship_type=RelationshipType.EXTENDS, confidence=0.8, description="Derived", metadata={}, created_at=now)
            db_session.add(relationship)
        return memory

capture_handler = MemoryCapture()