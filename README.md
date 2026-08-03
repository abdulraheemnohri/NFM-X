# NFM-X: Non-Forgettable Memory Layer

**NFM-X** is an **Open Source Memory Management System** that allows you to store, organize, and retrieve all your information efficiently with advanced AI-powered features. It provides an immutable, version-controlled memory layer with advanced hybrid search, cryptographic verification, and cognitive workflows.

---

## Table of Contents
1. [Features](#features)
2. [Architecture Source-of-Truth](#architecture-source-of-truth)
3. [Quick Start & Setup](#quick-start--setup)
   - [Local Backend Setup](#local-backend-setup)
   - [Local Frontend Setup](#local-frontend-setup)
4. [Docker & Containerized Deployment](#docker--containerized-deployment)
5. [Database Backups & Restorations](#database-backups--restorations)
6. [CI/CD Pipelines](#cicd-pipelines)
7. [API Endpoint Map](#api-endpoint-map)

---

## Features

### V4 Features (Latest Infrastructure & Security)
- **Enhanced OCR Engine**: Multiple backends (EasyOCR, Tesseract, Azure, Google) with table extraction.
- **Batch Processing**: Upload and process multiple documents synchronously or asynchronously.
- **Auto-Compression**: Automatic memory compression and archiving with configurable background schedules.
- **System Health Monitor**: Production-ready subsystem-level health checks (DB, vector store, storage).
- **CORS & Rate Limiting**: Robust security configurations with custom limit thresholds.
- **API Key Management**: MCP Server key authentication.

### V3 Features (Cognitive & Reasoning Layer)
- **World Model Graph**: Visualized entity merge and multi-hop co-occurrence pathfinding using NetworkX.
- **Predictive Engine**: Pattern-based state forecasting with custom confidence intervals.
- **Causal Reasoning Chains**: Contextual traces and cause-effect mapping.
- **Last-Write-Wins (LWW) Sync**: Secure synchronization across devices with conflict resolution.

### V2 Features (Evolution & Patterns)
- **Automated Memory Evolution**: Relationship classification (DUPLICATE, REINFORCE, CONTRADICT, REFINE, EXPAND).
- **Pattern & Skill Discovery**: Automatically cluster similar memories into discovered skills and procedures.

### V1 Features (Core Versioning & Capture)
- **Immutable Memory Capture**: Dual-committed soft version lineages where updates create new versions and archive parents.
- **Hybrid Retrieval**: Cosine semantic search combined with weighted TF-IDF keyword scores.

---

## Architecture Source-of-Truth
- **Database Pattern**: Standardized on a unified SQLAlchemy 2.0 Async Session pool ( aiomysql / aiosqlite ).
- **Versioning**: Each memory is soft-versioned. Modifying content generates a new row with `version = version + 1`, updates `parent_id`, and marks the parent as `ARCHIVED`.
- **FAISS Vector Indexing**: FlatIP index with L2 normalized vectors and index meta-mapping tracking to persist IDs and metadata across server reboots.

---

## Quick Start & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- SQLite
- Docker (optional)

### Local Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/abdulraheemnohri/NFM-X.git
   cd NFM-X
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database:**
   ```bash
   python -c "from backend.app.database import init_db; import asyncio; asyncio.run(init_db())"
   ```

5. **Run the server:**
   ```bash
   python -m backend.app.main
   ```

The backend API will be available at: http://localhost:8000

---

### Local Frontend Setup

1. **Navigate to the frontend folder:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run development mode:**
   ```bash
   npm run dev
   ```

The dashboard will be available at: http://localhost:5173

---

## Docker & Containerized Deployment

NFM-X is fully dockerized with secure non-root permissions and optimal multi-stage build layers.

### Run with Docker Compose

To start both the unified backend and the frontend dashboard automatically, execute:
```bash
docker-compose up --build
```

- **Backend Portal**: http://localhost:8000
- **Frontend Dashboard**: http://localhost:5173
- **Swagger Documentation**: http://localhost:8000/docs

---

## Database Backups & Restorations

Use the utility helper inside `scripts/backup.py` to package or restore system state into a `.tar.gz` compressed file:

### Create a Backup
```python
from scripts.backup import create_backup
archive_path = create_backup("/path/to/backup/dir")
print(f"Archive created at: {archive_path}")
```

### Restore from Backup
```python
from scripts.backup import restore_backup
restore_backup("/path/to/backup/backup.tar.gz")
```

---

## CI/CD Pipelines

Our `.github/workflows/ci.yml` pipeline automates standard code checks on every push or pull request to the `main` or `master` branches:
- Automatically runs complete Pytest test suites.
- Validates code coverage with coverage reports.

To run the check suite locally:
```bash
python -m pytest tests/
```

---

## API Endpoint Map

All routes are prefixed with `/api/v1` to ensure correct routing. Here is the base API registry:

| Subsystem | Method | Endpoint Path | Description |
| :--- | :---: | :--- | :--- |
| **Memories** | `POST` | `/api/v1/memories/` | Create a new soft-versioned memory |
| **Memories** | `GET` | `/api/v1/memories/` | List and search active memories |
| **Memories** | `GET` | `/api/v1/memories/{id}` | Retrieve memory by UUID |
| **Memories** | `PUT` | `/api/v1/memories/{id}` | Update and capture a new memory version |
| **Memories** | `DELETE` | `/api/v1/memories/{id}` | Soft delete or purge memory |
| **Search** | `GET` | `/api/v1/search/` | Execute weighted hybrid search |
| **Search** | `POST` | `/api/v1/search/semantic` | Execute pure cosine semantic search |
| **Conflicts** | `GET` | `/api/v1/conflicts/` | List outstanding sync conflicts |
| **Conflicts** | `POST` | `/api/v1/conflicts/{id}/resolve` | Resolve conflict with a specific strategy |
| **System** | `GET` | `/health` | Check detailed subsystem health metrics |
| **System** | `GET` | `/version` | Fetch API and environment version details |
