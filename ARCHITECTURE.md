# NFM-X Architecture Documentation

## Overview
NFM-X (Non-Forgettable Memory Layer) is a production-grade, model-independent long-term memory infrastructure for AI systems.

## System Architecture

USER -> AI APPLICATION/AGENT -> NFM-X MEMORY LAYER -> LLM/VLM/MULTIMODAL MODEL

### Memory Flow
Experience -> Observation -> Memory Candidate -> Validation -> Memory -> Relationship -> Knowledge -> Pattern -> Skill -> Improved Context -> AI -> New Experience

## Core Components

### 1. Memory Orchestrator
- capture(), retrieve(), remember(), recall()
- validate(), classify(), evolve(), compare()
- consolidate(), resolve_conflicts(), build_context()
- learn(), explain()

### 2. Memory Types (15+ classes)
- Working, Episodic, Semantic, Preference
- Project, Decision, Procedural, Skill
- Failure, Success, Temporal, Causal
- Hypothesis, Conflict, Source

### 3. Multimodal Support
TEXT, IMAGE, PDF, SCREENSHOT, AUDIO, VIDEO, DOCUMENT, CODE, TABLE, CSV, JSON, WEB CONTENT, OCR

### 4. OCR Engine
- Supports: Scanned docs, screenshots, photos, PDFs, receipts, invoices, forms, tables, books, code
- Languages: Urdu, English, Urdu-English mixed

### 5. Knowledge Graph
- Entity-Relationship modeling
- Confidence scores, Source tracking, Evidence links

### 6. Evolution Engine
- Reinforcement, Refinement, Expansion, Correction
- Merging, Splitting, Superseding, Contradiction handling

## Data Flow
1. Capture: Experience -> Observation -> Memory Candidate -> Validation -> Memory
2. Retrieval: Query -> Memory Search -> Context Building -> AI Model
3. Evolution: New Memory -> Find Related -> Compare -> Determine Relationship -> Evolve
4. Conflict Resolution: Detect Contradictions -> Analyze Evidence -> Resolve or Preserve

## Storage
- SQLite: Primary database
- FAISS: Vector index
- Filesystem: Document storage
- Backups: Versioned, encrypted

## API Architecture
Client -> API Gateway -> Authentication -> Memory Orchestrator -> Services -> Storage

## Security
- Authentication & Authorization
- API Keys/Tokens
- Memory Permissions
- Agent Isolation
- Encrypted Storage
- Audit Logs
- Integrity Verification

## Performance
Designed for 100K+ to 10M+ memories with indexed queries, pagination, async processing, cached retrieval, batched writes.

## Technology Stack
- Backend: Python 3.10+, FastAPI, Pydantic, SQLAlchemy, SQLite, FAISS
- Frontend: React 18+, TypeScript, Tailwind CSS, Zustand
- OCR: EasyOCR, PaddleOCR, PyTesseract
- AI: llama.cpp, Ollama, Transformers, ONNX, OpenAI-compatible