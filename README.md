# NFM-X: Non-Forgettable Memory Layer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Version: 1.5.0](https://img.shields.io/badge/version-1.5.0-orange.svg)]()

**NFM-X** is a production-grade, model-independent, local-first long-term memory layer for AI systems. It provides a robust foundation for building AI applications that can remember, learn, and evolve over time.

## Core Principles

- **Never Forget**: Once memory is committed, it is never silently overwritten or lost
- **Versioning**: New information creates a new version, history is preserved
- **Provenance**: Every memory has a source and lineage
- **Portability**: Memory remains portable between models and applications

## Features

### V1.0 (Core Memory Layer)
- Memory CRUD operations with versioning
- SQLite-based storage with async support
- Memory classification and capture
- Vector embeddings with FAISS
- Hybrid search (semantic + keyword)
- Context building for LLM prompts
- Python SDK
- CLI interface
- RESTful API with FastAPI

### V1.5 (Relationships & Analytics)
- Conflict detection
- Memory relationships and graph queries
- System statistics and analytics
- Background consolidation jobs
- TypeScript SDK
- React dashboard
- Backup and restore functionality

## Quick Start

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher (for frontend)

### Installation
1. Clone the repository
2. Set up backend with pip install -r requirements.txt
3. Configure environment with cp .env.example .env
4. Start the API with uvicorn app.main:app --reload

For full instructions, see the README.md file.