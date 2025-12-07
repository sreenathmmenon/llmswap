"""
HTTP Transport

For remote MCP servers using HTTP requests.
Best for: Enterprise scale, load balancing, cloud deployment.
"""

import json
import logging
import threading
import queue
import time
from typing import Dict, Any, Optional
import urllib.request
import urllib.error
from urllib.parse import urljoin

from .base import BaseTransport
from ..exceptions import (
    MCPConnectionError,
    MCPTransportError,
    MCPTimeoutError,
    MCPAuthenticationError,
)

logger = logging.getLogger(__name__)


class HTTPTransport(BaseTransport):
    """
    HTTP transport for remote MCP servers

    Uses request-response HTTP pattern with connection pooling and retry logic.
    Best for enterprise-grade deployments with load balancing.
    """

    def __init__(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_backoff: float = 1.0,
    ):
        """
        Initialize HTTP transport

        Args:
            url: Base URL of MCP server (e.g., https://api.example.com/mcp)
            headers: Optional HTTP headers (e.g., Authorization)
            timeout: Default timeout for operations
            max_retries: Maximum retry attempts on failure
            retry_backoff: Base backoff time for retries (exponential)
        """
        super().__init__(timeout)
        self.url = url.rstrip("/")
        self.headers = headers or {}
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff

        # Pending requests for async pattern (optional)
        self._pending_requests: Dict[str, queue.Queue] = {}
        self._lock = threading.Lock()

    def connect(self) -> None:
        """Test connection to MCP server"""
        try:
            # Send health check request
            request = urllib.request.Request(
                url=urljoin(self.url, "/health"), headers={**self.headers}, method="GET"
            )

            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                if response.status != 200:
                    raise MCPConnectionError(
                        f"Health check failed: HTTP {response.status}"
                    )

            self._connected = True
            logger.info(f"Connected to MCP server via HTTP: {self.url}")

        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise MCPAuthenticationError("Authentication failed")
            raise MCPConnectionError(f"HTTP error: {e.code} {e.reason}")
        except urllib.error.URLError as e:
            raise MCPConnectionError(f"Connection error: {e.reason}")
        except Exception as e:
            raise MCPConnectionError(f"Failed to connect: {e}")

    def send_message(self, message: Dict[str, Any]) -> None:
        """
        Send message to MCP server via HTTP POST

        Note: For request-response pattern, use send_and_receive() instead.
        This method is for fire-and-forget notifications.
        """
        if not self._connected:
            raise MCPTransportError("Not connected")

        self._send_http_request(message)

    def receive_message(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Receive message from MCP server

        Note: HTTP transport uses request-response pattern.
        This method is typically not used directly.
        Use send_and_receive() for synchronous request-response.
        """
        raise MCPTransportError(
            "HTTP transport uses request-response pattern. "
            "Use send_and_receive() method instead."
        )

    def send_and_receive(
        self, message: Dict[str, Any], timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Send request and wait for response (synchronous)

        Args:
            message: JSON-RPC request
            timeout: Timeout in seconds

        Returns:
            JSON-RPC response
        """
        if not self._connected:
            raise MCPTransportError("Not connected")

        timeout = timeout if timeout is not None else self.timeout

        # Send request with retry logic
        for attempt in range(self.max_retries):
            try:
                response_data = self._send_http_request(message, timeout)

                # Parse response
                response = json.loads(response_data)
                return response

            except (urllib.error.URLError, MCPTransportError) as e:
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    backoff_time = self.retry_backoff * (2**attempt)
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{self.max_retries}), "
                        f"retrying in {backoff_time}s: {e}"
                    )
                    time.sleep(backoff_time)
                else:
                    # Final attempt failed
                    raise MCPTransportError(
                        f"Request failed after {self.max_retries} attempts: {e}"
                    )

    def close(self) -> None:
        """Close HTTP connection"""
        self._connected = False
        logger.info("Closed HTTP connection")

    def is_healthy(self) -> bool:
        """Check if HTTP transport is healthy"""
        if not self._connected:
            return False

        try:
            # Quick health check
            request = urllib.request.Request(
                url=urljoin(self.url, "/health"), headers={**self.headers}, method="GET"
            )

            with urllib.request.urlopen(request, timeout=5.0) as response:
                return response.status == 200

        except Exception:
            return False

    def _send_http_request(
        self, message: Dict[str, Any], timeout: Optional[float] = None
    ) -> str:
        """
        Send HTTP request and return response body

        Args:
            message: JSON-RPC message
            timeout: Timeout in seconds

        Returns:
            Response body as string
        """
        timeout = timeout if timeout is not None else self.timeout

        try:
            # Serialize message
            data = json.dumps(message).encode("utf-8")

            # Create request
            request = urllib.request.Request(
                url=urljoin(self.url, "/rpc"),
                data=data,
                headers={
                    **self.headers,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                method="POST",
            )

            # Send request
            with urllib.request.urlopen(request, timeout=timeout) as response:
                if response.status != 200:
                    raise MCPTransportError(
                        f"HTTP {response.status}: {response.reason}"
                    )

                # Read response
                response_data = response.read().decode("utf-8")

                logger.debug(
                    f"HTTP request successful: {message.get('method', 'unknown')}"
                )

                return response_data

        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise MCPAuthenticationError("Authentication failed")
            elif e.code == 429:
                # Rate limited
                retry_after = float(e.headers.get("Retry-After", 5))
                raise MCPTransportError(
                    f"Rate limited. Retry after {retry_after}s", retry_after=retry_after
                )
            raise MCPTransportError(f"HTTP error: {e.code} {e.reason}")

        except urllib.error.URLError as e:
            raise MCPConnectionError(f"Connection error: {e.reason}")

        except Exception as e:
            raise MCPTransportError(f"Request failed: {e}")
