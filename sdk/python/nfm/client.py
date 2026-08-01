#!/usr/bin/env python3
"""
NFM-X Client
============

HTTP client for interacting with NFM-X API.
Provides methods for all API endpoints.

Urdu: NFM-X API ke sath interaction ke liye HTTP client
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel
import httpx
import json
from urllib.parse import urljoin

from .models import (
    Memory, MemoryVersion, MemoryCreate, MemoryUpdate,
    SearchQuery, SearchResult, ContextQuery, ContextResult,
    EvolutionQuery, EvolutionResult, GraphQuery, GraphResult,
    AgentQuery, AgentResult
)


class NFMClientConfig(BaseModel):
    base_url: str = "http://localhost:8000"
    api_key: Optional[str] = None
    timeout: float = 30.0
    max_retries: int = 3
    verify_ssl: bool = True


class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None


class NFMClient:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, 
                 timeout: float = 30.0, max_retries: int = 3, verify_ssl: bool = True):
        self.config = NFMClientConfig(
            base_url=base_url or "http://localhost:8000",
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
            verify_ssl=verify_ssl
        )
        self._client = httpx.Client(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            verify=verify_ssl
        )
    
    def _request(self, method: str, endpoint: str, **kwargs) -> APIResponse:
        url = urljoin(self.config.base_url, endpoint)
        headers = kwargs.get('headers', {})
        if self.config.api_key:
            headers['Authorization'] = f"Bearer {self.config.api_key}"
        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/json'
        kwargs['headers'] = headers
        
        for attempt in range(self.config.max_retries):
            try:
                response = self._client.request(method, url, **kwargs)
                if response.status_code >= 200 and response.status_code < 300:
                    try:
                        data = response.json()
                        return APIResponse(success=True, data=data, message=f"Request successful ({response.status_code})")
                    except json.JSONDecodeError:
                        return APIResponse(success=True, data=response.text, message=f"Request successful ({response.status_code})")
                else:
                    error_msg = f"Request failed with status {response.status_code}"
                    try:
                        error_data = response.json()
                        if 'detail' in error_data:
                            error_msg = error_data['detail']
                    except:
                        pass
                    return APIResponse(success=False, error=error_msg, message=f"Attempt {attempt + 1}/{self.config.max_retries}")
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    return APIResponse(success=False, error=str(e), message=f"After {self.config.max_retries} attempts")
                continue
        return APIResponse(success=False, error="Max retries exceeded", message="Request failed")
    
    def create_memory(self, memory: MemoryCreate) -> APIResponse:
        return self._request("POST", "/api/memory/", json=memory.dict())
    
    def get_memory(self, memory_id: str) -> APIResponse:
        return self._request("GET", f"/api/memory/{memory_id}")
    
    def update_memory(self, memory_id: str, memory: MemoryUpdate) -> APIResponse:
        return self._request("PUT", f"/api/memory/{memory_id}", json=memory.dict())
    
    def delete_memory(self, memory_id: str) -> APIResponse:
        return self._request("DELETE", f"/api/memory/{memory_id}")
    
    def list_memories(self, memory_type: Optional[str] = None, limit: int = 100, offset: int = 0) -> APIResponse:
        params = {'limit': limit, 'offset': offset}
        if memory_type:
            params['memory_type'] = memory_type
        return self._request("GET", "/api/memory/", params=params)
    
    def get_memory_versions(self, memory_id: str, limit: int = 100) -> APIResponse:
        return self._request("GET", f"/api/memory/{memory_id}/versions", params={'limit': limit})
    
    def search_memories(self, query: SearchQuery) -> APIResponse:
        return self._request("POST", "/api/search/", json=query.dict())
    
    def get_context(self, query: ContextQuery) -> APIResponse:
        return self._request("POST", "/api/context/", json=query.dict())
    
    def evolve_memory(self, query: EvolutionQuery) -> APIResponse:
        return self._request("POST", "/api/evolution/", json=query.dict())
    
    def query_graph(self, query: GraphQuery) -> APIResponse:
        return self._request("POST", "/api/graph/", json=query.dict())
    
    def query_agent(self, query: AgentQuery) -> APIResponse:
        return self._request("POST", "/api/agents/", json=query.dict())
    
    def health_check(self) -> APIResponse:
        return self._request("GET", "/health")
    
    def get_info(self) -> APIResponse:
        return self._request("GET", "/info")
    
    def close(self):
        self._client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()