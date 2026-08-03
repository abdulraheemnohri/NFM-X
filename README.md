# NFM-X: Non-Forgettable Memory Layer

**NFM-X** is an **Open Source Memory Management System** that allows you to store, organize, and retrieve all your information efficiently with advanced AI-powered features.

## Features

### Core Capabilities
- **Memory Storage**: Store text, documents, images, and structured data
- **Advanced Search**: Full-text search with semantic understanding
- **OCR Processing**: Extract text from PDFs, images, and documents
- **Graph Relationships**: Visualize connections between memories
- **Version Control**: Track changes and history of your memories
- **Sync & Backup**: Automatic synchronization across devices

### V4 Features (Latest)
- **Enhanced OCR Engine**: Multiple backends (EasyOCR, Tesseract, Azure, Google)
- **Batch Processing**: Upload and process multiple documents at once
- **Document Management**: Complete CRUD for uploaded documents
- **Structured Data Extraction**: Extract tables, key-value pairs, and entities
- **Auto-Compression**: Automatic memory compression with configurable schedules
- **Conflict Resolution**: Automatic and manual conflict resolution for sync
- **Pattern Search**: Regex-based search with saved patterns
- **Skill System**: Execute custom skills for advanced processing
- **MCP Authentication**: API key management and authentication
- **Detailed Health Check**: Comprehensive system monitoring
- **Rate Limiting**: Configurable API rate limits
- **File Logging**: Complete logging with file and console output

### V3 Features
- **World Model**: Entity merge and world state management
- **Predictions**: Confidence intervals and predictive analytics
- **Causal Analysis**: Causal graph visualization and analysis
- **Sharing**: Permission-based memory sharing
- **Sync**: Conflict auto-resolution and synchronization
- **Simulation**: Comparison and simulation capabilities
- **Compression**: Scheduling and memory optimization

### V2 Features
- **Enhanced Memory Management**: Advanced memory operations
- **Advanced Search**: Improved search algorithms
- **Graph Relationships**: Enhanced connection visualization
- **Enhanced Statistics**: Detailed analytics and metrics

### V1 Features
- **Core Memory Storage**: Basic memory CRUD operations
- **Simple Search**: Basic text search functionality
- **Basic Graph**: Simple memory relationship visualization

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- SQLite (included with Python)
- Git

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/abdulraheemnohri/NFM-X.git
   cd NFM-X
   ```

2. Create virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # OR
   venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   nano .env  # or use any editor
   ```

5. Initialize database:
   ```bash
   python -c "from backend.app.database import init_db; import asyncio; asyncio.run(init_db())"
   ```

6. Run the backend:
   ```bash
   python -m backend.app.main
   # OR for production
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
   ```

The backend will be available at: http://localhost:8000

### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Run development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

4. Preview production build:
   ```bash
   npm run preview
   ```

The frontend will be available at: http://localhost:5173

## API Documentation

All API endpoints are documented using Swagger UI and ReDoc:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
