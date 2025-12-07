"""
MCP Protocol Implementation (JSON-RPC 2.0)

Handles MCP message formatting and parsing according to the Model Context Protocol specification.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
import uuid


@dataclass
class JSONRPCRequest:
    """JSON-RPC 2.0 request"""

    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[str] = None
    jsonrpc: str = "2.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        request = {"jsonrpc": self.jsonrpc, "method": self.method}

        if self.params is not None:
            request["params"] = self.params

        if self.id is not None:
            request["id"] = self.id

        return request

    def to_json(self) -> str:
        """Serialize to JSON string"""
        return json.dumps(self.to_dict())


@dataclass
class JSONRPCResponse:
    """JSON-RPC 2.0 response"""

    id: Optional[str]
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    jsonrpc: str = "2.0"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JSONRPCResponse":
        """Parse from dictionary"""
        return cls(
            id=data.get("id"),
            result=data.get("result"),
            error=data.get("error"),
            jsonrpc=data.get("jsonrpc", "2.0"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "JSONRPCResponse":
        """Parse from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def is_error(self) -> bool:
        """Check if response is an error"""
        return self.error is not None


class MCPProtocol:
    """MCP protocol handler"""

    @staticmethod
    def create_request(
        method: str,
        params: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> JSONRPCRequest:
        """Create a JSON-RPC request"""
        if request_id is None:
            request_id = str(uuid.uuid4())

        return JSONRPCRequest(method=method, params=params, id=request_id)

    @staticmethod
    def create_notification(
        method: str, params: Optional[Dict[str, Any]] = None
    ) -> JSONRPCRequest:
        """Create a JSON-RPC notification (no response expected)"""
        return JSONRPCRequest(
            method=method, params=params, id=None  # Notifications have no ID
        )

    @staticmethod
    def parse_response(data: str) -> JSONRPCResponse:
        """Parse JSON-RPC response"""
        return JSONRPCResponse.from_json(data)

    # MCP-specific methods

    @staticmethod
    def initialize(client_info: Dict[str, Any]) -> JSONRPCRequest:
        """Create initialize request"""
        return MCPProtocol.create_request(
            method="initialize",
            params={
                "protocolVersion": "2024-11-05",
                "clientInfo": client_info,
                "capabilities": {"roots": {"listChanged": True}, "sampling": {}},
            },
        )

    @staticmethod
    def list_tools() -> JSONRPCRequest:
        """Create list_tools request"""
        return MCPProtocol.create_request(method="tools/list")

    @staticmethod
    def call_tool(tool_name: str, arguments: Dict[str, Any]) -> JSONRPCRequest:
        """Create call_tool request"""
        return MCPProtocol.create_request(
            method="tools/call", params={"name": tool_name, "arguments": arguments}
        )

    @staticmethod
    def list_resources() -> JSONRPCRequest:
        """Create list_resources request"""
        return MCPProtocol.create_request(method="resources/list")

    @staticmethod
    def read_resource(uri: str) -> JSONRPCRequest:
        """Create read_resource request"""
        return MCPProtocol.create_request(method="resources/read", params={"uri": uri})

    @staticmethod
    def list_prompts() -> JSONRPCRequest:
        """Create list_prompts request"""
        return MCPProtocol.create_request(method="prompts/list")

    @staticmethod
    def get_prompt(
        prompt_name: str, arguments: Optional[Dict[str, Any]] = None
    ) -> JSONRPCRequest:
        """Create get_prompt request"""
        params = {"name": prompt_name}
        if arguments:
            params["arguments"] = arguments

        return MCPProtocol.create_request(method="prompts/get", params=params)
