"""
MCP (Model Context Protocol) Client Implementation

Universal MCP client supporting stdio, SSE, and HTTP transports.
Connects to any MCP server and enables LLMs to use external tools.

Usage:
    from llmswap.mcp import MCPClient

    # Local MCP server via stdio
    client = MCPClient()
    client.connect_stdio(["python", "mcp_server.py"])
    tools = client.list_tools()
    result = client.call_tool("my_tool", {"arg": "value"})

    # Remote MCP server via HTTP
    from llmswap.mcp.transports import HTTPTransport
    transport = HTTPTransport("https://api.example.com/mcp")
    # ... (See documentation for full examples)
"""

from .client import MCPClient
from .connection_pool import ConnectionPool, ConnectionPoolMetrics
from .circuit_breaker import CircuitBreaker, CircuitState
from .exceptions import (
    MCPError,
    MCPConnectionError,
    MCPTimeoutError,
    MCPAuthenticationError,
    MCPTransportError,
    MCPServerError,
    MCPToolExecutionError,
    MCPProtocolError,
)

__all__ = [
    # Core client
    "MCPClient",
    # Connection management
    "ConnectionPool",
    "ConnectionPoolMetrics",
    "CircuitBreaker",
    "CircuitState",
    # Exceptions
    "MCPError",
    "MCPConnectionError",
    "MCPTimeoutError",
    "MCPAuthenticationError",
    "MCPTransportError",
    "MCPServerError",
    "MCPToolExecutionError",
    "MCPProtocolError",
]

__version__ = "0.2.0"
