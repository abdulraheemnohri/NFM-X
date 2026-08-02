# NFM-X V2 Documentation

## Overview

NFM-X V2 is the next generation of the Non-Forgettable Memory Layer, featuring:

- **Versioned Memory System**: Complete history and rollback capability
- **Multi-Modal Support**: Text, Image, and Audio memories
- **Hybrid Search**: 3-layer search (FAISS + SQLite + BM25)
- **Advanced Graph Relationships**: Semantic connections between memories
- **AI Auto-Resolution**: Automatic conflict detection and resolution
- **Enhanced Performance**: Optimized for speed and accuracy

## New Features in V2

### 1. Versioned Memory
Every memory update creates a new version while preserving the old ones. You can:
- View complete version history
- Rollback to any previous version
- Compare versions

### 2. Multi-Modal Support
Store and retrieve memories in different formats:
- **Text**: Standard text memories
- **Image**: Visual memories with embeddings
- **Audio**: Audio memories with transcription
- **Multimodal**: Combined memories

### 3. Hybrid Search
Three-layer search system for optimal results:
- **Semantic Search**: FAISS-based vector similarity
- **Keyword Search**: SQLite full-text search
- **BM25**: Traditional search algorithm
- **Weighted Combination**: Configurable weights for each layer

### 4. Graph Relationships
Advanced memory connections:
- Causal relationships (cause-effect)
- Temporal relationships (time-based)
- Semantic relationships (meaning-based)
- Referential relationships (citations)
- Hierarchical relationships (parent-child)

### 5. AI Auto-Resolution
Automatic conflict handling:
- Content duplicate detection
- Metadata conflict resolution
- Temporal conflict handling
- Semantic conflict analysis
- Relationship validation

## API Endpoints

### Memory V2
- `POST /api/v2/memory/` - Create a new memory
- `GET /api/v2/memory/{id}/versions` - Get all versions
- `POST /api/v2/memory/{id}/rollback/{version}` - Rollback to version

### Search V2
- `POST /api/v2/search/hybrid` - Hybrid search
- `GET /api/v2/search/semantic` - Semantic search
- `GET /api/v2/search/keyword` - Keyword search

### Graph V2
- `GET /api/v2/graph/nodes/{id}` - Get node info
- `GET /api/v2/graph/edges/{id}` - Get edges
- `POST /api/v2/graph/traverse` - Traverse graph

### Conflicts V2
- `GET /api/v2/conflicts/` - List conflicts
- `POST /api/v2/conflicts/resolve` - Resolve conflict
- `POST /api/v2/conflicts/auto-resolve-all` - Auto-resolve all

### Stats V2
- `GET /api/v2/stats/` - Get V2 statistics
- `GET /api/v2/stats/performance` - Performance metrics

## Migration from V1.5

V2 is designed to be backward compatible. Existing V1.5 memories will continue to work, and new V2 features can be adopted incrementally.

## SDK Usage

### Python SDK V2
```python
from sdk.python.v2 import NFMXClientV2

client = NFMXClientV2(base_url="http://localhost:8000")

# Create a memory
memory = await client.create_memory("Hello V2!", modality="text")

# Hybrid search
results = await client.hybrid_search({"query": "test"})
```

### TypeScript SDK V2
```typescript
import { NFMXClientV2 } from "sdk/typescript/src/v2";

const client = new NFMXClientV2("http://localhost:8000");

// Create a memory
const memory = await client.createMemory("Hello V2!");

// Hybrid search
const results = await client.hybridSearch({ query: "test" });
```