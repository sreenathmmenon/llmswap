"""
stdio Transport

For local MCP servers that communicate via standard input/output.
Best for: Local development, security-sensitive operations, low-latency.
"""

import subprocess
import threading
import queue
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from .base import BaseTransport
from ..exceptions import MCPConnectionError, MCPTransportError, MCPTimeoutError

logger = logging.getLogger(__name__)


class StdioTransport(BaseTransport):
    """stdio transport for local MCP servers"""

    def __init__(
        self,
        command: List[str],
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize stdio transport

        Args:
            command: Command to start MCP server (e.g., ["python", "server.py"])
            cwd: Working directory for server process
            env: Environment variables for server process
            timeout: Default timeout for operations
        """
        super().__init__(timeout)
        self.command = command
        self.cwd = cwd
        self.env = env

        self._process: Optional[subprocess.Popen] = None
        self._stdout_reader: Optional[threading.Thread] = None
        self._stderr_reader: Optional[threading.Thread] = None
        self._message_queue: queue.Queue = queue.Queue()
        self._running = False
        self._lock = threading.Lock()

    def connect(self) -> None:
        """Start MCP server process"""
        with self._lock:
            if self._process is not None:
                raise MCPConnectionError("Already connected")

            try:
                # Prepare environment
                process_env = self._prepare_env()

                # Start process
                self._process = subprocess.Popen(
                    self.command,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.cwd,
                    env=process_env,
                    bufsize=0,  # Unbuffered
                    text=False,  # Binary mode
                )

                # Start reader threads
                self._running = True
                self._stdout_reader = threading.Thread(
                    target=self._read_stdout, daemon=True, name="MCP-stdout-reader"
                )
                self._stderr_reader = threading.Thread(
                    target=self._read_stderr, daemon=True, name="MCP-stderr-reader"
                )

                self._stdout_reader.start()
                self._stderr_reader.start()

                self._connected = True

                logger.info(f"Started MCP server: {' '.join(self.command)}")

            except Exception as e:
                self._cleanup()
                raise MCPConnectionError(f"Failed to start MCP server: {e}")

    def send_message(self, message: Dict[str, Any]) -> None:
        """Send JSON-RPC message to MCP server"""
        if not self._is_connected():
            raise MCPTransportError("Not connected")

        try:
            # Serialize message
            json_str = json.dumps(message)
            data = json_str.encode("utf-8") + b"\n"

            # Write to stdin (thread-safe)
            with self._lock:
                if self._process and self._process.stdin:
                    self._process.stdin.write(data)
                    self._process.stdin.flush()
                else:
                    raise MCPTransportError("Process stdin not available")

            logger.debug(f"Sent message: {message.get('method', 'unknown')}")

        except Exception as e:
            raise MCPTransportError(f"Failed to send message: {e}")

    def receive_message(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Receive JSON-RPC message from MCP server"""
        timeout = timeout if timeout is not None else self.timeout

        try:
            message = self._message_queue.get(timeout=timeout)

            # Check if it's an error from reader thread
            if isinstance(message, Exception):
                raise message

            logger.debug(f"Received message: {message.get('id', 'notification')}")

            return message

        except queue.Empty:
            raise MCPTimeoutError(
                f"Timeout waiting for message ({timeout}s)", retry_after=timeout
            )

    def close(self) -> None:
        """Gracefully shutdown MCP server"""
        self._cleanup()
        logger.info("Closed MCP server connection")

    def is_healthy(self) -> bool:
        """Check if transport is healthy"""
        with self._lock:
            if self._process is None:
                return False

            # Check process is alive
            if self._process.poll() is not None:
                return False

            # Check reader threads are alive
            if not self._stdout_reader or not self._stdout_reader.is_alive():
                return False

            return True

    def _is_connected(self) -> bool:
        """Check if connected (internal)"""
        return (
            self._connected
            and self._process is not None
            and self._process.poll() is None
        )

    def _prepare_env(self) -> Dict[str, str]:
        """Prepare environment variables for process"""
        import os

        # Start with current environment
        process_env = os.environ.copy()

        # Add/override with provided env vars
        if self.env:
            process_env.update(self.env)

        return process_env

    def _read_stdout(self):
        """Read messages from stdout (runs in thread)"""
        buffer = b""

        while self._running:
            try:
                if not self._process or not self._process.stdout:
                    break

                # Read chunk
                chunk = self._process.stdout.read(4096)
                if not chunk:
                    break

                buffer += chunk

                # Process complete messages (newline-delimited JSON)
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)

                    if not line.strip():
                        continue

                    try:
                        message = json.loads(line.decode("utf-8"))
                        self._message_queue.put(message)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON from MCP server: {e}")
                        logger.error(f"Raw data: {line[:100]}")

            except Exception as e:
                if self._running:
                    logger.error(f"stdout read error: {e}")
                    self._message_queue.put(
                        MCPTransportError(f"stdout read error: {e}")
                    )
                break

    def _read_stderr(self):
        """Read stderr for logging (runs in thread)"""
        while self._running:
            try:
                if not self._process or not self._process.stderr:
                    break

                line = self._process.stderr.readline()
                if not line:
                    break

                # Log stderr output at warning level
                stderr_text = line.decode("utf-8", errors="ignore").strip()
                if stderr_text:
                    logger.warning(f"MCP server stderr: {stderr_text}")

            except Exception as e:
                if self._running:
                    logger.error(f"stderr read error: {e}")
                break

    def _cleanup(self):
        """Clean up process and threads"""
        with self._lock:
            self._running = False
            self._connected = False

            if self._process:
                try:
                    # Try graceful shutdown first
                    if self._process.poll() is None:
                        self._process.terminate()

                        # Wait briefly for graceful shutdown
                        try:
                            self._process.wait(timeout=2.0)
                        except subprocess.TimeoutExpired:
                            # Force kill if necessary
                            self._process.kill()
                            self._process.wait()

                    # Close pipes
                    if self._process.stdin:
                        self._process.stdin.close()
                    if self._process.stdout:
                        self._process.stdout.close()
                    if self._process.stderr:
                        self._process.stderr.close()

                except Exception as e:
                    logger.error(f"Error during cleanup: {e}")

                finally:
                    self._process = None

            # Wait for threads to finish
            if self._stdout_reader and self._stdout_reader.is_alive():
                self._stdout_reader.join(timeout=1.0)
            if self._stderr_reader and self._stderr_reader.is_alive():
                self._stderr_reader.join(timeout=1.0)
