# NFM-X Architecture Documentation

## Overview

NFM-X (Non-Forgettable Evolutionary AI Memory) is a **standalone, model-independent, local-first AI memory platform** that provides persistent, evolving memory for AI systems.

## System Architecture

```
USER / APPLICATION
        ↓
   AI AGENT
        ↓
   NFM-X MEMORY LAYER
        ↓
   LLM / AI MODEL
```

NFM-X operates as a **middleware layer** between users/applications and AI models.

## Core Components

### 1. Memory Orchestrator
The central controller that manages the entire memory lifecycle.

### 2. Memory Types
- **Working**: Temporary context
- **Episodic**: Experiences
- **Semantic**: Knowledge
- **Procedural**: Task procedures
- **Preference**: Long-term preferences
- **Decision**: Decision records
- **Failure**: Failed strategies
- **Success**: Successful patterns
- **Temporal**: Time-based changes
- **Causal**: Cause-effect relationships
- **Hypothesis**: Unverified knowledge
- **Conflict**: Contradictory knowledge
- **Multimodal**: Non-text memories

## Memory Object Structure

Each memory has:
- Unique ID and root ID
- Version number (immutable)
- Type and subtype
- Content and normalized content
- Agent and source information
- Confidence and importance scores
- Status and validity timestamps
- Relationships to other memories
- Evidence and provenance
- Metadata

## Immutable Version System

Every change creates a new version:
```
M001 (v1)
  ↓
M001 (v2) - REINFORCED
  ↓
M001 (v3) - REFINED
  ↓
M001 (v4) - CURRENT
```

Change types: CREATE, REINFORCE, REFINE, EXPAND, CORRECT, MERGE, SPLIT, SUPERSEDE, CONTRADICT, DISCOVER, RESTORE

## Memory Lifecycle

1. **Capture**: Record AI experiences
2. **Extract**: Identify entities, facts, preferences, etc.
3. **Classify**: Determine memory type
4. **Validate**: Ensure quality
5. **Store**: Permanent storage with provenance
6. **Retrieve**: Find relevant memories
7. **Evolve**: Update based on new information
8. **Preserve**: Maintain immutable history

## Storage Architecture

- **SQLite**: Main relational database
- **FAISS**: Vector index for semantic search
- **Filesystem**: Object storage

## Integration Modes

### Mode A: SDK Middleware (Recommended)
Automatic memory management with minimal code changes.

### Mode B: REST API
Full control via HTTP endpoints.

### Mode C: MCP Server
Expose as Model Context Protocol server.

## Key Innovations

1. **Continuous Memory Loop**: Unlike traditional RAG, NFM-X implements a complete memory lifecycle.
2. **Immutable Memory with Evolution**: Memories are never overwritten, but evolve through new versions.
3. **Hybrid Retrieval**: Combines semantic, keyword, graph, temporal, and other search methods.
4. **Automatic Knowledge Evolution**: Reinforcement, refinement, merging, splitting, contradiction handling.
5. **Model Independence**: Memory format works with any LLM.

## Fundamental Memory Laws

1. NEVER SILENTLY FORGET
2. NEVER SILENTLY OVERWRITE
3. EVOLVE THROUGH NEW VERSIONS
4. PRESERVE HISTORY
5. EVIDENCE FIRST
6. CONTRADICTIONS ARE PRESERVED
7. CURRENT STATE IS SEPARATE FROM HISTORY
8. AUTOMATIC EVOLUTION MUST BE EXPLAINABLE
9. MODEL-INDEPENDENT
10. LOCAL-FIRST

## Future Enhancements

### V2 Features:
- Procedural Memory & Skill Learning
- Causal Memory
- Pattern Discovery
- Memory Consolidation & Compression
- Multimodal Memory
- Memory Replay
- Memory Debugger
- MCP Server
- Android SDK

### V3 Features:
- Autonomous Memory Evolution
- World Model
- Advanced Causal Reasoning
- Predictive Memory
- Strategy Learning
- Cross-Agent Memory
- Multi-Device Synchronization
- Cryptographic Memory Checkpoints

## Conclusion

NFM-X is not just a RAG database. It's a **persistent cognitive memory layer** that enables AI systems to:
- Remember everything
- Understand change
- Evolve forever

*The AI can change its model, knowledge, skills, and beliefs, but its historical memory is never silently lost.*