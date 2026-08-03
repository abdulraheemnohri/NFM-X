# NFM-X V1 Documentation

# NFM-X Version 1.0.0 - Core Memory Management

## Overview

NFM-X V1 is the foundational version that introduces core memory management capabilities. This version provides the basic building blocks for storing, organizing, and retrieving memories.

## Features

### Core Capabilities
- Memory Storage: Store text-based memories with metadata
- Basic Search: Simple text search across memories
- Graph Visualization: Visual representation of memory relationships
- Statistics: Basic usage statistics
- Conflict Detection: Identify conflicting memories

## API Reference

### Memory API
- GET /api/v1/memories - List all memories
- POST /api/v1/memories - Create a memory
- GET /api/v1/memories/{id} - Get specific memory
- PUT /api/v1/memories/{id} - Update memory
- DELETE /api/v1/memories/{id} - Delete memory

### Search API
- GET /api/v1/search - Search memories
- POST /api/v1/search - Advanced search

### Graph API
- GET /api/v1/graph - Get memory graph
- GET /api/v1/graph/{id} - Get node connections

### Stats API
- GET /api/v1/stats - Get statistics

### Conflicts API
- GET /api/v1/conflicts - List conflicts
- POST /api/v1/conflicts/resolve - Resolve conflicts

## Database Models

### Memory Model
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from backend.app.database import Base

class Memory(Base):
    __tablename__ = "memories"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    title = Column(String(200))
    tags = Column(String(500))
    metadata = Column(Text)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(Integer, index=True)
    parent_id = Column(Integer, index=True)
```

### Conflict Model
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from backend.app.database import Base

class Conflict(Base):
    __tablename__ = "conflicts"
    id = Column(Integer, primary_key=True, index=True)
    memory_id_1 = Column(Integer, index=True)
    memory_id_2 = Column(Integer, index=True)
    conflict_type = Column(String(50))
    description = Column(Text)
    severity = Column(Float, default=0.5)
    status = Column(String(20), default="unresolved")
    resolved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, index=True)
```

## Usage Examples

### Create Memory
```bash
curl -X POST http://localhost:8000/api/v1/memories -H "Content-Type: application/json" -d '{"content": "Test memory", "title": "Test", "tags": "test"}'
```

### Search Memories
```bash
curl -X GET "http://localhost:8000/api/v1/search?q=test"
```

### Get Memory Graph
```bash
curl -X GET "http://localhost:8000/api/v1/graph"
```

## Testing
```bash
pytest backend/app/tests/ -v
```

## Changelog

### V1.0.0 (January 2026)
- Initial release of NFM-X
- Core memory storage system
- Basic CRUD operations
- Simple search functionality
- Basic graph visualization
- Conflict detection
- Usage statistics

---

*Last updated: August 3, 2026*