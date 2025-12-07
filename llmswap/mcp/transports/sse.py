"""
SSE (Server-Sent Events) Transport

For remote MCP servers with real-time streaming.
Best for: Real-time updates, remote servers, webhooks.
"""

import threading
import queue
import json
import logging
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


class SSETransport(BaseTransport):
    """
    SSE (Server-Sent Events) transport for remote MCP servers

    Uses HTTP GET for receiving events and POST for sending messages.
    Supports auto-reconnection with Last-Event-ID.
    """

    def __init__(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
        reconnect_interval: float = 5.0,
    ):
        """
        Initialize SSE transport

        Args:
            url: Base URL of MCP server (e.g., http://api.example.com/mcp)
            headers: Optional HTTP headers (e.g., Authorization)
            timeout: Default timeout for operations
            reconnect_interval: Time to wait before reconnecting
        """
        super().__init__(timeout)
        self.url = url.rstrip("/")
        self.headers = headers or {}
        self.reconnect_interval = reconnect_interval

        self._sse_thread: Optional[threading.Thread] = None
        self._message_queue: queue.Queue = queue.Queue()
        self._running = False
        self._last_event_id: Optional[str] = None
        self._lock = threading.Lock()

    def connect(self) -> None:
        """Establish SSE connection to MCP server"""
        with self._lock:
            if self._connected:
                raise MCPConnectionError("Already connected")

            # Start SSE listener thread
            self._running = True
            self._sse_thread = threading.Thread(
                target=self._sse_listener_loop, daemon=True, name="MCP-SSE-listener"
            )
            self._sse_thread.start()

            self._connected = True
            logger.info(f"Connected to MCP server via SSE: {self.url}")

    def send_message(self, message: Dict[str, Any]) -> None:
        """Send message to MCP server via HTTP POST"""
        if not self._connected:
            raise MCPTransportError("Not connected")

        try:
            # Serialize message
            data = json.dumps(message).encode("utf-8")

            # Send via POST
            request = urllib.request.Request(
                url=urljoin(self.url, "/messages"),
                data=data,
                headers={**self.headers, "Content-Type": "application/json"},
                method="POST",
            )

            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                if response.status != 200:
                    raise MCPTransportError(
                        f"HTTP {response.status}: {response.reason}"
                    )

            logger.debug(f"Sent message via SSE: {message.get('method', 'unknown')}")

        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise MCPAuthenticationError("Authentication failed")
            raise MCPTransportError(f"HTTP error: {e.code} {e.reason}")
        except urllib.error.URLError as e:
            raise MCPConnectionError(f"Connection error: {e.reason}")
        except Exception as e:
            raise MCPTransportError(f"Failed to send message: {e}")

    def receive_message(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Receive message from SSE stream"""
        timeout = timeout if timeout is not None else self.timeout

        try:
            message = self._message_queue.get(timeout=timeout)

            # Check if it's an error from listener thread
            if isinstance(message, Exception):
                raise message

            logger.debug(
                f"Received message via SSE: {message.get('id', 'notification')}"
            )

            return message

        except queue.Empty:
            raise MCPTimeoutError(
                f"Timeout waiting for SSE message ({timeout}s)", retry_after=timeout
            )

    def close(self) -> None:
        """Close SSE connection"""
        with self._lock:
            self._running = False
            self._connected = False

        if self._sse_thread and self._sse_thread.is_alive():
            self._sse_thread.join(timeout=2.0)

        logger.info("Closed SSE connection")

    def is_healthy(self) -> bool:
        """Check if SSE transport is healthy"""
        return (
            self._connected
            and self._running
            and self._sse_thread is not None
            and self._sse_thread.is_alive()
        )

    def _sse_listener_loop(self) -> None:
        """Background thread that listens to SSE stream"""
        while self._running:
            try:
                self._connect_and_listen()
            except Exception as e:
                if self._running:
                    logger.error(f"SSE listener error: {e}")
                    logger.info(f"Reconnecting in {self.reconnect_interval}s...")
                    threading.Event().wait(self.reconnect_interval)

    def _connect_and_listen(self) -> None:
        """Connect to SSE endpoint and listen for events"""
        # Prepare request headers
        headers = {
            **self.headers,
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
        }

        # Include Last-Event-ID for reconnection
        if self._last_event_id:
            headers["Last-Event-ID"] = self._last_event_id

        # Create request
        request = urllib.request.Request(
            url=urljoin(self.url, "/events"), headers=headers
        )

        # Open connection
        with urllib.request.urlopen(request, timeout=None) as response:
            if response.status != 200:
                raise MCPConnectionError(f"SSE connection failed: {response.status}")

            logger.info("SSE connection established")

            # Read event stream
            buffer = b""
            for chunk in iter(lambda: response.read(4096), b""):
                if not self._running:
                    break

                buffer += chunk

                # Process complete events (separated by double newline)
                while b"\n\n" in buffer:
                    event_data, buffer = buffer.split(b"\n\n", 1)
                    self._process_sse_event(event_data.decode("utf-8"))

    def _process_sse_event(self, event_data: str) -> None:
        """Process SSE event"""
        event_id = None
        event_type = None
        data_lines = []

        # Parse event fields
        for line in event_data.split("\n"):
            if line.startswith("id:"):
                event_id = line[3:].strip()
            elif line.startswith("event:"):
                event_type = line[6:].strip()
            elif line.startswith("data:"):
                data_lines.append(line[5:].strip())

        # Store event ID for reconnection
        if event_id:
            self._last_event_id = event_id

        # Parse data as JSON
        if data_lines:
            try:
                data = "\n".join(data_lines)
                message = json.loads(data)
                self._message_queue.put(message)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in SSE event: {e}")
                logger.error(f"Raw data: {data[:200]}")
