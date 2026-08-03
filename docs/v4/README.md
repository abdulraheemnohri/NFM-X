# NFM-X V4 Documentation

# NFM-X Version 4.0.0 - Complete Documentation

## Overview

NFM-X V4 introduces **major enhancements** with a focus on:
- **Enhanced OCR Processing**
- **Document Management**
- **Structured Data Extraction**
- **Automation & Scheduling**
- **API Security**
- **Modern UI**

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Configuration](#configuration)
3. [API Reference](#api-reference)
4. [Frontend Pages](#frontend-pages)
5. [Database Models](#database-models)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

---

## Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### Backend Setup

```bash
git clone https://github.com/abdulraheemnohri/NFM-X.git
cd NFM-X
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
python -c "from backend.app.database import init_db; import asyncio; asyncio.run(init_db())"
python -m backend.app.main
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
npm run build
npm run preview
```

---

## Configuration

### Environment Variables

```env
NFM_APP_NAME=NFM-X
NFM_APP_VERSION=4.0.0
NFM_DEBUG=True
NFM_ENVIRONMENT=development
NFM_DATABASE_URL=sqlite+aiosqlite:///./nfm.db
NFM_DATABASE_ECHO=False
NFM_DATABASE_POOL_SIZE=5
NFM_DATABASE_MAX_OVERFLOW=10
NFM_OCR_ENABLED=True
NFM_OCR_ENGINE=easyocr
NFM_OCR_LANGUAGES=eng
NFM_OCR_TABLE_EXTRACTION=True
NFM_COMPRESSION_ENABLED=True
NFM_COMPRESSION_AGE_DAYS=30
NFM_SYNC_ENABLED=True
NFM_SYNC_AUTO_RESOLVE=True
NFM_MCP_ENABLED=False
NFM_RATE_LIMIT_ENABLED=False
NFM_CORS_ALLOW_ORIGINS=http://localhost:3000
NFM_LOG_LEVEL=INFO
NFM_SECRET_KEY=change-this-in-production
NFM_STORAGE_DIR=./storage
```

---

## API Reference

### V4 API Endpoints

#### Health API
- GET /api/health - Detailed health check
- GET /api/health/status - System status
- GET /api/health/components - Component health

#### OCR API
- POST /api/ocr/process - Process document/image
- POST /api/ocr/batch - Batch OCR processing
- GET /api/ocr/status/{job_id} - Get OCR job status
- GET /api/ocr/engines - List available OCR engines

#### Documents API
- GET /api/documents - List all documents
- POST /api/documents - Upload document
- GET /api/documents/{id} - Get document details
- DELETE /api/documents/{id} - Delete document
- POST /api/documents/{id}/ocr - Process document with OCR

#### Batch API
- POST /api/batch/upload - Upload multiple documents
- POST /api/batch/process - Process batch of documents
- GET /api/batch/status/{batch_id} - Get batch status
- GET /api/batch/results/{batch_id} - Get batch results

#### Conflicts API
- GET /api/conflicts - List all conflicts
- GET /api/conflicts/{id} - Get conflict details
- POST /api/conflicts/resolve - Resolve conflict
- POST /api/conflicts/auto-resolve - Auto-resolve conflicts
- POST /api/conflicts/bulk-resolve - Bulk resolve conflicts
- DELETE /api/conflicts/{id} - Dismiss conflict

#### Patterns API
- GET /api/patterns - List all patterns
- POST /api/patterns - Create pattern
- GET /api/patterns/{id} - Get pattern
- PUT /api/patterns/{id} - Update pattern
- DELETE /api/patterns/{id} - Delete pattern
- POST /api/patterns/{id}/search - Search with pattern
- POST /api/patterns/{id}/test - Test pattern

#### Skills API
- GET /api/skills - List all skills
- POST /api/skills - Create skill
- GET /api/skills/{id} - Get skill
- PUT /api/skills/{id} - Update skill
- DELETE /api/skills/{id} - Delete skill
- POST /api/skills/{id}/execute - Execute skill
- GET /api/skills/{id}/executions - Get skill executions
- POST /api/skills/{id}/enable - Enable skill
- POST /api/skills/{id}/disable - Disable skill

#### MCP API
- POST /api/mcp/auth - MCP authentication
- GET /api/mcp/keys - List API keys
- POST /api/mcp/keys - Create API key
- GET /api/mcp/keys/{id} - Get API key
- PUT /api/mcp/keys/{id} - Update API key
- DELETE /api/mcp/keys/{id} - Delete API key
- POST /api/mcp/keys/{id}/regenerate - Regenerate API key

---

## Frontend Pages

### Main Pages
| Page | Path | Description |
|------|------|-------------|
| Dashboard | /dashboard | Main dashboard with stats and charts |
| Documents | /documents | Document management interface |
| Upload | /upload | File upload with OCR options |
| Health | /health | System health monitoring |
| Settings | /settings | Configuration management |
| Statistics | /statistics | Advanced analytics and charts |
| Patterns | /patterns | Pattern search interface |
| Skills | /skills | Skill execution interface |
| MCP | /mcp | API key management interface |

### V2 Pages
| Page | Path | Description |
|------|------|-------------|
| V2 Dashboard | /v2 | V2 dashboard |
| V2 Memory Explorer | /v2/memories | V2 memory explorer |
| V2 Graph | /v2/graph | V2 graph visualization |

---

## Database Models

### V4 Models

#### Memory Model
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.sql import func
from backend.app.database import Base

class Memory(Base):
    __tablename__ = "memories"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    title = Column(String(500))
    tags = Column(String(1000))
    metadata = Column(JSON)
    confidence = Column(Float, default=1.0)
    importance = Column(Float, default=0.5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(Integer, index=True)
    parent_id = Column(Integer, index=True)
```

#### Document Model
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from backend.app.database import Base

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer)
    ocr_status = Column(String(50), default="pending")
    ocr_text = Column(Text)
    processing_status = Column(String(50), default="pending")
    metadata = Column(JSON)
    tags = Column(String(1000))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, index=True)
```

#### Pattern Model
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from backend.app.database import Base

class Pattern(Base):
    __tablename__ = "patterns"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    regex = Column(String(1000), nullable=False)
    description = Column(Text)
    case_sensitive = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, index=True)
```

#### Skill Model
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from backend.app.database import Base

class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    code = Column(Text, nullable=False)
    language = Column(String(50), default="python")
    timeout_seconds = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, index=True)
```

#### APIKey Model
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from backend.app.database import Base

class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    key = Column(String(100), nullable=False, unique=True)
    key_hash = Column(String(255), nullable=False)
    permissions = Column(Text)
    rate_limit_per_minute = Column(Integer, default=100)
    usage_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    user_id = Column(Integer, index=True)
```

---

## Testing

```bash
pytest backend/app/tests/ -v
pytest backend/app/tests/test_v4.py -v
pytest backend/app/tests/test_api.py -v
pytest backend/app/tests/ --cov=backend/app --cov-report=html
```

---

## Deployment

### Docker Deployment

```bash
docker build -t nfm-x .
docker run -p 8000:8000 -v ./data:/app/data nfm-x
docker run -p 8000:8000 -v ./data:/app/data --env-file .env nfm-x
```

### Production Deployment

```bash
pip install -r requirements.txt
cp .env.example .env
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.app.main:app --bind 0.0.0.0:8000
```

---

## Troubleshooting

### Common Issues

#### Database Connection Error
```bash
ls -la data/nfm-x.db
chmod 666 data/nfm-x.db
cat .env | grep DATABASE_URL
```

#### API Not Responding
```bash
ps aux | grep nfm-x
cat /var/log/nfm-x/app.log
curl http://localhost:8000/health
```

#### Import Errors
```bash
pip install missing-package
python --version
which python
```

#### OCR Not Working
```bash
NFM_OCR_ENABLED=True
NFM_OCR_ENGINE=easyocr
pip install easyocr
sudo apt install tesseract-ocr
pip install pytesseract
```

---

## Changelog

### V4.0.0 (August 2026)
- Enhanced OCR Engine with multiple backends
- Document Management system
- Structured Data Extraction
- Auto-Compression Scheduler
- Conflict Resolution API
- Pattern Search & Management
- Skill Execution Tracking
- MCP Authentication
- Detailed Health Check System
- Rate Limiting Middleware
- File Logging Configuration
- Modern UI with 9+ pages

### V3.0.0 (2026)
- World Model Entity Merge
- Predictive Confidence Intervals
- Causal Graph Visualization
- Sharing Permission Updates
- Sync Conflict Auto-Resolution
- Simulation Comparison
- Compression Scheduling

---

*Last updated: August 3, 2026*