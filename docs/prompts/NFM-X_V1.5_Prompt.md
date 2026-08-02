# NFM-X V1.5 Development Prompt
## Next Phase: Dashboard, TypeScript SDK, Conflict Detection & Graph Queries

> **INSTRUCTION:** Build ONLY what is listed in V1.5 Scope. V1 must already be working and tested. This prompt adds new capabilities on top of a stable V1 foundation. No placeholder code. No stubs. If a feature cannot be fully implemented, exclude it.

---

## 1. PREREQUISITE

V1 MUST be complete and passing all tests before starting V1.5.

V1 includes:
- Core Data Layer (SQLite, SQLAlchemy async models)
- Memory CRUD API (FastAPI)
- FAISS Vector Store + Local Embeddings
- Hybrid Retrieval (keyword + vector)
- Context Builder
- Rule-based Classification
- Python SDK
- CLI (status, search, get, history)
- Tests (80%+ coverage)

---

## 2. V1.5 SCOPE

### IN SCOPE — Build These:

| # | Module | What It Does |
|---|--------|-------------|
| 1 | **Conflict Detection Engine** | Detect when two memories contradict each other. Store conflicts. Do NOT auto-resolve. |
| 2 | **Memory Relationship Queries** | Query related memories via the existing `memory_relationships` table. Basic graph traversal (1-hop only). |
| 3 | **TypeScript SDK** | HTTP client for browser/Node.js. Match Python SDK feature parity. |
| 4 | **React Dashboard** | Modern responsive web UI. Memory explorer, search, timeline, stats. |
| 5 | **Backup & Restore** | Full database + vector index export/import. CLI commands. |
| 6 | **Memory Update / Versioning** | Create new versions of existing memories (not just CREATE). |
| 7 | **Stats & Observability API** | System metrics endpoint. Memory growth, retrieval stats. |

### OUT OF SCOPE — Do NOT Build in V1.5:

- Auto-evolution engine (REINFORCE, REFINE, EXPAND automatically)
- Pattern discovery
- Skill learning
- OCR subsystem
- MCP Server
- Android SDK
- Encrypted storage
- Cross-agent memory sharing
- Memory compression
- Memory replay / simulator
- Advanced graph traversal (multi-hop graph queries)
- Real-time sync / WebSockets
- User authentication system (keep simple API token)

---

## 3. TECHNOLOGY STACK (ADDITIONS TO V1)

```
# Backend additions — none, use existing V1 stack

# Frontend
Node.js         >= 18
React           >= 18
TypeScript      >= 5.0
Vite            >= 5.0
Tailwind CSS    >= 3.4
Zustand         >= 4.5
React Router    >= 6.22
Recharts        >= 2.12
Lucide React    >= 0.300

# TypeScript SDK
TypeScript      >= 5.0

# Build
npm / pnpm
```

---

## 4. PROJECT STRUCTURE (V1.5 ADDITIONS)

Add these to existing V1 structure. Do not modify V1 files unless necessary.

```
nfm-x/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── conflicts.py        # NEW: Conflict detection endpoints
│   │   │   ├── graph.py            # NEW: Relationship query endpoints
│   │   │   └── stats.py            # NEW: System metrics endpoint
│   │   ├── memory/
│   │   │   ├── conflicts.py        # NEW: Conflict detection engine
│   │   │   └── evolution.py        # NEW: Manual version creation (not auto)
│   │   └── workers/
│   │       └── background.py       # NEW: Background conflict scanner
│   └── tests/
│       ├── test_conflicts.py
│       ├── test_graph.py
│       └── test_stats.py
│
├── sdk/
│   └── typescript/
│       ├── src/
│       │   ├── client.ts           # NFMClient
│       │   ├── models.ts           # TypeScript interfaces
│       │   └── index.ts            # Barrel export
│       ├── package.json
│       ├── tsconfig.json
│       └── tests/
│           └── client.test.ts
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css
│       ├── stores/
│       │   └── memoryStore.ts      # Zustand store
│       ├── services/
│       │   └── api.ts              # API client wrapper
│       ├── components/
│       │   ├── Layout.tsx
│       │   ├── MemoryCard.tsx
│       │   ├── MemoryList.tsx
│       │   ├── MemoryDetail.tsx
│       │   ├── SearchBar.tsx
│       │   ├── StatsPanel.tsx
│       │   ├── Timeline.tsx
│       │   └── ConflictBadge.tsx
│       └── pages/
│           ├── HomePage.tsx
│           ├── MemoryExplorerPage.tsx
│           └── StatsPage.tsx
│
├── cli/
│   └── nfm_cli/
│       └── main.py                 # UPDATE: Add backup/restore commands
│
└── scripts/
    └── backup.py                   # NEW: Backup/restore utility
```

---

## 5. IMPLEMENTATION ORDER

**Phase 1: Backend Enhancements**
1. `memory/evolution.py` — Manual memory versioning (update creates new version)
2. `memory/conflicts.py` — Conflict detection engine
3. `workers/background.py` — Background conflict scanner
4. `api/conflicts.py` — Conflict endpoints
5. `api/graph.py` — Relationship query endpoints
6. `api/stats.py` — Stats endpoint
7. Tests for all backend additions

**Phase 2: TypeScript SDK**
8. `sdk/typescript/src/models.ts`
9. `sdk/typescript/src/client.ts`
10. `sdk/typescript/package.json` + `tsconfig.json`
11. SDK tests

**Phase 3: Dashboard**
12. `frontend/` setup (Vite + React + Tailwind)
13. API service layer
14. Zustand store
15. Components (MemoryCard, SearchBar, etc.)
16. Pages (Home, Explorer, Stats)
17. Dashboard integration tests

**Phase 4: CLI & Backup**
18. `scripts/backup.py` — Export/import logic
19. Update CLI with backup/restore commands
20. Backup tests

---

## 6. MODULE 1: MEMORY VERSIONING (UPDATE)

### 6.1 Evolution Engine (`backend/app/memory/evolution.py`)

Manual versioning only. User or system explicitly creates a new version.

```python
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import hashlib

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..memory.models import Memory, MemoryVersion, MemoryStatus, ChangeType

def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

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
            confidence=confidence or current.confidence,
            importance=importance or current.importance,
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
```

### 6.2 Update Endpoint (`backend/app/api/memory.py` — add to existing)

```python
class MemoryUpdateRequest(BaseModel):
    content: str = Field(..., min_length=1)
    change_type: str = Field(..., description="One of: correct, refine, expand, supersede")
    change_reason: str = Field(..., min_length=1)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    importance: Optional[float] = Field(None, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None

    @field_validator('change_type')
    @classmethod
    def validate_change_type(cls, v):
        valid = {"correct", "refine", "expand", "supersede"}
        if v not in valid:
            raise ValueError(f"Invalid change type: {v}")
        return v

@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: str,
    request: MemoryUpdateRequest,
    db_session=Depends(get_db_session)
):
    from ..memory.evolution import MemoryEvolution
    evolution = MemoryEvolution()

    new_memory = await evolution.create_version(
        db_session=db_session,
        memory_id=memory_id,
        new_content=request.content,
        change_type=ChangeType(request.change_type),
        change_reason=request.change_reason,
        confidence=request.confidence,
        importance=request.importance,
        metadata=request.metadata
    )
    return _memory_to_response(new_memory)
```

---

## 7. MODULE 2: CONFLICT DETECTION ENGINE

### 7.1 Conflict Detector (`backend/app/memory/conflicts.py`)

Simple keyword-based contradiction detection. NOT LLM-based for V1.5.

```python
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
```

### 7.2 Conflict API (`backend/app/api/conflicts.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy import select

from ..storage.database import get_db_session
from ..memory.models import MemoryConflict
from ..memory.conflicts import ConflictDetector

router = APIRouter()

class ConflictResponse(BaseModel):
    id: str
    memory_a_id: str
    memory_b_id: str
    conflict_type: str
    description: Optional[str] = None
    severity: float
    status: str
    created_at: str

@router.get("/conflicts", response_model=List[ConflictResponse])
async def list_conflicts(
    status: Optional[str] = None,
    db_session=Depends(get_db_session)
):
    stmt = select(MemoryConflict)
    if status:
        stmt = stmt.where(MemoryConflict.status == status)
    stmt = stmt.order_by(MemoryConflict.created_at.desc())
    result = await db_session.execute(stmt)
    conflicts = result.scalars().all()
    return [
        ConflictResponse(
            id=c.id,
            memory_a_id=c.memory_a_id,
            memory_b_id=c.memory_b_id,
            conflict_type=c.conflict_type,
            description=c.description,
            severity=c.severity,
            status=c.status,
            created_at=c.created_at.isoformat() if c.created_at else None
        )
        for c in conflicts
    ]

@router.post("/memory/{memory_id}/scan-conflicts")
async def scan_memory_conflicts(memory_id: str, db_session=Depends(get_db_session)):
    detector = ConflictDetector()
    conflicts = await detector.scan_for_conflicts(db_session, memory_id)
    created = []
    for c in conflicts:
        record = await detector.create_conflict_record(
            db_session=db_session,
            memory_a_id=c["memory_a_id"],
            memory_b_id=c["memory_b_id"],
            conflict_type=c["conflict_type"],
            description=c["description"],
            severity=c["severity"]
        )
        created.append(record.id)
    return {"scanned": True, "conflicts_found": len(conflicts), "conflict_ids": created}
```

---

## 8. MODULE 3: MEMORY RELATIONSHIP QUERIES (GRAPH)

### 8.1 Graph API (`backend/app/api/graph.py`)

1-hop relationship queries only. No multi-hop graph traversal in V1.5.

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy import select

from ..storage.database import get_db_session
from ..memory.models import Memory, MemoryRelationship

router = APIRouter()

class RelatedMemoryResponse(BaseModel):
    relationship_type: str
    confidence: Optional[float] = None
    memory: Dict[str, Any]

@router.get("/memory/{memory_id}/related")
async def get_related_memories(
    memory_id: str,
    relationship_type: Optional[str] = None,
    db_session=Depends(get_db_session)
):
    stmt = select(MemoryRelationship).where(MemoryRelationship.memory_id == memory_id)
    if relationship_type:
        stmt = stmt.where(MemoryRelationship.relationship_type == relationship_type)
    result = await db_session.execute(stmt)
    relationships = result.scalars().all()

    related = []
    for rel in relationships:
        mem_result = await db_session.execute(
            select(Memory).where(Memory.id == rel.related_id)
        )
        mem = mem_result.scalar_one_or_none()
        if mem:
            related.append(RelatedMemoryResponse(
                relationship_type=rel.relationship_type,
                confidence=rel.confidence,
                memory={
                    "id": mem.id,
                    "type": mem.type.value,
                    "content": mem.content,
                    "confidence": mem.confidence,
                    "status": mem.status.value
                }
            ))
    return {"memory_id": memory_id, "related": related}

@router.post("/memory/{memory_id}/relate/{related_id}")
async def create_relationship(
    memory_id: str,
    related_id: str,
    relationship_type: str,
    confidence: Optional[float] = 0.7,
    db_session=Depends(get_db_session)
):
    rel = MemoryRelationship(
        memory_id=memory_id,
        related_id=related_id,
        relationship_type=relationship_type,
        confidence=confidence
    )
    db_session.add(rel)
    await db_session.commit()
    return {"id": rel.id, "relationship_type": relationship_type, "created": True}
```

---

## 9. MODULE 4: STATS & OBSERVABILITY

### 9.1 Stats API (`backend/app/api/stats.py`)

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any
from sqlalchemy import select, func

from ..storage.database import get_db_session
from ..memory.models import Memory, MemoryVersion, MemoryEvent, MemoryConflict

router = APIRouter()

class StatsResponse(BaseModel):
    total_memories: int
    active_memories: int
    historical_versions: int
    total_events: int
    unresolved_conflicts: int
    memories_by_type: Dict[str, int]
    avg_confidence: float
    avg_importance: float

@router.get("/stats", response_model=StatsResponse)
async def get_stats(db_session=Depends(get_db_session)):
    # Total memories
    total_result = await db_session.execute(select(func.count(Memory.id)))
    total = total_result.scalar() or 0

    # Active
    active_result = await db_session.execute(
        select(func.count(Memory.id)).where(Memory.status == MemoryStatus.ACTIVE)
    )
    active = active_result.scalar() or 0

    # Versions
    versions_result = await db_session.execute(select(func.count(MemoryVersion.id)))
    versions = versions_result.scalar() or 0

    # Events
    events_result = await db_session.execute(select(func.count(MemoryEvent.id)))
    events = events_result.scalar() or 0

    # Conflicts
    conflicts_result = await db_session.execute(
        select(func.count(MemoryConflict.id)).where(MemoryConflict.status == "unresolved")
    )
    conflicts = conflicts_result.scalar() or 0

    # By type
    type_result = await db_session.execute(
        select(Memory.type, func.count(Memory.id)).group_by(Memory.type)
    )
    by_type = {row.type.value: row.count for row in type_result}

    # Averages
    avg_conf_result = await db_session.execute(select(func.avg(Memory.confidence)))
    avg_conf = avg_conf_result.scalar() or 0.0

    avg_imp_result = await db_session.execute(select(func.avg(Memory.importance)))
    avg_imp = avg_imp_result.scalar() or 0.0

    return StatsResponse(
        total_memories=total,
        active_memories=active,
        historical_versions=versions,
        total_events=events,
        unresolved_conflicts=conflicts,
        memories_by_type=by_type,
        avg_confidence=round(float(avg_conf), 3),
        avg_importance=round(float(avg_imp), 3)
    )
```

---

## 10. MODULE 5: TYPESCRIPT SDK

### 10.1 Models (`sdk/typescript/src/models.ts`)

```typescript
export interface MemoryCreate {
  type: string;
  content: string;
  subtype?: string;
  agent_id?: string;
  source_id?: string;
  confidence?: number;
  importance?: number;
  metadata?: Record<string, any>;
}

export interface MemoryResponse {
  id: string;
  root_id: string;
  version: number;
  type: string;
  content: string;
  normalized_content?: string;
  agent_id?: string;
  source_id?: string;
  confidence: number;
  importance: number;
  status: string;
  created_at: string;
  observed_at?: string;
  valid_from?: string;
  valid_until?: string;
  parent_id?: string;
  metadata?: Record<string, any>;
}

export interface SearchQuery {
  query: string;
  agent_id?: string;
  limit?: number;
  memory_types?: string[];
}

export interface ContextQuery {
  agent_id: string;
  query: string;
  memory_types?: string[];
  max_memories?: number;
}

export interface StatsResponse {
  total_memories: number;
  active_memories: number;
  historical_versions: number;
  total_events: number;
  unresolved_conflicts: number;
  memories_by_type: Record<string, number>;
  avg_confidence: number;
  avg_importance: number;
}
```

### 10.2 Client (`sdk/typescript/src/client.ts`)

```typescript
export class NFMClient {
  private baseUrl: string;
  private apiKey?: string;
  private timeout: number;

  constructor(options: { baseUrl?: string; apiKey?: string; timeout?: number } = {}) {
    this.baseUrl = (options.baseUrl || "http://localhost:8765").replace(/\/$/, "");
    this.apiKey = options.apiKey;
    this.timeout = options.timeout || 30000;
  }

  private async request<T>(
    method: string,
    path: string,
    body?: any,
    params?: Record<string, any>
  ): Promise<T> {
    const url = new URL(path, this.baseUrl);
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined) url.searchParams.append(k, String(v));
      });
    }

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "application/json",
    };
    if (this.apiKey) {
      headers["Authorization"] = `Bearer ${this.apiKey}`;
    }

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url.toString(), {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });
      clearTimeout(timer);

      if (!response.ok) {
        const text = await response.text();
        throw new Error(`API error ${response.status}: ${text}`);
      }
      return await response.json();
    } catch (error) {
      clearTimeout(timer);
      throw error;
    }
  }

  async createMemory(memory: MemoryCreate): Promise<MemoryResponse> {
    return this.request<MemoryResponse>("POST", "/v1/memory/", memory);
  }

  async getMemory(memoryId: string): Promise<MemoryResponse> {
    return this.request<MemoryResponse>("GET", `/v1/memory/${memoryId}`);
  }

  async listMemories(params?: {
    agent_id?: string;
    memory_type?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ memories: MemoryResponse[]; total: number; limit: number; offset: number }> {
    return this.request("GET", "/v1/memory/", undefined, params);
  }

  async search(query: SearchQuery): Promise<any> {
    return this.request("POST", "/v1/memory/search", query);
  }

  async getContext(query: ContextQuery): Promise<any> {
    return this.request("POST", "/v1/memory/context", query);
  }

  async getHistory(memoryId: string): Promise<any> {
    return this.request("GET", `/v1/memory/${memoryId}/history`);
  }

  async getStats(): Promise<StatsResponse> {
    return this.request<StatsResponse>("GET", "/v1/stats");
  }

  async health(): Promise<any> {
    return this.request("GET", "/health");
  }
}
```

### 10.3 Package Config

`package.json`:
```json
{
  "name": "nfm-client",
  "version": "1.5.0",
  "description": "NFM-X TypeScript SDK",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "vitest": "^1.0.0"
  }
}
```

`tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "declaration": true,
    "outDir": "./dist",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"]
}
```

---

## 11. MODULE 6: REACT DASHBOARD

### 11.1 Setup

Use Vite + React + TypeScript + Tailwind CSS.

`vite.config.ts`:
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/v1': 'http://localhost:8765',
      '/health': 'http://localhost:8765'
    }
  }
});
```

### 11.2 API Service (`frontend/src/services/api.ts`)

```typescript
import { NFMClient } from '../../../sdk/typescript/src/client';

export const api = new NFMClient({ baseUrl: '' }); // Uses Vite proxy
```

### 11.3 Zustand Store (`frontend/src/stores/memoryStore.ts`)

```typescript
import { create } from 'zustand';
import { api } from '../services/api';
import { MemoryResponse } from '../../../sdk/typescript/src/models';

interface MemoryState {
  memories: MemoryResponse[];
  selectedMemory: MemoryResponse | null;
  searchQuery: string;
  stats: any;
  loading: boolean;
  error: string | null;
  fetchMemories: () => Promise<void>;
  searchMemories: (query: string) => Promise<void>;
  selectMemory: (memory: MemoryResponse | null) => void;
  fetchStats: () => Promise<void>;
}

export const useMemoryStore = create<MemoryState>((set) => ({
  memories: [],
  selectedMemory: null,
  searchQuery: '',
  stats: null,
  loading: false,
  error: null,

  fetchMemories: async () => {
    set({ loading: true, error: null });
    try {
      const result = await api.listMemories({ limit: 50 });
      set({ memories: result.memories, loading: false });
    } catch (err: any) {
      set({ error: err.message, loading: false });
    }
  },

  searchMemories: async (query: string) => {
    set({ loading: true, error: null, searchQuery: query });
    try {
      const result = await api.search({ query, limit: 20 });
      set({ memories: result.results || [], loading: false });
    } catch (err: any) {
      set({ error: err.message, loading: false });
    }
  },

  selectMemory: (memory) => set({ selectedMemory: memory }),

  fetchStats: async () => {
    try {
      const stats = await api.getStats();
      set({ stats });
    } catch (err: any) {
      set({ error: err.message });
    }
  },
}));
```

### 11.4 Components

**Layout.tsx:**
```tsx
import { Outlet, Link } from 'react-router-dom';

export function Layout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center gap-6">
          <h1 className="text-xl font-bold text-gray-900">NFM-X</h1>
          <Link to="/" className="text-gray-600 hover:text-gray-900">Home</Link>
          <Link to="/memories" className="text-gray-600 hover:text-gray-900">Memories</Link>
          <Link to="/stats" className="text-gray-600 hover:text-gray-900">Stats</Link>
        </div>
      </nav>
      <main className="p-6">
        <Outlet />
      </main>
    </div>
  );
}
```

**SearchBar.tsx:**
```tsx
import { useState } from 'react';
import { useMemoryStore } from '../stores/memoryStore';

export function SearchBar() {
  const [query, setQuery] = useState('');
  const searchMemories = useMemoryStore((s) => s.searchMemories);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) searchMemories(query);
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 mb-6">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search memories..."
        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />
      <button
        type="submit"
        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        Search
      </button>
    </form>
  );
}
```

**MemoryCard.tsx:**
```tsx
import { MemoryResponse } from '../../../sdk/typescript/src/models';

interface Props {
  memory: MemoryResponse;
  onClick: () => void;
}

export function MemoryCard({ memory, onClick }: Props) {
  const typeColors: Record<string, string> = {
    episodic: 'bg-purple-100 text-purple-800',
    semantic: 'bg-blue-100 text-blue-800',
    preference: 'bg-green-100 text-green-800',
    failure: 'bg-red-100 text-red-800',
    success: 'bg-emerald-100 text-emerald-800',
  };

  return (
    <div
      onClick={onClick}
      className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition cursor-pointer"
    >
      <div className="flex items-center justify-between mb-2">
        <span className={`text-xs font-medium px-2 py-1 rounded-full ${typeColors[memory.type] || 'bg-gray-100 text-gray-800'}`}>
          {memory.type}
        </span>
        <span className="text-xs text-gray-400">
          {new Date(memory.created_at).toLocaleDateString()}
        </span>
      </div>
      <p className="text-sm text-gray-700 line-clamp-3">{memory.content}</p>
      <div className="flex items-center gap-4 mt-3 text-xs text-gray-500">
        <span>Confidence: {(memory.confidence * 100).toFixed(0)}%</span>
        <span>Importance: {(memory.importance * 100).toFixed(0)}%</span>
      </div>
    </div>
  );
}
```

**StatsPanel.tsx:**
```tsx
import { useEffect } from 'react';
import { useMemoryStore } from '../stores/memoryStore';

export function StatsPanel() {
  const { stats, fetchStats } = useMemoryStore();

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, [fetchStats]);

  if (!stats) return <div className="text-gray-500">Loading stats...</div>;

  const cards = [
    { label: 'Total Memories', value: stats.total_memories, color: 'bg-blue-500' },
    { label: 'Active', value: stats.active_memories, color: 'bg-green-500' },
    { label: 'Versions', value: stats.historical_versions, color: 'bg-purple-500' },
    { label: 'Conflicts', value: stats.unresolved_conflicts, color: 'bg-red-500' },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      {cards.map((card) => (
        <div key={card.label} className="bg-white rounded-lg p-4 border border-gray-200">
          <div className={`w-2 h-2 rounded-full ${card.color} mb-2`} />
          <div className="text-2xl font-bold text-gray-900">{card.value}</div>
          <div className="text-xs text-gray-500">{card.label}</div>
        </div>
      ))}
    </div>
  );
}
```

**MemoryExplorerPage.tsx:**
```tsx
import { useEffect } from 'react';
import { useMemoryStore } from '../stores/memoryStore';
import { SearchBar } from '../components/SearchBar';
import { MemoryCard } from '../components/MemoryCard';

export function MemoryExplorerPage() {
  const { memories, selectedMemory, fetchMemories, selectMemory, loading } = useMemoryStore();

  useEffect(() => {
    fetchMemories();
  }, [fetchMemories]);

  return (
    <div className="max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Memory Explorer</h2>
      <SearchBar />

      {loading && <div className="text-gray-500">Loading...</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {memories.map((memory) => (
          <MemoryCard
            key={memory.id}
            memory={memory}
            onClick={() => selectMemory(memory)}
          />
        ))}
      </div>

      {selectedMemory && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-bold">Memory Details</h3>
              <button
                onClick={() => selectMemory(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                Close
              </button>
            </div>
            <div className="space-y-3 text-sm">
              <div><strong>ID:</strong> {selectedMemory.id}</div>
              <div><strong>Type:</strong> {selectedMemory.type}</div>
              <div><strong>Content:</strong> {selectedMemory.content}</div>
              <div><strong>Confidence:</strong> {selectedMemory.confidence}</div>
              <div><strong>Importance:</strong> {selectedMemory.importance}</div>
              <div><strong>Created:</strong> {new Date(selectedMemory.created_at).toLocaleString()}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

**App.tsx:**
```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { HomePage } from './pages/HomePage';
import { MemoryExplorerPage } from './pages/MemoryExplorerPage';
import { StatsPage } from './pages/StatsPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/memories" element={<MemoryExplorerPage />} />
          <Route path="/stats" element={<StatsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

**HomePage.tsx:**
```tsx
import { StatsPanel } from '../components/StatsPanel';

export function HomePage() {
  return (
    <div className="max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h2>
      <StatsPanel />
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-2">Welcome to NFM-X</h3>
        <p className="text-gray-600">
          Non-Forgettable Evolutionary AI Memory Layer. Navigate to Memories to explore
          your AI's long-term memory.
        </p>
      </div>
    </div>
  );
}
```

---

## 12. MODULE 7: BACKUP & RESTORE

### 12.1 Backup Script (`scripts/backup.py`)

```python
import json
import shutil
import tarfile
from pathlib import Path
from datetime import datetime, timezone

from backend.app.config import settings

def create_backup(output_dir: str = "./backups") -> str:
    """Create a full backup of database and vector index."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_name = f"nfm_backup_{timestamp}"
    backup_dir = output_path / backup_name
    backup_dir.mkdir()

    # Copy database
    if settings.NFM_DB_PATH.exists():
        shutil.copy2(settings.NFM_DB_PATH, backup_dir / "nfm.db")

    # Copy vector index
    if settings.NFM_VECTOR_PATH.exists():
        vector_backup = backup_dir / "vectors"
        shutil.copytree(settings.NFM_VECTOR_PATH, vector_backup)

    # Create manifest
    manifest = {
        "version": "1.5.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "nfm.db",
        "vectors": "vectors/"
    }
    with open(backup_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    # Create tar archive
    archive_path = output_path / f"{backup_name}.tar.gz"
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(backup_dir, arcname=backup_name)

    # Clean up temp dir
    shutil.rmtree(backup_dir)

    return str(archive_path)

def restore_backup(archive_path: str) -> bool:
    """Restore from a backup archive."""
    archive = Path(archive_path)
    if not archive.exists():
        raise FileNotFoundError(f"Backup not found: {archive_path}")

    # Extract
    extract_dir = Path("./backups/restore_temp")
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True)

    with tarfile.open(archive, "r:gz") as tar:
        tar.extractall(extract_dir)

    # Find extracted dir
    extracted = next(extract_dir.iterdir())

    # Validate manifest
    manifest_path = extracted / "manifest.json"
    if not manifest_path.exists():
        raise ValueError("Invalid backup: manifest.json missing")

    with open(manifest_path) as f:
        manifest = json.load(f)

    # Restore database
    db_backup = extracted / manifest["database"]
    if db_backup.exists():
        shutil.copy2(db_backup, settings.NFM_DB_PATH)

    # Restore vectors
    vector_backup = extracted / manifest["vectors"]
    if vector_backup.exists():
        if settings.NFM_VECTOR_PATH.exists():
            shutil.rmtree(settings.NFM_VECTOR_PATH)
        shutil.copytree(vector_backup, settings.NFM_VECTOR_PATH)

    # Cleanup
    shutil.rmtree(extract_dir)
    return True
```

### 12.2 CLI Commands (update `cli/nfm_cli/main.py`)

Add to existing CLI:

```python
@cli.command()
@click.option("--output", "-o", default="./backups", help="Backup output directory")
def backup_create(output):
    """Create a full backup"""
    from scripts.backup import create_backup
    try:
        path = create_backup(output)
        console.print(f"[green]Backup created: {path}[/green]")
    except Exception as e:
        console.print(f"[red]Backup failed: {e}[/red]")

@cli.command()
@click.argument("archive_path")
def backup_restore(archive_path):
    """Restore from backup archive"""
    from scripts.backup import restore_backup
    try:
        restore_backup(archive_path)
        console.print("[green]Restore completed successfully[/green]")
    except Exception as e:
        console.print(f"[red]Restore failed: {e}[/red]")
```

---

## 13. UPDATED MAIN.PY

Add new routers to `backend/app/main.py`:

```python
from .api import memory, search, context, conflicts, graph, stats

app.include_router(memory.router, prefix="/v1/memory", tags=["Memory"])
app.include_router(search.router, prefix="/v1/memory", tags=["Search"])
app.include_router(context.router, prefix="/v1/memory", tags=["Context"])
app.include_router(conflicts.router, prefix="/v1", tags=["Conflicts"])
app.include_router(graph.router, prefix="/v1", tags=["Graph"])
app.include_router(stats.router, prefix="/v1", tags=["Stats"])
```

---

## 14. TESTING REQUIREMENTS

### New Tests Required:

| Module | Tests |
|--------|-------|
| Memory Versioning | Update creates new version. Old version inactive. History shows both. |
| Conflict Detection | Two contradicting memories detected. Conflict record created. |
| Graph Queries | Create relationship. Query returns related memory. |
| Stats API | All metrics return valid numbers. |
| TypeScript SDK | All methods work against running server. |
| Dashboard | Basic rendering tests (Vitest + React Testing Library). |
| Backup/Restore | Create backup. Restore from backup. Data integrity preserved. |

---

## 15. CODE QUALITY STANDARDS (Same as V1)

1. Type hints everywhere.
2. No `raise NotImplementedError`.
3. No `pass` in function bodies.
4. Async consistency.
5. Proper error handling.
6. No print statements — use logging.
7. Pydantic v2 / TypeScript strict mode.
8. SQLAlchemy 2.0 style.
9. UTC timestamps.
10. Consistent naming.

---

## 16. FINAL CHECKLIST

- [ ] All V1 tests still pass
- [ ] New V1.5 tests pass (80%+ coverage)
- [ ] Memory update creates new version, preserves old
- [ ] Conflict detection finds contradictions
- [ ] Graph queries return related memories (1-hop)
- [ ] Stats endpoint returns accurate metrics
- [ ] TypeScript SDK compiles without errors
- [ ] Dashboard renders and shows memories
- [ ] Dashboard search works
- [ ] Dashboard stats update
- [ ] CLI backup creates valid archive
- [ ] CLI restore restores data correctly
- [ ] No `NotImplementedError` anywhere
- [ ] No `datetime.utcnow()` anywhere

---

**END OF V1.5 PROMPT.** Build ONLY what is specified above.
