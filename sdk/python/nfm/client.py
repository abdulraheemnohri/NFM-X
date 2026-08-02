"""
NFM-X Python SDK Client
"""
from typing import Optional, List, Dict, Any
import aiohttp
from .models import Memory, MemoryCreate

class NFMClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self._session = None
    async def create_memory(self, content: str, **kwargs) -> Memory:
        pass