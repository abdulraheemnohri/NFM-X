# NFM-X Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying NFM-X in various environments: development, staging, and production.

## Prerequisites

### Required Software

- **Python**: 3.10 or higher
- **Git**: Latest version
- **Docker**: 20.10 or higher (for containerized deployment)
- **Docker Compose**: 2.0 or higher (for multi-container deployment)
- **Redis**: 6.0 or higher (for distributed rate limiting)

### Optional Dependencies

- **PostgreSQL**: For production database (recommended)
- **FAISS**: For vector search (included in requirements)
- **EasyOCR/Tesseract**: For OCR functionality

---

## Installation Methods

### Method 1: Local Development Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/abdulraheemnohri/NFM-X.git
cd NFM-X
```

#### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venvScriptsactivate

# Using conda
conda create -n nfm-x python=3.10
conda activate nfm-x
```

#### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

#### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

#### 5. Initialize Database

```bash
# Create data directory
mkdir -p data storage/vectors

# Run database migrations (if using Alembic)
alembic upgrade head
```

#### 6. Start Development Server

```bash
# Start backend
uvicorn backend.app.main:app --reload --port 8000

# In another terminal, start frontend (if applicable)
cd frontend
npm install
npm run dev
```

---

### Method 2: Docker Compose Deployment

#### 1. Build and Start Containers

```bash
# Build images
docker-compose build

# Start containers
docker-compose up -d

# View logs
docker-compose logs -f
```

#### 2. Stop Containers

```bash
docker-compose down
```

#### 3. Update Containers

```bash
# Pull latest images
docker-compose pull

# Rebuild and restart
docker-compose up -d --build
```

---

### Method 3: Production Deployment with Docker

#### 1. Build Production Image

```bash
docker build -t nfm-x:latest -f Dockerfile .
```

#### 2. Run Production Container

```bash
docker run -d \
  --name nfm-x \
  -p 8000:8000 \
  -v /path/to/data:/app/data \
  -v /path/to/storage:/app/storage \
  --env NFM_SECRET_KEY=your-secret-key \
  --env NFM_DATABASE_URL=sqlite+aiosqlite:////app/data/nfm-x.db \
  nfm-x:latest
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Application
NFM_APP_NAME=NFM-X
NFM_APP_VERSION=4.0.0
NFM_ENVIRONMENT=development
NFM_DEBUG=true
NFM_HOST=0.0.0.0
NFM_PORT=8000
NFM_WORKERS=4

# Database
NFM_DATABASE_URL=sqlite+aiosqlite:///./data/nfm-x.db

# Security
NFM_SECRET_KEY=change-this-in-production-use-long-random-string
NFM_API_KEY=

# Storage
NFM_STORAGE_DIR=./storage
NFM_VECTOR_STORE_DIR=./storage/vectors

# OCR
NFM_OCR_ENABLED=true
NFM_OCR_ENGINE=easyocr
NFM_OCR_LANGUAGES=en,ur
NFM_OCR_TABLE_EXTRACTION=false

# Compression
NFM_COMPRESSION_ENABLED=true
NFM_COMPRESSION_AGE_DAYS=30
NFM_COMPRESSION_IMPORTANCE_THRESHOLD=0.5

# Synchronization
NFM_SYNC_ENABLED=true
NFM_SYNC_CONFLICT_STRATEGY=timestamp
NFM_SYNC_AUTO_RESOLVE=true
NFM_SYNC_INTERVAL_SECONDS=60

# Rate Limiting
NFM_RATE_LIMIT_ENABLED=false
NFM_RATE_LIMIT_REQUESTS_PER_MINUTE=100
NFM_RATE_LIMIT_BURST_REQUESTS=10

# MCP Server
NFM_MCP_ENABLED=false
NFM_MCP_HOST=localhost
NFM_MCP_PORT=8765

# Redis (for distributed rate limiting)
REDIS_URL=redis://localhost:6379/0
```

### Configuration File

Alternatively, you can configure NFM-X through the `backend/app/config.py` file or by setting environment variables before starting the application.

---

## Database Setup

### SQLite (Default)

For development and small deployments, SQLite is used by default:

```bash
# Create directory
mkdir -p data

# The database will be created automatically on first run
```

### PostgreSQL (Recommended for Production)

#### 1. Install PostgreSQL

Follow PostgreSQL installation instructions for your operating system.

#### 2. Create Database and User

```sql
CREATE DATABASE nfm_x;
CREATE USER nfm_user WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE nfm_x TO nfm_user;
```

#### 3. Configure Connection URL

```env
NFM_DATABASE_URL=postgresql+asyncpg://nfm_user:secure-password@localhost:5432/nfm_x
```

---

## Running Tests

### Run All Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html
```

### Run Specific Tests

```bash
# Run a specific test file
pytest backend/tests/test_memory_api.py

# Run tests with a specific marker
pytest -m unit
pytest -m integration
```

---

## Monitoring and Logging

### Access Logs

```bash
# View application logs
tail -f /var/log/nfm-x/app.log
```

### Health Checks

Access the health check endpoint:

```bash
curl http://localhost:8000/api/health
```

### Metrics

NFM-X provides basic metrics through the health check endpoint. For production monitoring, consider integrating with:

- Prometheus + Grafana
- Datadog
- New Relic

---

## Scaling

### Horizontal Scaling

For production deployments with high traffic:

1. **Use a production ASGI server** like Gunicorn with Uvicorn workers:

```bash
gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000 backend.app.main:app
```

2. **Use Redis for shared rate limiting** and session storage

3. **Use a load balancer** (Nginx, HAProxy) in front of multiple instances

### Database Scaling

For high-traffic applications:

- **Use connection pooling** with SQLAlchemy
- **Consider read replicas** for read-heavy workloads
- **Use PostgreSQL** for better performance with concurrent connections

---

## Security Best Practices

### 1. Use HTTPS

Always use HTTPS in production. Use a reverse proxy like Nginx with SSL certificates.

### 2. Secure Secrets

- Never commit secrets to version control
- Use environment variables or secret management services
- Rotate secrets regularly

### 3. Authentication

Enable JWT authentication by configuring the `NFM_SECRET_KEY` and using the authentication middleware.

### 4. Rate Limiting

Enable rate limiting in production:

```env
NFM_RATE_LIMIT_ENABLED=true
NFM_RATE_LIMIT_REQUESTS_PER_MINUTE=100
REDIS_URL=redis://your-redis-server:6379/0
```

### 5. Regular Updates

- Keep dependencies up to date
- Regularly update base images in Docker
- Monitor for security vulnerabilities

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Error:** `sqlite3.OperationalError: unable to open database file`

**Solution:**
- Ensure the data directory exists: `mkdir -p data`
- Check file permissions: `chmod 755 data`
- Verify the database URL in your configuration

#### 2. FAISS Index Errors

**Error:** `FAISS not installed`

**Solution:**
```bash
pip install faiss-cpu  # For CPU
# or
pip install faiss-gpu  # For GPU support
```

#### 3. OCR Engine Errors

**Error:** `EasyOCR not installed`

**Solution:**
```bash
pip install easyocr
```

#### 4. Import Errors

**Error:** `ModuleNotFoundError: No module named '...'`

**Solution:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version compatibility
- Verify virtual environment is activated

---

## API Documentation

After starting the server, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Updates

### Check for Updates

```bash
# Check GitHub for new releases
git fetch origin
git log --oneline origin/main..HEAD
```

### Update Application

```bash
# Pull latest changes
git pull origin main

# Reinstall dependencies
pip install -r requirements.txt

# Restart application
# (depending on your deployment method)
```

---

## Support

For issues, questions, or contributions:

- **GitHub Repository**: https://github.com/abdulraheemnohri/NFM-X
- **Issue Tracker**: https://github.com/abdulraheemnohri/NFM-X/issues
- **Contribution Guide**: See CONTRIBUTING.md

---

## License

NFM-X is licensed under the MIT License. See LICENSE for details.
