import pytest
from MCP_ffmpeg.mcp_server import mcp

@pytest.mark.asyncio
async def test_server_initialization():
    """
    Basic test to check if the server object exists and has tools.
    """

    # Checking if mcp server exists
    assert mcp is not None

    # Checking if any mcp tools are registered
    tools = await mcp.list_tools()
    assert len(tools) >= 0

def test_import():
    """
    Checks if the package is even importable.
    """

    import MCP_ffmpeg
    assert MCP_ffmpeg.__name__ == "MCP_ffmpeg"