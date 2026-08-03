# NFM-X: Non-Forgettable Memory Layer

## اردو - Urdu

**NFM-X** ایک **Open Source Memory Management System** ہے جو آپ کی تمام معلومات کو محفوظ، منظم، اور تلاش کرنے کے قابل بناتا ہے۔

---

## English

**NFM-X** is an **Open Source Memory Management System** that allows you to store, organize, and retrieve all your information efficiently.

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

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- SQLite (included with Python)

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/abdulraheemnohri/NFM-X.git
   cd NFM-X
   ```

2. Install dependencies:
   ```bash
   cd backend
   pip install -r ../requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. Run the backend:
   ```bash
   python -m backend.app.main
   # or: uvicorn backend.app.main:app --reload
   ```

The backend will be available at: http://localhost:8000

### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Run the frontend:
   ```bash
   npm run dev
   ```

The frontend will be available at: http://localhost:5173

## API Documentation

All API endpoints are documented using Swagger UI and ReDoc:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
NFM-X/
├── backend/                  # FastAPI Backend
│   └── app/
│       ├── api/              # API Routers (v1, v2, v3, v4)
│       ├── config.py         # Configuration
│       ├── database.py       # Database setup
│       ├── health.py         # Health checks
│       ├── logging_config.py # Logging
│       ├── main.py           # Main application
│       ├── middleware/       # Middleware (rate limiting)
│       ├── models/           # Database models
│       ├── ocr/              # OCR engine
│       ├── compression/      # Compression scheduler
│       └── tests/            # Tests
│
├── frontend/                 # React Frontend
│   └── src/
│       ├── components/       # React components
│       ├── pages/            # All pages
│       ├── App.tsx           # Main router
│       ├── Layout.tsx        # Layout component
│       └── index.css         # Modern CSS
│
├── docs/                     # Documentation
│   ├── v2/                  # V2 docs
│   ├── v3/                  # V3 docs
│   └── README.md            # Main docs
│
├── cli/                      # Command Line Interface
├── sdk/                      # SDKs (Python, TypeScript)
├── scripts/                  # Utility scripts
├── storage/                  # Storage files
└── tests/                    # Integration tests
```

## API Endpoints

### V1 Endpoints
- `GET /api/v1/memories` - List all memories
- `POST /api/v1/memories` - Create a memory
- `GET /api/v1/memories/{id}` - Get a memory
- `PUT /api/v1/memories/{id}` - Update a memory
- `DELETE /api/v1/memories/{id}` - Delete a memory
- `GET /api/v1/search` - Search memories
- `GET /api/v1/graph` - Get memory graph
- `GET /api/v1/stats` - Get statistics

### V2 Endpoints
- All V1 endpoints plus enhanced features
- `GET /api/v2/memories` - Enhanced memory listing
- `POST /api/v2/search` - Advanced search
- `GET /api/v2/graph` - Enhanced graph
- `GET /api/v2/stats` - Enhanced statistics

### V3 Endpoints
- World Model entity merge
- Predictive confidence intervals
- Causal graph visualization
- Sharing permissions
- Sync conflict auto-resolution
- Simulation comparison
- Compression scheduling

### V4 Endpoints
- **Health**: `/api/health` - Detailed health checks
- **OCR**: `/api/ocr` - Enhanced OCR processing
- **Documents**: `/api/documents` - Document management
- **Batch**: `/api/batch` - Batch upload
- **Conflicts**: `/api/conflicts` - Conflict resolution
- **Patterns**: `/api/patterns` - Pattern search
- **Skills**: `/api/skills` - Skill execution
- **MCP**: `/api/mcp` - Authentication

## Frontend Pages

| Page | Path | Description |
|------|------|-------------|
| Home | / | Home page |
| Dashboard | /dashboard | Overview dashboard |
| Memories | /memories | Memory explorer |
| Memory Detail | /memories/:id | Single memory view |
| Graph | /graph | Memory graph |
| Stats | /stats | Statistics |
| Conflicts | /conflicts | Conflict resolution |
| Documents | /documents | Document management |
| Upload | /upload | Upload documents |
| Health | /health | Health monitoring |
| Settings | /settings | Configuration |
| Statistics | /statistics | Advanced statistics |
| Patterns | /patterns | Pattern search |
| Skills | /skills | Skill execution |
| MCP | /mcp | API key management |

## Configuration

Copy `.env.example` to `.env` and configure:

```env
# Application
NFM_APP_NAME=NFM-X
NFM_APP_VERSION=4.0.0
NFM_DEBUG=True

# Database
NFM_DATABASE_URL=sqlite+aiosqlite:///./nfm.db
NFM_DATABASE_ECHO=False

# OCR
NFM_OCR_ENABLED=True
NFM_OCR_LANGUAGES=eng,urd,ara
NFM_OCR_TABLE_EXTRACTION=True

# Compression
NFM_COMPRESSION_ENABLED=True
NFM_COMPRESSION_INTERVAL=daily

# MCP
NFM_MCP_ENABLED=True

# Rate Limiting
NFM_RATE_LIMIT_ENABLED=True
NFM_RATE_LIMIT_REQUESTS=100
NFM_RATE_LIMIT_WINDOW=60

# CORS
NFM_CORS_ORIGINS=["*"]
NFM_CORS_METHODS=["*"]
NFM_CORS_HEADERS=["*"]
```

## Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: SQLite (async) with SQLAlchemy 2.0
- **OCR**: EasyOCR, Tesseract, Azure OCR, Google Vision
- **Embeddings**: Sentence Transformers, FAISS
- **Async**: asyncio, aiosqlite

### Frontend
- **Framework**: React 18
- **Language**: TypeScript 5
- **Build**: Vite
- **UI**: Tailwind CSS, Ant Design, Recharts
- **State**: Zustand

### DevOps
- **Testing**: pytest
- **Linting**: ruff, mypy
- **Formatting**: black

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest `
5. Run linting: ` ruff check . `
6. Submit a pull request

## License

MIT License - Feel free to use, modify, and distribute.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: abdulraheemnohri@gmail.com

## Changelog

### V4.0.0 (Latest)
- Enhanced OCR Engine with multiple backends
- Batch Processing and Document Management
- Structured Data Extraction (tables, key-value, entities)
- Auto-Compression Scheduler
- Conflict Resolution API
- Pattern Search & Management
- Skill Execution Tracking
- MCP Authentication
- Detailed Health Check System
- Rate Limiting Middleware
- File Logging Configuration
- Modern UI with 9+ pages

### V3.0.0
- World Model Entity Merge
- Predictive Confidence Intervals
- Causal Graph Visualization
- Sharing Permission Updates
- Sync Conflict Auto-Resolution
- Simulation Comparison
- Compression Scheduling

### V2.0.0
- Enhanced Memory Management
- Advanced Search
- Graph Relationships
- Enhanced Statistics

### V1.0.0
- Core Memory Storage
- Basic Search
- Simple API

---

## اردو وضح - Urdu Explanation

**NFM-X** ایک **Open Source Memory Management System** ہے جو آپ کو آپنی تمام معلومات کو **محفوظ، منظم، اور تلاش** کرنے کی سہولت فراہم کرتا ہے۔

### خاصیتیں:
- **میموری اسٹوریج**: ٹیکسٹ، دستاویزات، امیجز، اور structured data کو محفوظ کریں
- **ایڈوانسڈ سرچ**: پورا ٹیکسٹ سرچ سمجھ کے
- **OCR پروسیسنگ**: PDFs، امیجز، اور دستاویزات سے ٹیکسٹ نکالیں
- **گراف ریلیشنز**: میموریز کے درمیان کنکشنز کو وزوئلائز کریں
- **ورژن کنٹرول**: اپنی میموریز کے چینجز کو ٹریک کریں
- **سنک اینڈ بیکپ**: خودکار طور پر ڈیوائسز کے درمیان سنک کریں

### V4 نئی خصوصیات:
- **بہتر OCR انجن**: کئی بیک اینڈز (EasyOCR, Tesseract, Azure, Google)
- **بیچ پروسیسنگ**: ایک ہی وقت میں کئی دستاویزات اپلوڈ اور پروسیس کریں
- **دستاویز مینجمنٹ**: اپلوڈ کردہ دستاویزات کے لیے مکمل CRUD
- **Structured Data Extraction**: ٹیبلز، کی-ویلیو پیئرز، اور entities نکالیں
- **خودکار کمپریشن**: کنفیگر ایبل شیڈول کے ساتھ خودکار میموری کمپریشن
- **ٹکراؤ حل**: سنک کے لیے خودکار اور مینوئل ٹکراؤ حل
- **پٹرن سرچ**: ریگیکس پر مبنی سرچ کے ساتھ محفوظ پٹرنز
- **ہنر سسٹم**: ایڈوانسڈ پروسیسنگ کے لیے کسٹم ہنر کو چلائیں
- **MCP تصدیق**: API کی چابیوں کا انتظام اور تصدیق
- **تفصیلی ہیلتھ چیک**: مکمل سسٹم مانیٹرنگ
- **ریٹ لیمٹ**: کنفیگر ایبل API ریٹ لیمٹ
- **فائل لاگنگ**: فائل اور کنسل آؤٹ پٹ کے ساتھ مکمل لاگنگ

### تیز آغاز:

1. **ریپوزٹری کلون کریں:**
   ```bash
   git clone https://github.com/abdulraheemnohri/NFM-X.git
   cd NFM-X
   ```

2. **Backed سیٹ اپ کریں:**
   ```bash
   cd backend
   pip install -r ../requirements.txt
   cp .env.example .env
   python -m backend.app.main
   ```

3. **Frontend سیٹ اپ کریں:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

**مبارک ہو!** NFM-X چل رہا ہے۔

- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

---

**All code is automatically pushed to GitHub.**
**کوئی manual command کی ضرورت نہیں۔**
