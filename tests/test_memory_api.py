"""
NFM-X Memory API Tests

Tests for memory API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.main import app
from backend.app.memory.models import Memory, MemoryStatus, MemoryType
from backend.app.storage.database import get_db


@pytest.mark.asyncio
async def test_create_memory(async_test_client: httpx.AsyncClient, test_memory_data: dict):
    response = await async_test_client.post("/api/memories", json=test_memory_data)
    
    assert response.status_code == 201
    data = response.json()
    
    assert "id" in data
    assert data["content"] == test_memory_data["content"]
    assert data["title"] == test_memory_data["title"]
    assert data["tags"] == test_memory_data["tags"]
    assert data["status"] == MemoryStatus.ACTIVE
    assert data["version"] == 1
    assert "createdAt" in data
    assert "updatedAt" in data


@pytest.mark.asyncio
async def test_get_memory(async_test_client: httpx.AsyncClient, test_memory_data: dict):
    create_response = await async_test_client.post("/api/memories", json=test_memory_data)
    memory_id = create_response.json()["id"]
    
    response = await async_test_client.get(f"/api/memories/{memory_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == memory_id
    assert data["content"] == test_memory_data["content"]


@pytest.mark.asyncio
async def test_list_memories(async_test_client: httpx.AsyncClient, test_memory_data: dict):
    for i in range(3):
        await async_test_client.post("/api/memories", json={
            **test_memory_data,
            "content": f"Test content {i}",
            "title": f"Test Title {i}",
        })
    
    response = await async_test_client.get("/api/memories")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 3


@pytest.mark.asyncio
async def test_update_memory(async_test_client: httpx.AsyncClient, test_memory_data: dict):
    create_response = await async_test_client.post("/api/memories", json=test_memory_data)
    memory_id = create_response.json()["id"]
    
    update_data = {
        "content": "Updated content",
        "title": "Updated Title",
        "tags": ["updated", "test"],
    }
    response = await async_test_client.put(f"/api/memories/{memory_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == memory_id
    assert data["content"] == update_data["content"]
    assert data["title"] == update_data["title"]
    assert data["tags"] == update_data["tags"]
    assert data["version"] == 2


@pytest.mark.asyncio
async def test_delete_memory(async_test_client: httpx.AsyncClient, test_memory_data: dict):
    create_response = await async_test_client.post("/api/memories", json=test_memory_data)
    memory_id = create_response.json()["id"]
    
    response = await async_test_client.delete(f"/api/memories/{memory_id}")
    
    assert response.status_code == 200
    
    get_response = await async_test_client.get(f"/api/memories/{memory_id}")
    data = get_response.json()
    
    assert data["status"] == MemoryStatus.DELETED


@pytest.mark.asyncio
async def test_search_memories(async_test_client: httpx.AsyncClient, test_memory_data: dict, test_search_query: str):
    await async_test_client.post("/api/memories", json={
        **test_memory_data,
        "content": "This is a test memory for searching",
    })
    
    response = await async_test_client.get(
        "/api/search",
        params={"q": test_search_query, "limit": 10}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_get_stats(async_test_client: httpx.AsyncClient, test_memory_data: dict):
    for i in range(3):
        await async_test_client.post("/api/memories", json={
            **test_memory_data,
            "content": f"Test content {i}",
        })
    
    response = await async_test_client.get("/api/stats")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "totalMemories" in data
    assert "activeMemories" in data
    assert data["totalMemories"] >= 3
    assert data["activeMemories"] >= 3


@pytest.mark.asyncio
async def test_health_check(async_test_client: httpx.AsyncClient):
    response = await async_test_client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_version_endpoint(async_test_client: httpx.AsyncClient):
    response = await async_test_client.get("/version")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "version" in data
    assert "app_name" in data