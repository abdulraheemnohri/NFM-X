# NFM-X V2 API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
All V2 endpoints require an API key in the Authorization header:
```
Authorization: Bearer YOUR_API_KEY
```

## Memory V2 Endpoints

### Create Memory
**POST** `/api/v2/memory/`

Request Body:
```json
{
  "content": "string",
  "metadata": {},
  "tags": ["string"],
  "source": "string",
  "modality": "text"
}
```

Response:
```json
{
  "id": "string",
  "content": "string",
  "version": 1,
  "created_at": "datetime",
  "updated_at": "datetime",
  "metadata": {},
  "tags": [],
  "status": "ACTIVE",
  "modality": "text"
}
```

### Get Memory Versions
**GET** `/api/v2/memory/{memory_id}/versions`

Response: Array of memory versions

### Rollback Memory
**POST** `/api/v2/memory/{memory_id}/rollback/{version}`

Rolls back a memory to a specific version.

## Search V2 Endpoints

### Hybrid Search
**POST** `/api/v2/search/hybrid`

Request Body:
```json
{
  "query": "string",
  "limit": 10,
  "semantic_weight": 0.6,
  "keyword_weight": 0.3,
  "bm25_weight": 0.1,
  "filters": {}
}
```

### Semantic Search
**GET** `/api/v2/search/semantic?query=string&limit=10&threshold=0.7`

### Keyword Search
**GET** `/api/v2/search/keyword?query=string&limit=10`

## Graph V2 Endpoints

### Get Node
**GET** `/api/v2/graph/nodes/{memory_id}`

### Get Edges
**GET** `/api/v2/graph/edges/{memory_id}`

### Traverse Graph
**POST** `/api/v2/graph/traverse`

Request Body:
```json
{
  "start_memory_id": "string",
  "relationship_type": "string",
  "max_depth": 3
}
```

## Conflicts V2 Endpoints

### List Conflicts
**GET** `/api/v2/conflicts/`

### Resolve Conflict
**POST** `/api/v2/conflicts/resolve`

Request Body:
```json
{
  "conflict_id": "string",
  "resolution_strategy": "string",
  "auto_resolve": true
}
```

### Auto-Resolve All
**POST** `/api/v2/conflicts/auto-resolve-all`

## Stats V2 Endpoints

### Get Statistics
**GET** `/api/v2/stats/`

### Get Performance Metrics
**GET** `/api/v2/stats/performance`