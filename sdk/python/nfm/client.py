"""
NFM-X Python SDK Client
"""
from typing import Optional, Dict, Any, List
import asyncio
import httpx
from .models import Memory, MemoryVersion, MemoryCreateRequest, MemoryUpdateRequest, SearchRequest, SearchResponse, ContextRequest, ContextResponse, MemoryType, MemoryStatus, ChangeType

class NFMClient:
    def __init__(self, base_url="http://localhost:8000", api_version="v1", timeout=30.0):
        self.base_url = base_url.rstrip("/")
        self.api_version = api_version
        self.timeout = timeout
        self._client = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    def _build_url(self, path):
        return f"{self.base_url}/{self.api_version}{path}"

    async def _request(self, method, path, data=None, params=None, response_model=None):
        url = self._build_url(path)
        for attempt in range(3):
            try:
                response = await self._client.request(method, url, json=data, params=params, timeout=self.timeout)
                if response.status_code >= 400:
                    error = response.json() if response.text else {"error": "Unknown"}
                    if response.status_code == 404:
                        raise ValueError(f"Not found: {path}")
                    raise RuntimeError(f"API error: {response.status_code} - {error.get('error')}")
                if response.status_code == 204:
                    return None
                response_data = response.json() if response.text else {}
                return response_model(**response_data) if response_model else response_data
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                if attempt == 2:
                    raise ConnectionError(f"Connection failed: {e}")
                await asyncio.sleep(0.5)

    async def health_check(self):
        return await self._request("GET", "/health")

    async def create_memory(self, content, memory_type=None, source=None, author_id=None, confidence=None, importance=None, metadata=None, tags=None):
        req = MemoryCreateRequest(content=content, memory_type=memory_type, source=source, author_id=author_id, confidence=confidence, importance=importance, metadata=metadata, tags=tags)
        return await self._request("POST", "/memory/", data=req.dict(), response_model=Memory)

    async def get_memory(self, memory_id):
        return await self._request("GET", f"/memory/{memory_id}", response_model=Memory)

    async def list_memories(self, limit=50, offset=0, memory_type=None, status=None, author_id=None):
        params = {"limit": limit, "offset": offset}
        if memory_type:
            params["memory_type"] = memory_type.value
        if status:
            params["status"] = status.value
        if author_id:
            params["author_id"] = author_id
        from .models import MemoryListResponse
        return await self._request("GET", "/memory/", params=params, response_model=MemoryListResponse)

    async def update_memory(self, memory_id, content, change_type, change_reason, confidence=None, importance=None):
        req = MemoryUpdateRequest(content=content, change_type=change_type, change_reason=change_reason, confidence=confidence, importance=importance)
        return await self._request("PUT", f"/memory/{memory_id}", data=req.dict(), response_model=Memory)

    async def delete_memory(self, memory_id):
        await self._request("DELETE", f"/memory/{memory_id}")

    async def search(self, query, limit=10, memory_types=None, status=None):
        req = SearchRequest(query=query, limit=limit, memory_types=memory_types, status=status)
        return await self._request("POST", "/memory/search", data=req.dict(), response_model=SearchResponse)

    async def get_context(self, query, limit=10, max_tokens=None, format="text"):
        req = ContextRequest(query=query, limit=limit, max_tokens=max_tokens, format=format)
        return await self._request("POST", "/memory/context", data=req.dict(), response_model=ContextResponse)