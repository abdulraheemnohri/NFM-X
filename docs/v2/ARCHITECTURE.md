# NFM-X V2 Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        NFM-X V2 System                          │
├─────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │   Frontend    │    │    Backend    │    │    Storage    │   │
│  │  (React/TS)   │◄───►│  (FastAPI)    │◄───►│   (SQLite)    │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│                       │                                      │
│                       ▼                                      │
│  ┌───────────────────────────────────────────────────────┐   │
│  │                    V2 Core Components                     │   │
│  ├─────────────────┬─────────────────┬──────────────────┤   │
│  │  V2 API Layer    │ V2 Memory Layer  │  V2 Retrieval      │   │
│  │  - memory_v2     │ - models_v2      │  - engine_v2       │   │
│  │  - search_v2     │ - capture_v2     │  - hybrid_search   │   │
│  │  - graph_v2      │ - versioning     │                   │   │
│  │  - conflicts_v2  │                  │                   │   │
│  │  - stats_v2      │                  │                   │   │
│  ├─────────────────┼─────────────────┼──────────────────┤   │
│  │  V2 Graph Layer  │ V2 Conflicts     │  Existing Modules  │   │
│  │  - relationships │ - auto_resolver   │  - embeddings      │   │
│  │  - traversal    │                  │  - compression     │   │
│  │                 │                  │  - causal          │   │
│  │                 │                  │  - world_model     │   │
│  └─────────────────┴─────────────────┴──────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────┘
```

## V2 API Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (backend/app/api/v2/)              │
├─────────────────┬─────────────────┬─────────────────┬─────────┤
│  memory_v2.py    │  search_v2.py    │  graph_v2.py     │  ...    │
│  - CRUD ops      │  - Hybrid search │  - Node ops      │         │
│  - Versioning    │  - Semantic      │  - Edge ops      │         │
│                  │  - Keyword        │  - Traversal     │         │
└─────────────────┴─────────────────┴─────────────────┴─────────┘
```

## V2 Memory Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Memory Layer (backend/app/memory/v2/)          │
├─────────────────┬─────────────────┬──────────────────────────┤
│  models_v2.py    │  capture_v2.py    │       versioning.py         │
│  - MemoryV2      │  - Multi-modal    │  - MemoryVersion           │
│  - Enums         │    capture       │  - VersionManager          │
│                  │                  │  - add_version()            │
│                  │                  │  - get_versions()           │
│                  │                  │  - rollback()               │
└─────────────────┴─────────────────┴──────────────────────────┘
```

## V2 Retrieval Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Retrieval Layer (backend/app/retrieval/v2/)     │
├─────────────────┬───────────────────────────────────────────┤
│  engine_v2.py    │           hybrid_search.py                     │
│  - retrieve()    │  - HybridSearchEngine                         │
│                  │  - _semantic_search() (FAISS)                 │
│                  │  - _keyword_search() (SQLite FTS)             │
│                  │  - _bm25_search() (BM25)                       │
└─────────────────┴───────────────────────────────────────────┘
```

## V2 Graph Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Graph Layer (backend/app/graph/v2/)           │
├─────────────────┬───────────────────────────────────────────┤
│  relationships.py│           traversal.py                            │
│  - MemoryRelation│  - GraphTraversalEngine                       │
│  - RelationshipType│  - bfs()                                    │
│  - add_relationship()│  - dfs()                                    │
│  - get_relationships()│  - find_shortest_path()                     │
└─────────────────┴───────────────────────────────────────────┘
```

## Data Flow

1. **User Request** → Frontend → API Layer
2. **API Layer** → Memory/Graph/Conflicts Layer
3. **Core Layers** → Storage (SQLite) + Embeddings (FAISS)
4. **Storage** → Persist data
5. **Response** → API Layer → Frontend → User

## Key Design Principles

1. **Versioning**: Every change creates a new version
2. **Immutability**: Old versions are never modified
3. **Soft Deletion**: Memories are marked as DELETED, not removed
4. **Bidirectional**: All relationships are bidirectional
5. **Extensible**: Easy to add new modalities and features
6. **Backward Compatible**: V2 works alongside V1.5