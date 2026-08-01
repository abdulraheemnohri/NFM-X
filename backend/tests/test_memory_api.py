import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status

from backend.app.main import app
from backend.app.memory.models import MemoryType, MemoryStatus
from backend.app.storage.database import get_db_session

@pytest.mark.asyncio
async def test_create_memory(db_session):
    # Override dependency to use our fixture's in-memory session
    app.dependency_overrides[get_db_session] = lambda: db_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "type": "semantic",
            "content": "Paris is the capital of France.",
            "confidence": 0.9,
            "importance": 0.8,
            "metadata": {"tags": ["europe", "geography"]}
        }
        response = await ac.post("/v1/memory/", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["type"] == "semantic"
        assert data["content"] == "Paris is the capital of France."
        assert data["confidence"] == 0.9
        assert data["importance"] == 0.8
        assert data["metadata"] == {"tags": ["europe", "geography"]}
        assert "id" in data
        assert data["version"] == 1

        # Retrieve memory
        memory_id = data["id"]
        get_response = await ac.get(f"/v1/memory/{memory_id}")
        assert get_response.status_code == status.HTTP_200_OK
        get_data = get_response.json()
        assert get_data["id"] == memory_id
        assert get_data["content"] == "Paris is the capital of France."

        # Check history
        history_response = await ac.get(f"/v1/memory/{memory_id}/history")
        assert history_response.status_code == status.HTTP_200_OK
        hist_data = history_response.json()
        assert hist_data["memory_id"] == memory_id
        assert len(hist_data["versions"]) == 1
        assert hist_data["versions"][0]["version"] == 1
        assert hist_data["versions"][0]["content"] == "Paris is the capital of France."

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_validation_errors(db_session):
    app.dependency_overrides[get_db_session] = lambda: db_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Invalid type
        payload = {
            "type": "invalid_type",
            "content": "Hello world"
        }
        response = await ac.post("/v1/memory/", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Empty content
        payload = {
            "type": "episodic",
            "content": ""
        }
        response = await ac.post("/v1/memory/", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_list_memories(db_session):
    app.dependency_overrides[get_db_session] = lambda: db_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create a couple of memories
        await ac.post("/v1/memory/", json={"type": "semantic", "content": "Fact 1", "agent_id": "agent-1"})
        await ac.post("/v1/memory/", json={"type": "episodic", "content": "Event 1", "agent_id": "agent-1"})
        await ac.post("/v1/memory/", json={"type": "preference", "content": "Pref 1", "agent_id": "agent-2"})

        # List all
        response = await ac.get("/v1/memory/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 3
        assert len(data["memories"]) == 3

        # Filter by agent
        response = await ac.get("/v1/memory/?agent_id=agent-1")
        data = response.json()
        assert data["total"] == 2

        # Filter by type
        response = await ac.get("/v1/memory/?memory_type=preference")
        data = response.json()
        assert data["total"] == 1
        assert data["memories"][0]["content"] == "Pref 1"

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_learn_endpoint(db_session):
    app.dependency_overrides[get_db_session] = lambda: db_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "agent_id": "agent-abc",
            "user_input": "First meeting on project architecture.",
            "ai_output": "Let's use a microservices approach with FastAPI.",
            "metadata": {"project": "NFM-X"}
        }
        response = await ac.post("/v1/memory/learn", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "memory_ids" in data
        assert len(data["memory_ids"]) == 2

        # Verify memories were created in the database
        list_resp = await ac.get("/v1/memory/")
        list_data = list_resp.json()
        assert list_data["total"] == 2

    app.dependency_overrides.clear()
