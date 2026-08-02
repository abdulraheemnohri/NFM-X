from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
import re

from ..memory.models import Memory, MemoryConflict, MemoryStatus

class ConflictDetector:
    """Detect contradictions between memories using keyword analysis."""

    # Simple contradiction patterns
    CONTRADICTION_PATTERNS = [
        # "uses X" vs "uses Y" for same entity
        (r"uses\s+(\w+)", r"uses\s+(\w+)"),
        # "is X" vs "is not X"
        (r"is\s+(\w+)", r"is\s+not\s+(\w+)"),
        # "prefers X" vs "prefers Y"
        (r"prefers\s+(\w+)", r"prefers\s+(\w+)"),
        # "deployed on X" vs "deployed on Y"
        (r"deployed\s+on\s+(\w+)", r"deployed\s+on\s+(\w+)"),
    ]

    async def scan_for_conflicts(
        self,
        db_session: AsyncSession,
        memory_id: str
    ) -> List[Dict[str, Any]]:
        """Scan existing memories for conflicts with the given memory."""
        result = await db_session.execute(select(Memory).where(Memory.id == memory_id))
        target = result.scalar_one_or_none()
        if not target:
            return []

        # Find same-type, same-agent memories
        stmt = select(Memory).where(
            Memory.type == target.type,
            Memory.agent_id == target.agent_id,
            Memory.status == MemoryStatus.ACTIVE,
            Memory.id != memory_id
        )
        result = await db_session.execute(stmt)
        candidates = result.scalars().all()

        conflicts = []
        for candidate in candidates:
            conflict = self._detect_conflict(target.content, candidate.content)
            if conflict:
                conflicts.append({
                    "memory_a_id": memory_id,
                    "memory_b_id": candidate.id,
                    "conflict_type": conflict["type"],
                    "description": conflict["description"],
                    "severity": conflict["severity"]
                })

        return conflicts

    def _detect_conflict(self, content_a: str, content_b: str) -> Optional[Dict[str, Any]]:
        """Check if two memory contents contradict each other."""
        a_lower = content_a.lower()
        b_lower = content_b.lower()

        for pattern_a, pattern_b in self.CONTRADICTION_PATTERNS:
            match_a = re.search(pattern_a, a_lower)
            match_b = re.search(pattern_b, b_lower)
            if match_a and match_b:
                val_a = match_a.group(1)
                val_b = match_b.group(1)
                if val_a != val_b:
                    return {
                        "type": "value_mismatch",
                        "description": f"'{content_a}' contradicts '{content_b}'",
                        "severity": 0.7
                    }

        # Check for direct negation
        if f"not {content_b}" in a_lower or f"not {content_a}" in b_lower:
            return {
                "type": "negation",
                "description": f"Direct negation detected",
                "severity": 0.9
            }

        return None

    async def create_conflict_record(
        self,
        db_session: AsyncSession,
        memory_a_id: str,
        memory_b_id: str,
        conflict_type: str,
        description: str,
        severity: float
    ) -> MemoryConflict:
        conflict = MemoryConflict(
            memory_a_id=memory_a_id,
            memory_b_id=memory_b_id,
            conflict_type=conflict_type,
            description=description,
            severity=severity,
            status="unresolved"
        )
        db_session.add(conflict)
        await db_session.commit()
        return conflict
