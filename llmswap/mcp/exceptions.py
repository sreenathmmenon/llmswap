"""
MCP-specific exceptions

Production-grade error handling with clear messages and recovery guidance.
"""

from typing import Optional, Dict, Any
from datetime import datetime


class MCPError(Exception):
    """Base exception for all MCP errors"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        retry_after: Optional[float] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.retry_after = retry_after
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dict for logging/monitoring"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "retry_after": self.retry_after,
        }


class MCPConnectionError(MCPError):
    """Connection to MCP server failed"""

    pass


class MCPTimeoutError(MCPError):
    """MCP operation timed out"""

    pass


class MCPAuthenticationError(MCPError):
    """MCP server authentication failed"""

    pass


class MCPTransportError(MCPError):
    """MCP transport layer error"""

    pass


class MCPServerError(MCPError):
    """MCP server returned an error"""

    pass


class MCPToolExecutionError(MCPError):
    """MCP tool execution failed"""

    def __init__(self, tool_name: str, message: str, tool_error: Optional[Dict] = None):
        super().__init__(
            message=f"Tool '{tool_name}' execution failed: {message}",
            error_code="TOOL_EXECUTION_FAILED",
            details={"tool_name": tool_name, "tool_error": tool_error},
        )


class MCPProtocolError(MCPError):
    """MCP protocol violation"""

    pass
