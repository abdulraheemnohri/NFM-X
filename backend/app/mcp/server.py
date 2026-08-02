from typing import Any, Dict, List, Optional
import json

try:
    from mcp.server import MCPServer
except ImportError:
    try:
        from mcp.server.mcpserver import MCPServer
    except ImportError:
        from mcp.server import Server as MCPServer

from mcp.types import TextContent, Tool
from sdk.python.nfm.client import NFMClient
from sdk.python.nfm.models import MemoryCreate

class NFMMCPService:
    def __init__(self, nfm_base_url: str = "http://localhost:8765"):
        self.nfm = NFMClient(base_url=nfm_base_url)
        self.server = MCPServer("nfm-x-mcp")
        self._register_tools()

    def _register_tools(self):
        # Support both server.tool decorator and fallback mechanisms
        tool_decorator = getattr(self.server, "tool", None)
        if tool_decorator is not None:
            @tool_decorator()
            async def memory_search(query: str, agent_id: Optional[str] = None, limit: int = 10) -> str:
                """Search NFM-X memories.

                Args:
                    query: Search query string.
                    agent_id: Optional agent filter.
                    limit: Max results.
                """
                result = self.nfm.search({"query": query, "agent_id": agent_id, "limit": limit})
                return json.dumps(result, indent=2)

            @tool_decorator()
            async def memory_recall(memory_id: str) -> str:
                """Get memory by ID.

                Args:
                    memory_id: The UUID of the memory to fetch.
                """
                result = self.nfm.get_memory(memory_id)
                return json.dumps(result, indent=2)

            @tool_decorator()
            async def memory_context(agent_id: str, query: str, max_memories: int = 10) -> str:
                """Build context for task.

                Args:
                    agent_id: The agent context ID.
                    query: The context query string.
                    max_memories: Max memories.
                """
                result = self.nfm.get_context({"agent_id": agent_id, "query": query, "max_memories": max_memories})
                return json.dumps(result, indent=2)

            @tool_decorator()
            async def memory_store(type: str, content: str, agent_id: Optional[str] = None, confidence: Optional[float] = None, importance: Optional[float] = None) -> str:
                """Store a new memory.

                Args:
                    type: Memory type.
                    content: The memory content string.
                    agent_id: Optional agent context ID.
                    confidence: Optional confidence.
                    importance: Optional importance.
                """
                mem = MemoryCreate(
                    type=type, content=content, agent_id=agent_id,
                    confidence=confidence, importance=importance
                )
                result = self.nfm.create_memory(mem)
                return json.dumps(result, indent=2)

            @tool_decorator()
            async def memory_history(memory_id: str) -> str:
                """Get memory version history.

                Args:
                    memory_id: The UUID of the memory to inspect.
                """
                result = self.nfm.get_history(memory_id)
                return json.dumps(result, indent=2)

    def run(self, transport: str = "stdio"):
        if transport == "stdio":
            import asyncio
            async def main():
                await self.server.run_stdio_async()
            asyncio.run(main())
