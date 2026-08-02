import pytest
from mcp.types import Tool, TextContent
from backend.app.mcp.server import NFMMCPService

@pytest.mark.asyncio
async def test_mcp_server_tool_listings():
    # Construct MCP service pointing to a mock/default base URL
    service = NFMMCPService(nfm_base_url="http://localhost:8765")

    # We can fetch registered tools directly through the tool manager synchronously
    tools = service.server._tool_manager.list_tools()

    # Verify we have registered the 5 tools correctly
    assert len(tools) >= 5
    tool_names = [t.name for t in tools]
    assert "memory_search" in tool_names
    assert "memory_recall" in tool_names
    assert "memory_context" in tool_names
    assert "memory_store" in tool_names
    assert "memory_history" in tool_names
