# NFM-X V1.5 Documentation

# NFM-X Version 1.5.0 - Complete Documentation

## Overview

NFM-X V1.5 introduces the foundational memory management system with core features:
- Basic Memory CRUD Operations
- Simple Search Functionality
- Graph-based Relationships
- Conflict Detection
- Statistics & Analytics

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Configuration](#configuration)
3. [API Reference](#api-reference)
4. [Features](#features)
5. [Database Models](#database-models)
6. [Usage Examples](#usage-examples)
7. [Testing](#testing)
8. [Migration Guide](#migration-guide)
9. [Changelog](#changelog)

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- FastAPI
- SQLAlchemy
- SQLite

### Backend Setup

```bash
git clone https://github.com/abdulraheemnohri/NFM-X.git
cd NFM-X
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -c "from backend.app.database import init_db; import asyncio; asyncio.run(init_db())"
python -m backend.app.main
```

---

## Configuration

### Environment Variables

```env
NFM_APP_NAME=NFM-X
NFM_APP_VERSION=1.5.0
NFM_DEBUG=True
NFM_ENVIRONMENT=development
NFM_DATABASE_URL=sqlite+aiosqlite:///./nfm.db
```

---

## API Reference

### Memory API
- GET /api/v1/memories - List all memories
- POST /api/v1/memories - Create memory
- GET /api/v1/memories/{id} - Get memory
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

---

## Features

### Memory Management
- Create, Read, Update, Delete memories
- Metadata support
- Tagging system

### Search
- Full-text search
- Filter by tags and dates

### Graph
- Visualize connections
- Navigate relationships

### Conflicts
- Automatic detection
- Manual resolution

### Statistics
- Memory metrics
- Usage analytics

---

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
from sqlalchemy import Column, Integer, String, Text, DateTime
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
```

---

## Usage Examples

### Create Memory
```bash
curl -X POST "http://localhost:8000/api/v1/memories" -H "Content-Type: application/json" -d '{"content": "Test memory", "title": "Test", "tags": "test"}'
```

### Search
```bash
curl -X GET "http://localhost:8000/api/v1/search?q=test"
```

### Get Graph
```bash
curl -X GET "http://localhost:8000/api/v1/graph"
```

---

## Testing
```bash
pytest backend/app/tests/ -v
```

---

## Migration Guide

V1.5 is fully backward compatible with V1.0. No breaking changes.

---

## Changelog

### V1.5.0 (2026-08-03)
- Added memory CRUD operations
- Implemented search functionality
- Added graph relationships
- Introduced conflict detection
- Added statistics
- Improved error handling
- Enhanced documentation

### V1.0.0 (2026-01-01)
- Initial release
- Basic memory storage
- Simple API endpoints

---

## License

MIT License - Copyright (c) 2026 Abdulraheem Nohari

---

*Last updated: August 3, 2026*