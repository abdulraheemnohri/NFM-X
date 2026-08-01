import pytest
import respx
from httpx import Response
from sdk.python.nfm.client import NFMClient
from sdk.python.nfm.models import MemoryCreate, SearchQuery, ContextQuery

@respx.mock
def test_client_create_memory():
    client = NFMClient(base_url="http://localhost:8765")

    route = respx.post("http://localhost:8765/v1/memory/").mock(return_value=Response(201, json={
        "id": "mem-123",
        "root_id": "mem-123",
        "version": 1,
        "type": "semantic",
        "content": "Test semantic memory",
        "confidence": 0.8,
        "importance": 0.5,
        "status": "active",
        "created_at": "2026-08-01T00:00:00Z",
        "metadata": {}
    }))

    req = MemoryCreate(type="semantic", content="Test semantic memory")
    result = client.create_memory(req)

    assert route.called
    assert result["id"] == "mem-123"
    assert result["content"] == "Test semantic memory"
    client.close()

@respx.mock
def test_client_get_memory():
    client = NFMClient(base_url="http://localhost:8765")
    route = respx.get("http://localhost:8765/v1/memory/mem-123").mock(return_value=Response(200, json={
        "id": "mem-123",
        "root_id": "mem-123",
        "version": 1,
        "type": "semantic",
        "content": "Test semantic memory",
        "confidence": 0.8,
        "importance": 0.5,
        "status": "active",
        "created_at": "2026-08-01T00:00:00Z",
        "metadata": {}
    }))

    result = client.get_memory("mem-123")
    assert route.called
    assert result["id"] == "mem-123"
    client.close()

@respx.mock
def test_client_list_memories():
    client = NFMClient(base_url="http://localhost:8765")
    route = respx.get("http://localhost:8765/v1/memory/").mock(return_value=Response(200, json={
        "memories": [
            {"id": "mem-1", "root_id": "mem-1", "version": 1, "type": "semantic", "content": "Memory 1", "confidence": 0.8, "importance": 0.5, "status": "active", "created_at": "2026-08-01T00:00:00Z"}
        ],
        "total": 1,
        "limit": 50,
        "offset": 0
    }))

    result = client.list_memories(agent_id="agent-1", memory_type="semantic")
    assert route.called
    assert result["total"] == 1
    assert result["memories"][0]["content"] == "Memory 1"
    client.close()

@respx.mock
def test_client_search():
    client = NFMClient(base_url="http://localhost:8765")
    route = respx.post("http://localhost:8765/v1/memory/search").mock(return_value=Response(200, json={
        "query": "test",
        "results": [{"id": "mem-1", "type": "semantic", "content": "Match", "confidence": 0.9, "importance": 0.8, "score": 0.95}],
        "count": 1
    }))

    result = client.search(SearchQuery(query="test"))
    assert route.called
    assert result["count"] == 1
    assert result["results"][0]["content"] == "Match"
    client.close()

@respx.mock
def test_client_get_context():
    client = NFMClient(base_url="http://localhost:8765")
    route = respx.post("http://localhost:8765/v1/memory/context").mock(return_value=Response(200, json={
        "agent_id": "agent-1",
        "query": "test",
        "memories": [{"id": "mem-1", "type": "semantic", "content": "Match", "confidence": 0.9, "importance": 0.8, "score": 0.95}],
        "total_tokens_estimate": 10
    }))

    result = client.get_context(ContextQuery(agent_id="agent-1", query="test"))
    assert route.called
    assert result["total_tokens_estimate"] == 10
    client.close()

@respx.mock
def test_client_get_history():
    client = NFMClient(base_url="http://localhost:8765")
    route = respx.get("http://localhost:8765/v1/memory/mem-123/history").mock(return_value=Response(200, json={
        "memory_id": "mem-123",
        "versions": [{"version": 1, "content": "v1 content"}]
    }))

    result = client.get_history("mem-123")
    assert route.called
    assert len(result["versions"]) == 1
    client.close()

@respx.mock
def test_client_health():
    client = NFMClient(base_url="http://localhost:8765")
    route = respx.get("http://localhost:8765/health").mock(return_value=Response(200, json={"status": "healthy"}))

    result = client.health()
    assert route.called
    assert result["status"] == "healthy"
    client.close()
