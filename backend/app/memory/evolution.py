"""
NFM-X Memory Evolution Engine
Automatically evolves memories based on new information
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import uuid
import re

from sqlalchemy import select

from ..config import settings
from .models import Memory, MemoryVersion, MemoryEvent, MemoryConflict
from .models import ChangeType, MemoryType, MemoryStatus

logger = logging.getLogger(__name__)


class MemoryEvolutionEngine:
    def __init__(self):
        pass

    async def evolve(
        self,
        session,
        memory: Memory,
        new_content: Optional[str] = None,
        change_type: Optional[str] = None,
        change_reason: Optional[str] = None,
        evidence: Optional[List[Dict[str, Any]]] = None,
        agent_id: Optional[str] = None
    ) -> MemoryVersion:
        if new_content and new_content != memory.content:
            relationship = self._determine_relationship(memory.content, new_content)
        else:
            relationship = "reinforce"

        if change_type:
            change_type_enum = ChangeType(change_type)
        else:
            change_type_enum = self._map_relationship_to_change_type(relationship)

        if new_content:
            memory.content = new_content
            memory.normalized_content = self._normalize_text(new_content)
            memory.content_hash = self._hash_content(new_content)

        if change_type_enum == ChangeType.REINFORCE:
            memory.confidence = min(1.0, memory.confidence + 0.05)
        elif change_type_enum == ChangeType.CORRECT:
            memory.confidence = max(0.3, memory.confidence - 0.1)
        elif change_type_enum == ChangeType.REFINE:
            memory.confidence = min(1.0, memory.confidence + 0.02)

        new_version = MemoryVersion(
            id=str(uuid.uuid4()),
            memory_id=memory.id,
            version=memory.version + 1,
            content=memory.content,
            normalized_content=memory.normalized_content,
            content_hash=memory.content_hash,
            confidence=memory.confidence,
            importance=memory.importance,
            status=memory.status,
            metadata=memory.metadata,
            change_type=change_type_enum,
            change_reason=change_reason or f"Evolved via {relationship}",
            created_at=datetime.utcnow(),
            actor_id=agent_id or memory.agent_id,
            actor_type="agent"
        )
        session.add(new_version)
        memory.version += 1

        event = MemoryEvent(
            id=str(uuid.uuid4()),
            memory_id=memory.id,
            event_type="evolve",
            details={
                "change_type": change_type_enum.value,
                "relationship": relationship,
                "old_content_hash": memory.content_hash,
                "new_content_hash": new_version.content_hash,
                "evidence": evidence
            },
            timestamp=datetime.utcnow(),
            agent_id=agent_id or memory.agent_id,
            actor_type="agent"
        )
        session.add(event)

        if change_type_enum == ChangeType.CONTRADICT:
            await self._handle_contradiction(session, memory, new_content, agent_id)

        logger.info(f"Evolved memory {memory.id} with change type {change_type_enum.value}")
        return new_version

    def _determine_relationship(self, old_content: str, new_content: str) -> str:
        old_normalized = self._normalize_text(old_content).lower()
        new_normalized = self._normalize_text(new_content).lower()

        if old_normalized == new_normalized:
            return "duplicate"
        if old_normalized in new_normalized:
            return "expand"
        if new_normalized in old_normalized:
            return "refine"
        if self._is_contradiction(old_normalized, new_normalized):
            return "contradict"
        if self._is_similar(old_normalized, new_normalized):
            return "reinforce"
        return "new"

    def _map_relationship_to_change_type(self, relationship: str) -> ChangeType:
        mapping = {
            "duplicate": ChangeType.CREATE,
            "expand": ChangeType.EXPAND,
            "refine": ChangeType.REFINE,
            "contradict": ChangeType.CONTRADICT,
            "reinforce": ChangeType.REINFORCE,
            "new": ChangeType.CREATE,
            "correct": ChangeType.CORRECT,
            "merge": ChangeType.MERGE,
            "split": ChangeType.SPLIT
        }
        return mapping.get(relationship, ChangeType.REFINE)

    async def _handle_contradiction(self, session, memory: Memory, new_content: str, agent_id: Optional[str]):
        conflict = MemoryConflict(
            id=str(uuid.uuid4()),
            memory_a_id=memory.id,
            memory_b_id=memory.id,
            conflict_type="contradiction",
            description=f"Contradiction detected: {new_content[:100]}...",
            severity=0.8,
            status="unresolved",
            created_at=datetime.utcnow(),
            metadata={"new_content": new_content}
        )
        session.add(conflict)
        logger.warning(f"Contradiction detected for memory {memory.id}")

    def _is_contradiction(self, old_content: str, new_content: str) -> bool:
        old_lower = old_content.lower()
        new_lower = new_content.lower()
        contradiction_pairs = [
            ("yes", "no"), ("true", "false"), ("correct", "wrong"),
            ("good", "bad"), ("success", "failure"), ("like", "dislike"),
            ("prefer", "avoid"), ("use", "not use")
        ]
        for old, new in contradiction_pairs:
            if old in old_lower and new in new_lower:
                return True
            if new in old_lower and old in new_lower:
                return True
        return False

    def _is_similar(self, old_content: str, new_content: str, threshold: float = 0.7) -> bool:
        old_words = set(self._extract_keywords(old_content))
        new_words = set(self._extract_keywords(new_content))
        if not old_words or not new_words:
            return False
        common = old_words & new_words
        similarity = len(common) / max(len(old_words), len(new_words))
        return similarity >= threshold

    def _normalize_text(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text).strip()

    def _hash_content(self, content: str) -> str:
        import hashlib
        return hashlib.sha256(content.encode()).hexdigest()

    def _extract_keywords(self, text: str) -> List[str]:
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        stop_words = {"the", "and", "for", "are", "but", "not", "you", "all", "can", "her", "was", "one", "our", "out", "day", "get", "has", "him", "his", "how"}
        return [w for w in words if w not in stop_words]


_evolution_engine = None

def get_evolution_engine() -> MemoryEvolutionEngine:
    global _evolution_engine
    if _evolution_engine is None:
        _evolution_engine = MemoryEvolutionEngine()
    return _evolution_engine