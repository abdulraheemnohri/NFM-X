# NFM-X V2 Development Prompt
## Evolution Engine, Pattern Discovery, MCP Server, OCR & Advanced Memory Systems

> **INSTRUCTION:** Build ONLY what is listed in V2 Scope. V1 and V1.5 MUST be complete, tested, and stable. No placeholder code. No stubs.

---

## 1. PREREQUISITE

V1 and V1.5 MUST be complete and passing all tests.

---

## 2. V2 SCOPE

### IN SCOPE:

| # | Module | Description |
|---|--------|-------------|
| 1 | **Evolution Engine** | Auto-compare new memories with existing. Auto-reinforce, refine, expand, detect contradictions. |
| 2 | **Pattern Discovery** | Identify recurring patterns across memories. Cluster similar experiences. |
| 3 | **Skill Learning** | Convert repeated successful procedures into reusable skills. |
| 4 | **Causal Memory** | Store and query cause-effect relationships. |
| 5 | **Multimodal Memory** | Ingest images, PDFs, audio transcripts. Extract text/entities. |
| 6 | **OCR Subsystem** | Full OCR: document -> text + layout + entities -> memory. |
| 7 | **MCP Server** | Model Context Protocol server. Expose memory tools to AI agents. |
| 8 | **Memory Replay** | Replay complete evolution timeline of any memory. |
| 9 | **Memory Debugger** | Inspector showing why a memory was retrieved, lineage, confidence trajectory. |
| 10 | **Advanced Consolidation** | Background jobs: duplicate detection, pattern discovery, graph optimization. |
| 11 | **Android SDK** | Native Android client. Remote API mode + offline core. |

### OUT OF SCOPE:

- Cross-agent memory sharing
- Predictive memory / world model
- Strategy learning
- Cross-device sync
- Cryptographic checkpoints
- Real-time collaborative editing
- Advanced memory compression
- Memory simulation sandbox
- Encrypted storage at rest
- Multi-tenant SaaS

---

## 3. TECH STACK ADDITIONS

```
python-multipart     >= 0.0.6
Pillow               >= 10.0.0
pymupdf              >= 1.23.0
easyocr              >= 1.7.0
schedule             >= 1.2.0
apscheduler          >= 3.10.0
mcp                  >= 1.0.0

# Android
Kotlin               >= 1.9.0
Jetpack Compose      >= 2024.01
Room                 >= 2.6.0
OkHttp               >= 4.12.0
Gson                 >= 2.10.0
```

---

## 4. IMPLEMENTATION ORDER

**Phase 1:** Evolution Engine + API
**Phase 2:** Background Consolidation + Pattern Discovery
**Phase 3:** Causal Memory + Skill Learning
**Phase 4:** Multimodal + OCR
**Phase 5:** MCP Server
**Phase 6:** Memory Replay + Debugger API
**Phase 7:** Dashboard Updates (Evolution, Patterns, Skills, Debugger, OCR pages)
**Phase 8:** Android SDK

---

## 5. MODULE 1: EVOLUTION ENGINE

### 5.1 Core Logic (`backend/app/memory/evolution.py`)

```python
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import re
import numpy as np

from ..memory.models import Memory, MemoryVersion, MemoryEvent, MemoryConflict, MemoryRelationship, MemoryStatus, ChangeType
from ..embeddings.models import get_embedding_model
from ..config import settings

class EvolutionEngine:
    """Automatically compares new memories with existing and decides relationship."""

    def __init__(self):
        self.embedding_model = get_embedding_model()
        self.similarity_threshold = 0.85
        self.reinforce_threshold = 0.75
        self.contradiction_threshold = 0.70

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

        new_embedding = self.embedding_model.embed(new_memory.content)
        scored = []
        for mem in candidates:
            mem_embedding = self.embedding_model.embed(mem.content)
            similarity = self._cosine_similarity(new_embedding, mem_embedding)
            scored.append((mem, similarity))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [mem for mem, score in scored[:limit] if score > 0.5]

    def _analyze_relationship(self, new_mem: Memory, existing: Memory) -> str:
        new_emb = self.embedding_model.embed(new_mem.content)
        exist_emb = self.embedding_model.embed(existing.content)
        similarity = self._cosine_similarity(new_emb, exist_emb)

        if similarity >= self.similarity_threshold:
            if self._is_near_duplicate(new_mem.content, existing.content):
                return "DUPLICATE"

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
        a_norm = re.sub(r"\s+", " ", a.lower().strip())
        b_norm = re.sub(r"\s+", " ", b.lower().strip())
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
            (r"is\s+(\w+)", r"is\s+(\w+)"),
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
        from ..memory.evolution import MemoryEvolution
        evo = MemoryEvolution()
        return await evo.create_version(
            db_session=db_session, memory_id=existing.id, new_content=new_memory.content,
            change_type=ChangeType.REFINE, change_reason=f"Refined: {new_memory.content[:100]}",
            actor_id=new_memory.agent_id or "system",
            confidence=min(0.99, existing.confidence + 0.05), importance=max(existing.importance, new_memory.importance)
        )

    async def _create_expanded_version(self, db_session, existing, new_memory):
        combined = f"{existing.content} Additionally: {new_memory.content}"
        from ..memory.evolution import MemoryEvolution
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
        rel = MemoryRelationship(id=str(uuid.uuid4()), memory_id=source.id, related_id=target.id,
            relationship_type=rel_type, confidence=0.7)
        db_session.add(rel)
        await db_session.commit()
```

### 5.2 Evolution API (`backend/app/api/evolution.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select

from ..storage.database import get_db_session
from ..memory.models import Memory, MemoryEvent
from ..memory.evolution import EvolutionEngine

router = APIRouter()

class EvolutionTriggerRequest(BaseModel):
    memory_id: str

class EvolutionResult(BaseModel):
    memory_id: str
    action: str
    details: Dict[str, Any]
    timestamp: str

@router.post("/evolve")
async def trigger_evolution(request: EvolutionTriggerRequest, db_session=Depends(get_db_session)):
    result = await db_session.execute(select(Memory).where(Memory.id == request.memory_id))
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    engine = EvolutionEngine()
    evolution_result = await engine.evolve(db_session, memory)
    return EvolutionResult(
        memory_id=request.memory_id, action=evolution_result["action"],
        details=evolution_result["details"], timestamp=datetime.now(timezone.utc).isoformat()
    )

@router.get("/memory/{memory_id}/evolution")
async def get_evolution_history(memory_id: str, db_session=Depends(get_db_session)):
    stmt = select(MemoryEvent).where(
        MemoryEvent.memory_id == memory_id,
        MemoryEvent.event_type.in_(["reinforce", "refine", "expand", "contradicted", "duplicate_detected"])
    ).order_by(MemoryEvent.timestamp.desc())
    result = await db_session.execute(stmt)
    events = result.scalars().all()
    return {
        "memory_id": memory_id,
        "evolution_events": [{"event_type": e.event_type, "details": e.details,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None, "agent_id": e.agent_id} for e in events]
    }
```

---

## 6. MODULE 2: PATTERN DISCOVERY

### 6.1 Pattern Engine (`backend/app/memory/patterns.py`)

```python
from typing import List, Dict, Any, Optional
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import uuid
import numpy as np

from ..memory.models import Memory, MemoryPattern, MemoryType, MemoryStatus
from ..embeddings.models import get_embedding_model

class PatternDiscoveryEngine:
    def __init__(self):
        self.embedding_model = get_embedding_model()
        self.min_cluster_size = 3
        self.similarity_threshold = 0.75

    async def discover_patterns(self, db_session: AsyncSession, agent_id: Optional[str] = None,
                                 memory_type: Optional[MemoryType] = None) -> List[MemoryPattern]:
        stmt = select(Memory).where(Memory.status == MemoryStatus.ACTIVE)
        if agent_id:
            stmt = stmt.where(Memory.agent_id == agent_id)
        if memory_type:
            stmt = stmt.where(Memory.type == memory_type)
        result = await db_session.execute(stmt)
        memories = result.scalars().all()
        if len(memories) < self.min_cluster_size:
            return []
        clusters = self._cluster_memories(memories)
        patterns = []
        for cluster in clusters:
            if len(cluster) >= self.min_cluster_size:
                pattern = await self._create_pattern(db_session, cluster)
                patterns.append(pattern)
        return patterns

    def _cluster_memories(self, memories: List[Memory]) -> List[List[Memory]]:
        if not memories:
            return []
        embeddings = {mem.id: self.embedding_model.embed(mem.content) for mem in memories}
        clusters, used = [], set()
        for mem in memories:
            if mem.id in used:
                continue
            cluster, used_add = [mem], {mem.id}
            mem_emb = embeddings[mem.id]
            for other in memories:
                if other.id in used or other.id in used_add:
                    continue
                sim = self._cosine_similarity(mem_emb, embeddings[other.id])
                if sim >= self.similarity_threshold:
                    cluster.append(other)
                    used_add.add(other.id)
            if len(cluster) >= self.min_cluster_size:
                clusters.append(cluster)
                used.update(used_add)
        return clusters

    async def _create_pattern(self, db_session, cluster):
        all_words = []
        for mem in cluster:
            all_words.extend(mem.content.lower().split())
        word_freq = defaultdict(int)
        for w in all_words:
            if len(w) > 3:
                word_freq[w] += 1
        common = [w for w, freq in word_freq.items() if freq >= len(cluster) * 0.5]
        pattern = MemoryPattern(
            id=str(uuid.uuid4()), pattern_type="semantic_cluster",
            name=f"Pattern: {' '.join(common[:5])}",
            description=f"Pattern across {len(cluster)} memories",
            supporting_memories=[m.id for m in cluster],
            pattern_data={"common_terms": common[:10], "memory_count": len(cluster),
                          "types": list(set(m.type.value for m in cluster))},
            confidence=0.7, strength=min(1.0, len(cluster) / 10.0),
            discovered_at=datetime.now(timezone.utc)
        )
        db_session.add(pattern)
        await db_session.commit()
        return pattern

    def _cosine_similarity(self, a, b):
        a_arr, b_arr = np.array(a), np.array(b)
        dot = np.dot(a_arr, b_arr)
        na, nb = np.linalg.norm(a_arr), np.linalg.norm(b_arr)
        return 0.0 if na == 0 or nb == 0 else float(dot / (na * nb))
```

---

## 7. MODULE 3: SKILL LEARNING

### 7.1 Skill Engine (`backend/app/memory/skills.py`)

```python
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from ..memory.models import Memory, MemoryProcedure, MemorySkill, MemoryType, MemoryStatus

class SkillLearningEngine:
    async def learn_skill_from_procedure(self, db_session: AsyncSession, procedure_name: str,
                                          agent_id: Optional[str] = None) -> Optional[MemorySkill]:
        stmt = select(MemoryProcedure).where(MemoryProcedure.name == procedure_name)
        result = await db_session.execute(stmt)
        procedures = result.scalars().all()
        if not procedures:
            return None
        total = len(procedures)
        successes = sum(1 for p in procedures if p.success_count > 0)
        success_rate = successes / total if total > 0 else 0
        if success_rate < 0.7 or total < 3:
            return None
        skill = MemorySkill(
            id=str(uuid.uuid4()), name=procedure_name,
            description=f"Skill from {total} executions ({success_rate:.0%} success)",
            source_procedure_ids=[p.id for p in procedures],
            success_rate=success_rate, execution_count=total,
            confidence=min(0.95, 0.5 + success_rate * 0.4),
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(skill)
        await db_session.commit()
        return skill

    async def evaluate_procedure_execution(self, db_session, procedure_id: str, success: bool,
                                            error_message: Optional[str] = None):
        result = await db_session.execute(select(MemoryProcedure).where(MemoryProcedure.id == procedure_id))
        proc = result.scalar_one_or_none()
        if not proc:
            raise ValueError(f"Procedure {procedure_id} not found")
        proc.execution_count += 1
        if success:
            proc.success_count += 1
        else:
            proc.failure_count += 1
            current = proc.metadata.get("failure_log", [])
            current.append({"timestamp": datetime.now(timezone.utc).isoformat(), "error": error_message})
            proc.metadata["failure_log"] = current
        proc.success_rate = proc.success_count / proc.execution_count
        proc.last_executed = datetime.now(timezone.utc)
        await db_session.commit()
        return proc
```

---

## 8. MODULE 4: CAUSAL MEMORY

### 8.1 Causal Engine (`backend/app/memory/causal.py`)

```python
from typing import List, Dict, Any, Optional
import re
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from ..memory.models import Memory, MemoryRelationship, MemoryType, MemoryStatus

class CausalExtractionEngine:
    CAUSAL_PATTERNS = [
        (r"(\w+(?:\s+\w+){0,5})\s+caused?\s+(\w+(?:\s+\w+){0,10})", "caused"),
        (r"(\w+(?:\s+\w+){0,5})\s+led?\s+to\s+(\w+(?:\s+\w+){0,10})", "led_to"),
        (r"(\w+(?:\s+\w+){0,5})\s+resulted?\s+in\s+(\w+(?:\s+\w+){0,10})", "resulted_in"),
        (r"because\s+(\w+(?:\s+\w+){0,10})\s*,?\s+(\w+(?:\s+\w+){0,10})", "because"),
        (r"if\s+(\w+(?:\s+\w+){0,10})\s*,?\s+then\s+(\w+(?:\s+\w+){0,10})", "if_then"),
        (r"(\w+(?:\s+\w+){0,5})\s+increased?\s+(\w+(?:\s+\w+){0,10})", "increased"),
        (r"(\w+(?:\s+\w+){0,5})\s+decreased?\s+(\w+(?:\s+\w+){0,10})", "decreased"),
    ]

    def extract_causal_relationships(self, content: str) -> List[Dict[str, str]]:
        relationships = []
        for pattern, rel_type in self.CAUSAL_PATTERNS:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                cause, effect = match.group(1).strip(), match.group(2).strip()
                if len(cause) > 3 and len(effect) > 3:
                    relationships.append({"cause": cause, "effect": effect,
                                          "relationship_type": rel_type, "source_text": match.group(0)})
        return relationships

    async def store_causal_memory(self, db_session, source_memory_id: str, cause: str, effect: str, relationship_type: str):
        content = f"Cause: {cause}. Effect: {effect}. Relationship: {relationship_type}"
        mem = Memory(
            id=str(uuid.uuid4()), root_id=str(uuid.uuid4()), version=1,
            type=MemoryType.CAUSAL, content=content, normalized_content=content.lower(),
            source_id=source_memory_id, confidence=0.6, importance=0.7,
            status=MemoryStatus.ACTIVE, created_at=datetime.now(timezone.utc),
            observed_at=datetime.now(timezone.utc), valid_from=datetime.now(timezone.utc),
            metadata={"cause": cause, "effect": effect, "relationship_type": relationship_type,
                      "source_memory_id": source_memory_id, "verified": False}
        )
        db_session.add(mem)
        rel = MemoryRelationship(id=str(uuid.uuid4()), memory_id=source_memory_id, related_id=mem.id,
            relationship_type="causes", confidence=0.6)
        db_session.add(rel)
        await db_session.commit()
        return mem
```

---

## 9. MODULE 5: MULTIMODAL MEMORY

### 9.1 Processor (`backend/app/multimodal/processor.py`)

```python
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timezone
import uuid
from fastapi import UploadFile
from PIL import Image
import fitz
from io import BytesIO

class MultimodalProcessor:
    SUPPORTED_TYPES = {
        "image": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"],
        "pdf": [".pdf"],
        "document": [".txt", ".md", ".json", ".csv"],
        "audio": [".wav", ".mp3", ".m4a", ".ogg"],
    }

    def detect_type(self, filename: str) -> Optional[str]:
        ext = Path(filename).suffix.lower()
        for file_type, extensions in self.SUPPORTED_TYPES.items():
            if ext in extensions:
                return file_type
        return None

    async def process_file(self, file: UploadFile, agent_id: Optional[str] = None) -> Dict[str, Any]:
        file_type = self.detect_type(file.filename)
        if not file_type:
            raise ValueError(f"Unsupported file type: {file.filename}")
        content = await file.read()
        if file_type == "image":
            return await self._process_image(content, file.filename, agent_id)
        elif file_type == "pdf":
            return await self._process_pdf(content, file.filename, agent_id)
        elif file_type == "document":
            return await self._process_document(content, file.filename, agent_id)
        elif file_type == "audio":
            return await self._process_audio(content, file.filename, agent_id)
        return {"error": "Unknown file type"}

    async def _process_image(self, content, filename, agent_id):
        doc_id = f"IMG-{uuid.uuid4().hex[:8]}"
        storage_path = Path(f"./storage/objects/{doc_id}_{filename}")
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        storage_path.write_bytes(content)
        img = Image.open(BytesIO(content))
        return {"document_id": doc_id, "type": "image", "filename": filename,
                "file_path": str(storage_path), "dimensions": {"width": img.width, "height": img.height},
                "agent_id": agent_id, "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "pending_ocr"}

    async def _process_pdf(self, content, filename, agent_id):
        doc_id = f"PDF-{uuid.uuid4().hex[:8]}"
        storage_path = Path(f"./storage/objects/{doc_id}_{filename}")
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        storage_path.write_bytes(content)
        doc = fitz.open(stream=content, filetype="pdf")
        pages = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            pages.append({"page_number": page_num + 1, "text": text, "word_count": len(text.split())})
        doc.close()
        return {"document_id": doc_id, "type": "pdf", "filename": filename,
                "file_path": str(storage_path), "page_count": len(pages), "pages": pages,
                "agent_id": agent_id, "timestamp": datetime.now(timezone.utc).isoformat()}

    async def _process_document(self, content, filename, agent_id):
        doc_id = f"DOC-{uuid.uuid4().hex[:8]}"
        text = content.decode("utf-8", errors="replace")
        return {"document_id": doc_id, "type": "document", "filename": filename,
                "text": text, "word_count": len(text.split()),
                "agent_id": agent_id, "timestamp": datetime.now(timezone.utc).isoformat()}

    async def _process_audio(self, content, filename, agent_id):
        doc_id = f"AUD-{uuid.uuid4().hex[:8]}"
        storage_path = Path(f"./storage/objects/{doc_id}_{filename}")
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        storage_path.write_bytes(content)
        return {"document_id": doc_id, "type": "audio", "filename": filename,
                "file_path": str(storage_path), "agent_id": agent_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "pending_transcription",
                "note": "Audio transcription requires external STT service"}
```

### 9.2 Multimodal API (`backend/app/api/multimodal.py`)

```python
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional

from ..multimodal.processor import MultimodalProcessor

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), agent_id: Optional[str] = Form(None)):
    processor = MultimodalProcessor()
    return await processor.process_file(file, agent_id)

@router.post("/extract-memory")
async def extract_memory_from_file(file: UploadFile = File(...), agent_id: Optional[str] = Form(None),
                                    memory_type: Optional[str] = Form("semantic")):
    processor = MultimodalProcessor()
    processed = await processor.process_file(file, agent_id)
    texts = []
    if processed["type"] == "pdf":
        for page in processed.get("pages", []):
            texts.append(page["text"])
    elif processed["type"] in ("document", "image"):
        texts.append(processed.get("text", ""))
    combined = "\n\n".join(texts)
    return {"document_id": processed["document_id"], "extracted_text": combined[:5000],
            "word_count": len(combined.split()), "suggested_memory_type": memory_type, "status": "extracted"}
```

---

## 10. MODULE 6: OCR SUBSYSTEM

### 10.1 OCR Engine (`backend/app/ocr/engine.py`)

```python
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, timezone
import uuid
import easyocr
from PIL import Image
import numpy as np

class OCREngine:
    def __init__(self, languages: List[str] = None):
        self.languages = languages or ["en"]
        self._reader = None

    def _get_reader(self):
        if self._reader is None:
            self._reader = easyocr.Reader(self.languages, gpu=False)
        return self._reader

    async def process_image(self, image_path: str, document_id: Optional[str] = None) -> Dict[str, Any]:
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        reader = self._get_reader()
        img = Image.open(path)
        img_array = np.array(img)
        results = reader.readtext(img_array)
        regions, full_text_parts, total_confidence = [], [], 0.0
        for bbox, text, conf in results:
            regions.append({"text": text, "confidence": round(conf, 3),
                            "bbox": [[int(x), int(y)] for x, y in bbox]})
            full_text_parts.append(text)
            total_confidence += conf
        avg_confidence = total_confidence / len(results) if results else 0.0
        return {"document_id": document_id or f"OCR-{uuid.uuid4().hex[:8]}",
                "file_path": str(path), "text": " ".join(full_text_parts),
                "confidence": round(avg_confidence, 3), "language": self.languages[0],
                "regions": regions, "region_count": len(regions),
                "processed_at": datetime.now(timezone.utc).isoformat()}

    async def process_pdf(self, pdf_path: str, document_id: Optional[str] = None) -> Dict[str, Any]:
        import fitz
        path = Path(pdf_path)
        doc = fitz.open(path)
        all_pages = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=200)
            img_path = f"./storage/temp/page_{page_num}.png"
            pix.save(img_path)
            page_result = await self.process_image(img_path, document_id)
            page_result["page_number"] = page_num + 1
            all_pages.append(page_result)
        doc.close()
        combined_text = "\n\n".join(p["text"] for p in all_pages)
        avg_conf = sum(p["confidence"] for p in all_pages) / len(all_pages) if all_pages else 0
        return {"document_id": document_id or f"OCR-{uuid.uuid4().hex[:8]}", "file_path": str(path),
                "type": "pdf", "page_count": len(all_pages), "pages": all_pages,
                "text": combined_text, "confidence": round(avg_conf, 3),
                "processed_at": datetime.now(timezone.utc).isoformat()}
```

### 10.2 OCR API (`backend/app/api/ocr.py`)

```python
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from pathlib import Path

from ..ocr.engine import OCREngine

router = APIRouter()

@router.post("/ocr/image")
async def ocr_image(file: UploadFile = File(...), language: Optional[str] = Form("en")):
    temp_path = f"./storage/temp/{file.filename}"
    Path("./storage/temp").mkdir(parents=True, exist_ok=True)
    content = await file.read()
    Path(temp_path).write_bytes(content)
    engine = OCREngine(languages=[language])
    return await engine.process_image(temp_path)

@router.post("/ocr/pdf")
async def ocr_pdf(file: UploadFile = File(...), language: Optional[str] = Form("en")):
    temp_path = f"./storage/temp/{file.filename}"
    Path("./storage/temp").mkdir(parents=True, exist_ok=True)
    content = await file.read()
    Path(temp_path).write_bytes(content)
    engine = OCREngine(languages=[language])
    return await engine.process_pdf(temp_path)
```

---

## 11. MODULE 7: MCP SERVER

### 11.1 MCP Server (`backend/app/mcp/server.py`)

```python
from typing import Any, Dict, List
import json
from mcp.server import Server
from mcp.types import TextContent, Tool
from sdk.python.nfm.client import NFMClient
from sdk.python.nfm.models import MemoryCreate

class NFMMCPService:
    def __init__(self, nfm_base_url: str = "http://localhost:8765"):
        self.nfm = NFMClient(base_url=nfm_base_url)
        self.server = Server("nfm-x-mcp")
        self._register_tools()

    def _register_tools(self):
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(name="memory_search", description="Search NFM-X memories",
                     inputSchema={"type": "object", "properties": {
                         "query": {"type": "string"}, "agent_id": {"type": "string"},
                         "limit": {"type": "integer", "default": 10}}, "required": ["query"]}),
                Tool(name="memory_recall", description="Get memory by ID",
                     inputSchema={"type": "object", "properties": {"memory_id": {"type": "string"}}, "required": ["memory_id"]}),
                Tool(name="memory_context", description="Build context for task",
                     inputSchema={"type": "object", "properties": {
                         "agent_id": {"type": "string"}, "query": {"type": "string"},
                         "max_memories": {"type": "integer", "default": 10}}, "required": ["agent_id", "query"]}),
                Tool(name="memory_store", description="Store a new memory",
                     inputSchema={"type": "object", "properties": {
                         "type": {"type": "string", "enum": ["episodic", "semantic", "preference", "decision", "failure", "success"]},
                         "content": {"type": "string"}, "agent_id": {"type": "string"},
                         "confidence": {"type": "number"}, "importance": {"type": "number"}},
                     "required": ["type", "content"]}),
                Tool(name="memory_history", description="Get memory version history",
                     inputSchema={"type": "object", "properties": {"memory_id": {"type": "string"}}, "required": ["memory_id"]}),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if name == "memory_search":
                    result = self.nfm.search({"query": arguments["query"], "agent_id": arguments.get("agent_id"),
                                               "limit": arguments.get("limit", 10)})
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                elif name == "memory_recall":
                    result = self.nfm.get_memory(arguments["memory_id"])
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                elif name == "memory_context":
                    result = self.nfm.get_context({"agent_id": arguments["agent_id"], "query": arguments["query"],
                                                    "max_memories": arguments.get("max_memories", 10)})
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                elif name == "memory_store":
                    mem = MemoryCreate(**{k: v for k, v in arguments.items() if v is not None})
                    result = self.nfm.create_memory(mem)
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                elif name == "memory_history":
                    result = self.nfm.get_history(arguments["memory_id"])
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    def run(self, transport: str = "stdio"):
        if transport == "stdio":
            from mcp.server.stdio import stdio_server
            import asyncio
            async def main():
                async with stdio_server() as (read_stream, write_stream):
                    await self.server.run(read_stream, write_stream, self.server.create_initialization_options())
            asyncio.run(main())
```

---

## 12. MODULE 8: BACKGROUND CONSOLIDATION

### 12.1 Scheduler & Jobs

```python
# backend/app/workers/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

logger = logging.getLogger(__name__)
_scheduler = None

def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler

def start_scheduler():
    scheduler = get_scheduler()
    scheduler.start()
    logger.info("Background scheduler started")

def stop_scheduler():
    scheduler = get_scheduler()
    scheduler.shutdown()
    logger.info("Background scheduler stopped")
```

```python
# backend/app/workers/jobs.py
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from ..storage.database import _async_session_maker
from ..memory.models import Memory, MemoryStatus
from ..memory.patterns import PatternDiscoveryEngine

logger = logging.getLogger(__name__)

async def run_consolidation_job():
    logger.info("Starting consolidation job...")
    async with _async_session_maker() as session:
        pattern_engine = PatternDiscoveryEngine()
        patterns = await pattern_engine.discover_patterns(session)
        logger.info(f"Discovered {len(patterns)} patterns")
        await _recalculate_confidences(session)
        await _detect_stale_memories(session)
        await session.commit()
    logger.info("Consolidation job completed")

async def _recalculate_confidences(session):
    from sqlalchemy import func
    stmt = select(Memory).where(Memory.status == MemoryStatus.ACTIVE)
    result = await session.execute(stmt)
    memories = result.scalars().all()
    now = datetime.now(timezone.utc)
    for mem in memories:
        if mem.created_at:
            age_days = (now - mem.created_at).days
            if age_days > 90 and mem.confidence > 0.5:
                decay = min(0.1, age_days / 1000)
                mem.confidence = max(0.3, mem.confidence - decay)

async def _detect_stale_memories(session):
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    stmt = select(Memory).where(Memory.type == "working", Memory.status == MemoryStatus.ACTIVE, Memory.created_at < cutoff)
    result = await session.execute(stmt)
    stale = result.scalars().all()
    for mem in stale:
        mem.status = MemoryStatus.ARCHIVED
        logger.info(f"Archived stale working memory: {mem.id}")
```

---

## 13. MODULE 9: MEMORY REPLAY & DEBUGGER

### 13.1 Replay API (`backend/app/api/replay.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from typing import List, Dict, Any

from ..storage.database import get_db_session
from ..memory.models import Memory, MemoryVersion, MemoryEvent, MemoryConflict

router = APIRouter()

@router.get("/memory/{memory_id}/replay")
async def replay_memory_evolution(memory_id: str, db_session=Depends(get_db_session)):
    """Replay complete evolution of a memory."""
    result = await db_session.execute(select(Memory).where(Memory.id == memory_id))
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    # Get all versions
    versions_result = await db_session.execute(
        select(MemoryVersion).where(MemoryVersion.memory_id == memory_id).order_by(MemoryVersion.version)
    )
    versions = versions_result.scalars().all()

    # Get all events
    events_result = await db_session.execute(
        select(MemoryEvent).where(MemoryEvent.memory_id == memory_id).order_by(MemoryEvent.timestamp)
    )
    events = events_result.scalars().all()

    # Get conflicts
    conflicts_result = await db_session.execute(
        select(MemoryConflict).where(
            (MemoryConflict.memory_a_id == memory_id) | (MemoryConflict.memory_b_id == memory_id)
        )
    )
    conflicts = conflicts_result.scalars().all()

    timeline = []
    for v in versions:
        timeline.append({
            "type": "version", "version": v.version, "content": v.content,
            "change_type": v.change_type.value, "change_reason": v.change_reason,
            "confidence": v.confidence, "created_at": v.created_at.isoformat() if v.created_at else None
        })
    for e in events:
        timeline.append({
            "type": "event", "event_type": e.event_type, "details": e.details,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None, "agent_id": e.agent_id
        })
    for c in conflicts:
        timeline.append({
            "type": "conflict", "conflict_id": c.id, "conflict_type": c.conflict_type,
            "severity": c.severity, "status": c.status, "created_at": c.created_at.isoformat() if c.created_at else None
        })

    timeline.sort(key=lambda x: x.get("created_at") or x.get("timestamp") or "")

    return {
        "memory_id": memory_id,
        "current_content": memory.content,
        "current_confidence": memory.confidence,
        "total_versions": len(versions),
        "total_events": len(events),
        "total_conflicts": len(conflicts),
        "timeline": timeline
    }
```

### 13.2 Debugger API (`backend/app/api/debugger.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from typing import Dict, Any

from ..storage.database import get_db_session
from ..memory.models import Memory, MemoryEvent, MemoryRelationship

router = APIRouter()

@router.get("/memory/{memory_id}/debug")
async def debug_memory(memory_id: str, db_session=Depends(get_db_session)):
    """Debug inspector for a memory."""
    result = await db_session.execute(select(Memory).where(Memory.id == memory_id))
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    # Event counts
    events_result = await db_session.execute(
        select(MemoryEvent.event_type, func.count(MemoryEvent.id))
        .where(MemoryEvent.memory_id == memory_id)
        .group_by(MemoryEvent.event_type)
    )
    event_counts = {row.event_type: row.count for row in events_result}

    # Relationship counts
    rel_result = await db_session.execute(
        select(func.count(MemoryRelationship.id)).where(MemoryRelationship.memory_id == memory_id)
    )
    outgoing_rels = rel_result.scalar() or 0

    rel_result2 = await db_session.execute(
        select(func.count(MemoryRelationship.id)).where(MemoryRelationship.related_id == memory_id)
    )
    incoming_rels = rel_result2.scalar() or 0

    return {
        "memory_id": memory_id,
        "type": memory.type.value,
        "content_preview": memory.content[:200],
        "confidence": memory.confidence,
        "importance": memory.importance,
        "status": memory.status.value,
        "version": memory.version,
        "event_summary": event_counts,
        "relationships": {"outgoing": outgoing_rels, "incoming": incoming_rels},
        "created_at": memory.created_at.isoformat() if memory.created_at else None,
        "last_observed": memory.observed_at.isoformat() if memory.observed_at else None,
        "metadata": memory.metadata
    }
```

---

## 14. MODULE 10: ANDROID SDK

### 14.1 Core Client (`sdk/android/nfm-android/src/main/java/com/nfm/client/NFMClient.kt`)

```kotlin
package com.nfm.client

import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import com.google.gson.Gson
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.IOException

class NFMClient(
    private val baseUrl: String = "http://localhost:8765",
    private val apiKey: String? = null
) {
    private val client = OkHttpClient()
    private val gson = Gson()
    private val jsonMediaType = "application/json; charset=utf-8".toMediaType()

    private fun buildRequest(method: String, path: String, body: String? = null): Request {
        val builder = Request.Builder().url("$baseUrl$path")
        apiKey?.let { builder.header("Authorization", "Bearer $it") }
        builder.header("Content-Type", "application/json")
        builder.header("Accept", "application/json")
        when (method) {
            "GET" -> builder.get()
            "POST" -> builder.post(body!!.toRequestBody(jsonMediaType))
            "PUT" -> builder.put(body!!.toRequestBody(jsonMediaType))
            "DELETE" -> builder.delete()
        }
        return builder.build()
    }

    suspend fun createMemory(memory: NFMMemory): Result<NFMMemory> = withContext(Dispatchers.IO) {
        try {
            val request = buildRequest("POST", "/v1/memory/", gson.toJson(memory))
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) return@withContext Result.failure(IOException("HTTP ${response.code}"))
                val body = response.body?.string() ?: return@withContext Result.failure(IOException("Empty"))
                Result.success(gson.fromJson(body, NFMMemory::class.java))
            }
        } catch (e: Exception) { Result.failure(e) }
    }

    suspend fun getMemory(memoryId: String): Result<NFMMemory> = withContext(Dispatchers.IO) {
        try {
            val request = buildRequest("GET", "/v1/memory/$memoryId")
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) return@withContext Result.failure(IOException("HTTP ${response.code}"))
                val body = response.body?.string() ?: return@withContext Result.failure(IOException("Empty"))
                Result.success(gson.fromJson(body, NFMMemory::class.java))
            }
        } catch (e: Exception) { Result.failure(e) }
    }

    suspend fun searchMemories(query: String, agentId: String? = null, limit: Int = 10): Result<SearchResponse> = withContext(Dispatchers.IO) {
        try {
            val searchQuery = SearchQuery(query = query, agent_id = agentId, limit = limit)
            val request = buildRequest("POST", "/v1/memory/search", gson.toJson(searchQuery))
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) return@withContext Result.failure(IOException("HTTP ${response.code}"))
                val body = response.body?.string() ?: return@withContext Result.failure(IOException("Empty"))
                Result.success(gson.fromJson(body, SearchResponse::class.java))
            }
        } catch (e: Exception) { Result.failure(e) }
    }

    suspend fun health(): Result<Map<String, Any>> = withContext(Dispatchers.IO) {
        try {
            val request = buildRequest("GET", "/health")
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) return@withContext Result.failure(IOException("HTTP ${response.code}"))
                val body = response.body?.string() ?: return@withContext Result.failure(IOException("Empty"))
                @Suppress("UNCHECKED_CAST")
                Result.success(gson.fromJson(body, Map::class.java) as Map<String, Any>)
            }
        } catch (e: Exception) { Result.failure(e) }
    }
}
```

### 14.2 Data Models

```kotlin
package com.nfm.client

data class NFMMemory(
    val id: String? = null,
    val root_id: String? = null,
    val version: Int = 1,
    val type: String,
    val content: String,
    val subtype: String? = null,
    val agent_id: String? = null,
    val source_id: String? = null,
    val confidence: Double = 0.7,
    val importance: Double = 0.5,
    val status: String = "active",
    val created_at: String? = null,
    val metadata: Map<String, Any>? = null
)

data class SearchQuery(
    val query: String,
    val agent_id: String? = null,
    val limit: Int = 10,
    val memory_types: List<String>? = null
)

data class SearchResponse(
    val query: String,
    val results: List<MemoryResult>,
    val count: Int
)

data class MemoryResult(
    val id: String,
    val type: String,
    val content: String,
    val confidence: Double,
    val importance: Double,
    val score: Double
)
```

---

## 15. UPDATED MAIN.PY

Add new routers:

```python
from .api import memory, search, context, conflicts, graph, stats, evolution, multimodal, ocr, replay

app.include_router(memory.router, prefix="/v1/memory", tags=["Memory"])
app.include_router(search.router, prefix="/v1/memory", tags=["Search"])
app.include_router(context.router, prefix="/v1/memory", tags=["Context"])
app.include_router(conflicts.router, prefix="/v1", tags=["Conflicts"])
app.include_router(graph.router, prefix="/v1", tags=["Graph"])
app.include_router(stats.router, prefix="/v1", tags=["Stats"])
app.include_router(evolution.router, prefix="/v1", tags=["Evolution"])
app.include_router(multimodal.router, prefix="/v1", tags=["Multimodal"])
app.include_router(ocr.router, prefix="/v1", tags=["OCR"])
app.include_router(replay.router, prefix="/v1", tags=["Replay"])
```

Add scheduler to lifespan:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting NFM-X V2...")
    settings.NFM_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    await init_database(str(settings.NFM_DB_PATH))

    # Start background scheduler
    from .workers.scheduler import start_scheduler, get_scheduler
    from .workers.jobs import run_consolidation_job
    from apscheduler.triggers.interval import IntervalTrigger

    start_scheduler()
    scheduler = get_scheduler()
    scheduler.add_job(run_consolidation_job, IntervalTrigger(hours=1), id="consolidation", replace_existing=True)

    logger.info("NFM-X V2 ready")
    yield

    from .workers.scheduler import stop_scheduler
    stop_scheduler()
    logger.info("Shutting down NFM-X V2...")
```

---

## 16. TESTING REQUIREMENTS

| Module | Tests |
|--------|-------|
| Evolution Engine | Duplicate detection, reinforcement, refinement, expansion, contradiction. |
| Pattern Discovery | Clustering creates patterns. Min cluster size respected. |
| Skill Learning | Skill created after 3+ successful procedures. No skill if success rate < 70%. |
| Causal Memory | Causal patterns extracted correctly. CAUSAL memory created. |
| Multimodal | Image/PDF upload processed. Document text extracted. |
| OCR | Image OCR returns text + confidence + regions. PDF OCR handles multiple pages. |
| MCP Server | All 5 tools callable. Correct responses. |
| Memory Replay | Timeline includes versions, events, conflicts in order. |
| Debugger | Event counts accurate. Relationship counts correct. |
| Android SDK | Create memory, get memory, search, health — all work. |
| Consolidation | Stale working memories archived. Old memory confidence decays. |

---

## 17. CODE QUALITY STANDARDS

Same as V1 + V1.5:
1. Type hints everywhere.
2. No `raise NotImplementedError`.
3. No `pass` in function bodies.
4. Async consistency.
5. Proper error handling.
6. No print statements — use logging.
7. Pydantic v2 / TypeScript strict.
8. SQLAlchemy 2.0 style.
9. UTC timestamps only.
10. Consistent naming.

---

## 18. FINAL CHECKLIST

- [ ] All V1 + V1.5 tests still pass
- [ ] New V2 tests pass (80%+ coverage)
- [ ] Evolution engine correctly classifies relationships
- [ ] Pattern discovery finds real patterns
- [ ] Skill learning triggers after sufficient evidence
- [ ] Causal extraction works on sample texts
- [ ] Multimodal upload processes images and PDFs
- [ ] OCR extracts text with confidence scores
- [ ] MCP server responds to all tool calls
- [ ] Memory replay shows complete timeline
- [ ] Debugger shows accurate metrics
- [ ] Android SDK compiles and basic tests pass
- [ ] Background consolidation runs on schedule
- [ ] No `NotImplementedError` anywhere
- [ ] No `datetime.utcnow()` anywhere

---

**END OF V2 PROMPT.** Build ONLY what is specified above.
