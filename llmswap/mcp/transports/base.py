"""
Base Transport Interface

Abstract base class for all MCP transports.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseTransport(ABC):
    """Base class for MCP transports"""

    def __init__(self, timeout: float = 30.0):
        """
        Initialize transport

        Args:
            timeout: Default timeout for operations in seconds
        """
        self.timeout = timeout
        self._connected = False

    @abstractmethod
    def connect(self) -> None:
        """
        Establish connection to MCP server

        Raises:
            MCPConnectionError: If connection fails
        """
        pass

    @abstractmethod
    def send_message(self, message: Dict[str, Any]) -> None:
        """
        Send message to MCP server

        Args:
            message: JSON-RPC message to send

        Raises:
            MCPTransportError: If send fails
        """
        pass

    @abstractmethod
    def receive_message(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Receive message from MCP server

        Args:
            timeout: Timeout in seconds (None for default)

        Returns:
            Received JSON-RPC message

        Raises:
            MCPTimeoutError: If timeout exceeded
            MCPTransportError: If receive fails
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close connection to MCP server"""
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        """
        Check if transport is healthy

        Returns:
            True if connection is healthy, False otherwise
        """
        pass

    def is_connected(self) -> bool:
        """Check if transport is connected"""
        return self._connected

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False
