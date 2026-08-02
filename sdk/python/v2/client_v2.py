"""NFM-X V2 Python Client - Advanced API client for V2 endpoints"""

import httpx
from typing import Optional, List
from .models_v2 import MemoryV2, SearchRequestV2, SearchResultV2


class NFMXClientV2:
    """Client for NFM-X V2 API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    async def create_memory(self, content: str, **kwargs) -> MemoryV2:
        """Create a new memory with V2 features"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v2/memory/",
                json={"content": content, **kwargs},
                headers=self.headers
            )
            response.raise_for_status()
            return MemoryV2(**response.json())
    
    async def hybrid_search(self, request: SearchRequestV2) -> List[SearchResultV2]:
        """Perform hybrid search"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v2/search/hybrid",
                json=request.dict(),
                headers=self.headers
            )
            response.raise_for_status()
            return [SearchResultV2(**item) for item in response.json()]
    
    async def get_memory_versions(self, memory_id: str) -> List[MemoryV2]:
        """Get all versions of a memory"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v2/memory/{memory_id}/versions",
                headers=self.headers
            )
            response.raise_for_status()
            return [MemoryV2(**item) for item in response.json()]
    
    async def rollback_memory(self, memory_id: str, version: int) -> MemoryV2:
        """Rollback a memory to a specific version"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v2/memory/{memory_id}/rollback/{version}",
                headers=self.headers
            )
            response.raise_for_status()
            return MemoryV2(**response.json())