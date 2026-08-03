# NFM-X V4 Documentation

## اردو - Urdu Documentation

 NFM-X V4 کی مکمل دستاویزات۔

---

## English - V4 Features Documentation

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
# Clone repository
git clone https://github.com/abdulraheemnohri/NFM-X.git
cd NFM-X

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venvScriptsactivate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
nano .env  # Edit with your settings

# Initialize database
python -c "from backend.app.database import init_db; import asyncio; asyncio.run(init_db())"

# Run backend
python -m backend.app.main
# OR for production
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## Configuration

### Environment Variables (.env)

```env
# Application Settings
NFM_APP_NAME=NFM-X
NFM_APP_VERSION=4.0.0
NFM_DEBUG=True
NFM_ENVIRONMENT=development

# Database Configuration
NFM_DATABASE_URL=sqlite+aiosqlite:///./nfm.db
NFM_DATABASE_ECHO=False
NFM_DATABASE_POOL_SIZE=5
NFM_DATABASE_MAX_OVERFLOW=10

# OCR Configuration
NFM_OCR_ENABLED=True
NFM_OCR_DEFAULT_BACKEND=easyocr
NFM_OCR_LANGUAGES=eng,urd,ara,fra,spa,deu,chi_sim
NFM_OCR_TABLE_EXTRACTION=True
NFM_OCR_IMAGE_EXTRACTION=False
NFM_OCR_CONFIDENCE_THRESHOLD=0.7

# Compression Configuration
NFM_COMPRESSION_ENABLED=True
NFM_COMPRESSION_INTERVAL=daily
NFM_COMPRESSION_RETENTION_DAYS=365
NFM_COMPRESSION_BATCH_SIZE=100
NFM_COMPRESSION_MIN_CONFIDENCE=0.7

# MCP Configuration
NFM_MCP_ENABLED=True
NFM_MCP_REQUIRE_AUTHENTICATION=True
NFM_MCP_DEFAULT_PERMISSIONS=read,write
NFM_MCP_RATE_LIMIT_DEFAULT=100

# Rate Limiting
NFM_RATE_LIMIT_ENABLED=True
NFM_RATE_LIMIT_REQUESTS=100
NFM_RATE_LIMIT_WINDOW=60

# CORS Configuration
NFM_CORS_ORIGINS=["*"]
NFM_CORS_METHODS=["GET","POST","PUT","DELETE","OPTIONS"]
NFM_CORS_HEADERS=["*"]
NFM_CORS_ALLOW_CREDENTIALS=True

# Logging
NFM_LOG_LEVEL=INFO
NFM_LOG_FILE=logs/nfm-x.log
NFM_LOG_MAX_SIZE=10MB
NFM_LOG_BACKUP_COUNT=5

# Storage
NFM_STORAGE_PATH=./storage
NFM_MAX_FILE_SIZE=50MB
NFM_ALLOWED_EXTENSIONS=.pdf,.docx,.pptx,.txt,.jpg,.jpeg,.png,.gif

# Health Check
NFM_HEALTH_CHECK_INTERVAL=30
```

### Configuration File (config.py)

The main configuration file is located at `backend/app/config.py`. It contains:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    NFM_APP_NAME: str = "NFM-X"
    NFM_APP_VERSION: str = "4.0.0"
    NFM_DEBUG: bool = True
    
    # Database
    NFM_DATABASE_URL: str = "sqlite+aiosqlite:///./nfm.db"
    NFM_DATABASE_ECHO: bool = False
    
    # OCR
    NFM_OCR_ENABLED: bool = True
    NFM_OCR_DEFAULT_BACKEND: str = "easyocr"
    NFM_OCR_LANGUAGES: str = "eng,urd,ara"
    NFM_OCR_TABLE_EXTRACTION: bool = True
    
    # Compression
    NFM_COMPRESSION_ENABLED: bool = True
    NFM_COMPRESSION_INTERVAL: str = "daily"
    
    # MCP
    NFM_MCP_ENABLED: bool = True
    
    # Rate Limiting
    NFM_RATE_LIMIT_ENABLED: bool = True
    NFM_RATE_LIMIT_REQUESTS: int = 100
    
    # CORS
    NFM_CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

---

## API Reference

### Base URL
`https://your-server.com/api`

All endpoints return JSON responses and use standard HTTP status codes.

### Authentication

For MCP-protected endpoints, include the API key in the header:

```bash
curl -H "X-API-Key: your_api_key_here" https://your-server.com/api/mcp/config
```

### V4 Endpoints

#### Health Check
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/health | Simple health check |
| GET | /api/health/detailed | Detailed health with all subsystems |
| GET | /api/health/subsystems | Individual subsystem status |
| GET | /api/health/uptime | System uptime |

#### OCR Processing
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/ocr/config | Get OCR configuration |
| GET | /api/ocr/health | Check OCR service health |
| POST | /api/ocr/process | Process a document for OCR |
| POST | /api/ocr/async | Start async OCR job |
| POST | /api/ocr/tables | Extract tables from document |
| GET | /api/ocr/jobs/{job_id} | Get OCR job status |

#### Document Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/documents | List all documents |
| POST | /api/documents | Upload a document |
| GET | /api/documents/{id} | Get document details |
| PUT | /api/documents/{id} | Update document |
| DELETE | /api/documents/{id} | Delete document |
| POST | /api/documents/{id}/reprocess | Reprocess document |

#### Batch Processing
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/batch/upload | Upload multiple files (ZIP/TAR) |
| GET | /api/batch/jobs/{job_id} | Get batch job status |
| POST | /api/batch/cancel/{job_id} | Cancel batch job |

#### Conflict Resolution
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/conflicts | List all conflicts |
| POST | /api/conflicts | Create conflict record |
| GET | /api/conflicts/{id} | Get conflict details |
| POST | /api/conflicts/{id}/resolve | Resolve a conflict |
| POST | /api/conflicts/auto-resolve | Auto-resolve all conflicts |
| POST | /api/conflicts/bulk-resolve | Bulk resolve conflicts |
| DELETE | /api/conflicts/{id} | Dismiss a conflict |

**Conflict Resolution Strategies:**
- `keep_both`: Keep both versions
- `keep_local`: Keep local version
- `keep_remote`: Keep remote version
- `merge`: Merge both versions
- `latest`: Keep the most recent version

#### Pattern Search
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/patterns | List all saved patterns |
| POST | /api/patterns | Create a new pattern |
| GET | /api/patterns/{id} | Get pattern details |
| PUT | /api/patterns/{id} | Update a pattern |
| DELETE | /api/patterns/{id} | Delete a pattern |
| POST | /api/patterns/search | Search with a pattern |
| POST | /api/patterns/{id}/search | Search with saved pattern |
| POST | /api/patterns/validate | Validate a regex pattern |

**Pattern Object:**
```json
{
  "name": "Email Extractor",
  "pattern": "\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
  "description": "Extracts email addresses from text",
  "case_sensitive": false,
  "enabled": true,
  "tags": ["email", "extraction"]
}
```

#### Skill Execution
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/skills | List all skills |
| POST | /api/skills | Register a new skill |
| GET | /api/skills/{id} | Get skill details |
| PUT | /api/skills/{id} | Update a skill |
| DELETE | /api/skills/{id} | Delete a skill |
| POST | /api/skills/{id}/execute | Execute a skill |
| GET | /api/skills/executions | List all executions |
| GET | /api/skills/{id}/executions | List skill executions |
| GET | /api/skills/executions/{execution_id} | Get execution details |

**Skill Object:**
```json
{
  "name": "Text Extractor",
  "description": "Extracts text from documents",
  "skill_type": "extraction",
  "handler": "skills.text_extractor",
  "version": "1.0.0",
  "author": "System",
  "config": {},
  "enabled": true,
  "tags": ["extraction", "text"]
}
```

**Execution Request:**
```json
{
  "input_data": {
    "document_id": "doc_123",
    "options": {}
  },
  "async_execution": false,
  "callback_url": null
}
```

#### MCP Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/mcp/config | Get MCP configuration |
| GET | /api/mcp/keys | List all API keys |
| POST | /api/mcp/keys | Create a new API key |
| GET | /api/mcp/keys/{key_id} | Get API key details |
| PUT | /api/mcp/keys/{key_id} | Update API key |
| DELETE | /api/mcp/keys/{key_id} | Revoke API key |
| POST | /api/mcp/authenticate | Test API key authentication |
| GET | /api/mcp/rate-limit | Get rate limit info |

**API Key Object:**
```json
{
  "name": "Production Key",
  "description": "Main production API key",
  "permissions": ["read", "write"],
  "enabled": true,
  "expires_at": null,
  "rate_limit": 100
}
```

**Permissions:**
- `read`: Read-only access (GET requests)
- `write`: Create and update access (POST, PUT requests)
- `delete`: Delete access (DELETE requests)
- `admin`: Full access including API key management

---

## Frontend Pages

### Page Structure

All pages use:
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Ant Design** components
- **Recharts** for charts
- **Zustand** for state management

### Available Pages

| Page | Path | Description | Features |
|------|------|-------------|----------|
| **Home** | / | Landing page | Overview, quick access |
| **Dashboard** | /dashboard | Main dashboard | Stats, charts, activity |
| **Memories** | /memories | Memory explorer | List, filter, search |
| **Memory Detail** | /memories/:id | Single memory | Full details, edit |
| **Graph** | /graph | Memory graph | Visualize connections |
| **Stats** | /stats | V1 Statistics | Basic stats |
| **Statistics** | /statistics | V4 Statistics | Advanced analytics |
| **Conflicts** | /conflicts | Conflict resolution | List, resolve conflicts |
| **Documents** | /documents | Document management | List, view, delete |
| **Upload** | /upload | Upload documents | Drag & drop, OCR options |
| **Health** | /health | Health monitoring | System status, uptime |
| **Settings** | /settings | Configuration | App, OCR, Memory, API |
| **Patterns** | /patterns | Pattern search | Create, search, validate |
| **Skills** | /skills | Skill execution | Execute, track, manage |
| **MCP** | /mcp | API management | Create keys, test auth |

### Page Components

Each page follows this structure:

```tsx
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

export default function PageName() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Page Title</h1>
          <p className="text-muted-foreground">Description</p>
        </div>
        
        {/* Content */}
        <Card>
          <CardHeader>
            <CardTitle>Section Title</CardTitle>
          </CardHeader>
          <CardContent>
            {/* Content here */}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

---

## Database Models

### SQLAlchemy Models

All models are defined in `backend/app/models/` and use SQLAlchemy 2.0 with async support.

#### Core Models

**Memory** (backend/app/models/memory.py)
```python
class Memory(Base):
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    subtype = Column(String, default="text")
    metadata = Column(JSON, default={})
    confidence = Column(Float, default=1.0)
    compressed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

**User** (backend/app/models/user.py)
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(255), unique=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
```

**Conflict** (backend/app/models/conflict.py)
```python
class Conflict(Base):
    __tablename__ = "conflicts"
    
    id = Column(Integer, primary_key=True)
    memory_id = Column(String, index=True)
    local_content = Column(Text)
    remote_content = Column(Text)
    conflict_type = Column(String)
    status = Column(String, default="pending")
    resolution = Column(String)
    detected_at = Column(DateTime)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
```

**Document** (backend/app/models/document.py)
```python
class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    file_type = Column(String)
    file_path = Column(String)
    size = Column(Integer)
    pages = Column(Integer)
    status = Column(String, default="pending")
    ocr_data = Column(JSON)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, server_default=func.now())

class OCRJob(Base):
    __tablename__ = "ocr_jobs"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer)
    job_id = Column(String, unique=True)
    status = Column(String, default="pending")
    backend = Column(String)
    language = Column(String)
    result = Column(JSON)
    error = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
```

**Pattern** (backend/app/models/pattern.py)
```python
class SearchPattern(Base):
    __tablename__ = "search_patterns"
    
    id = Column(Integer, primary_key=True)
    key_id = Column(String, unique=True)
    name = Column(String)
    pattern = Column(Text)
    description = Column(Text)
    case_sensitive = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)
    tags = Column(String, default="")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    last_used_at = Column(DateTime)
    usage_count = Column(Integer, default=0)
```

**Skill** (backend/app/models/skill.py)
```python
class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    skill_type = Column(String)
    handler = Column(String)
    config = Column(JSON, default={})
    version = Column(String, default="1.0.0")
    author = Column(String)
    enabled = Column(Boolean, default=True)
    tags = Column(String, default="")
    status = Column(String, default="available")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    last_executed_at = Column(DateTime)
    execution_count = Column(Integer, default=0)

class SkillExecution(Base):
    __tablename__ = "skill_executions"
    
    execution_id = Column(String, primary_key=True)
    skill_id = Column(Integer)
    skill_name = Column(String)
    input_data = Column(JSON, default={})
    output_data = Column(JSON)
    error = Column(Text)
    status = Column(String)
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    execution_time_ms = Column(Float)
```

**API Key** (backend/app/models/mcp.py)
```python
class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True)
    key_id = Column(String, unique=True)
    name = Column(String)
    description = Column(Text)
    hashed_secret = Column(String)
    permissions = Column(String, default="read,write")
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime)
    last_used_at = Column(DateTime)
    usage_count = Column(Integer, default=0)
    rate_limit = Column(Integer, default=100)
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest backend/app/tests/test_api.py

# Run with verbose output
pytest -v

# Run and exit on first failure
pytest -x

# Run with coverage
pytest --cov=backend/app --cov-report=html
```

### Test Files

| File | Description |
|------|-------------|
| test_api.py | Core API tests |
| test_v4.py | V4 specific tests |
| test_memory.py | Memory tests |
| test_ocr.py | OCR tests |
| test_conflicts.py | Conflict tests |
| test_patterns.py | Pattern tests |
| test_skills.py | Skill tests |
| test_mcp.py | MCP tests |

### Test Structure

```python
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

class TestEndpointName:
    def test_something(self):
        response = client.get("/api/endpoint")
        assert response.status_code == 200
        data = response.json()
        assert "key" in data
```

---

## Deployment

### Docker Deployment (Recommended)

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY backend/ ./backend/

# Create storage directory
RUN mkdir -p storage logs

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./storage:/app/storage
      - ./logs:/app/logs
      - ./nfm.db:/app/nfm.db
    environment:
      - NFM_ENVIRONMENT=production
      - NFM_DATABASE_URL=sqlite+aiosqlite:///./nfm.db
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    ports:
      - "5173:80"
    depends_on:
      - backend
    restart: unless-stopped
```

**frontend/Dockerfile:**
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY frontend/package*.json ./

RUN npm install

COPY frontend/ ./

RUN npm run build

EXPOSE 80

CMD ["npx", "serve", "-s", "dist", "-l", "80"]
```

### Production Deployment

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /docs {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

**Systemd Service:**
```ini
[Unit]
Description=NFM-X Backend
After=network.target

[Service]
User=your-user
Group=your-group
WorkingDirectory=/path/to/NFM-X
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Troubleshooting

### Common Issues

**1. Database not initialized**
```bash
python -c "from backend.app.database import init_db; import asyncio; asyncio.run(init_db())"
```

**2. Port already in use**
```bash
# Linux/Mac
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**3. Module not found**
```bash
pip install -r requirements.txt
```

**4. CORS issues**
Update `.env`:
```env
NFM_CORS_ORIGINS=["http://localhost:5173", "http://your-domain.com"]
```

**5. OCR not working**
```bash
pip install easyocr
# OR
pip install pytesseract
```

### Debug Mode

Enable debug logging:
```env
NFM_DEBUG=True
NFM_LOG_LEVEL=DEBUG
```

View logs:
```bash
tail -f logs/nfm-x.log
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 4.0.0 | Current | Enhanced OCR, Document Management, Structured Data Extraction, Auto-Compression, Conflict Resolution, Pattern Search, Skill System, MCP Authentication, Modern UI |
| 3.0.0 | Previous | World Model, Predictive Confidence, Causal Graph, Sharing, Sync, Simulation, Compression |
| 2.0.0 | Previous | Enhanced Memory, Advanced Search, Graph, Statistics |
| 1.5.0 | Previous | Bug fixes, improvements |
| 1.0.0 | Initial | Core Memory Storage, Basic Search, Simple API |

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Update documentation
6. Submit a pull request

### Code Style

- **Python**: Follow PEP 8, use type hints
- **TypeScript**: Use TypeScript strict mode
- **Commit Messages**: Use conventional commits
- **Tests**: Minimum 80% coverage

---

## License

MIT License - Copyright (c) 2024 Abdulraheem Nohari

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

---

## Contact

- **Email**: abdulraheemnohri@gmail.com
- **GitHub**: https://github.com/abdulraheemnohri
- **Project**: https://github.com/abdulraheemnohri/NFM-X

---

## اردو وضح - Complete Urdu Documentation

مکمل اردو دستاویزات کے لیے **docs/v4/ur/README_ur.md** دیکھیں۔

---

**Last Updated**: August 3, 2026
**Version**: 4.0.0
