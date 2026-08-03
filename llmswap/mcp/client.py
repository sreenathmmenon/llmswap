"""
MCP Client

Main client for connecting to and interacting with MCP servers.
"""

from typing import Dict, List, Any, Optional
import logging

from .protocol import MCPProtocol, JSONRPCResponse
from .transports import BaseTransport, StdioTransport
from .exceptions import MCPError, MCPConnectionError, MCPTimeoutError, MCPProtocolError

logger = logging.getLogger(__name__)


class MCPClient:
    """
    MCP Client for connecting to Model Context Protocol servers

    Usage:
        # Create client
        client = MCPClient()

        # Connect to MCP server (stdio)
        client.connect_stdio(["python", "mcp_server.py"])

        # List available tools
        tools = client.list_tools()

        # Call a tool
        result = client.call_tool("calculator", {"expression": "2+2"})

        # Close connection
        client.close()
    """

    def __init__(self, client_name: str = "llmswap", client_version: str = "5.6.0"):
        """
        Initialize MCP client

        Args:
            client_name: Name of this MCP client
            client_version: Version of this MCP client
        """
        self.client_name = client_name
        self.client_version = client_version
        self.transport: Optional[BaseTransport] = None
        self._initialized = False
        self._server_info: Optional[Dict[str, Any]] = None

    def connect_stdio(
        self,
        command: List[str],
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
    ) -> None:
        """
        Connect to MCP server via stdio transport

        Args:
            command: Command to start MCP server
            cwd: Working directory for server
            env: Environment variables
            timeout: Connection timeout
        """
        from pathlib import Path

        # Create transport
        self.transport = StdioTransport(
            command=command, cwd=Path(cwd) if cwd else None, env=env, timeout=timeout
        )

        # Connect
        self.transport.connect()

        # Initialize MCP session
        self._initialize()

        logger.info(f"Connected to MCP server via stdio: {' '.join(command)}")

    def _initialize(self) -> None:
        """Initialize MCP session with server"""
        if not self.transport:
            raise MCPError("No transport connected")

        # Send initialize request
        init_request = MCPProtocol.initialize(
            {"name": self.client_name, "version": self.client_version}
        )

        self.transport.send_message(init_request.to_dict())

        # Wait for response
        response = self._receive_response(init_request.id)

        if response.is_error():
            raise MCPConnectionError(
                f"Initialize failed: {response.error}", details=response.error
            )

        if not isinstance(response.result, dict):
            raise MCPProtocolError("Initialize response did not contain a result")

        self._initialized = True
        self._server_info = response.result

        # The MCP lifecycle requires this notification before normal requests.
        initialized = MCPProtocol.initialized()
        self.transport.send_message(initialized.to_dict())

        logger.info(
            f"MCP session initialized: {self._server_info.get('serverInfo', {}).get('name', 'unknown')}"
        )

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from MCP server

        Returns:
            List of tool definitions
        """
        self._ensure_initialized()

        # Send list_tools request
        request = MCPProtocol.list_tools()
        self.transport.send_message(request.to_dict())

        # Wait for response
        response = self._receive_response(request.id)

        if response.is_error():
            raise MCPError(
                f"list_tools failed: {response.error}", details=response.error
            )

        # Extract tools from response
        tools = response.result.get("tools", [])

        logger.info(f"Discovered {len(tools)} tools from MCP server")

        return tools

    def call_tool(
        self, tool_name: str, arguments: Dict[str, Any], timeout: Optional[float] = None
    ) -> Any:
        """
        Call a tool on the MCP server

        Args:
            tool_name: Name of tool to call
            arguments: Tool arguments
            timeout: Optional timeout override

        Returns:
            Tool result
        """
        self._ensure_initialized()

        # Send call_tool request
        request = MCPProtocol.call_tool(tool_name, arguments)
        self.transport.send_message(request.to_dict())

        # Wait for response
        response = self._receive_response(request.id, timeout=timeout)

        if response.is_error():
            raise MCPError(
                f"Tool '{tool_name}' execution failed: {response.error}",
                details=response.error,
            )

        logger.info(f"Tool '{tool_name}' executed successfully")

        return response.result

    def list_resources(self) -> List[Dict[str, Any]]:
        """
        List available resources from MCP server

        Returns:
            List of resource definitions
        """
        self._ensure_initialized()

        request = MCPProtocol.list_resources()
        self.transport.send_message(request.to_dict())

        response = self._receive_response(request.id)

        if response.is_error():
            raise MCPError(
                f"list_resources failed: {response.error}", details=response.error
            )

        return response.result.get("resources", [])

    def close(self) -> None:
        """Close connection to MCP server"""
        if self.transport:
            self.transport.close()
            self.transport = None
            self._initialized = False
            self._server_info = None
            logger.info("Closed MCP connection")

    def is_connected(self) -> bool:
        """Check if connected to MCP server"""
        return (
            self.transport is not None
            and self.transport.is_connected()
            and self._initialized
        )

    def _ensure_initialized(self) -> None:
        """Ensure MCP session is initialized"""
        if not self._initialized:
            raise MCPError("MCP session not initialized. Call connect_* first.")

        if not self.transport:
            raise MCPError("No transport connected")

    def _receive_response(
        self, request_id: str, timeout: Optional[float] = None
    ) -> JSONRPCResponse:
        """Wait for the response matching a request, skipping notifications."""
        if not self.transport:
            raise MCPError("No transport connected")

        while True:
            message = self.transport.receive_message(timeout=timeout)
            if message.get("id") == request_id:
                return JSONRPCResponse.from_dict(message)

            # This synchronous client does not implement server-initiated
            # requests. Reply explicitly instead of treating one as a result.
            if message.get("method") and message.get("id") is not None:
                self.transport.send_message(
                    {
                        "jsonrpc": "2.0",
                        "id": message["id"],
                        "error": {
                            "code": -32601,
                            "message": "Server-initiated requests are not supported",
                        },
                    }
                )

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False
