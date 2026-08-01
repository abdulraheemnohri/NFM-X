import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status

from backend.app.main import app
from backend.app.storage.database import get_db_session
from backend.app.embeddings.vector_store import get_vector_store

@pytest.mark.asyncio
async def test_hybrid_search(db_session):
    app.dependency_overrides[get_db_session] = lambda: db_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create memories
        resp1 = await ac.post("/v1/memory/", json={
            "type": "semantic",
            "content": "Python is a popular programming language.",
            "confidence": 0.9,
            "importance": 0.8
        })
        mem1 = resp1.json()

        resp2 = await ac.post("/v1/memory/", json={
            "type": "semantic",
            "content": "Deep learning uses neural networks to learn representations.",
            "confidence": 0.8,
            "importance": 0.7
        })
        mem2 = resp2.json()

        # Add to mock vector store manually for retrieval testing
        vs = get_vector_store()
        # In a real run, the embedder and vector store additions would happen in capture.
        # Let's populate the FAISS store to mimic that.
        from backend.app.embeddings.models import get_embedding_model
        model = get_embedding_model()
        vs.add(mem1["id"], mem1["content"], model.embed(mem1["content"]))
        vs.add(mem2["id"], mem2["content"], model.embed(mem2["content"]))

        # Keyword matching query
        search_resp = await ac.post("/v1/memory/search", json={
            "query": "programming language",
            "limit": 5
        })
        assert search_resp.status_code == status.HTTP_200_OK
        search_data = search_resp.json()
        assert len(search_data["results"]) > 0
        # The Python memory should have high score due to keyword match + semantic similarity
        assert search_data["results"][0]["id"] == mem1["id"]

        # Semantic matching query
        search_resp = await ac.post("/v1/memory/search", json={
            "query": "artificial intelligence representation learning",
            "limit": 5
        })
        assert search_resp.status_code == status.HTTP_200_OK
        search_data = search_resp.json()
        assert len(search_data["results"]) > 0
        # Deep learning memory should rank first semantically
        assert search_data["results"][0]["id"] == mem2["id"]

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_context_builder(db_session):
    app.dependency_overrides[get_db_session] = lambda: db_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create and add semantic/episodic memories
        resp1 = await ac.post("/v1/memory/", json={
            "type": "semantic",
            "content": "FastAPI is extremely fast and easy to write.",
            "agent_id": "agent-xyz"
        })
        mem1 = resp1.json()

        # Populate FAISS
        from backend.app.embeddings.models import get_embedding_model
        model = get_embedding_model()
        vs = get_vector_store()
        vs.add(mem1["id"], mem1["content"], model.embed(mem1["content"]))

        context_resp = await ac.post("/v1/memory/context", json={
            "agent_id": "agent-xyz",
            "query": "performance of FastAPI",
            "max_memories": 5
        })
        assert context_resp.status_code == status.HTTP_200_OK
        ctx_data = context_resp.json()
        assert ctx_data["agent_id"] == "agent-xyz"
        assert len(ctx_data["memories"]) > 0
        assert ctx_data["memories"][0]["id"] == mem1["id"]
        assert ctx_data["total_tokens_estimate"] > 0

    app.dependency_overrides.clear()
