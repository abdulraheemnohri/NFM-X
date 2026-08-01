# NFM-X REST API Documentation

## Base URL
http://localhost:8765

## Authentication
Authorization: Bearer YOUR_API_KEY

## Endpoints

### Memory
- POST /v1/memory - Create Memory
- GET /v1/memory/{id} - Get Memory
- POST /v1/memory/search - Search Memories
- POST /v1/memory/context - Get Context
- POST /v1/memory/experience - Capture Experience
- POST /v1/memory/evolve - Evolve Memory
- POST /v1/memory/confirm - Confirm Memory
- POST /v1/memory/contradict - Contradict Memory

### Memory History
- GET /v1/memory/{id}/history - Get Memory History
- GET /v1/memory/{id}/lineage - Get Memory Lineage
- GET /v1/memory/{id}/evidence - Get Memory Evidence

### Knowledge Graph
- GET /v1/graph - Get Graph

### Statistics
- GET /v1/stats - Get Stats

### Consolidation
- POST /v1/consolidate - Consolidate Memories

### Backup & Restore
- POST /v1/backup - Create Backup
- POST /v1/restore - Restore Backup

## WebSocket
ws://localhost:8765/ws

## Error Codes
400, 401, 403, 404, 409, 429, 500

## SDK Usage

### Python
from nfm import NFMClient
nfm = NFMClient("http://localhost:8765")
context = nfm.context(agent_id="assistant", query=user_message)
nfm.learn(agent_id="assistant", user_input=user_message, ai_output=response)

### TypeScript
import { NFMClient } from 'nfm-x'
const nfm = new NFMClient('http://localhost:8765')
const context = await nfm.context({ agentId: 'assistant', query: userMessage })
await nfm.learn({ agentId: 'assistant', userInput: userMessage, aiOutput: response })

## Versioning
/v1/, /v2/, /v3/