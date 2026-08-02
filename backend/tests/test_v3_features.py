import pytest
from datetime import datetime, timezone, timedelta
from fastapi import status
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from backend.app.storage.database import get_db_session
from backend.app.memory.models import (
    Memory, MemoryStatus, MemoryType, MemoryCheckpoint, MemorySkill
)
from backend.app.crypto.integrity import IntegrityChain
from backend.app.crypto.merkle import MerkleTree
from backend.app.crypto.signatures import MemorySigner
from backend.app.world_model.engine import WorldModel
from backend.app.predictions.engine import PredictiveMemoryEngine
from backend.app.strategy.engine import StrategyLearningEngine
from backend.app.causal.advanced import AdvancedCausalEngine
from backend.app.sharing.protocol import MemoryBundle, SharePermission
from backend.app.sync.engine import SyncEngine
from backend.app.simulation.engine import MemorySandbox
from backend.app.compression.engine import MemoryCompressionEngine

@pytest.mark.asyncio
async def test_cryptographic_checkpoints_and_merkle_tree(db_session):
    app.dependency_overrides[get_db_session] = lambda: db_session

    # Create dummy memories
    mem1 = Memory(
        id="crypto-mem-1", root_id="crypto-mem-1", version=1,
        type=MemoryType.SEMANTIC, content="Fact A", confidence=0.8,
        status=MemoryStatus.ACTIVE, created_at=datetime.now(timezone.utc)
    )
    db_session.add(mem1)
    await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create Checkpoint
        cp_resp = await ac.post("/v1/checkpoints/create")
        assert cp_resp.status_code == status.HTTP_200_OK
        cp_data = cp_resp.json()
        assert "merkle_root" in cp_data
        assert cp_data["memory_count"] == 1

        # List Checkpoints
        list_resp = await ac.get("/v1/checkpoints")
        assert list_resp.status_code == status.HTTP_200_OK
        list_data = list_resp.json()
        assert len(list_data) >= 1

        # Verify Checkpoint
        cp_id = cp_data["id"]
        verify_resp = await ac.get(f"/v1/checkpoints/{cp_id}/verify")
        assert verify_resp.status_code == status.HTTP_200_OK
        verify_data = verify_resp.json()
        assert verify_data["roots_match"] is True
        assert verify_data["signature_valid"] is True

    # Standalone Merkle Tree tests
    leaves = ["hash1", "hash2", "hash3", "hash4"]
    tree = MerkleTree(leaves)
    assert tree.root is not None
    proof = tree.get_proof(1)
    assert len(proof) > 0
    assert tree.verify_proof("hash2", 1, proof) is True

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_world_model_queries(db_session):
    app.dependency_overrides[get_db_session] = lambda: db_session

    # Insert technological semantic memories
    mem1 = Memory(
        id="wm-m-1", root_id="wm-m-1", version=1,
        type=MemoryType.SEMANTIC, content="NFM-X is an AI long-term memory layer using python.",
        status=MemoryStatus.ACTIVE, created_at=datetime.now(timezone.utc)
    )
    mem2 = Memory(
        id="wm-m-2", root_id="wm-m-2", version=1,
        type=MemoryType.SEMANTIC, content="python is fully compatible with fastapi.",
        status=MemoryStatus.ACTIVE, created_at=datetime.now(timezone.utc)
    )
    db_session.add(mem1)
    db_session.add(mem2)
    await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Rebuild World Model
        rebuild_resp = await ac.post("/v1/world-model/rebuild")
        assert rebuild_resp.status_code == status.HTTP_200_OK

        # Query Entity
        entity_resp = await ac.get("/v1/world-model/entity/python")
        assert entity_resp.status_code == status.HTTP_200_OK
        entity_data = entity_resp.json()
        assert entity_data["entity"] == "python"
        assert entity_data["entity_type"] == "technology"

        # Query central entities
        central_resp = await ac.get("/v1/world-model/central")
        assert central_resp.status_code == status.HTTP_200_OK
        central_data = central_resp.json()
        assert len(central_data["entities"]) > 0

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_predictive_memory(db_session):
    app.dependency_overrides[get_db_session] = lambda: db_session

    # Insert sequence of memories
    now = datetime.now(timezone.utc)
    m1 = Memory(
        id="pred-1", root_id="pred-1", version=1,
        type=MemoryType.SEMANTIC, content="User started terminal.",
        status=MemoryStatus.ACTIVE, created_at=now - timedelta(seconds=10)
    )
    m2 = Memory(
        id="pred-2", root_id="pred-2", version=1,
        type=MemoryType.SEMANTIC, content="User ran python command.",
        status=MemoryStatus.ACTIVE, created_at=now - timedelta(seconds=5)
    )
    m3 = Memory(
        id="pred-3", root_id="pred-3", version=1,
        type=MemoryType.SEMANTIC, content="User started terminal.",
        status=MemoryStatus.ACTIVE, created_at=now - timedelta(seconds=4)
    )
    m4 = Memory(
        id="pred-4", root_id="pred-4", version=1,
        type=MemoryType.SEMANTIC, content="User ran python command.",
        status=MemoryStatus.ACTIVE, created_at=now - timedelta(seconds=2)
    )
    m5 = Memory(
        id="pred-5", root_id="pred-5", version=1,
        type=MemoryType.SEMANTIC, content="User closed python terminal.",
        status=MemoryStatus.ACTIVE, created_at=now - timedelta(seconds=1)
    )
    db_session.add(m1)
    db_session.add(m2)
    db_session.add(m3)
    db_session.add(m4)
    db_session.add(m5)
    await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        predict_resp = await ac.post("/v1/predictions/next", json={
            "context_query": "started terminal"
        })
        assert predict_resp.status_code == status.HTTP_200_OK
        p_data = predict_resp.json()
        assert len(p_data["predictions"]) > 0
        assert "python" in p_data["predictions"][0]["predicted_content"].lower()

        # Trend analysis API
        trend_resp = await ac.post("/v1/predictions/trend", json={
            "entity": "python"
        })
        assert trend_resp.status_code == status.HTTP_200_OK
        t_data = trend_resp.json()
        assert t_data["trend"] in ("stable", "increasing", "decreasing")

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_strategy_learning(db_session):
    app.dependency_overrides[get_db_session] = lambda: db_session

    now = datetime.now(timezone.utc)
    # Decision -> Success outcome sequence
    m1 = Memory(
        id="strat-dec", root_id="strat-dec", version=1,
        type=MemoryType.DECISION, content="Choose Postgres as DB",
        agent_id="agent-strat", status=MemoryStatus.ACTIVE, created_at=now - timedelta(seconds=60)
    )
    m2 = Memory(
        id="strat-succ-1", root_id="strat-succ-1", version=1,
        type=MemoryType.SUCCESS, content="Postgres DB performance is exceptional",
        agent_id="agent-strat", status=MemoryStatus.ACTIVE, created_at=now - timedelta(seconds=10)
    )
    db_session.add(m1)
    db_session.add(m2)
    await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        strategies_resp = await ac.get("/v1/strategies?agent_id=agent-strat")
        assert strategies_resp.status_code == status.HTTP_200_OK
        data = strategies_resp.json()
        assert "strategies" in data

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_advanced_causal_reasoning(db_session):
    app.dependency_overrides[get_db_session] = lambda: db_session

    # Create causal memories forming a chain: broken code -> DB crash -> outage
    m1 = Memory(
        id="causal-chain-1", root_id="causal-chain-1", version=1,
        type=MemoryType.CAUSAL, content="Cause: broken code. Effect: db crash. Relationship: caused",
        status=MemoryStatus.ACTIVE, metadata={"cause": "broken code", "effect": "db crash", "relationship_type": "caused"}
    )
    m2 = Memory(
        id="causal-chain-2", root_id="causal-chain-2", version=1,
        type=MemoryType.CAUSAL, content="Cause: db crash. Effect: system outage. Relationship: caused",
        status=MemoryStatus.ACTIVE, metadata={"cause": "db crash", "effect": "system outage", "relationship_type": "caused"}
    )
    db_session.add(m1)
    db_session.add(m2)
    await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Multi-hop causal chain
        chain_resp = await ac.post("/v1/causal/chain", json={
            "cause": "broken code",
            "effect": "system outage"
        })
        assert chain_resp.status_code == status.HTTP_200_OK
        c_data = chain_resp.json()
        assert c_data["found"] is True
        assert c_data["hops"] == 2

        # Counterfactual query
        cf_resp = await ac.post("/v1/causal/counterfactual", json={
            "remove_event": "broken code"
        })
        assert cf_resp.status_code == status.HTTP_200_OK
        cf_data = cf_resp.json()
        assert cf_data["removed_memory_count"] == 1

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_sharing_and_sync_and_sandbox(db_session):
    app.dependency_overrides[get_db_session] = lambda: db_session

    # Insert memory to share/sync
    mem = Memory(
        id="share-mem-1", root_id="share-mem-1", version=1,
        type=MemoryType.SEMANTIC, content="Shared knowledge",
        agent_id="agent-src", status=MemoryStatus.ACTIVE, created_at=datetime.now(timezone.utc)
    )
    db_session.add(mem)
    await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. CROSS-AGENT SHARING
        export_resp = await ac.post("/v1/sharing/export", json={
            "source_agent_id": "agent-src",
            "target_agent_id": "agent-tgt",
            "memory_ids": ["share-mem-1"],
            "permissions": "read"
        })
        assert export_resp.status_code == status.HTTP_200_OK
        export_data = export_resp.json()
        assert "bundle" in export_data

        import_resp = await ac.post("/v1/sharing/import", json={
            "bundle": export_data["bundle"],
            "target_agent_id": "agent-tgt"
        })
        assert import_resp.status_code == status.HTTP_200_OK
        import_data = import_resp.json()
        assert import_data["imported_count"] == 1

        # 2. MULTI-DEVICE SYNC
        pull_resp = await ac.post("/v1/sync/pull", json={
            "device_id": "device-abc"
        })
        assert pull_resp.status_code == status.HTTP_200_OK
        pull_data = pull_resp.json()
        assert pull_data["memory_count"] >= 1

        push_resp = await ac.post("/v1/sync/push", json={
            "device_id": "device-xyz",
            "payload": pull_data
        })
        assert push_resp.status_code == status.HTTP_200_OK
        push_data = push_resp.json()
        assert len(push_data["skipped"]) >= 1

        # 3. MEMORY SANDBOX SIMULATION
        sandbox_resp = await ac.post("/v1/simulation/create", json={
            "agent_id": "agent-src"
        })
        assert sandbox_resp.status_code == status.HTTP_200_OK
        sb_data = sandbox_resp.json()
        simulation_id = sb_data["simulation_id"]

        inject_resp = await ac.post("/v1/simulation/inject", json={
            "simulation_id": simulation_id,
            "memory": {"type": "semantic", "content": "Hypothetical memory fact"}
        })
        assert inject_resp.status_code == status.HTTP_200_OK

        query_resp = await ac.get(f"/v1/simulation/{simulation_id}/query?q=Hypothetical")
        assert query_resp.status_code == status.HTTP_200_OK
        q_data = query_resp.json()
        assert len(q_data["results"]) == 1

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_memory_compression_engine(db_session):
    app.dependency_overrides[get_db_session] = lambda: db_session

    # Insert old memories with low importance
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=100)
    m1 = Memory(
        id="comp-1", root_id="comp-1", version=1,
        type=MemoryType.SEMANTIC, content="Old useless detail 1",
        importance=0.1, confidence=0.8, status=MemoryStatus.ACTIVE, created_at=cutoff_date
    )
    m2 = Memory(
        id="comp-2", root_id="comp-2", version=1,
        type=MemoryType.SEMANTIC, content="Old useless detail 2",
        importance=0.1, confidence=0.8, status=MemoryStatus.ACTIVE, created_at=cutoff_date
    )
    db_session.add(m1)
    db_session.add(m2)
    await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Archive old compression action
        comp_resp = await ac.post("/v1/compression/run", json={
            "action": "archive_old"
        })
        assert comp_resp.status_code == status.HTTP_200_OK
        comp_data = comp_resp.json()
        assert comp_data["archived_count"] == 2

        # Cluster summarization action
        m3 = Memory(
            id="comp-3", root_id="comp-3", version=1,
            type=MemoryType.SEMANTIC, content="Deep learning neural network representations.",
            status=MemoryStatus.ACTIVE
        )
        m4 = Memory(
            id="comp-4", root_id="comp-4", version=1,
            type=MemoryType.SEMANTIC, content="Neural network architectures learn from representation parameters.",
            status=MemoryStatus.ACTIVE
        )
        db_session.add(m3)
        db_session.add(m4)
        await db_session.commit()

        sum_resp = await ac.post("/v1/compression/run", json={
            "action": "summarize_cluster",
            "memory_ids": ["comp-3", "comp-4"]
        })
        assert sum_resp.status_code == status.HTTP_200_OK
        sum_data = sum_resp.json()
        assert sum_data["summary_id"] is not None

    app.dependency_overrides.clear()
