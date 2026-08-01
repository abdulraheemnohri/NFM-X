import httpx
import time
from typing import Optional, Dict, Any

from .models import MemoryCreate, SearchQuery, ContextQuery

class NFMClient:
    def __init__(self, base_url: str = "http://localhost:8765", api_key: Optional[str] = None, timeout: float = 30.0, max_retries: int = 3):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        kwargs["headers"] = {**self._headers(), **kwargs.get("headers", {})}
        retries = 0
        while True:
            try:
                response = self._client.request(method, path, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise Exception(f"API error {e.response.status_code}: {e.response.text}")
            except (httpx.RequestError, httpx.TimeoutException) as e:
                retries += 1
                if retries > self.max_retries:
                    raise Exception(f"Request failed after {self.max_retries} retries: {str(e)}")
                time.sleep(0.5 * retries)
            except Exception as e:
                raise Exception(f"Request failed: {str(e)}")

    def create_memory(self, memory: MemoryCreate) -> Dict[str, Any]:
        return self._request("POST", "/v1/memory/", json=memory.model_dump(exclude_none=True))

    def get_memory(self, memory_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/v1/memory/{memory_id}")

    def list_memories(self, agent_id: Optional[str] = None, memory_type: Optional[str] = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        params = {"limit": limit, "offset": offset}
        if agent_id:
            params["agent_id"] = agent_id
        if memory_type:
            params["memory_type"] = memory_type
        return self._request("GET", "/v1/memory/", params=params)

    def search(self, query: SearchQuery) -> Dict[str, Any]:
        return self._request("POST", "/v1/memory/search", json=query.model_dump(exclude_none=True))

    def get_context(self, query: ContextQuery) -> Dict[str, Any]:
        return self._request("POST", "/v1/memory/context", json=query.model_dump(exclude_none=True))

    def get_history(self, memory_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/v1/memory/{memory_id}/history")

    def health(self) -> Dict[str, Any]:
        return self._request("GET", "/health")

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
