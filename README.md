# NFM-X: Non-Forgettable Evolutionary AI Memory

**[Remember Everything. Understand Change. Evolve Forever.[**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-07405E?style=flat-square)](https://www.sqlite.org/)

NFM-X is a **standalone, model-independent, local-first AI memory platform** that gives AI systems **persistent, non-forgettable, automatically evolving memory**.

## [32mCore Features[0m

- **Immutable Memory Versions** - Never silently overwrite or forget
- **Automatic Evolution** - Memories evolve through reinforcement, refinement, and contradiction
- **Knowledge Graph** - Structured relationships between memories
- **Multi-Memory Types** - Episodic, Semantic, Procedural, Preference, Decision, and more
- **Model Independence** - Works with any LLM (local or cloud)
- **Local-First** - Complete core functionality works offline
- **Contradiction Preservation** - Conflicting information remains visible
- **Provenance Tracking** - Every memory has full lineage and evidence

## [34mArchitecture[0m

```
USER / APPLICATION
        ↓
   AI AGENT
        ↓
   NFM-X MEMORY LAYER
        ↓
   LLM / AI MODEL
```

NFM-X operates as a **middleware layer** that automatically:
1. Retrieves relevant memories
2. Injects them into AI context
3. Captures new experiences
4. Validates and classifies memories
5. Evolves knowledge over time
6. Preserves immutable history

## [33mInstallation[0m

### Prerequisites
- Python 3.10+
- Git
- (Optional) Local LLM for advanced features

### Quick Start

```bash
# Clone the repository
git clone https://github.com/abdulraheemnohri/NFM-X.git
cd NFM-X

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the NFM-X server
python -m backend.app.main
```

The server will start at `http://localhost:8765`

## [35mUsage[0m

### Python SDK

```python
from nfm import NFMClient

# Connect to NFM-X
nfm = NFMClient("http://localhost:8765")

# Build context for AI
context = nfm.build_context(
    agent_id="my-agent",
    query="Continue my project"
)

# Get AI response (with automatic memory)
response = nfm.ai.chat(
    agent_id="my-agent",
    message="Continue my project"
)

# Manual memory operations
nfm.learn(
    agent_id="my-agent",
    user_input="Continue my project",
    ai_output=response
)
```

### REST API

```bash
# Store a memory
curl -X POST http://localhost:8765/v1/memory \
  -H "Content-Type: application/json" \
  -d '{"type": "episodic", "content": "User requested project continuation"}'

# Search memories
curl -X POST http://localhost:8765/v1/memory/search \
  -H "Content-Type: application/json" \
  -d '{"query": "project", "limit": 10}'

# Get memory context
curl -X POST http://localhost:8765/v1/memory/context \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "my-agent", "query": "project status"}'
```

### CLI

```bash
# Search memories
nfm memory search "project architecture"

# Get memory details
nfm memory get NFM-000001

# View memory history
nfm memory history NFM-000001

# Create backup
nfm backup create

# Verify integrity
nfm integrity verify
```

## [36mProject Structure[0m

```
NFM-X/
├── backend/           # FastAPI server
│   ├── app/           # Main application
│   │   ├── api/       # API endpoints
│   │   ├── memory/    # Memory engines
│   │   ├── graph/     # Knowledge graph
│   │   ├── storage/   # Database and storage
│   │   └── ...
│   └── tests/
├── sdk/              # Client SDKs
│   ├── python/
│   └── typescript/
├── frontend/         # React dashboard
├── cli/              # Command-line interface
├── storage/          # Local storage
├── docs/             # Documentation
└── scripts/          # Utility scripts
```

## Memory Types

| Type | Purpose | Example |
|------|---------|---------|
| **Working** | Temporary context | Current conversation |
| **Episodic** | Experiences | User approved architecture |
| **Semantic** | Knowledge | Facts, definitions |
| **Procedural** | Task procedures | Deployment steps |
| **Preference** | Long-term preferences | User prefers TypeScript |
| **Decision** | Decision records | Architecture choices |
| **Failure** | Failed strategies | Remember what didn't work |
| **Success** | Successful patterns | Working solutions |
| **Temporal** | Time-based changes | Version history |
| **Causal** | Cause-effect relationships | Action outcomes |
| **Hypothesis** | Unverified knowledge | Assumptions to test |
| **Conflict** | Contradictory knowledge | Preserved contradictions |
| **Multimodal** | Non-text memories | Images, audio, video |

## Memory Evolution

Every memory follows an **immutable versioning system**:

```
M001 (v1)
  ↓
M001 (v2) - REINFORCED
  ↓
M001 (v3) - REFINED
  ↓
M001 (v4) - CURRENT
```

Change types:
- `CREATE` - Initial memory
- `REINFORCE` - Confirmed by new evidence
- `REFINE` - Improved detail
- `EXPAND` - Added information
- `CORRECT` - Fixed error
- `MERGE` - Combined with related memory
- `SPLIT` - Divided into multiple memories
- `SUPERSEDE` - Replaced by better version
- `CONTRADICT` - Conflicting evidence found
- `DISCOVER` - New pattern identified
- `RESTORE` - Reverted to previous version

## Integration Modes

### Mode A: SDK Middleware (Recommended)
Automatic memory management with minimal code changes.

### Mode B: REST API
Full control via HTTP endpoints.

### Mode C: MCP Server
Expose as Model Context Protocol server for AI agents.

## Configuration

Create a `.env` file:

```bash
# Server settings
NFM_HOST=0.0.0.0
NFM_PORT=8765
NFM_DEBUG=true

# Storage
NFM_STORAGE_PATH=./storage
NFM_VECTOR_BACKEND=faiss  # or lancedb

# AI Provider (optional)
NFM_LLM_PROVIDER=ollama
NFM_LLM_MODEL=llama3.2
NFM_LLM_BASE_URL=http://localhost:11434

# Authentication
NFM_API_TOKEN=your-secret-token
```

## Dashboard

Start the React dashboard:

```bash
cd frontend
npm install
npm run dev
```

Access at `http://localhost:3000`

Features:
- Memory explorer with search and filtering
- Knowledge graph visualization
- Evolution timeline
- Conflict center
- Pattern discovery
- Debugger
- Settings and configuration

## AI Provider Adapters

NFM-X supports multiple AI providers through adapters:

- **Local LLMs**: llama.cpp, Ollama, Transformers, ONNX Runtime
- **Cloud LLMs**: OpenAI-compatible endpoints
- **Custom Providers**: Implement your own adapter

## Security

- Local authentication with API tokens
- Encrypted storage option
- Access policies and permissions
- Audit logging
- Integrity verification
- Secure export/import

## Releases

### V1 (Current)
- Permanent Memory with Immutable Versions
- Episodic, Semantic, Preference Memory
- Confidence & Provenance Tracking
- Vector Search & Knowledge Graph
- Contradiction Detection
- Automatic Refinement
- REST API & Python SDK
- React Dashboard
- SQLite Storage
- Local Embeddings
- Backup & Import/Export
- CLI

### V2 (Planned)
- Procedural Memory & Skill Learning
- Causal Memory
- Pattern Discovery
- Memory Consolidation & Compression
- Multimodal Memory
- Memory Replay
- Memory Debugger
- MCP Server
- Android SDK

### V3 (Future)
- Autonomous Memory Evolution
- World Model
- Advanced Causal Reasoning
- Predictive Memory
- Strategy Learning
- Cross-Agent Memory
- Multi-Device Synchronization
- Cryptographic Memory Checkpoints

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by human memory systems
- Built with FastAPI, SQLite, and modern AI technologies
- Designed for model independence and longevity

---

**NFM-X: The Memory Operating System for AI**

*"The AI can change its model. The AI can change its knowledge. The AI can improve its skills. The AI can correct its beliefs. But its historical memory is never silently lost."*