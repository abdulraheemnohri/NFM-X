# NFM-X V3 Development Prompt
## Vision Phase: Cross-Agent Memory, World Model, Predictive Memory & Cryptographic Integrity

> **INSTRUCTION:** Build ONLY what is listed in V3 Scope. V1, V1.5, and V2 MUST be complete, tested, and stable. No placeholder code. No stubs. If a feature cannot be fully implemented, exclude it from V3.

---

## 1. PREREQUISITE

V1, V1.5, and V2 MUST be complete and passing all tests.

---

## 2. V3 SCOPE

### IN SCOPE:

| # | Module | Description |
|---|--------|-------------|
| 1 | **Cross-Agent Memory Sharing** | Share memories between different AI agents with permission controls. Import/export memory bundles. |
| 2 | **World Model** | Structured representation of entities, states, and transitions. Query "what is the current state of X?" |
| 3 | **Predictive Memory** | Use temporal patterns to predict future states. "Based on past patterns, what will happen next?" |
| 4 | **Strategy Learning** | Learn WHEN to use skills, not just HOW. Decision policies from successful/failed strategies. |
| 5 | **Advanced Causal Reasoning** | Multi-hop causal chains. Counterfactual queries. "What if X had not happened?" |
| 6 | **Cryptographic Memory Checkpoints** | SHA-256 chain, periodic Merkle tree, digital signatures for tamper-proof audit trails. |
| 7 | **Multi-Device Synchronization** | Sync memory across devices. Conflict resolution for concurrent edits. |
| 8 | **Memory Simulation Sandbox** | Replay scenarios with modified parameters. Hypothetical reasoning without affecting real memory. |
| 9 | **Advanced Memory Compression** | Summarize old memories. Archive low-importance memories. Semantic deduplication at scale. |

### OUT OF SCOPE:

- Distributed consensus (blockchain-style)
- Federated learning
- Real-time collaborative editing (Google Docs style)
- Natural language generation from memory
- Emotional/sentiment modeling
- Biological neural network integration
- Quantum-resistant cryptography (use standard SHA-256 + ECDSA)
- SaaS multi-tenancy
- Automatic legal compliance (GDPR auto-deletion without user confirmation)

---

## 3. TECH STACK ADDITIONS

```
cryptography         >= 42.0.0
merkletools          >= 1.0.3
pycrdt               >= 0.8.0          # CRDT for multi-device sync
networkx             >= 3.2.0          # World model graph
scikit-learn         >= 1.4.0          # Predictive models (optional, local)
```

---

## 4. IMPLEMENTATION ORDER

**Phase 1:** Cryptographic Checkpoints + Integrity Chain
**Phase 2:** World Model (Entity Graph + State Tracking)
**Phase 3:** Advanced Causal Reasoning (Multi-hop chains)
**Phase 4:** Predictive Memory (Temporal pattern forecasting)
**Phase 5:** Strategy Learning (Decision policies)
**Phase 6:** Cross-Agent Memory Sharing
**Phase 7:** Multi-Device Synchronization
**Phase 8:** Memory Simulation Sandbox
**Phase 9:** Advanced Memory Compression
**Phase 10:** Dashboard Updates (World Model, Predictions, Strategies, Sync Status)

---

## 5. MODULE 1: CRYPTOGRAPHIC MEMORY CHECKPOINTS

### 5.1 Integrity Chain (`backend/app/crypto/integrity.py`)

Every memory gets a hash. Every new memory includes the hash of the previous memory, creating an immutable chain.

```python
import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime, timezone

class IntegrityChain:
    def __init__(self):
        self.algorithm = "sha256"

    def hash_memory(self, memory_data: Dict[str, Any], previous_hash: Optional[str] = None) -> str:
        """Create a cryptographic hash of memory data including previous hash."""
        data = {
            "memory": {k: str(v) if v is not None else None for k, v in memory_data.items()},
            "previous_hash": previous_hash or "0" * 64,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def verify_chain(self, memories: list) -> bool:
        """Verify that a sequence of memories forms a valid integrity chain."""
        for i, mem in enumerate(memories):
            expected_prev = memories[i - 1]["integrity_hash"] if i > 0 else "0" * 64
            recalculated = self.hash_memory(mem, expected_prev)
            if recalculated != mem.get("integrity_hash"):
                return False
        return True
```

### 5.2 Merkle Tree (`backend/app/crypto/merkle.py`)

Periodic Merkle tree over all active memories for batch verification.

```python
import hashlib
from typing import List, Optional

class MerkleTree:
    def __init__(self, leaves: List[str]):
        self.leaves = leaves
        self.tree = self._build_tree(leaves)
        self.root = self.tree[0][0] if self.tree else None

    def _hash_pair(self, a: str, b: str) -> str:
        combined = sorted([a, b])
        return hashlib.sha256((combined[0] + combined[1]).encode()).hexdigest()

    def _build_tree(self, leaves: List[str]) -> List[List[str]]:
        if not leaves:
            return []
        current = leaves[:]
        tree = [current]
        while len(current) > 1:
            next_level = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if i + 1 < len(current) else left
                next_level.append(self._hash_pair(left, right))
            tree.insert(0, next_level)
            current = next_level
        return tree

    def get_proof(self, index: int) -> List[dict]:
        """Get Merkle proof for a leaf at given index."""
        proof = []
        for level in reversed(self.tree[1:]):
            sibling_idx = index + 1 if index % 2 == 0 else index - 1
            if sibling_idx < len(level):
                proof.append({"index": sibling_idx, "hash": level[sibling_idx], "direction": "right" if index % 2 == 0 else "left"})
            index //= 2
        return proof

    def verify_proof(self, leaf_hash: str, index: int, proof: List[dict]) -> bool:
        current = leaf_hash
        for step in proof:
            if step["direction"] == "right":
                current = self._hash_pair(current, step["hash"])
            else:
                current = self._hash_pair(step["hash"], current)
            index //= 2
        return current == self.root
```

### 5.3 Digital Signatures (`backend/app/crypto/signatures.py`)

Sign memory checkpoints with ECDSA for non-repudiation.

```python
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
from typing import Tuple
import base64

class MemorySigner:
    def __init__(self, private_key_pem: str = None):
        if private_key_pem:
            self.private_key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
        else:
            self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()

    def sign(self, data: str) -> str:
        signature = self.private_key.sign(data.encode(), ec.ECDSA(hashes.SHA256()))
        return base64.b64encode(signature).decode()

    def verify(self, data: str, signature_b64: str, public_key_pem: str = None) -> bool:
        try:
            if public_key_pem:
                pub_key = serialization.load_pem_public_key(public_key_pem.encode())
            else:
                pub_key = self.public_key
            signature = base64.b64decode(signature_b64)
            pub_key.verify(signature, data.encode(), ec.ECDSA(hashes.SHA256()))
            return True
        except InvalidSignature:
            return False
        except Exception:
            return False

    def get_public_key_pem(self) -> str:
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
```

### 5.4 Checkpoint API (`backend/app/api/checkpoints.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import select, func

from ..storage.database import get_db_session
from ..memory.models import Memory, MemoryCheckpoint
from ..crypto.integrity import IntegrityChain
from ..crypto.merkle import MerkleTree
from ..crypto.signatures import MemorySigner

router = APIRouter()

class CheckpointResponse(BaseModel):
    id: str
    checkpoint_type: str
    merkle_root: Optional[str] = None
    memory_count: int
    created_at: str
    signature: Optional[str] = None

@router.post("/checkpoints/create")
async def create_checkpoint(db_session=Depends(get_db_session)):
    """Create a cryptographic checkpoint of all active memories."""
    stmt = select(Memory).where(Memory.status == MemoryStatus.ACTIVE).order_by(Memory.created_at)
    result = await db_session.execute(stmt)
    memories = result.scalars().all()

    if not memories:
        raise HTTPException(status_code=400, detail="No active memories to checkpoint")

    # Build integrity chain
    chain = IntegrityChain()
    hashes = []
    prev_hash = None
    for mem in memories:
        mem_hash = chain.hash_memory({
            "id": mem.id, "content": mem.content, "type": mem.type.value,
            "confidence": mem.confidence, "created_at": mem.created_at.isoformat()
        }, prev_hash)
        hashes.append(mem_hash)
        prev_hash = mem_hash

    # Build Merkle tree
    merkle = MerkleTree(hashes)

    # Sign checkpoint
    signer = MemorySigner()
    signature = signer.sign(merkle.root)

    checkpoint = MemoryCheckpoint(
        id=str(uuid.uuid4()), checkpoint_type="full",
        merkle_root=merkle.root, memory_count=len(memories),
        signature=signature, public_key=signer.get_public_key_pem(),
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(checkpoint)
    await db_session.commit()

    return CheckpointResponse(
        id=checkpoint.id, checkpoint_type="full",
        merkle_root=merkle.root, memory_count=len(memories),
        created_at=checkpoint.created_at.isoformat(),
        signature=signature
    )

@router.get("/checkpoints")
async def list_checkpoints(limit: int = 10, db_session=Depends(get_db_session)):
    stmt = select(MemoryCheckpoint).order_by(MemoryCheckpoint.created_at.desc()).limit(limit)
    result = await db_session.execute(stmt)
    checkpoints = result.scalars().all()
    return [CheckpointResponse(
        id=c.id, checkpoint_type=c.checkpoint_type,
        merkle_root=c.merkle_root, memory_count=c.memory_count,
        created_at=c.created_at.isoformat(), signature=c.signature
    ) for c in checkpoints]

@router.get("/checkpoints/{checkpoint_id}/verify")
async def verify_checkpoint(checkpoint_id: str, db_session=Depends(get_db_session)):
    """Verify a checkpoint against current memory state."""
    cp_result = await db_session.execute(select(MemoryCheckpoint).where(MemoryCheckpoint.id == checkpoint_id))
    checkpoint = cp_result.scalar_one_or_none()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    stmt = select(Memory).where(Memory.status == MemoryStatus.ACTIVE).order_by(Memory.created_at)
    result = await db_session.execute(stmt)
    memories = result.scalars().all()

    chain = IntegrityChain()
    hashes = []
    prev_hash = None
    for mem in memories:
        mem_hash = chain.hash_memory({
            "id": mem.id, "content": mem.content, "type": mem.type.value,
            "confidence": mem.confidence, "created_at": mem.created_at.isoformat()
        }, prev_hash)
        hashes.append(mem_hash)
        prev_hash = mem_hash

    merkle = MerkleTree(hashes)
    current_root = merkle.root

    # Verify signature
    signer = MemorySigner()
    signature_valid = signer.verify(checkpoint.merkle_root, checkpoint.signature, checkpoint.public_key)

    return {
        "checkpoint_id": checkpoint_id,
        "stored_root": checkpoint.merkle_root,
        "current_root": current_root,
        "roots_match": checkpoint.merkle_root == current_root,
        "signature_valid": signature_valid,
        "stored_memory_count": checkpoint.memory_count,
        "current_memory_count": len(memories),
        "verified_at": datetime.now(timezone.utc).isoformat()
    }
```

---

## 6. MODULE 2: WORLD MODEL

### 6.1 World Model Engine (`backend/app/world_model/engine.py`)

```python
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

import networkx as nx

from ..memory.models import Memory, MemoryType, MemoryStatus

class WorldModel:
    """Structured representation of entities, states, and transitions."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.entity_types = {"person", "organization", "technology", "location", "concept", "system"}

    async def build_from_memories(self, db_session: AsyncSession, agent_id: Optional[str] = None):
        """Build world model graph from semantic memories."""
        stmt = select(Memory).where(
            Memory.type == MemoryType.SEMANTIC,
            Memory.status == MemoryStatus.ACTIVE
        )
        if agent_id:
            stmt = stmt.where(Memory.agent_id == agent_id)
        result = await db_session.execute(stmt)
        memories = result.scalars().all()

        for mem in memories:
            self._extract_entities_from_memory(mem)

        # Build relationships between entities that co-occur
        for mem in memories:
            entities_in_mem = [n for n, data in self.graph.nodes(data=True)
                               if data.get("source_memory_id") == mem.id]
            for i, e1 in enumerate(entities_in_mem):
                for e2 in entities_in_mem[i + 1:]:
                    if not self.graph.has_edge(e1, e2):
                        self.graph.add_edge(e1, e2, relationship="co_occurs",
                                           strength=1, memories=[mem.id])
                    else:
                        self.graph[e1][e2]["strength"] += 1
                        self.graph[e1][e2]["memories"].append(mem.id)

    def _extract_entities_from_memory(self, memory: Memory):
        """Extract named entities from memory content. Simple NER using keyword lists."""
        content_lower = memory.content.lower()

        # Technology entities
        tech_keywords = ["python", "javascript", "react", "fastapi", "sqlalchemy",
                        "docker", "kubernetes", "aws", "azure", "gpt", "llm"]
        for tech in tech_keywords:
            if tech in content_lower:
                if tech not in self.graph:
                    self.graph.add_node(tech, entity_type="technology",
                                       first_seen=memory.created_at.isoformat(),
                                       source_memory_id=memory.id,
                                       mentions=1)
                else:
                    self.graph.nodes[tech]["mentions"] += 1

        # Person entities (simple heuristic: capitalized words)
        import re
        persons = re.findall(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b", memory.content)
        for person in persons:
            person_lower = person.lower()
            if person_lower not in self.graph:
                self.graph.add_node(person_lower, entity_type="person",
                                   first_seen=memory.created_at.isoformat(),
                                   source_memory_id=memory.id, mentions=1)
            else:
                self.graph.nodes[person_lower]["mentions"] += 1

    def query_entity(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """Query the current state of an entity in the world model."""
        if entity_name not in self.graph:
            return None

        node_data = dict(self.graph.nodes[entity_name])
        neighbors = []
        for neighbor in self.graph.neighbors(entity_name):
            edge_data = self.graph[entity_name][neighbor]
            neighbors.append({
                "entity": neighbor,
                "relationship": edge_data.get("relationship", "related"),
                "strength": edge_data.get("strength", 1),
                "entity_type": self.graph.nodes[neighbor].get("entity_type", "unknown")
            })

        return {
            "entity": entity_name,
            "entity_type": node_data.get("entity_type", "unknown"),
            "mentions": node_data.get("mentions", 0),
            "first_seen": node_data.get("first_seen"),
            "related_entities": neighbors,
            "related_count": len(neighbors)
        }

    def find_path(self, source: str, target: str, max_hops: int = 3) -> Optional[List[str]]:
        """Find connection path between two entities."""
        try:
            path = nx.shortest_path(self.graph, source, target)
            if len(path) - 1 <= max_hops:
                return path
            return None
        except nx.NetworkXNoPath:
            return None

    def get_central_entities(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Get most central entities by degree centrality."""
        centrality = nx.degree_centrality(self.graph)
        sorted_entities = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        return [
            {"entity": name, "centrality": round(score, 4),
             "entity_type": self.graph.nodes[name].get("entity_type", "unknown"),
             "mentions": self.graph.nodes[name].get("mentions", 0)}
            for name, score in sorted_entities[:top_n]
        ]
```

### 6.2 World Model API (`backend/app/api/world_model.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from ..storage.database import get_db_session
from ..world_model.engine import WorldModel

router = APIRouter()

_world_model_cache = None

async def _get_world_model(db_session):
    global _world_model_cache
    if _world_model_cache is None:
        _world_model_cache = WorldModel()
        await _world_model_cache.build_from_memories(db_session)
    return _world_model_cache

@router.get("/world-model/entity/{entity_name}")
async def get_entity(entity_name: str, db_session=Depends(get_db_session)):
    wm = await _get_world_model(db_session)
    result = wm.query_entity(entity_name.lower())
    if not result:
        raise HTTPException(status_code=404, detail="Entity not found in world model")
    return result

@router.get("/world-model/path")
async def find_entity_path(source: str, target: str, max_hops: int = 3, db_session=Depends(get_db_session)):
    wm = await _get_world_model(db_session)
    path = wm.find_path(source.lower(), target.lower(), max_hops)
    if not path:
        return {"source": source, "target": target, "path": None, "connected": False}
    return {"source": source, "target": target, "path": path, "hops": len(path) - 1, "connected": True}

@router.get("/world-model/central")
async def get_central_entities(top_n: int = 10, db_session=Depends(get_db_session)):
    wm = await _get_world_model(db_session)
    return {"entities": wm.get_central_entities(top_n)}

@router.post("/world-model/rebuild")
async def rebuild_world_model(db_session=Depends(get_db_session)):
    global _world_model_cache
    _world_model_cache = None
    wm = await _get_world_model(db_session)
    return {"status": "rebuilt", "entity_count": len(wm.graph.nodes), "relationship_count": len(wm.graph.edges)}
```

---

## 7. MODULE 3: PREDICTIVE MEMORY

### 7.1 Predictive Engine (`backend/app/predictions/engine.py`)

```python
from typing import List, Dict, Any, Optional
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import numpy as np

from ..memory.models import Memory, MemoryType, MemoryStatus

class PredictiveMemoryEngine:
    """Predict future states based on temporal patterns in memory."""

    def __init__(self):
        self.min_pattern_length = 2
        self.confidence_threshold = 0.6

    async def predict_next(self, db_session: AsyncSession, agent_id: Optional[str] = None,
                           context_query: str = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """Predict what memory/state is most likely to follow given context."""
        stmt = select(Memory).where(Memory.status == MemoryStatus.ACTIVE)
        if agent_id:
            stmt = stmt.where(Memory.agent_id == agent_id)
        stmt = stmt.order_by(Memory.created_at)
        result = await db_session.execute(stmt)
        memories = result.scalars().all()

        if len(memories) < 3:
            return []

        # Find sequences where context_query appears
        if context_query:
            relevant_indices = [i for i, m in enumerate(memories) if context_query.lower() in m.content.lower()]
        else:
            relevant_indices = list(range(len(memories) - 1))

        # What typically follows these memories?
        next_memory_counts = defaultdict(lambda: {"count": 0, "memories": []})
        for idx in relevant_indices:
            if idx + 1 < len(memories):
                next_mem = memories[idx + 1]
                key = (next_mem.type.value, next_mem.content[:100])
                next_memory_counts[key]["count"] += 1
                next_memory_counts[key]["memories"].append(next_mem.id)
                next_memory_counts[key]["full_content"] = next_mem.content

        total = len(relevant_indices)
        predictions = []
        for key, data in sorted(next_memory_counts.items(), key=lambda x: x[1]["count"], reverse=True)[:top_k]:
            confidence = min(0.95, data["count"] / total if total > 0 else 0)
            if confidence >= self.confidence_threshold:
                predictions.append({
                    "predicted_type": key[0],
                    "predicted_content": data["full_content"],
                    "confidence": round(confidence, 3),
                    "based_on_count": data["count"],
                    "sample_memory_ids": data["memories"][:3]
                })

        return predictions

    async def predict_trend(self, db_session: AsyncSession, entity: str,
                            agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Predict trend for an entity (increasing, decreasing, stable)."""
        stmt = select(Memory).where(
            Memory.status == MemoryStatus.ACTIVE,
            Memory.content.ilike(f"%{entity}%")
        )
        if agent_id:
            stmt = stmt.where(Memory.agent_id == agent_id)
        stmt = stmt.order_by(Memory.created_at)
        result = await db_session.execute(stmt)
        memories = result.scalars().all()

        if len(memories) < 3:
            return {"entity": entity, "trend": "insufficient_data", "confidence": 0.0}

        # Simple trend: check if confidence is increasing over time
        confidences = [m.confidence for m in memories]
        x = np.arange(len(confidences))
        slope = np.polyfit(x, confidences, 1)[0] if len(confidences) > 1 else 0

        if slope > 0.01:
            trend = "increasing"
        elif slope < -0.01:
            trend = "decreasing"
        else:
            trend = "stable"

        return {
            "entity": entity,
            "trend": trend,
            "slope": round(float(slope), 4),
            "confidence": round(min(0.95, abs(slope) * 10 + 0.3), 3),
            "data_points": len(memories),
            "latest_confidence": confidences[-1]
        }
```

### 7.2 Predictions API (`backend/app/api/predictions.py`)

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional

from ..storage.database import get_db_session
from ..predictions.engine import PredictiveMemoryEngine

router = APIRouter()

class PredictRequest(BaseModel):
    context_query: Optional[str] = None
    agent_id: Optional[str] = None
    top_k: int = 3

class TrendRequest(BaseModel):
    entity: str
    agent_id: Optional[str] = None

@router.post("/predictions/next")
async def predict_next(request: PredictRequest, db_session=Depends(get_db_session)):
    engine = PredictiveMemoryEngine()
    predictions = await engine.predict_next(
        db_session=db_session, agent_id=request.agent_id,
        context_query=request.context_query, top_k=request.top_k
    )
    return {"predictions": predictions, "context": request.context_query}

@router.post("/predictions/trend")
async def predict_trend(request: TrendRequest, db_session=Depends(get_db_session)):
    engine = PredictiveMemoryEngine()
    trend = await engine.predict_trend(db_session=db_session, entity=request.entity, agent_id=request.agent_id)
    return trend
```

---

## 8. MODULE 4: STRATEGY LEARNING

### 8.1 Strategy Engine (`backend/app/strategy/engine.py`)

```python
from typing import List, Dict, Any, Optional
from collections import defaultdict
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid

from ..memory.models import Memory, MemoryDecision, MemorySkill, MemoryType, MemoryStatus

class StrategyLearningEngine:
    """Learn WHEN to use skills (decision policies), not just HOW."""

    async def analyze_decision_outcomes(self, db_session: AsyncSession,
                                        agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Analyze which decisions led to success vs failure."""
        stmt = select(Memory).where(Memory.type == MemoryType.DECISION, Memory.status == MemoryStatus.ACTIVE)
        if agent_id:
            stmt = stmt.where(Memory.agent_id == agent_id)
        result = await db_session.execute(stmt)
        decisions = result.scalars().all()

        # Find subsequent success/failure memories for each decision
        strategies = defaultdict(lambda: {"successes": 0, "failures": 0, "total": 0, "contexts": []})

        for decision in decisions:
            # Look for success/failure within next 10 memories
            stmt2 = select(Memory).where(
                Memory.agent_id == decision.agent_id,
                Memory.created_at > decision.created_at,
                Memory.type.in_([MemoryType.SUCCESS, MemoryType.FAILURE])
            ).order_by(Memory.created_at).limit(10)
            result2 = await db_session.execute(stmt2)
            outcomes = result2.scalars().all()

            decision_key = decision.content[:100]
            for outcome in outcomes:
                if (outcome.created_at - decision.created_at).total_seconds() < 3600:  # Within 1 hour
                    strategies[decision_key]["total"] += 1
                    strategies[decision_key]["contexts"].append({
                        "decision_id": decision.id,
                        "outcome_id": outcome.id,
                        "outcome_type": outcome.type.value,
                        "time_delta_sec": (outcome.created_at - decision.created_at).total_seconds()
                    })
                    if outcome.type == MemoryType.SUCCESS:
                        strategies[decision_key]["successes"] += 1
                    else:
                        strategies[decision_key]["failures"] += 1

        # Build strategy recommendations
        recommendations = []
        for decision_text, data in strategies.items():
            if data["total"] >= 3:
                success_rate = data["successes"] / data["total"]
                if success_rate >= 0.7:
                    recommendation = "recommended"
                elif success_rate <= 0.3:
                    recommendation = "avoid"
                else:
                    recommendation = "conditional"

                recommendations.append({
                    "decision": decision_text,
                    "success_rate": round(success_rate, 3),
                    "total_attempts": data["total"],
                    "successes": data["successes"],
                    "failures": data["failures"],
                    "recommendation": recommendation,
                    "confidence": round(min(0.95, 0.3 + success_rate * 0.6), 3)
                })

        recommendations.sort(key=lambda x: x["success_rate"], reverse=True)
        return recommendations

    async def create_strategy(self, db_session: AsyncSession, decision_pattern: str,
                              recommendation: str, confidence: float) -> MemorySkill:
        """Create a high-level strategy from analyzed patterns."""
        strategy = MemorySkill(
            id=str(uuid.uuid4()),
            name=f"Strategy: {decision_pattern[:50]}",
            description=f"Learned strategy: {recommendation} | Confidence: {confidence}",
            source_procedure_ids=[],
            success_rate=confidence,
            execution_count=0,
            confidence=confidence,
            created_at=datetime.now(timezone.utc),
            skill_type="strategy",
            metadata={"decision_pattern": decision_pattern, "recommendation": recommendation}
        )
        db_session.add(strategy)
        await db_session.commit()
        return strategy
```

### 8.2 Strategy API (`backend/app/api/strategy.py`)

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from ..storage.database import get_db_session
from ..strategy.engine import StrategyLearningEngine

router = APIRouter()

@router.get("/strategies")
async def get_strategies(agent_id: Optional[str] = None, db_session=Depends(get_db_session)):
    engine = StrategyLearningEngine()
    strategies = await engine.analyze_decision_outcomes(db_session, agent_id)
    return {"strategies": strategies, "count": len(strategies)}

@router.post("/strategies/learn")
async def learn_strategies(agent_id: Optional[str] = None, db_session=Depends(get_db_session)):
    engine = StrategyLearningEngine()
    strategies = await engine.analyze_decision_outcomes(db_session, agent_id)
    created = []
    for s in strategies:
        if s["confidence"] >= 0.7 and s["total_attempts"] >= 5:
            strategy = await engine.create_strategy(
                db_session, s["decision"], s["recommendation"], s["confidence"]
            )
            created.append({"id": strategy.id, "name": strategy.name, "confidence": strategy.confidence})
    return {"analyzed": len(strategies), "created": len(created), "strategies": created}
```

---

## 9. MODULE 5: ADVANCED CAUSAL REASONING

### 9.1 Multi-hop Causal Engine (`backend/app/causal/advanced.py`)

```python
from typing import List, Dict, Any, Optional, Set
from collections import deque
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..memory.models import Memory, MemoryType, MemoryStatus, MemoryRelationship

class AdvancedCausalEngine:
    """Multi-hop causal chain reasoning and counterfactual queries."""

    async def find_causal_chain(self, db_session: AsyncSession, cause: str, effect: str,
                                 max_hops: int = 5) -> Optional[List[Dict[str, Any]]]:
        """Find causal chain from cause to effect through multiple hops."""
        # BFS through causal relationships
        stmt = select(Memory).where(Memory.type == MemoryType.CAUSAL, Memory.status == MemoryStatus.ACTIVE)
        result = await db_session.execute(stmt)
        causal_memories = result.scalars().all()

        # Build adjacency list
        graph = {}
        for mem in causal_memories:
            meta = mem.metadata or {}
            c = meta.get("cause", "").lower()
            e = meta.get("effect", "").lower()
            if c and e:
                if c not in graph:
                    graph[c] = []
                graph[c].append({"effect": e, "memory_id": mem.id, "relationship_type": meta.get("relationship_type", "causes")})

        # BFS
        queue = deque([(cause.lower(), [])])
        visited = set()
        while queue:
            current, path = queue.popleft()
            if current == effect.lower():
                return path
            if current in visited or len(path) >= max_hops:
                continue
            visited.add(current)
            for edge in graph.get(current, []):
                if edge["effect"] not in visited:
                    new_path = path + [{"cause": current, **edge}]
                    queue.append((edge["effect"], new_path))
        return None

    async def counterfactual_query(self, db_session: AsyncSession, hypothetical_remove: str,
                                   agent_id: Optional[str] = None) -> Dict[str, Any]:
        """What would be different if 'hypothetical_remove' had not happened?"""
        # Find all memories that mention the removed event
        stmt = select(Memory).where(
            Memory.content.ilike(f"%{hypothetical_remove}%"),
            Memory.status == MemoryStatus.ACTIVE
        )
        if agent_id:
            stmt = stmt.where(Memory.agent_id == agent_id)
        result = await db_session.execute(stmt)
        removed_memories = result.scalars().all()

        # Find downstream effects (memories that reference these)
        downstream = []
        for mem in removed_memories:
            stmt2 = select(MemoryRelationship).where(MemoryRelationship.memory_id == mem.id)
            result2 = await db_session.execute(stmt2)
            rels = result2.scalars().all()
            for rel in rels:
                mem_result = await db_session.execute(select(Memory).where(Memory.id == rel.related_id))
                related = mem_result.scalar_one_or_none()
                if related:
                    downstream.append({
                        "removed_memory_id": mem.id,
                        "removed_content": mem.content[:100],
                        "affected_memory_id": related.id,
                        "affected_content": related.content[:100],
                        "relationship": rel.relationship_type
                    })

        return {
            "hypothetical_remove": hypothetical_remove,
            "removed_memory_count": len(removed_memories),
            "downstream_effects": downstream,
            "affected_count": len(downstream),
            "note": "Counterfactual: These effects would potentially not exist"
        }
```

### 9.2 Causal API (`backend/app/api/causal_advanced.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..storage.database import get_db_session
from ..causal.advanced import AdvancedCausalEngine

router = APIRouter()

class CausalChainRequest(BaseModel):
    cause: str
    effect: str
    max_hops: int = 5

class CounterfactualRequest(BaseModel):
    remove_event: str
    agent_id: Optional[str] = None

@router.post("/causal/chain")
async def find_causal_chain(request: CausalChainRequest, db_session=Depends(get_db_session)):
    engine = AdvancedCausalEngine()
    chain = await engine.find_causal_chain(db_session, request.cause, request.effect, request.max_hops)
    if not chain:
        return {"cause": request.cause, "effect": request.effect, "chain": None, "found": False}
    return {"cause": request.cause, "effect": request.effect, "chain": chain, "hops": len(chain), "found": True}

@router.post("/causal/counterfactual")
async def counterfactual(request: CounterfactualRequest, db_session=Depends(get_db_session)):
    engine = AdvancedCausalEngine()
    return await engine.counterfactual_query(db_session, request.remove_event, request.agent_id)
```

---

## 10. MODULE 6: CROSS-AGENT MEMORY SHARING

### 10.1 Sharing Protocol (`backend/app/sharing/protocol.py`)

```python
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from enum import Enum
import uuid

class SharePermission(str, Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

class MemoryBundle:
    """A portable package of memories for sharing between agents."""

    def __init__(self, source_agent_id: str, target_agent_id: str,
                 memories: List[Dict[str, Any]], permissions: SharePermission = SharePermission.READ):
        self.bundle_id = str(uuid.uuid4())
        self.source_agent_id = source_agent_id
        self.target_agent_id = target_agent_id
        self.memories = memories
        self.permissions = permissions
        self.created_at = datetime.now(timezone.utc)
        self.status = "pending"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "source_agent_id": self.source_agent_id,
            "target_agent_id": self.target_agent_id,
            "memory_count": len(self.memories),
            "permissions": self.permissions.value,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "memories": self.memories
        }

    def validate_bundle(self) -> bool:
        """Validate bundle integrity before import."""
        if not self.memories:
            return False
        for mem in self.memories:
            if not mem.get("content") or not mem.get("type"):
                return False
        return True
```

### 10.2 Sharing API (`backend/app/api/sharing.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import select
from datetime import datetime, timezone
import uuid

from ..storage.database import get_db_session
from ..memory.models import Memory, MemoryStatus, MemoryType
from ..sharing.protocol import MemoryBundle, SharePermission

router = APIRouter()

class ShareRequest(BaseModel):
    source_agent_id: str
    target_agent_id: str
    memory_ids: List[str]
    permissions: str = "read"  # read, write, admin
    note: Optional[str] = None

class ImportRequest(BaseModel):
    bundle: dict
    target_agent_id: str

@router.post("/sharing/export")
async def export_memories(request: ShareRequest, db_session=Depends(get_db_session)):
    """Export memories into a shareable bundle."""
    memories = []
    for mem_id in request.memory_ids:
        result = await db_session.execute(select(Memory).where(Memory.id == mem_id))
        mem = result.scalar_one_or_none()
        if mem:
            memories.append({
                "id": mem.id, "type": mem.type.value, "content": mem.content,
                "confidence": mem.confidence, "importance": mem.importance,
                "metadata": mem.metadata, "original_agent": mem.agent_id,
                "original_created_at": mem.created_at.isoformat() if mem.created_at else None
            })

    bundle = MemoryBundle(
        source_agent_id=request.source_agent_id,
        target_agent_id=request.target_agent_id,
        memories=memories,
        permissions=SharePermission(request.permissions)
    )
    bundle.status = "ready"

    return {"bundle": bundle.to_dict(), "export_count": len(memories)}

@router.post("/sharing/import")
async def import_memories(request: ImportRequest, db_session=Depends(get_db_session)):
    """Import memories from a bundle."""
    bundle_data = request.bundle
    bundle = MemoryBundle(
        source_agent_id=bundle_data["source_agent_id"],
        target_agent_id=request.target_agent_id,
        memories=bundle_data["memories"],
        permissions=SharePermission(bundle_data.get("permissions", "read"))
    )

    if not bundle.validate_bundle():
        raise HTTPException(status_code=400, detail="Invalid bundle")

    imported = []
    for mem_data in bundle.memories:
        new_mem = Memory(
            id=str(uuid.uuid4()),
            root_id=str(uuid.uuid4()),
            version=1,
            type=MemoryType(mem_data["type"]),
            content=mem_data["content"],
            normalized_content=mem_data["content"].lower().strip(),
            agent_id=request.target_agent_id,
            source_id=f"imported:{mem_data.get('original_agent', 'unknown')}",
            confidence=mem_data.get("confidence", 0.5),
            importance=mem_data.get("importance", 0.5),
            status=MemoryStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            observed_at=datetime.now(timezone.utc),
            valid_from=datetime.now(timezone.utc),
            metadata={
                **(mem_data.get("metadata") or {}),
                "imported_from": bundle.source_agent_id,
                "original_id": mem_data["id"],
                "imported_at": datetime.now(timezone.utc).isoformat()
            }
        )
        db_session.add(new_mem)
        imported.append(new_mem.id)

    await db_session.commit()
    return {"imported_count": len(imported), "imported_ids": imported, "source_agent": bundle.source_agent_id}
```

---

## 11. MODULE 7: MULTI-DEVICE SYNCHRONIZATION

### 11.1 Sync Engine (`backend/app/sync/engine.py`)

Use last-write-wins with conflict detection. NOT full CRDT (too complex for V3).

```python
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from ..memory.models import Memory, MemoryStatus, MemoryType, MemoryVersion

class SyncEngine:
    """Synchronize memories across devices."""

    async def generate_sync_payload(self, db_session: AsyncSession, device_id: str,
                                     last_sync: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate sync payload for a device."""
        stmt = select(Memory).where(Memory.status == MemoryStatus.ACTIVE)
        if last_sync:
            stmt = stmt.where(Memory.created_at > last_sync)
        stmt = stmt.order_by(Memory.created_at)
        result = await db_session.execute(stmt)
        memories = result.scalars().all()

        return {
            "device_id": device_id,
            "sync_timestamp": datetime.now(timezone.utc).isoformat(),
            "memory_count": len(memories),
            "memories": [
                {
                    "id": m.id, "root_id": m.root_id, "version": m.version,
                    "type": m.type.value, "content": m.content,
                    "confidence": m.confidence, "importance": m.importance,
                    "status": m.status.value, "created_at": m.created_at.isoformat(),
                    "agent_id": m.agent_id, "metadata": m.metadata
                }
                for m in memories
            ]
        }

    async def apply_sync_payload(self, db_session: AsyncSession, payload: Dict[str, Any],
                                  local_device_id: str) -> Dict[str, Any]:
        """Apply incoming sync payload. Detect and report conflicts."""
        conflicts = []
        imported = []
        skipped = []

        for mem_data in payload.get("memories", []):
            # Check if memory already exists locally
            result = await db_session.execute(select(Memory).where(Memory.id == mem_data["id"]))
            existing = result.scalar_one_or_none()

            if existing:
                # Conflict detection: same ID, different content
                if existing.content != mem_data["content"]:
                    if existing.created_at > datetime.fromisoformat(mem_data["created_at"]):
                        # Local is newer — keep local, report conflict
                        conflicts.append({
                            "memory_id": mem_data["id"],
                            "resolution": "local_wins",
                            "local_version": existing.version,
                            "remote_version": mem_data["version"],
                            "reason": "Local memory is newer"
                        })
                        skipped.append(mem_data["id"])
                    else:
                        # Remote is newer — create new version
                        from ..memory.evolution import MemoryEvolution
                        evo = MemoryEvolution()
                        new_version = await evo.create_version(
                            db_session=db_session,
                            memory_id=existing.id,
                            new_content=mem_data["content"],
                            change_type="sync_update",
                            change_reason=f"Synced from device {payload.get('device_id', 'unknown')}",
                            actor_id="sync",
                            confidence=mem_data.get("confidence", existing.confidence)
                        )
                        imported.append(new_version.id)
                        conflicts.append({
                            "memory_id": mem_data["id"],
                            "resolution": "remote_wins",
                            "new_version_id": new_version.id,
                            "reason": "Remote memory is newer"
                        })
                else:
                    # Same content — no conflict
                    skipped.append(mem_data["id"])
            else:
                # New memory — import directly
                new_mem = Memory(
                    id=mem_data["id"],
                    root_id=mem_data.get("root_id", mem_data["id"]),
                    version=mem_data.get("version", 1),
                    type=MemoryType(mem_data["type"]),
                    content=mem_data["content"],
                    normalized_content=mem_data["content"].lower().strip(),
                    agent_id=mem_data.get("agent_id"),
                    source_id=f"sync:{payload.get('device_id', 'unknown')}",
                    confidence=mem_data.get("confidence", 0.7),
                    importance=mem_data.get("importance", 0.5),
                    status=MemoryStatus.ACTIVE,
                    created_at=datetime.fromisoformat(mem_data["created_at"]),
                    observed_at=datetime.now(timezone.utc),
                    valid_from=datetime.now(timezone.utc),
                    metadata={
                        **(mem_data.get("metadata") or {}),
                        "synced_from": payload.get("device_id"),
                        "synced_at": datetime.now(timezone.utc).isoformat()
                    }
                )
                db_session.add(new_mem)
                imported.append(new_mem.id)

        await db_session.commit()
        return {
            "imported": imported,
            "skipped": skipped,
            "conflicts": conflicts,
            "conflict_count": len(conflicts),
            "local_device_id": local_device_id
        }
```

### 11.2 Sync API (`backend/app/api/sync.py`)

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ..storage.database import get_db_session
from ..sync.engine import SyncEngine

router = APIRouter()

class SyncPullRequest(BaseModel):
    device_id: str
    last_sync: Optional[str] = None

class SyncPushRequest(BaseModel):
    device_id: str
    payload: dict

@router.post("/sync/pull")
async def sync_pull(request: SyncPullRequest, db_session=Depends(get_db_session)):
    engine = SyncEngine()
    last_sync = datetime.fromisoformat(request.last_sync) if request.last_sync else None
    payload = await engine.generate_sync_payload(db_session, request.device_id, last_sync)
    return payload

@router.post("/sync/push")
async def sync_push(request: SyncPushRequest, db_session=Depends(get_db_session)):
    engine = SyncEngine()
    result = await engine.apply_sync_payload(db_session, request.payload, request.device_id)
    return result
```

---

## 12. MODULE 8: MEMORY SIMULATION SANDBOX

### 12.1 Simulation Engine (`backend/app/simulation/engine.py`)

```python
from typing import Dict, Any, List, Optional
from copy import deepcopy
from datetime import datetime, timezone

class MemorySandbox:
    """Simulate scenarios without affecting real memory."""

    def __init__(self, memories: List[Dict[str, Any]]):
        self.original_memories = memories
        self.simulated_memories = deepcopy(memories)
        self.simulation_log = []
        self.simulation_id = f"sim-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    def inject_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """Inject a hypothetical memory into the simulation."""
        mem_copy = deepcopy(memory)
        mem_copy["id"] = f"sim_{mem_copy.get('id', 'new')}"
        mem_copy["_simulated"] = True
        self.simulated_memories.append(mem_copy)
        self.simulation_log.append({"action": "inject", "memory_id": mem_copy["id"]})
        return mem_copy

    def remove_memory(self, memory_id: str) -> bool:
        """Remove a memory from the simulation."""
        original_count = len(self.simulated_memories)
        self.simulated_memories = [m for m in self.simulated_memories if m.get("id") != memory_id]
        removed = len(self.simulated_memories) < original_count
        if removed:
            self.simulation_log.append({"action": "remove", "memory_id": memory_id})
        return removed

    def modify_memory(self, memory_id: str, new_content: str) -> Optional[Dict[str, Any]]:
        """Modify a memory in the simulation."""
        for mem in self.simulated_memories:
            if mem.get("id") == memory_id:
                mem["content"] = new_content
                mem["_modified"] = True
                self.simulation_log.append({"action": "modify", "memory_id": memory_id})
                return mem
        return None

    def query_simulation(self, query: str) -> List[Dict[str, Any]]:
        """Search within simulated memories."""
        results = []
        query_lower = query.lower()
        for mem in self.simulated_memories:
            score = 0
            if query_lower in mem.get("content", "").lower():
                score += 1.0
            if query_lower in mem.get("type", "").lower():
                score += 0.5
            if score > 0:
                results.append({**mem, "simulated_score": score})
        results.sort(key=lambda x: x["simulated_score"], reverse=True)
        return results

    def get_state(self) -> Dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "original_count": len(self.original_memories),
            "simulated_count": len(self.simulated_memories),
            "injected_count": sum(1 for m in self.simulated_memories if m.get("_simulated")),
            "modified_count": sum(1 for m in self.simulated_memories if m.get("_modified")),
            "log": self.simulation_log
        }
```

### 12.2 Simulation API (`backend/app/api/simulation.py`)

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import select

from ..storage.database import get_db_session
from ..memory.models import Memory, MemoryStatus
from ..simulation.engine import MemorySandbox

router = APIRouter()

# In-memory sandbox storage (resets on server restart)
_sandboxes: dict = {}

class CreateSandboxRequest(BaseModel):
    agent_id: Optional[str] = None

class InjectMemoryRequest(BaseModel):
    simulation_id: str
    memory: dict

class ModifyMemoryRequest(BaseModel):
    simulation_id: str
    memory_id: str
    new_content: str

@router.post("/simulation/create")
async def create_sandbox(request: CreateSandboxRequest, db_session=Depends(get_db_session)):
    stmt = select(Memory).where(Memory.status == MemoryStatus.ACTIVE)
    if request.agent_id:
        stmt = stmt.where(Memory.agent_id == request.agent_id)
    result = await db_session.execute(stmt)
    memories = result.scalars().all()

    mem_dicts = [
        {"id": m.id, "type": m.type.value, "content": m.content,
         "confidence": m.confidence, "importance": m.importance,
         "created_at": m.created_at.isoformat() if m.created_at else None}
        for m in memories
    ]

    sandbox = MemorySandbox(mem_dicts)
    _sandboxes[sandbox.simulation_id] = sandbox
    return {"simulation_id": sandbox.simulation_id, "state": sandbox.get_state()}

@router.post("/simulation/inject")
async def inject_memory(request: InjectMemoryRequest):
    sandbox = _sandboxes.get(request.simulation_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="Simulation not found")
    injected = sandbox.inject_memory(request.memory)
    return {"injected": injected, "state": sandbox.get_state()}

@router.post("/simulation/modify")
async def modify_memory(request: ModifyMemoryRequest):
    sandbox = _sandboxes.get(request.simulation_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="Simulation not found")
    modified = sandbox.modify_memory(request.memory_id, request.new_content)
    return {"modified": modified, "state": sandbox.get_state()}

@router.get("/simulation/{simulation_id}/query")
async def query_sandbox(simulation_id: str, q: str):
    sandbox = _sandboxes.get(simulation_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="Simulation not found")
    results = sandbox.query_simulation(q)
    return {"query": q, "results": results, "state": sandbox.get_state()}

@router.get("/simulation/{simulation_id}/state")
async def get_sandbox_state(simulation_id: str):
    sandbox = _sandboxes.get(simulation_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sandbox.get_state()
```

---

## 13. MODULE 9: ADVANCED MEMORY COMPRESSION

### 13.1 Compression Engine (`backend/app/compression/engine.py`)

```python
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from ..memory.models import Memory, MemoryStatus, MemoryType

class MemoryCompressionEngine:
    """Summarize old memories, archive low-importance, semantic deduplication."""

    def __init__(self):
        self.archive_age_days = 90
        self.archive_importance_threshold = 0.3
        self.min_confidence_for_summary = 0.6

    async def find_compressible_memories(self, db_session: AsyncSession,
                                          agent_id: Optional[str] = None) -> List[Memory]:
        """Find memories that can be compressed or archived."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.archive_age_days)
        stmt = select(Memory).where(
            Memory.status == MemoryStatus.ACTIVE,
            Memory.created_at < cutoff,
            Memory.importance < self.archive_importance_threshold
        )
        if agent_id:
            stmt = stmt.where(Memory.agent_id == agent_id)
        result = await db_session.execute(stmt)
        return result.scalars().all()

    async def summarize_memory_cluster(self, db_session: AsyncSession,
                                        memory_ids: List[str]) -> Optional[Memory]:
        """Create a summary memory from a cluster of related memories."""
        stmt = select(Memory).where(Memory.id.in_(memory_ids))
        result = await db_session.execute(stmt)
        memories = result.scalars().all()
        if len(memories) < 2:
            return None

        # Simple extraction-based summary
        all_content = " ".join([m.content for m in memories])
        words = all_content.lower().split()
        word_freq = {}
        for w in words:
            if len(w) > 3:
                word_freq[w] = word_freq.get(w, 0) + 1
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        summary_text = f"Summary of {len(memories)} memories: " + ", ".join([w for w, _ in top_words])

        summary = Memory(
            id=str(uuid.uuid4()),
            root_id=str(uuid.uuid4()),
            version=1,
            type=MemoryType.SEMANTIC,
            content=summary_text,
            normalized_content=summary_text.lower(),
            agent_id=memories[0].agent_id,
            source_id="compression_engine",
            confidence=min(0.8, sum(m.confidence for m in memories) / len(memories)),
            importance=max(m.importance for m in memories),
            status=MemoryStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            observed_at=datetime.now(timezone.utc),
            valid_from=datetime.now(timezone.utc),
            metadata={
                "summarized_memory_ids": [m.id for m in memories],
                "summarized_count": len(memories),
                "compression_type": "cluster_summary",
                "original_date_range": {
                    "oldest": min(m.created_at.isoformat() for m in memories if m.created_at),
                    "newest": max(m.created_at.isoformat() for m in memories if m.created_at)
                }
            }
        )
        db_session.add(summary)

        # Archive original memories
        for mem in memories:
            mem.status = MemoryStatus.ARCHIVED
            if mem.metadata is None:
                mem.metadata = {}
            mem.metadata["archived_reason"] = "compressed_into_summary"
            mem.metadata["summary_memory_id"] = summary.id

        await db_session.commit()
        return summary

    async def deduplicate_semantic(self, db_session: AsyncSession,
                                    agent_id: Optional[str] = None,
                                    similarity_threshold: float = 0.95) -> Dict[str, Any]:
        """Find and merge near-duplicate memories."""
        from ..embeddings.models import get_embedding_model
        from ..embeddings.vector_store import get_vector_store

        embedding_model = get_embedding_model()
        vector_store = get_vector_store()

        stmt = select(Memory).where(Memory.status == MemoryStatus.ACTIVE)
        if agent_id:
            stmt = stmt.where(Memory.agent_id == agent_id)
        result = await db_session.execute(stmt)
        memories = result.scalars().all()

        duplicates_found = []
        processed = set()

        for i, mem_a in enumerate(memories):
            if mem_a.id in processed:
                continue
            emb_a = embedding_model.embed(mem_a.content)

            for mem_b in memories[i + 1:]:
                if mem_b.id in processed:
                    continue
                emb_b = embedding_model.embed(mem_b.content)
                similarity = self._cosine_similarity(emb_a, emb_b)

                if similarity >= similarity_threshold:
                    # Mark B as duplicate of A
                    mem_b.status = MemoryStatus.ARCHIVED
                    mem_b.metadata = {**(mem_b.metadata or {}),
                                      "duplicate_of": mem_a.id, "similarity": round(similarity, 4)}
                    mem_a.confidence = min(0.99, mem_a.confidence + 0.02)
                    processed.add(mem_b.id)
                    duplicates_found.append({
                        "kept": mem_a.id,
                        "removed": mem_b.id,
                        "similarity": round(similarity, 4)
                    })

        await db_session.commit()
        return {"duplicates_found": len(duplicates_found), "details": duplicates_found}

    def _cosine_similarity(self, a, b):
        import numpy as np
        a_arr, b_arr = np.array(a), np.array(b)
        dot = np.dot(a_arr, b_arr)
        na, nb = np.linalg.norm(a_arr), np.linalg.norm(b_arr)
        return 0.0 if na == 0 or nb == 0 else float(dot / (na * nb))
```

### 13.2 Compression API (`backend/app/api/compression.py`)

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from ..storage.database import get_db_session
from ..compression.engine import MemoryCompressionEngine

router = APIRouter()

class CompressRequest(BaseModel):
    agent_id: Optional[str] = None
    action: str = "archive_old"  # archive_old, summarize_cluster, deduplicate
    memory_ids: Optional[list] = None

@router.post("/compression/run")
async def run_compression(request: CompressRequest, db_session=Depends(get_db_session)):
    engine = MemoryCompressionEngine()

    if request.action == "archive_old":
        memories = await engine.find_compressible_memories(db_session, request.agent_id)
        for mem in memories:
            mem.status = MemoryStatus.ARCHIVED
            if mem.metadata is None:
                mem.metadata = {}
            mem.metadata["archived_reason"] = "old_and_low_importance"
        await db_session.commit()
        return {"action": "archive_old", "archived_count": len(memories)}

    elif request.action == "summarize_cluster":
        if not request.memory_ids or len(request.memory_ids) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 memory IDs for summarization")
        summary = await engine.summarize_memory_cluster(db_session, request.memory_ids)
        return {"action": "summarize_cluster", "summary_id": summary.id if summary else None}

    elif request.action == "deduplicate":
        result = await engine.deduplicate_semantic(db_session, request.agent_id)
        return {"action": "deduplicate", **result}

    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")
```

---

## 14. UPDATED MAIN.PY

Add all V3 routers:

```python
from .api import (
    memory, search, context, conflicts, graph, stats, evolution,
    multimodal, ocr, replay, checkpoints, world_model, predictions,
    strategy, causal_advanced, sharing, sync, simulation, compression
)

# V1 + V1.5 + V2 routers
app.include_router(memory.router, prefix="/v1/memory", tags=["Memory"])
app.include_router(search.router, prefix="/v1/memory", tags=["Search"])
app.include_router(context.router, prefix="/v1/memory", tags=["Context"])
app.include_router(conflicts.router, prefix="/v1", tags=["Conflicts"])
app.include_router(graph.router, prefix="/v1", tags=["Graph"])
app.include_router(stats.router, prefix="/v1", tags=["Stats"])
app.include_router(evolution.router, prefix="/v1", tags=["Evolution"])
app.include_router(multimodal.router, prefix="/v1", tags=["Multimodal"])
app.include_router(ocr.router, prefix="/v1", tags=["OCR"])
app.include_router(replay.router, prefix="/v1", tags=["Replay"])

# V3 routers
app.include_router(checkpoints.router, prefix="/v1", tags=["Checkpoints"])
app.include_router(world_model.router, prefix="/v1", tags=["World Model"])
app.include_router(predictions.router, prefix="/v1", tags=["Predictions"])
app.include_router(strategy.router, prefix="/v1", tags=["Strategy"])
app.include_router(causal_advanced.router, prefix="/v1", tags=["Causal"])
app.include_router(sharing.router, prefix="/v1", tags=["Sharing"])
app.include_router(sync.router, prefix="/v1", tags=["Sync"])
app.include_router(simulation.router, prefix="/v1", tags=["Simulation"])
app.include_router(compression.router, prefix="/v1", tags=["Compression"])
```

---

## 15. TESTING REQUIREMENTS

| Module | Tests |
|--------|-------|
| Cryptographic Checkpoints | Create checkpoint. Verify integrity. Signature validation. |
| Merkle Tree | Build tree. Generate proof. Verify proof. |
| World Model | Build from memories. Query entity. Find path. Central entities. |
| Predictive Memory | Predict next memory. Trend analysis. |
| Strategy Learning | Analyze decisions. Create strategy. Success rate calculation. |
| Advanced Causal | Multi-hop chain. Counterfactual query. |
| Cross-Agent Sharing | Export bundle. Import bundle. Permission validation. |
| Multi-Device Sync | Generate payload. Apply payload. Conflict resolution. |
| Simulation Sandbox | Create sandbox. Inject memory. Query. Modify. |
| Compression | Archive old. Summarize cluster. Deduplicate. |

---

## 16. CODE QUALITY STANDARDS

Same as V1 + V1.5 + V2:
1. Type hints everywhere.
2. No `raise NotImplementedError`.
3. No `pass` in function bodies.
4. Async consistency.
5. Proper error handling.
6. No print statements — use logging.
7. Pydantic v2.
8. SQLAlchemy 2.0 style.
9. UTC timestamps only.
10. Consistent naming.

---

## 17. FINAL CHECKLIST

- [ ] All V1 + V1.5 + V2 tests still pass
- [ ] New V3 tests pass (80%+ coverage)
- [ ] Checkpoints create valid Merkle roots
- [ ] Checkpoint verification works correctly
- [ ] World model builds from semantic memories
- [ ] Predictions return plausible next states
- [ ] Strategies learned from decision outcomes
- [ ] Causal chains found through multiple hops
- [ ] Counterfactual queries show downstream effects
- [ ] Cross-agent bundles export/import correctly
- [ ] Multi-device sync handles conflicts
- [ ] Simulation sandbox isolates from real memory
- [ ] Compression archives old memories
- [ ] Deduplication finds near-duplicates
- [ ] No `NotImplementedError` anywhere
- [ ] No `datetime.utcnow()` anywhere

---

**END OF V3 PROMPT.** Build ONLY what is specified above.
