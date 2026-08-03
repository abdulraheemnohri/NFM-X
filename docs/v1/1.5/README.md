# NFM-X V1.5 Documentation

## اردو - دستاویزات

NFM-X V1.5 کی مکمل دستاویزات۔ یہ ورژن بنیادی مموری مینجمنٹ سسٹم فراہم کرتا ہے۔

---

## English - V1.5 Features Documentation

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

### Graph API
- GET /api/v1/graph - Get memory graph

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
- id, content, title, tags, metadata, confidence
- created_at, updated_at
- user_id, parent_id

### Conflict Model
- id, memory_id_1, memory_id_2
- conflict_type, description, severity
- status, resolved_at, created_at

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

### V1.0.0 (2026-01-01)
- Initial release

---

## License

MIT License - Copyright (c) 2026 Abdulraheem Nohari

---

*Last updated: August 3, 2026*