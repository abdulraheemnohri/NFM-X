# NFM-X Master Development Prompt v2
## Non-Forgettable AI Long-Term Memory Layer — V1 Implementation Guide

> **INSTRUCTION:** This is a single, consolidated prompt. Build ONLY what is explicitly listed in the V1 Scope. Everything else is roadmap for future versions. Do not add placeholder files. Do not implement stubs. If a feature is not in V1, do not write code for it.

---

## 1. PROJECT IDENTITY

**NFM-X** is a production-grade, model-independent, local-first long-term memory layer for AI systems. It sits between an AI application and its LLM as middleware.

**Core Promise:** Once memory is committed, it is never silently overwritten or lost. New information creates a new version. History is preserved.

**V1 Goal:** A working, tested, deployable memory API with Python SDK and CLI. Not a prototype. Not a demo. Working code.

---

## 2. NON-NEGOTIABLE RULES

1. **Never silently overwrite permanent memory.** New info = new version row.
2. **Never silently delete historical memory.** Soft delete only (status = deleted).
3. **Never treat vector similarity as truth.** It is retrieval signal only.
4. **Never treat an AI-generated assumption as a confirmed fact.** Confidence must reflect evidence.
5. **Always preserve provenance.** Every memory has a source.
6. **Always preserve memory lineage.** Parent → Child → Version chain.
7. **Always distinguish current knowledge from historical knowledge.** Current = latest active version.
8. **Always preserve contradictions.** Do not auto-resolve. Flag them.
9. **Never send the entire memory database into the model context.** Retrieve only relevant memories.
10. **Keep the memory layer independent from the LLM.** Core works without any LLM.
11. **Core functionality must work locally.** No internet required for V1.
12. **All automatic operations must be auditable.** Every change = event log entry.
13. **User must inspect, correct, export, and explicitly delete memory.**
14. **Memory must remain portable between models and applications.**
15. **No placeholder code.** Every function must do what it says or be excluded from V1.

---

## 3. V1 SCOPE (RUTHLESSLY DEFINED)

### IN SCOPE — Build These:

| # | Module | What It Does |
|---|--------|-------------|
| 1 | **Core Data Layer** | SQLAlchemy async models, SQLite DB, config |
| 2 | **Memory CRUD API** | FastAPI endpoints for create, read, list, history |
| 3 | **Vector Store** | FAISS backend for semantic search |
| 4 | **Local Embeddings** | sentence-transformers (all-MiniLM-L6-v2) |
| 5 | **Hybrid Retrieval** | Keyword + Vector search with simple reranking |
| 6 | **Context Builder** | Select top-N relevant memories for LLM context |
| 7 | **Basic Classification** | Rule-based memory type detection (regex + keywords) |
| 8 | **Python SDK** | HTTP client with retry logic |
| 9 | **CLI** | Basic commands: status, search, get, history, backup |
| 10 | **Tests** | pytest, 80%+ coverage, in-memory test DB |

### OUT OF SCOPE — Do NOT Build in V1:

- Dashboard / Frontend
- TypeScript SDK
- OCR subsystem
- Knowledge Graph queries (relationship table exists, but no graph traversal)
- Evolution Engine (tables exist, but auto-evolution is V2)
- Conflict Resolution Engine (detection exists, resolution is V2)
- Pattern Discovery
- Skill Learning
- Procedural Memory execution
- Android SDK
- MCP Server
- Integrity hash chaining
- Memory compression
- Memory replay / simulator
- Cross-agent memory sharing
- Multimodal memory (images, audio, video)
- Encrypted storage
- Advanced temporal reasoning

---

## 4. TECHNOLOGY STACK (EXACT VERSIONS)

```
Python          >= 3.10
FastAPI         >= 0.110.0
Pydantic        >= 2.5.0
pydantic-settings >= 2.1.0
SQLAlchemy      >= 2.0.25
aiosqlite       >= 0.19.0
faiss-cpu       >= 1.7.4
sentence-transformers >= 2.2.2
numpy           >= 1.24.0
httpx           >= 0.25.0
click           >= 8.1.0
rich            >= 13.7.0
pytest          >= 7.4.0
pytest-asyncio  >= 0.21.0
```

---

## 5. PROJECT STRUCTURE (V1 ONLY)

```
nfm-x/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app, lifespan, CORS
│   │   ├── config.py               # Pydantic Settings
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── memory.py           # CRUD + history endpoints
│   │   │   ├── search.py           # Hybrid search endpoint
│   │   │   └── context.py          # Context builder endpoint
│   │   ├── memory/
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # SQLAlchemy models
│   │   │   ├── classification.py   # Rule-based type classifier
│   │   │   └── capture.py          # Memory capture logic
│   │   ├── retrieval/
│   │   │   ├── __init__.py
│   │   │   └── engine.py           # Hybrid retrieval engine
│   │   ├── embeddings/
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # Embedding model wrapper
│   │   │   └── vector_store.py     # FAISS vector store
│   │   └── storage/
│   │       ├── __init__.py
│   │       └── database.py         # DB engine, session, init
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py             # pytest fixtures
│       ├── test_memory_api.py
│       ├── test_retrieval.py
│       └── test_vector_store.py
├── sdk/
│   └── python/
│       ├── nfm/
│       │   ├── __init__.py
│       │   ├── client.py           # NFMClient
│       │   └── models.py           # Pydantic request/response models
│       └── tests/
│           └── test_client.py
├── cli/
│   └── nfm_cli/
│       ├── __init__.py
│       └── main.py                 # Click CLI
├── storage/                        # Runtime data (gitignored)
├── requirements.txt
└── pytest.ini
```

**NO other directories in V1.** No frontend/, no android/, no mcp/, no docs/ beyond README.

---

## 6. IMPLEMENTATION ORDER

Build in this exact order. Do not skip ahead.

**Phase 1: Foundation**
1. `config.py` — Pydantic settings with .env support
2. `storage/database.py` — Async SQLite engine, session maker, init
3. `memory/models.py` — All SQLAlchemy models
4. Tests for models

**Phase 2: Core Memory**
5. `memory/classification.py` — Rule-based classifier
6. `memory/capture.py` — Capture + persist logic
7. `api/memory.py` — CRUD endpoints
8. Tests for API

**Phase 3: Search**
9. `embeddings/models.py` — Sentence transformer wrapper
10. `embeddings/vector_store.py` — FAISS store
11. `retrieval/engine.py` — Hybrid retrieval
12. `api/search.py` — Search endpoint
13. `api/context.py` — Context builder endpoint
14. Tests for retrieval

**Phase 4: SDK & CLI**
15. `sdk/python/nfm/models.py` — Pydantic models
16. `sdk/python/nfm/client.py` — HTTP client
17. `cli/nfm_cli/main.py` — Click CLI
18. Tests for SDK

**Phase 5: Main & Integration**
19. `main.py` — FastAPI app, routers, lifespan
20. Integration tests
21. `requirements.txt`
22. `pytest.ini`

---

## 7. MODULE 1: CORE DATA LAYER

### 7.1 Config (`backend/app/config.py`)

```python
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    NFM_HOST: str = "0.0.0.0"
    NFM_PORT: int = 8765
    NFM_DEBUG: bool = True
    NFM_LOG_LEVEL: str = "INFO"

    NFM_STORAGE_PATH: Path = Path("./storage")
    NFM_DB_PATH: Path = Path("./storage/nfm.db")
    NFM_VECTOR_PATH: Path = Path("./storage/vectors")

    NFM_DB_POOL_SIZE: int = 5
    NFM_DB_MAX_OVERFLOW: int = 10

    NFM_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    NFM_EMBEDDING_DIM: int = 384

    NFM_MAX_CONTEXT_MEMORIES: int = 20
    NFM_MIN_CONFIDENCE: float = 0.3
    NFM_DEFAULT_CONFIDENCE: float = 0.7
    NFM_MEMORY_EXPIRY_DAYS: int = 30

    NFM_SEMANTIC_WEIGHT: float = 0.7
    NFM_KEYWORD_WEIGHT: float = 0.3

    NFM_API_TOKEN: Optional[str] = None
    NFM_ENABLE_AUTH: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
```

### 7.2 Database (`backend/app/storage/database.py`)

Use `create_async_engine` with `sqlite+aiosqlite://`. Use `async_sessionmaker` with `expire_on_commit=False`. Provide `get_db_session()` as a FastAPI dependency using `yield`. Do NOT use `async with session.begin()` inside endpoints.

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import event
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
Base = declarative_base()
_engine = None
_async_session_maker = None

async def init_database(db_path: str = None):
    global _engine, _async_session_maker
    db_path = db_path or str(settings.NFM_DB_PATH)
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    _engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
        echo=settings.NFM_DEBUG,
        pool_pre_ping=True
    )
    _async_session_maker = async_sessionmaker(
        _engine, class_=AsyncSession, expire_on_commit=False
    )

    @event.listens_for(_engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    from backend.app.memory.models import Base as MemoryBase
    async with _engine.begin() as conn:
        await conn.run_sync(MemoryBase.metadata.create_all)
    logger.info("Database initialized")

async def get_db_session() -> AsyncSession:
    async with _async_session_maker() as session:
        yield session
```

### 7.3 Models (`backend/app/memory/models.py`)

These are the ONLY tables for V1. Do not add extra tables.

```python
from sqlalchemy import Column, String, Text, Float, Integer, DateTime, JSON, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
from enum import Enum as PyEnum
import uuid

Base = declarative_base()

def now_utc():
    return datetime.now(timezone.utc)

class MemoryType(PyEnum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    PREFERENCE = "preference"
    DECISION = "decision"
    FAILURE = "failure"
    SUCCESS = "success"
    TEMPORAL = "temporal"
    CAUSAL = "causal"
    HYPOTHESIS = "hypothesis"
    CONFLICT = "conflict"
    MULTIMODAL = "multimodal"

class MemoryStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    DELETED = "deleted"

class ChangeType(PyEnum):
    CREATE = "create"
    REINFORCE = "reinforce"
    REFINE = "refine"
    EXPAND = "expand"
    CORRECT = "correct"
    MERGE = "merge"
    SPLIT = "split"
    SUPERSEDE = "supersede"
    CONTRADICT = "contradict"
    RESTORE = "restore"

class Memory(Base):
    __tablename__ = "memories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    root_id = Column(String(36), nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1)
    type = Column(Enum(MemoryType), nullable=False, index=True)
    subtype = Column(String(50), nullable=True, index=True)
    content = Column(Text, nullable=False)
    normalized_content = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=True, index=True)
    agent_id = Column(String(36), nullable=True, index=True)
    source_id = Column(String(36), nullable=True, index=True)
    confidence = Column(Float, nullable=False, default=0.7)
    importance = Column(Float, nullable=False, default=0.5)
    status = Column(Enum(MemoryStatus), nullable=False, default=MemoryStatus.ACTIVE)
    created_at = Column(DateTime, nullable=False, default=now_utc)
    observed_at = Column(DateTime, nullable=True)
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    parent_id = Column(String(36), nullable=True, index=True)
    integrity_hash = Column(String(64), nullable=True)
    metadata = Column(JSON, nullable=True, default=dict)

    versions = relationship("MemoryVersion", back_populates="memory", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_memory_type_status', 'type', 'status'),
        Index('idx_memory_agent', 'agent_id'),
        Index('idx_memory_root', 'root_id'),
    )

class MemoryVersion(Base):
    __tablename__ = "memory_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = Column(String(36), ForeignKey('memories.id'), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    normalized_content = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=True)
    confidence = Column(Float, nullable=False)
    importance = Column(Float, nullable=False)
    status = Column(Enum(MemoryStatus), nullable=False)
    change_type = Column(Enum(ChangeType), nullable=False)
    change_reason = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, nullable=False, default=now_utc)
    actor_id = Column(String(36), nullable=True)
    actor_type = Column(String(20), nullable=True)

    memory = relationship("Memory", back_populates="versions")

    __table_args__ = (Index('idx_version_memory', 'memory_id', 'version'),)

class MemoryEvent(Base):
    __tablename__ = "memory_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = Column(String(36), nullable=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=now_utc)
    agent_id = Column(String(36), nullable=True)

    __table_args__ = (
        Index('idx_event_memory', 'memory_id'),
        Index('idx_event_type', 'event_type'),
        Index('idx_event_timestamp', 'timestamp'),
    )

class MemoryRelationship(Base):
    __tablename__ = "memory_relationships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = Column(String(36), ForeignKey('memories.id'), nullable=False, index=True)
    related_id = Column(String(36), ForeignKey('memories.id'), nullable=False, index=True)
    relationship_type = Column(String(50), nullable=False, index=True)
    confidence = Column(Float, nullable=True, default=0.7)
    metadata = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, nullable=False, default=now_utc)

    __table_args__ = (
        Index('idx_rel_memory', 'memory_id'),
        Index('idx_rel_related', 'related_id'),
        Index('idx_rel_type', 'relationship_type'),
    )

class MemoryEmbedding(Base):
    __tablename__ = "memory_embeddings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = Column(String(36), ForeignKey('memories.id'), nullable=False, index=True, unique=True)
    vector = Column(JSON, nullable=False)  # Stored as list of floats
    model = Column(String(100), nullable=True)
    dimension = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=now_utc)
```

**CRITICAL:** The `Memory` model does NOT have `tags`, `updated_at`, or `current_version_id`. The `capture.py` must use these exact fields. `content_hash` must be SHA256 of content, not a UUID.

---

## 8. MODULE 2: MEMORY API

### 8.1 Pydantic Schemas (`backend/app/api/memory.py` — top of file)

```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

class MemoryCreateRequest(BaseModel):
    type: str = Field(..., description="Memory type: episodic, semantic, preference, etc.")
    content: str = Field(..., min_length=1)
    subtype: Optional[str] = None
    agent_id: Optional[str] = None
    source_id: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    importance: Optional[float] = Field(None, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None

    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        valid = {"working","episodic","semantic","procedural","preference",
                 "decision","failure","success","temporal","causal",
                 "hypothesis","conflict","multimodal"}
        if v not in valid:
            raise ValueError(f"Invalid memory type: {v}. Must be one of {valid}")
        return v

class MemoryResponse(BaseModel):
    id: str
    root_id: str
    version: int
    type: str
    content: str
    normalized_content: Optional[str] = None
    agent_id: Optional[str] = None
    source_id: Optional[str] = None
    confidence: float
    importance: float
    status: str
    created_at: str
    observed_at: Optional[str] = None
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    parent_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class MemoryListResponse(BaseModel):
    memories: List[MemoryResponse]
    total: int
    limit: int
    offset: int

class LearnRequest(BaseModel):
    agent_id: str
    user_input: str
    ai_output: str
    metadata: Optional[Dict[str, Any]] = None
```

### 8.2 Endpoints

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
import uuid
import hashlib

from ..storage.database import get_db_session
from ..memory.models import Memory, MemoryVersion, MemoryEvent, MemoryType, MemoryStatus, ChangeType
from ..config import settings

router = APIRouter()

def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def _memory_to_response(memory: Memory) -> MemoryResponse:
    return MemoryResponse(
        id=memory.id,
        root_id=memory.root_id,
        version=memory.version,
        type=memory.type.value,
        content=memory.content,
        normalized_content=memory.normalized_content,
        agent_id=memory.agent_id,
        source_id=memory.source_id,
        confidence=memory.confidence,
        importance=memory.importance,
        status=memory.status.value,
        created_at=memory.created_at.isoformat() if memory.created_at else None,
        observed_at=memory.observed_at.isoformat() if memory.observed_at else None,
        valid_from=memory.valid_from.isoformat() if memory.valid_from else None,
        valid_until=memory.valid_until.isoformat() if memory.valid_until else None,
        parent_id=memory.parent_id,
        metadata=memory.metadata or {}
    )

@router.post("/", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(request: MemoryCreateRequest, db_session=Depends(get_db_session)):
    memory_id = str(uuid.uuid4())
    content_hash = _sha256(request.content)
    now = datetime.now(timezone.utc)

    memory = Memory(
        id=memory_id,
        root_id=memory_id,
        version=1,
        type=MemoryType(request.type),
        subtype=request.subtype,
        content=request.content,
        normalized_content=request.content.lower().strip(),
        content_hash=content_hash,
        agent_id=request.agent_id,
        source_id=request.source_id,
        confidence=request.confidence or settings.NFM_DEFAULT_CONFIDENCE,
        importance=request.importance or 0.5,
        status=MemoryStatus.ACTIVE,
        created_at=now,
        observed_at=now,
        valid_from=now,
        metadata=request.metadata or {}
    )

    version = MemoryVersion(
        id=str(uuid.uuid4()),
        memory_id=memory_id,
        version=1,
        content=request.content,
        normalized_content=memory.normalized_content,
        content_hash=content_hash,
        confidence=memory.confidence,
        importance=memory.importance,
        status=MemoryStatus.ACTIVE,
        change_type=ChangeType.CREATE,
        change_reason="Initial creation",
        created_at=now,
        actor_id=request.agent_id or "system",
        actor_type="agent"
    )

    event = MemoryEvent(
        id=str(uuid.uuid4()),
        memory_id=memory_id,
        event_type="create",
        details={"type": request.type, "content_length": len(request.content)},
        timestamp=now,
        agent_id=request.agent_id or "system"
    )

    db_session.add(memory)
    db_session.add(version)
    db_session.add(event)
    await db_session.commit()

    return _memory_to_response(memory)

@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(memory_id: str, db_session=Depends(get_db_session)):
    result = await db_session.execute(select(Memory).where(Memory.id == memory_id))
    memory = result.scalar_one_or_none()
    if memory is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    return _memory_to_response(memory)

@router.get("/", response_model=MemoryListResponse)
async def list_memories(
    agent_id: Optional[str] = None,
    memory_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db_session=Depends(get_db_session)
):
    stmt = select(Memory)
    conditions = []
    if agent_id:
        conditions.append(Memory.agent_id == agent_id)
    if memory_type:
        conditions.append(Memory.type == MemoryType(memory_type))
    if conditions:
        stmt = stmt.where(*conditions)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db_session.execute(count_stmt)
    total = count_result.scalar() or 0

    stmt = stmt.order_by(Memory.created_at.desc()).limit(limit).offset(offset)
    result = await db_session.execute(stmt)
    memories = result.scalars().all()

    return MemoryListResponse(
        memories=[_memory_to_response(m) for m in memories],
        total=total,
        limit=limit,
        offset=offset
    )

@router.get("/{memory_id}/history")
async def get_memory_history(memory_id: str, db_session=Depends(get_db_session)):
    stmt = select(MemoryVersion).where(MemoryVersion.memory_id == memory_id).order_by(MemoryVersion.version)
    result = await db_session.execute(stmt)
    versions = result.scalars().all()
    if not versions:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {
        "memory_id": memory_id,
        "versions": [{
            "version": v.version,
            "content": v.content,
            "confidence": v.confidence,
            "importance": v.importance,
            "status": v.status.value,
            "change_type": v.change_type.value,
            "change_reason": v.change_reason,
            "created_at": v.created_at.isoformat() if v.created_at else None,
            "actor_id": v.actor_id,
            "actor_type": v.actor_type
        } for v in versions]
    }
```

**CRITICAL RULES:**
- NO `async with db_session.begin()` inside endpoints.
- Use `await db_session.commit()` explicitly.
- Use `datetime.now(timezone.utc)`, NOT `datetime.utcnow()`.
- `content_hash` MUST be SHA256, never UUID.

---

## 9. MODULE 3: VECTOR STORE & EMBEDDINGS

### 9.1 Embedding Model (`backend/app/embeddings/models.py`)

```python
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()

    def embed(self, text: str) -> List[float]:
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

# Singleton
_embedding_model = None

def get_embedding_model() -> EmbeddingModel:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = EmbeddingModel()
    return _embedding_model
```

### 9.2 FAISS Vector Store (`backend/app/embeddings/vector_store.py`)

```python
import faiss
import numpy as np
import json
from typing import List, Optional, Dict, Any
from pathlib import Path

class FAISSVectorStore:
    def __init__(self, dimension: int = 384, index_path: str = "./storage/vectors"):
        self.dimension = dimension
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.index = faiss.IndexFlatIP(dimension)
        self._id_map = {}      # faiss_idx -> memory_id
        self._reverse_map = {} # memory_id -> faiss_idx
        self._metadata = {}    # memory_id -> metadata
        self._texts = {}       # memory_id -> text
        self._count = 0

    def _normalize(self, vector: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    def add(self, memory_id: str, text: str, vector: List[float], metadata: Optional[Dict] = None):
        vec = np.array([vector], dtype=np.float32)
        vec = self._normalize(vec)
        idx = self._count
        self.index.add(vec)
        self._id_map[idx] = memory_id
        self._reverse_map[memory_id] = idx
        self._metadata[memory_id] = metadata or {}
        self._texts[memory_id] = text
        self._count += 1

    def search(self, query_vector: List[float], k: int = 10) -> List[Dict[str, Any]]:
        if self._count == 0:
            return []
        vec = np.array([query_vector], dtype=np.float32)
        vec = self._normalize(vec)
        k = min(k, self._count)
        scores, indices = self.index.search(vec, k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            memory_id = self._id_map.get(int(idx))
            if memory_id:
                results.append({
                    "memory_id": memory_id,
                    "text": self._texts.get(memory_id, ""),
                    "score": float(score),
                    "metadata": self._metadata.get(memory_id, {})
                })
        return results

    def delete(self, memory_id: str) -> bool:
        if memory_id in self._metadata:
            self._metadata[memory_id]["_deleted"] = True
            return True
        return False

    def save(self):
        faiss.write_index(self.index, str(self.index_path / "index.faiss"))
        with open(self.index_path / "meta.json", "w") as f:
            json.dump({
                "id_map": self._id_map,
                "reverse_map": self._reverse_map,
                "metadata": self._metadata,
                "texts": self._texts,
                "count": self._count,
                "dimension": self.dimension
            }, f)

    def load(self):
        index_file = self.index_path / "index.faiss"
        meta_file = self.index_path / "meta.json"
        if index_file.exists() and meta_file.exists():
            self.index = faiss.read_index(str(index_file))
            with open(meta_file, "r") as f:
                data = json.load(f)
            self._id_map = {int(k): v for k, v in data["id_map"].items()}
            self._reverse_map = data["reverse_map"]
            self._metadata = data["metadata"]
            self._texts = data["texts"]
            self._count = data["count"]
            self.dimension = data["dimension"]

# Singleton
_vector_store = None

def get_vector_store() -> FAISSVectorStore:
    global _vector_store
    if _vector_store is None:
        from backend.app.config import settings
        _vector_store = FAISSVectorStore(
            dimension=settings.NFM_EMBEDDING_DIM,
            index_path=str(settings.NFM_VECTOR_PATH)
        )
        _vector_store.load()
    return _vector_store
```

**NOTE:** FAISS `IndexFlatIP` does not support deletion. For V1, deletion is a soft-mark in metadata. Rebuild index for true deletion (V2).

---

## 10. MODULE 4: RETRIEVAL ENGINE

### 10.1 Simple Hybrid Retrieval (`backend/app/retrieval/engine.py`)

```python
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import re

from ..memory.models import Memory, MemoryStatus
from ..embeddings.models import get_embedding_model
from ..embeddings.vector_store import get_vector_store
from ..config import settings

class RetrievalEngine:
    def __init__(self):
        self.embedding_model = get_embedding_model()
        self.vector_store = get_vector_store()

    def _keyword_score(self, query: str, content: str) -> float:
        query_words = set(re.findall(r'\w+', query.lower()))
        content_words = set(re.findall(r'\w+', content.lower()))
        if not query_words:
            return 0.0
        overlap = len(query_words & content_words)
        return overlap / len(query_words)

    async def retrieve(
        self,
        db_session: AsyncSession,
        query: str,
        agent_id: Optional[str] = None,
        limit: int = 20,
        memory_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        # 1. Semantic search via FAISS
        query_embedding = self.embedding_model.embed(query)
        semantic_results = self.vector_store.search(query_embedding, k=limit * 2)
        semantic_ids = {r["memory_id"]: r["score"] for r in semantic_results
                        if not r["metadata"].get("_deleted")}

        # 2. Keyword search via SQLite
        stmt = select(Memory).where(Memory.status == MemoryStatus.ACTIVE)
        if agent_id:
            stmt = stmt.where(Memory.agent_id == agent_id)
        if memory_types:
            stmt = stmt.where(Memory.type.in_([MemoryType(t) for t in memory_types]))

        result = await db_session.execute(stmt)
        memories = result.scalars().all()

        # 3. Hybrid scoring
        scored = []
        for mem in memories:
            sem_score = semantic_ids.get(mem.id, 0.0)
            kw_score = self._keyword_score(query, mem.content)

            final_score = (
                settings.NFM_SEMANTIC_WEIGHT * sem_score +
                settings.NFM_KEYWORD_WEIGHT * kw_score
            )

            final_score *= (0.5 + 0.5 * mem.confidence)
            final_score *= (0.5 + 0.5 * mem.importance)

            scored.append({
                "memory": mem,
                "score": final_score,
                "semantic_score": sem_score,
                "keyword_score": kw_score
            })

        scored.sort(key=lambda x: x["score"], reverse=True)

        results = []
        for item in scored[:limit]:
            mem = item["memory"]
            results.append({
                "id": mem.id,
                "type": mem.type.value,
                "content": mem.content,
                "confidence": mem.confidence,
                "importance": mem.importance,
                "score": round(item["score"], 4),
                "semantic_score": round(item["semantic_score"], 4),
                "keyword_score": round(item["keyword_score"], 4),
                "created_at": mem.created_at.isoformat() if mem.created_at else None
            })
        return results

def get_retrieval_engine() -> RetrievalEngine:
    return RetrievalEngine()
```

### 10.2 Context Builder (`backend/app/api/context.py`)

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from ..storage.database import get_db_session
from ..retrieval.engine import get_retrieval_engine
from ..config import settings

router = APIRouter()

class ContextRequest(BaseModel):
    agent_id: str
    query: str
    memory_types: Optional[List[str]] = None
    max_memories: Optional[int] = None

class ContextResponse(BaseModel):
    agent_id: str
    query: str
    memories: List[Dict[str, Any]]
    total_tokens_estimate: int

@router.post("/context")
async def build_context(request: ContextRequest, db_session=Depends(get_db_session)):
    engine = get_retrieval_engine()
    limit = request.max_memories or settings.NFM_MAX_CONTEXT_MEMORIES

    results = await engine.retrieve(
        db_session=db_session,
        query=request.query,
        agent_id=request.agent_id,
        limit=limit,
        memory_types=request.memory_types
    )

    total_chars = sum(len(r["content"]) for r in results)
    token_estimate = total_chars // 4

    return ContextResponse(
        agent_id=request.agent_id,
        query=request.query,
        memories=results,
        total_tokens_estimate=token_estimate
    )
```

---

## 11. MODULE 5: PYTHON SDK

### 11.1 Models (`sdk/python/nfm/models.py`)

```python
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class MemoryCreate(BaseModel):
    type: str
    content: str
    subtype: Optional[str] = None
    agent_id: Optional[str] = None
    source_id: Optional[str] = None
    confidence: Optional[float] = None
    importance: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class MemoryUpdate(BaseModel):
    content: Optional[str] = None
    confidence: Optional[float] = None
    importance: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class SearchQuery(BaseModel):
    query: str
    agent_id: Optional[str] = None
    limit: Optional[int] = 20
    memory_types: Optional[List[str]] = None

class ContextQuery(BaseModel):
    agent_id: str
    query: str
    memory_types: Optional[List[str]] = None
    max_memories: Optional[int] = None
```

### 11.2 Client (`sdk/python/nfm/client.py`)

```python
import httpx
from typing import Optional, Dict, Any

from .models import MemoryCreate, SearchQuery, ContextQuery

class NFMClient:
    def __init__(self, base_url: str = "http://localhost:8765", api_key: Optional[str] = None, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        kwargs["headers"] = {**self._headers(), **kwargs.get("headers", {})}
        try:
            response = self._client.request(method, path, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"API error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def create_memory(self, memory: MemoryCreate) -> Dict[str, Any]:
        return self._request("POST", "/v1/memory/", json=memory.model_dump(exclude_none=True))

    def get_memory(self, memory_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/v1/memory/{memory_id}")

    def list_memories(self, agent_id: Optional[str] = None, memory_type: Optional[str] = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        params = {"limit": limit, "offset": offset}
        if agent_id:
            params["agent_id"] = agent_id
        if memory_type:
            params["memory_type"] = memory_type
        return self._request("GET", "/v1/memory/", params=params)

    def search(self, query: SearchQuery) -> Dict[str, Any]:
        return self._request("POST", "/v1/memory/search", json=query.model_dump(exclude_none=True))

    def get_context(self, query: ContextQuery) -> Dict[str, Any]:
        return self._request("POST", "/v1/memory/context", json=query.model_dump(exclude_none=True))

    def get_history(self, memory_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/v1/memory/{memory_id}/history")

    def health(self) -> Dict[str, Any]:
        return self._request("GET", "/health")

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
```

**CRITICAL:** SDK uses `/v1/` prefix, NOT `/api/`. Uses `.model_dump()`, NOT `.dict()`.

---

## 12. MODULE 6: CLI

### 12.1 CLI (`cli/nfm_cli/main.py`)

```python
import click
from rich.console import Console
from rich.table import Table
from rich.json import JSON
from sdk.python.nfm.client import NFMClient
from sdk.python.nfm.models import MemoryCreate, SearchQuery

console = Console()

def get_client():
    return NFMClient()

@click.group()
def cli():
    """NFM-X Command Line Interface"""
    pass

@cli.command()
def status():
    """Check server status"""
    client = get_client()
    try:
        health = client.health()
        console.print("[green]Server is healthy[/green]")
        console.print_json(data=health)
    except Exception as e:
        console.print(f"[red]Server unreachable: {e}[/red]")
    finally:
        client.close()

@cli.command()
@click.argument("query")
@click.option("--agent", "-a", help="Filter by agent ID")
@click.option("--limit", "-l", default=10, help="Max results")
def search(query, agent, limit):
    """Search memories"""
    client = get_client()
    try:
        result = client.search(SearchQuery(query=query, agent_id=agent, limit=limit))
        table = Table(title=f"Search: '{query}'")
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Score", style="green")
        table.add_column("Content", style="white")

        for mem in result.get("results", []):
            table.add_row(
                mem.get("id", "")[:8] + "...",
                mem.get("type", ""),
                str(mem.get("score", 0)),
                mem.get("content", "")[:80]
            )
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    finally:
        client.close()

@cli.command()
@click.argument("memory_id")
def get(memory_id):
    """Get memory details"""
    client = get_client()
    try:
        mem = client.get_memory(memory_id)
        console.print_json(data=mem)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    finally:
        client.close()

@cli.command()
@click.argument("memory_id")
def history(memory_id):
    """Get memory history"""
    client = get_client()
    try:
        hist = client.get_history(memory_id)
        console.print_json(data=hist)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    finally:
        client.close()

if __name__ == "__main__":
    cli()
```

---

## 13. MAIN APPLICATION

### 13.1 FastAPI App (`backend/app/main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
from datetime import datetime, timezone

from .config import settings
from .storage.database import init_database
from .api import memory, search, context

logging.basicConfig(
    level=settings.NFM_LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting NFM-X...")
    settings.NFM_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    await init_database(str(settings.NFM_DB_PATH))
    logger.info("NFM-X ready")
    yield
    logger.info("Shutting down NFM-X...")

app = FastAPI(
    title="NFM-X API",
    description="Non-Forgettable Evolutionary AI Memory",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8765"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(memory.router, prefix="/v1/memory", tags=["Memory"])
app.include_router(search.router, prefix="/v1/memory", tags=["Search"])
app.include_router(context.router, prefix="/v1/memory", tags=["Context"])

@app.get("/", tags=["Health"])
async def root():
    return {"name": "NFM-X", "version": "1.0.0", "docs": "/docs"}

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
```

---

## 14. TESTING REQUIREMENTS

Every module MUST have tests. Minimum 80% coverage.

### 14.1 Test Config (`backend/tests/conftest.py`)

```python
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.app.memory.models import Base

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

    await engine.dispose()
```

### 14.2 Required Test Coverage

| Module | Minimum Tests |
|--------|--------------|
| Memory CRUD | Create, read, list, history. Test versioning creates MemoryVersion row. |
| Validation | Invalid memory_type returns 422. Empty content rejected. |
| Retrieval | Keyword search finds match. Vector search returns results. Hybrid scoring works. |
| SDK | All methods call correct endpoints. Retry on failure. |
| Context Builder | Returns max N memories. Token estimate is positive. |

**NO test = NO merge.** Do not generate code without corresponding tests.

---

## 15. CODE QUALITY STANDARDS

1. **Type hints everywhere.** Every function parameter and return type must be annotated.
2. **No `raise NotImplementedError`.** If you can't implement it, exclude it from V1.
3. **No `pass` in function bodies.** Every function must do something or be removed.
4. **Async consistency.** All DB operations async. All FastAPI endpoints async.
5. **Error handling.** Catch specific exceptions. Return meaningful error messages.
6. **No print statements.** Use `logging` module only.
7. **Pydantic v2.** Use `.model_dump()`, `.model_validate()`, NOT `.dict()` or `.parse_obj()`.
8. **SQLAlchemy 2.0 style.** Use `select()`, `where()`, NOT `query()`.
9. **UTC timestamps.** Use `datetime.now(timezone.utc)`, NEVER `datetime.utcnow()`.
10. **Consistent naming.** `memory_id`, not `mem_id` or `id` in ambiguous contexts.

---

## 16. ROADMAP (For Reference Only — NOT V1)

### V1.5 (Next Phase)
- Dashboard (React)
- TypeScript SDK
- Basic conflict detection
- Memory relationships graph query
- Backup/restore CLI commands

### V2 (Future)
- Evolution engine (auto-reinforce, refine, contradict)
- Pattern discovery
- Skill learning from procedures
- MCP server
- OCR subsystem
- Android SDK

### V3 (Vision)
- Autonomous memory evolution
- Cross-agent memory sharing
- Predictive memory
- World model
- Cryptographic integrity checkpoints

**DO NOT write code for V1.5, V2, or V3 now.**

---

## 17. FINAL CHECKLIST BEFORE SUBMITTING CODE

- [ ] `pytest` passes with 80%+ coverage
- [ ] `python -m backend.app.main` starts without errors
- [ ] SDK can create and retrieve a memory
- [ ] Search returns relevant results
- [ ] Context builder returns under max memory limit
- [ ] No `NotImplementedError` anywhere
- [ ] No `datetime.utcnow()` anywhere
- [ ] No `/api/` endpoints (all `/v1/`)
- [ ] CORS restricted to localhost origins
- [ ] `.env` file loads correctly
- [ ] `requirements.txt` has all dependencies with versions

---

**END OF PROMPT.** Build ONLY what is specified above. Nothing more. Nothing less.
