from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid
import hashlib
import re
import numpy as np

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..memory.models import Memory, MemoryVersion, MemoryEvent, MemoryConflict, MemoryRelationship, MemoryStatus, ChangeType
from ..embeddings.models import get_embedding_model

class MemoryEvolution:
    """Manual memory versioning. Creates new versions, never overwrites."""

    async def create_version(
        self,
        db_session: AsyncSession,
        memory_id: str,
        new_content: str,
        change_type: ChangeType,
        change_reason: str,
        actor_id: str = "system",
        confidence: Optional[float] = None,
        importance: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Memory:
        # Get current memory
        result = await db_session.execute(select(Memory).where(Memory.id == memory_id))
        current = result.scalar_one_or_none()
        if current is None:
            raise ValueError(f"Memory {memory_id} not found")

        # Mark current as superseded
        current.status = MemoryStatus.INACTIVE

        # Create new memory entry (new version)
        new_version_num = current.version + 1
        new_memory_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        content_hash = _sha256(new_content)

        new_memory = Memory(
            id=new_memory_id,
            root_id=current.root_id,
            version=new_version_num,
            type=current.type,
            subtype=current.subtype,
            content=new_content,
            normalized_content=new_content.lower().strip(),
            content_hash=content_hash,
            agent_id=current.agent_id,
            source_id=current.source_id,
            confidence=confidence if confidence is not None else current.confidence,
            importance=importance if importance is not None else current.importance,
            status=MemoryStatus.ACTIVE,
            created_at=now,
            observed_at=now,
            valid_from=now,
            parent_id=current.id,
            metadata={**(current.metadata or {}), **(metadata or {})}
        )

        # Create version record
        version = MemoryVersion(
            id=str(uuid.uuid4()),
            memory_id=new_memory_id,
            version=new_version_num,
            content=new_content,
            normalized_content=new_memory.normalized_content,
            content_hash=content_hash,
            confidence=new_memory.confidence,
            importance=new_memory.importance,
            status=MemoryStatus.ACTIVE,
            change_type=change_type,
            change_reason=change_reason,
            created_at=now,
            actor_id=actor_id,
            actor_type="agent"
        )

        db_session.add(new_memory)
        db_session.add(version)
        await db_session.commit()

        return new_memory


def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


class EvolutionEngine:
    """Automatically compares new memories with existing and decides relationship."""

    def __init__(self):
        self.embedding_model = get_embedding_model()
        self.similarity_threshold = 0.85
        self.reinforce_threshold = 0.75
        self.contradiction_threshold = 0.70
        self._embedding_cache: Dict[str, Any] = {}

    async def evolve(self, db_session: AsyncSession, new_memory: Memory) -> Dict[str, Any]:
        similar = await self._find_similar_memories(db_session, new_memory)

        if not similar:
            return {"action": "NEW", "memory_id": new_memory.id, "details": {}}

        best_match = similar[0]
        relationship = self._analyze_relationship(new_memory, best_match)

        if relationship == "DUPLICATE":
            await self._mark_duplicate(db_session, new_memory, best_match)
            return {"action": "DUPLICATE", "memory_id": best_match.id, "details": {}}

        elif relationship == "REINFORCE":
            updated = await self._reinforce_memory(db_session, best_match, new_memory)
            return {"action": "REINFORCE", "memory_id": updated.id, "details": {}}

        elif relationship == "CONTRADICT":
            conflict = await self._create_contradiction(db_session, best_match, new_memory)
            return {"action": "CONTRADICT", "memory_id": new_memory.id, "details": {"conflict_id": conflict.id}}

        elif relationship == "REFINE":
            version = await self._create_refined_version(db_session, best_match, new_memory)
            return {"action": "REFINE", "memory_id": version.id, "details": {}}

        elif relationship == "EXPAND":
            version = await self._create_expanded_version(db_session, best_match, new_memory)
            return {"action": "EXPAND", "memory_id": version.id, "details": {}}

        else:
            await self._create_relationship(db_session, new_memory, best_match, "related")
            return {"action": "NEW_RELATED", "memory_id": new_memory.id, "details": {}}

    async def _find_similar_memories(self, db_session: AsyncSession, new_memory: Memory, limit: int = 5) -> List[Memory]:
        stmt = select(Memory).where(
            Memory.type == new_memory.type,
            Memory.agent_id == new_memory.agent_id,
            Memory.status == MemoryStatus.ACTIVE,
            Memory.id != new_memory.id
        ).limit(50)
        result = await db_session.execute(stmt)
        candidates = result.scalars().all()

        if not candidates:
            return []

        # Cache embeddings to avoid O(n²) calls
        new_embedding = self._get_cached_embedding(new_memory.content)
        scored = []
        for mem in candidates:
            mem_embedding = self._get_cached_embedding(mem.content)
            similarity = self._cosine_similarity(new_embedding, mem_embedding)
            scored.append((mem, similarity))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [mem for mem, score in scored[:limit] if score > 0.5]

    def _get_cached_embedding(self, content: str) -> Any:
        """Get embedding from cache or generate new one."""
        content_hash = _sha256(content)
        if content_hash not in self._embedding_cache:
            self._embedding_cache[content_hash] = self.embedding_model.embed(content)
        return self._embedding_cache[content_hash]

    def _analyze_relationship(self, new_mem: Memory, existing: Memory) -> str:
        if self._is_near_duplicate(new_mem.content, existing.content):
            return "DUPLICATE"

        new_emb = self._get_cached_embedding(new_mem.content)
        exist_emb = self._get_cached_embedding(existing.content)
        similarity = self._cosine_similarity(new_emb, exist_emb)

        if similarity >= self.reinforce_threshold:
            if self._detect_contradiction(new_mem.content, existing.content):
                return "CONTRADICT"
            if self._is_refinement(existing.content, new_mem.content):
                return "REFINE"
            if self._is_expansion(existing.content, new_mem.content):
                return "EXPAND"
            return "REINFORCE"

        if similarity >= 0.6:
            if self._detect_contradiction(new_mem.content, existing.content):
                return "CONTRADICT"
            if self._is_expansion(existing.content, new_mem.content):
                return "EXPAND"

        return "RELATED"

    def _is_near_duplicate(self, a: str, b: str) -> bool:
        a_norm = re.sub(r"[^\w\s]", "", a.lower().strip())
        b_norm = re.sub(r"[^\w\s]", "", b.lower().strip())
        a_norm = re.sub(r"\s+", " ", a_norm)
        b_norm = re.sub(r"\s+", " ", b_norm)
        if a_norm == b_norm:
            return True
        a_words, b_words = set(a_norm.split()), set(b_norm.split())
        if not a_words or not b_words:
            return False
        jaccard = len(a_words & b_words) / len(a_words | b_words)
        return jaccard > 0.9

    def _detect_contradiction(self, a: str, b: str) -> bool:
        a_lower, b_lower = a.lower(), b.lower()
        if f"not {b_lower}" in a_lower or f"not {a_lower}" in b_lower:
            return True
        patterns = [
            (r"uses?\s+(\w+)", r"uses?\s+(\w+)"),
            (r"is\s+(\w+)", r"is\s+not\s+(\w+)"),
            (r"is\s+not\s+(\w+)", r"is\s+(\w+)"),
            (r"deployed\s+on\s+(\w+)", r"deployed\s+on\s+(\w+)"),
            (r"runs?\s+on\s+(\w+)", r"runs?\s+on\s+(\w+)"),
            (r"prefers?\s+(\w+)", r"prefers?\s+(\w+)"),
        ]
        for pat_a, pat_b in patterns:
            ma = re.search(pat_a, a_lower)
            mb = re.search(pat_b, b_lower)
            if ma and mb and ma.group(1) != mb.group(1):
                return True
        return False

    def _is_refinement(self, existing: str, new: str) -> bool:
        exist_words = set(re.findall(r"\w+", existing.lower()))
        new_words = set(re.findall(r"\w+", new.lower()))
        if not exist_words:
            return False
        overlap = len(exist_words & new_words) / len(exist_words)
        if overlap < 0.7:
            return False
        if len(new) <= len(existing) * 1.1:
            return False
        indicators = ["specifically", "particularly", "especially", "namely", "called", "known as", "such as", "including"]
        return any(ind in new.lower() for ind in indicators) or len(new_words) > len(exist_words) * 1.3

    def _is_expansion(self, existing: str, new: str) -> bool:
        exist_words = set(re.findall(r"\w+", existing.lower()))
        new_words = set(re.findall(r"\w+", new.lower()))
        if not exist_words:
            return False
        overlap = len(exist_words & new_words) / len(exist_words)
        if overlap < 0.5:
            return False
        new_unique = new_words - exist_words
        return len(new_unique) >= 3

    def _cosine_similarity(self, a, b):
        a_arr, b_arr = np.array(a), np.array(b)
        dot = np.dot(a_arr, b_arr)
        na, nb = np.linalg.norm(a_arr), np.linalg.norm(b_arr)
        return 0.0 if na == 0 or nb == 0 else float(dot / (na * nb))

    async def _reinforce_memory(self, db_session, existing, new_evidence):
        old_conf = existing.confidence
        boost = (1.0 - old_conf) * 0.2
        existing.confidence = round(min(0.99, old_conf + boost), 3)
        existing.importance = max(existing.importance, new_evidence.importance)
        event = MemoryEvent(
            id=str(uuid.uuid4()), memory_id=existing.id, event_type="reinforce",
            details={"previous_confidence": old_conf, "new_confidence": existing.confidence, "evidence_memory_id": new_evidence.id},
            timestamp=datetime.now(timezone.utc), agent_id=new_evidence.agent_id or "system"
        )
        db_session.add(event)
        await db_session.commit()
        return existing

    async def _create_refined_version(self, db_session, existing, new_memory):
        evo = MemoryEvolution()
        return await evo.create_version(
            db_session=db_session, memory_id=existing.id, new_content=new_memory.content,
            change_type=ChangeType.REFINE, change_reason=f"Refined: {new_memory.content[:100]}",
            actor_id=new_memory.agent_id or "system",
            confidence=min(0.99, existing.confidence + 0.05), importance=max(existing.importance, new_memory.importance)
        )

    async def _create_expanded_version(self, db_session, existing, new_memory):
        combined = f"{existing.content} Additionally: {new_memory.content}"
        evo = MemoryEvolution()
        return await evo.create_version(
            db_session=db_session, memory_id=existing.id, new_content=combined,
            change_type=ChangeType.EXPAND, change_reason=f"Expanded: {new_memory.content[:100]}",
            actor_id=new_memory.agent_id or "system",
            confidence=min(0.95, existing.confidence + 0.03), importance=max(existing.importance, new_memory.importance)
        )

    async def _create_contradiction(self, db_session, existing, new_memory):
        conflict = MemoryConflict(
            id=str(uuid.uuid4()), memory_a_id=existing.id, memory_b_id=new_memory.id,
            conflict_type="value_mismatch",
            description=f"Contradiction: '{existing.content[:100]}' vs '{new_memory.content[:100]}'",
            severity=0.8, status="unresolved"
        )
        db_session.add(conflict)
        event_a = MemoryEvent(id=str(uuid.uuid4()), memory_id=existing.id, event_type="contradicted",
            details={"by_memory_id": new_memory.id}, timestamp=datetime.now(timezone.utc))
        event_b = MemoryEvent(id=str(uuid.uuid4()), memory_id=new_memory.id, event_type="contradicts",
            details={"existing_memory_id": existing.id}, timestamp=datetime.now(timezone.utc))
        db_session.add(event_a)
        db_session.add(event_b)
        await db_session.commit()
        return conflict

    async def _mark_duplicate(self, db_session, duplicate, original):
        duplicate.status = MemoryStatus.DELETED
        original.confidence = min(0.99, original.confidence + 0.02)
        event = MemoryEvent(id=str(uuid.uuid4()), memory_id=original.id, event_type="duplicate_detected",
            details={"duplicate_memory_id": duplicate.id}, timestamp=datetime.now(timezone.utc))
        db_session.add(event)
        await db_session.commit()

    async def _create_relationship(self, db_session, source, target, rel_type):
        rel = MemoryRelationship(
            id=str(uuid.uuid4()), 
            from_id=source.id, 
            to_id=target.id,
            relationship_type=rel_type, 
            strength=0.7
        )
        db_session.add(rel)
        await db_session.commit()