"""
NFM-X Conflict Detection
Detects and manages conflicts between memories
"""
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, timezone
from enum import Enum
import logging
import re
import difflib
import hashlib
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import Memory, MemoryStatus, MemoryType, MemoryEvent, EventType
from ..storage.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


class ConflictType(str, Enum):
    CONTRADICTION = "contradiction"
    DUPLICATE = "duplicate"
    TEMPORAL = "temporal"
    HIERARCHICAL = "hierarchical"
    SEMANTIC = "semantic"
    FACTUAL = "factual"


class ConflictStatus(str, Enum):
    DETECTED = "detected"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class Conflict:
    def __init__(
        self,
        id: str,
        conflict_type: ConflictType,
        status: ConflictStatus,
        memory_a_id: str,
        memory_b_id: str,
        description: str,
        details: Dict[str, Any],
        severity: float,
        detected_at: datetime,
        resolved_at: Optional[datetime] = None,
        resolved_by: Optional[str] = None,
        resolution_notes: Optional[str] = None
    ):
        self.id = id
        self.conflict_type = conflict_type
        self.status = status
        self.memory_a_id = memory_a_id
        self.memory_b_id = memory_b_id
        self.description = description
        self.details = details
        self.severity = severity
        self.detected_at = detected_at
        self.resolved_at = resolved_at
        self.resolved_by = resolved_by
        self.resolution_notes = resolution_notes


class ConflictDetectionResult:
    def __init__(
        self,
        conflicts: List[Conflict],
        total_conflicts: int,
        new_conflicts: int,
        resolved_conflicts: int
    ):
        self.conflicts = conflicts
        self.total_conflicts = total_conflicts
        self.new_conflicts = new_conflicts
        self.resolved_conflicts = resolved_conflicts


class ConflictDetector:
    def __init__(self):
        self.contradiction_patterns = [
            (r'\bnot\b.*\bbut\b', 0.9),
            (r'\bnever\b.*\balways\b', 0.9),
            (r'\ball\b.*\bnone\b', 0.9),
            (r'\btrue\b.*\bfalse\b', 0.9),
            (r'\bcorrect\b.*\bincorrect\b', 0.9),
            (r'\bpossible\b.*\bimpossible\b', 0.9),
            (r'\bopen\b.*\bclosed\b', 0.8),
            (r'\bon\b.*\boff\b', 0.8),
            (r'\bup\b.*\bdown\b', 0.8),
        ]
        
        self.temporal_patterns = [
            (r'\bbefore\b.*\bafter\b', 0.8),
            (r'\bearlier\b.*\blater\b', 0.8),
        ]
        
        self.duplicate_similarity_threshold = 0.9
        self.near_duplicate_similarity_threshold = 0.7
    
    async def detect_conflicts(
        self,
        db_session: Optional[AsyncSession] = None,
        memory_id: Optional[str] = None,
        limit: int = 100
    ) -> ConflictDetectionResult:
        if db_session is None:
            db_session = AsyncSessionLocal()
        
        try:
            conflicts: List[Conflict] = []
            
            if memory_id:
                memories = await self._get_memories_for_comparison(db_session, memory_id, limit)
            else:
                memories = await self._get_active_memories(db_session, limit * 2)
            
            for i, mem1 in enumerate(memories):
                for j, mem2 in enumerate(memories[i + 1:], start=i + 1):
                    if self._are_same_memory_chain(mem1, mem2):
                        continue
                    
                    conflict = await self._detect_memory_conflict(mem1, mem2)
                    if conflict:
                        conflicts.append(conflict)
            
            total_conflicts = len(conflicts)
            new_conflicts = len([c for c in conflicts if c.status == ConflictStatus.DETECTED])
            resolved_conflicts = len([c for c in conflicts if c.status == ConflictStatus.RESOLVED])
            
            return ConflictDetectionResult(
                conflicts=conflicts,
                total_conflicts=total_conflicts,
                new_conflicts=new_conflicts,
                resolved_conflicts=resolved_conflicts
            )
            
        except Exception as e:
            logger.error(f"Failed to detect conflicts: {e}")
            return ConflictDetectionResult(conflicts=[], total_conflicts=0, new_conflicts=0, resolved_conflicts=0)
        finally:
            if db_session is not None:
                await db_session.close()
    
    async def _get_memories_for_comparison(self, db_session: AsyncSession, memory_id: str, limit: int) -> List[Memory]:
        result = await db_session.execute(
            select(Memory).where(Memory.id == memory_id)
        )
        target_memory = result.scalar_one_or_none()
        
        if not target_memory:
            return []
        
        result = await db_session.execute(
            select(Memory)
            .where(Memory.status == MemoryStatus.ACTIVE)
            .where(Memory.id != memory_id)
            .limit(limit)
        )
        other_memories = result.scalars().all()
        return [target_memory] + other_memories
    
    async def _get_active_memories(self, db_session: AsyncSession, limit: int) -> List[Memory]:
        result = await db_session.execute(
            select(Memory)
            .where(Memory.status == MemoryStatus.ACTIVE)
            .limit(limit)
        )
        return result.scalars().all()
    
    def _are_same_memory_chain(self, mem1: Memory, mem2: Memory) -> bool:
        if mem1.id == mem2.id:
            return True
        if mem1.parent_id == mem2.id or mem2.parent_id == mem1.id:
            return True
        
        chain1 = self._get_version_chain(mem1)
        chain2 = self._get_version_chain(mem2)
        return bool(set(chain1) & set(chain2))
    
    def _get_version_chain(self, memory: Memory) -> List[str]:
        chain = []
        current = memory
        while current:
            chain.append(current.id)
            current = current.parent
        return chain
    
    async def _detect_memory_conflict(self, mem1: Memory, mem2: Memory) -> Optional[Conflict]:
        content1 = (mem1.content or "").lower()
        content2 = (mem2.content or "").lower()
        
        if not content1 or not content2:
            return None
        
        if self._is_duplicate(content1, content2):
            return self._create_conflict(
                mem1, mem2,
                ConflictType.DUPLICATE,
                "Duplicate content detected",
                {"similarity": self._calculate_similarity(content1, content2)},
                0.8
            )
        
        similarity = self._calculate_similarity(content1, content2)
        if similarity >= self.near_duplicate_similarity_threshold:
            return self._create_conflict(
                mem1, mem2,
                ConflictType.DUPLICATE,
                "Near-duplicate content detected",
                {"similarity": similarity},
                0.6
            )
        
        contradiction = self._detect_contradiction(content1, content2)
        if contradiction:
            conflict_type, description, details = contradiction
            return self._create_conflict(mem1, mem2, conflict_type, description, details, 0.9)
        
        temporal_conflict = self._detect_temporal_conflict(content1, content2)
        if temporal_conflict:
            conflict_type, description, details = temporal_conflict
            return self._create_conflict(mem1, mem2, conflict_type, description, details, 0.8)
        
        return None
    
    def _is_duplicate(self, content1: str, content2: str) -> bool:
        if content1 == content2:
            return True
        normalized1 = re.sub(r'\s+', ' ', content1).strip()
        normalized2 = re.sub(r'\s+', ' ', content2).strip()
        return normalized1 == normalized2
    
    def _calculate_similarity(self, content1: str, content2: str) -> float:
        return difflib.SequenceMatcher(None, content1, content2).ratio()
    
    def _detect_contradiction(self, content1: str, content2: str) -> Optional[Tuple[ConflictType, str, Dict[str, Any]]]:
        combined = f"{content1} {content2}"
        
        for pattern, confidence in self.contradiction_patterns:
            if re.search(pattern, combined, re.IGNORECASE):
                return (ConflictType.CONTRADICTION, f"Contradiction detected: {pattern}", {"pattern": pattern, "confidence": confidence})
        
        opposites = [("true", "false"), ("yes", "no"), ("correct", "incorrect"), ("possible", "impossible")]
        words1 = set(content1.split())
        words2 = set(content2.split())
        
        for word1, word2 in opposites:
            if (word1 in words1 and word2 in words2) or (word2 in words1 and word1 in words2):
                return (ConflictType.CONTRADICTION, f"Opposite concepts: {word1} vs {word2}", {"opposites": [word1, word2]})
        
        return None
    
    def _detect_temporal_conflict(self, content1: str, content2: str) -> Optional[Tuple[ConflictType, str, Dict[str, Any]]]:
        combined = f"{content1} {content2}"
        for pattern, confidence in self.temporal_patterns:
            if re.search(pattern, combined, re.IGNORECASE):
                return (ConflictType.TEMPORAL, f"Temporal conflict: {pattern}", {"pattern": pattern, "confidence": confidence})
        return None
    
    def _create_conflict(
        self,
        mem1: Memory,
        mem2: Memory,
        conflict_type: ConflictType,
        description: str,
        details: Dict[str, Any],
        severity: float
    ) -> Conflict:
        conflict_id = str(uuid.uuid4())
        if mem1.created_at and mem2.created_at and mem1.created_at > mem2.created_at:
            mem1, mem2 = mem2, mem1
        
        return Conflict(
            id=conflict_id,
            conflict_type=conflict_type,
            status=ConflictStatus.DETECTED,
            memory_a_id=mem1.id,
            memory_b_id=mem2.id,
            description=description,
            details=details,
            severity=severity,
            detected_at=datetime.now(timezone.utc),
            resolved_at=None,
            resolved_by=None,
            resolution_notes=None
        )
    
    async def get_conflict(self, db_session: AsyncSession, conflict_id: str) -> Optional[Conflict]:
        result = await db_session.execute(
            select(Memory).where(Memory.metadata["conflict_id"].as_string() == conflict_id)
        )
        conflict_memory = result.scalar_one_or_none()
        
        if not conflict_memory:
            return None
        
        metadata = conflict_memory.metadata or {}
        return Conflict(
            id=conflict_id,
            conflict_type=ConflictType(metadata.get("conflict_type", "contradiction")),
            status=ConflictStatus(metadata.get("status", "detected")),
            memory_a_id=metadata.get("memory_a_id", ""),
            memory_b_id=metadata.get("memory_b_id", ""),
            description=conflict_memory.content or "",
            details=metadata.get("details", {}),
            severity=metadata.get("severity", 0.5),
            detected_at=conflict_memory.created_at or datetime.now(timezone.utc),
            resolved_at=datetime.fromisoformat(metadata.get("resolved_at")) if metadata.get("resolved_at") else None,
            resolved_by=metadata.get("resolved_by"),
            resolution_notes=metadata.get("resolution_notes")
        )


detector = ConflictDetector()