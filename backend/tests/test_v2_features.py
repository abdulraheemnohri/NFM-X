import pytest
import os
import shutil
from pathlib import Path
from datetime import datetime, timezone, timedelta
from fastapi import status
from httpx import AsyncClient, ASGITransport
from PIL import Image

from backend.app.main import app
from backend.app.storage.database import get_db_session
from backend.app.memory.models import (
    Memory, MemoryVersion, MemoryEvent, MemoryConflict,
    MemoryRelationship, MemoryType, MemoryStatus, ChangeType,
    MemoryPattern, MemoryProcedure, MemorySkill
)
from backend.app.memory.evolution import EvolutionEngine, MemoryEvolution
from backend.app.memory.patterns import PatternDiscoveryEngine
from backend.app.memory.skills import SkillLearningEngine
from backend.app.memory.causal import CausalExtractionEngine
from backend.app.ocr.engine import OCREngine

@pytest.mark.asyncio
async def test_evolution_engine_rules(db_session):
    app.dependency_overrides[get_db_session] = lambda: db_session
    engine = EvolutionEngine()

    # Create original memory
    original = Memory(
        id="orig-123", root_id="orig-123", version=1,
        type=MemoryType.PREFERENCE, content="User prefers dark mode.",
        agent_id="agent-999", status=MemoryStatus.ACTIVE,
        confidence=0.8, importance=0.7, created_at=datetime.now(timezone.utc)
    )
    db_session.add(original)
    await db_session.commit()

    # 1. DUPLICATE test
    duplicate = Memory(
        id="dup-123", root_id="dup-123", version=1,
        type=MemoryType.PREFERENCE, content="user prefers dark mode",
        agent_id="agent-999", status=MemoryStatus.ACTIVE,
        confidence=0.8, importance=0.7, created_at=datetime.now(timezone.utc)
    )
    res_dup = await engine.evolve(db_session, duplicate)
    assert res_dup["action"] == "DUPLICATE"
    assert duplicate.status == MemoryStatus.DELETED

    # 2. CONTRADICT test
    contradictory = Memory(
        id="cont-123", root_id="cont-123", version=1,
        type=MemoryType.PREFERENCE, content="User prefers light mode.",
        agent_id="agent-999", status=MemoryStatus.ACTIVE,
        confidence=0.8, importance=0.7, created_at=datetime.now(timezone.utc)
    )
    res_cont = await engine.evolve(db_session, contradictory)
    assert res_cont["action"] == "CONTRADICT"

    # 3. REINFORCE test
    reinforce = Memory(
        id="reinf-123", root_id="reinf-123", version=1,
        type=MemoryType.PREFERENCE, content="User indeed prefers dark mode.",
        agent_id="agent-999", status=MemoryStatus.ACTIVE,
        confidence=0.8, importance=0.7, created_at=datetime.now(timezone.utc)
    )
    res_reinf = await engine.evolve(db_session, reinforce)
    assert res_reinf["action"] == "REINFORCE"

    # 4. REFINE test
    refine = Memory(
        id="ref-123", root_id="ref-123", version=1,
        type=MemoryType.PREFERENCE, content="User prefers dark mode, specifically midnight theme.",
        agent_id="agent-999", status=MemoryStatus.ACTIVE,
        confidence=0.8, importance=0.7, created_at=datetime.now(timezone.utc)
    )
    res_ref = await engine.evolve(db_session, refine)
    assert res_ref["action"] == "REFINE"

    # 5. EXPAND test
    expand = Memory(
        id="exp-123", root_id="exp-123", version=1,
        type=MemoryType.PREFERENCE, content="User prefers dark mode. Also they use terminal a lot.",
        agent_id="agent-999", status=MemoryStatus.ACTIVE,
        confidence=0.8, importance=0.7, created_at=datetime.now(timezone.utc)
    )
    res_exp = await engine.evolve(db_session, expand)
    assert res_exp["action"] == "EXPAND"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_pattern_discovery(db_session):
    engine = PatternDiscoveryEngine()

    # Insert 3 similar memories (min_cluster_size is 3)
    memories = [
        Memory(
            id=f"pat-m-{i}", root_id=f"pat-m-{i}", version=1,
            type=MemoryType.SEMANTIC, content="The python language is extremely versatile and easy to learn.",
            agent_id="agent-p", status=MemoryStatus.ACTIVE,
            confidence=0.9, importance=0.8, created_at=datetime.now(timezone.utc)
        ) for i in range(3)
    ]
    for m in memories:
        db_session.add(m)
    await db_session.commit()

    patterns = await engine.discover_patterns(db_session, agent_id="agent-p")
    assert len(patterns) == 1
    assert "Pattern" in patterns[0].name
    assert patterns[0].pattern_data["memory_count"] == 3


@pytest.mark.asyncio
async def test_skill_learning(db_session):
    engine = SkillLearningEngine()

    # Insert 3 successful executions (procedure_name "deploy_app")
    procs = [
        MemoryProcedure(
            id=f"proc-{i}", name="deploy_app", description="Deploying application step",
            execution_count=1, success_count=1, failure_count=0, success_rate=1.0,
            last_executed=datetime.now(timezone.utc)
        ) for i in range(3)
    ]
    for p in procs:
        db_session.add(p)
    await db_session.commit()

    skill = await engine.learn_skill_from_procedure(db_session, "deploy_app")
    assert skill is not None
    assert skill.name == "deploy_app"
    assert skill.success_rate == 1.0


@pytest.mark.asyncio
async def test_causal_extraction(db_session):
    engine = CausalExtractionEngine()
    text = "Deploying broken code caused the database crash."
    extracted = engine.extract_causal_relationships(text)
    assert len(extracted) == 1
    assert extracted[0]["cause"].lower() == "deploying broken code"
    assert extracted[0]["effect"].lower() == "the database crash"

    mem = await engine.store_causal_memory(
        db_session, "source-123", extracted[0]["cause"], extracted[0]["effect"], extracted[0]["relationship_type"]
    )
    assert mem.type == MemoryType.CAUSAL
    assert "Cause:" in mem.content


@pytest.mark.asyncio
async def test_multimodal_api(db_session):
    app.dependency_overrides[get_db_session] = lambda: db_session

    # Create temporary dummy file for testing
    dummy_path = "./storage/temp/test_image.png"
    Path("./storage/temp").mkdir(parents=True, exist_ok=True)
    img = Image.new('RGB', (100, 100), color = 'red')
    img.save(dummy_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        with open(dummy_path, "rb") as f:
            resp = await ac.post("/v1/upload", files={"file": ("test_image.png", f, "image/png")}, data={"agent_id": "agent-img"})
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["type"] == "image"
        assert "document_id" in data

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_ocr_subsystem(db_session):
    engine = OCREngine()
    engine._reader = "mock" # Force mock fallback for rapid testing
    dummy_path = "./storage/temp/test_ocr.png"
    Path("./storage/temp").mkdir(parents=True, exist_ok=True)
    img = Image.new('RGB', (100, 100), color = 'blue')
    img.save(dummy_path)

    res = await engine.process_image(dummy_path)
    assert "Mock OCR Text" in res["text"]
    assert res["confidence"] == 0.95


@pytest.mark.asyncio
async def test_replay_and_debugger_apis(db_session):
    app.dependency_overrides[get_db_session] = lambda: db_session

    # Create a memory
    memory = Memory(
        id="debug-mem-123", root_id="debug-mem-123", version=1,
        type=MemoryType.SEMANTIC, content="Causal analysis fact",
        confidence=0.85, importance=0.75, status=MemoryStatus.ACTIVE,
        created_at=datetime.now(timezone.utc)
    )
    # Add a version
    version = MemoryVersion(
        id="debug-ver-123", memory_id="debug-mem-123", version=1,
        content="Causal analysis fact", confidence=0.85, importance=0.75,
        status=MemoryStatus.ACTIVE, change_type=ChangeType.CREATE,
        change_reason="Initial"
    )
    # Add an event
    event = MemoryEvent(
        id="debug-event-123", memory_id="debug-mem-123", event_type="create",
        timestamp=datetime.now(timezone.utc)
    )
    db_session.add(memory)
    db_session.add(version)
    db_session.add(event)
    await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Replay API
        replay_resp = await ac.get("/v1/memory/debug-mem-123/replay")
        assert replay_resp.status_code == status.HTTP_200_OK
        replay_data = replay_resp.json()
        assert replay_data["total_versions"] == 1
        assert replay_data["total_events"] == 1

        # Debugger API
        debug_resp = await ac.get("/v1/memory/debug-mem-123/debug")
        assert debug_resp.status_code == status.HTTP_200_OK
        debug_data = debug_resp.json()
        assert debug_data["version"] == 1
        assert debug_data["event_summary"] == {"create": 1}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_background_consolidation_jobs(db_session):
    from backend.app.workers.jobs import run_consolidation_job, _recalculate_confidences, _detect_stale_memories

    # Insert a stale working memory (>30 days old)
    stale_mem = Memory(
        id="stale-work-123", root_id="stale-work-123", version=1,
        type=MemoryType.WORKING, content="Stale daily chat",
        agent_id="agent-work", status=MemoryStatus.ACTIVE,
        created_at=datetime.now(timezone.utc) - timedelta(days=35)
    )
    # Insert an old memory with high confidence to test confidence decay (>90 days old)
    decay_mem = Memory(
        id="decay-mem-123", root_id="decay-mem-123", version=1,
        type=MemoryType.SEMANTIC, content="Old python fact",
        agent_id="agent-work", status=MemoryStatus.ACTIVE,
        confidence=0.9, importance=0.8,
        created_at=datetime.now(timezone.utc) - timedelta(days=95)
    )
    db_session.add(stale_mem)
    db_session.add(decay_mem)
    await db_session.commit()

    # Recalculate confidences
    await _recalculate_confidences(db_session)
    assert decay_mem.confidence < 0.9

    # Archive stale working memory
    await _detect_stale_memories(db_session)
    assert stale_mem.status == MemoryStatus.ARCHIVED
