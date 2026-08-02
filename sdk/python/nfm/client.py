"""
NFM-X Python SDK Client

Async client for interacting with NFM-X API.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union

import httpx

from .models import (
    Context,
    Conflict,
    GraphData,
    Memory,
    MemoryCreate,
    MemoryStats,
    MemoryUpdate,
    SearchResponse,
)


class NFMClient:
    """
    Async client for NFM-X API.
    
    Example usage:
        async with NFMClient() as client:
            memory = await client.create_memory(content="Hello World", title="Test")
            results = await client.search("hello")
            print(results)
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self) -> "NFMClient":
        await self._ensure_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def _ensure_client(self) -> httpx.AsyncClient:
        if not self._client or self._client.is_closed:
            headers = {"User-Agent": "NFM-X-Python-SDK/1.5.0"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=headers,
            )
        return self._client
    
    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        client = await self._ensure_client()
        response = await client.request(method, path, **kwargs)
        response.raise_for_status()
        return response
    
    async def create_memory(
        self,
        content: str,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Memory:
        payload = MemoryCreate(
            content=content,
            title=title,
            tags=tags or [],
            source=source,
            metadata=metadata or {},
        )
        
        response = await self._request("POST", "/api/memories", json=payload.model_dump())
        return Memory.model_validate(response.json())
    
    async def get_memory(self, memory_id: str) -> Memory:
        response = await self._request("GET", f"/api/memories/{memory_id}")
        return Memory.model_validate(response.json())
    
    async def list_memories(
        self,
        limit: int = 10,
        offset: int = 0,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        if tags:
            params["tags"] = ",".join(tags)
        
        response = await self._request("GET", "/api/memories", params=params)
        return response.json()
    
    async def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Memory:
        payload = MemoryUpdate(
            content=content,
            title=title,
            tags=tags,
            metadata=metadata,
        )
        
        response = await self._request(
            "PUT", 
            f"/api/memories/{memory_id}", 
            json=payload.model_dump(exclude_unset=True)
        )
        return Memory.model_validate(response.json())
    
    async def delete_memory(self, memory_id: str) -> bool:
        await self._request("DELETE", f"/api/memories/{memory_id}")
        return True
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        semantic: bool = True,
        keyword: bool = True,
    ) -> SearchResponse:
        params = {
            "q": query,
            "limit": limit,
            "semantic": semantic,
            "keyword": keyword,
        }
        
        response = await self._request("GET", "/api/search", params=params)
        return SearchResponse.model_validate(response.json())
    
    async def build_context(
        self,
        query: str,
        limit: int = 5,
        max_tokens: int = 2000,
    ) -> Context:
        params = {
            "query": query,
            "limit": limit,
            "max_tokens": max_tokens,
        }
        
        response = await self._request("GET", "/api/context", params=params)
        return Context.model_validate(response.json())
    
    async def get_stats(self) -> MemoryStats:
        response = await self._request("GET", "/api/stats")
        return MemoryStats.model_validate(response.json())
    
    async def list_conflicts(
        self,
        limit: int = 10,
        offset: int = 0,
        resolved: Optional[bool] = None,
    ) -> Dict[str, Any]:
        params = {"limit": limit, "offset": offset}
        if resolved is not None:
            params["resolved"] = resolved
        
        response = await self._request("GET", "/api/conflicts", params=params)
        return response.json()
    
    async def detect_conflicts(self) -> Dict[str, Any]:
        response = await self._request("POST", "/api/conflicts/detect")
        return response.json()
    
    async def resolve_conflict(self, conflict_id: str) -> Conflict:
        response = await self._request("POST", f"/api/conflicts/{conflict_id}/resolve")
        return Conflict.model_validate(response.json())
    
    async def get_graph(self) -> GraphData:
        response = await self._request("GET", "/api/graph")
        return GraphData.model_validate(response.json())
    
    async def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        weight: float = 1.0,
    ) -> Dict[str, Any]:
        payload = {
            "source_id": source_id,
            "target_id": target_id,
            "type": relationship_type,
            "weight": weight,
        }
        
        response = await self._request("POST", "/api/graph/relationships", json=payload)
        return response.json()
    
    async def delete_relationship(self, source_id: str, target_id: str) -> bool:
        await self._request("DELETE", f"/api/graph/relationships/{source_id}/{target_id}")
        return True
    
    async def health_check(self) -> bool:
        try:
            response = await self._request("GET", "/health")
            return response.status_code == 200
        except Exception:
            return False
    
    async def get_version(self) -> Dict[str, str]:
        response = await self._request("GET", "/version")
        return response.json()