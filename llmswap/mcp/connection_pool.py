"""
Connection Pool for MCP Servers

Production-grade connection pooling with health monitoring and auto-recovery.
"""

import threading
import queue
import time
import logging
from typing import Dict, Optional, Set, Any
from dataclasses import dataclass
from datetime import datetime

from .client import MCPClient
from .exceptions import MCPConnectionError, MCPError

logger = logging.getLogger(__name__)


@dataclass
class ConnectionPoolMetrics:
    """Metrics for connection pool monitoring"""

    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    total_acquires: int = 0
    total_releases: int = 0
    pool_exhausted_count: int = 0
    average_acquire_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_connections": self.total_connections,
            "active_connections": self.active_connections,
            "idle_connections": self.idle_connections,
            "total_acquires": self.total_acquires,
            "total_releases": self.total_releases,
            "pool_exhausted_count": self.pool_exhausted_count,
            "average_acquire_time": self.average_acquire_time,
        }


class ConnectionPool:
    """
    Thread-safe connection pool for MCP servers

    Manages a pool of MCPClient connections with automatic scaling,
    health monitoring, and connection reuse.
    """

    def __init__(
        self,
        server_name: str,
        create_connection,  # Callable that creates new MCPClient
        min_connections: int = 1,
        max_connections: int = 10,
        connection_timeout: float = 30.0,
        idle_timeout: float = 300.0,
        health_check_interval: float = 60.0,
    ):
        """
        Initialize connection pool

        Args:
            server_name: Name of the MCP server
            create_connection: Function to create new connections
            min_connections: Minimum connections to maintain
            max_connections: Maximum connections allowed
            connection_timeout: Timeout for acquiring connection
            idle_timeout: Time before idle connection is closed
            health_check_interval: Interval for health checks
        """
        self.server_name = server_name
        self.create_connection = create_connection
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.idle_timeout = idle_timeout
        self.health_check_interval = health_check_interval

        # Connection management
        self._available = queue.Queue(maxsize=max_connections)
        self._in_use: Set[MCPClient] = set()
        self._total_created = 0
        self._lock = threading.RLock()
        self._closed = False

        # Metrics
        self._metrics = ConnectionPoolMetrics()
        self._acquire_times = []

        # Health monitoring
        self._health_monitor_thread: Optional[threading.Thread] = None
        self._start_health_monitor()

        # Pre-create minimum connections
        self._initialize_pool()

        logger.info(
            f"Connection pool created for {server_name}: "
            f"min={min_connections}, max={max_connections}"
        )

    def acquire(self, timeout: Optional[float] = None) -> MCPClient:
        """
        Acquire connection from pool

        Args:
            timeout: Timeout in seconds (None for default)

        Returns:
            MCPClient instance

        Raises:
            MCPConnectionError: If pool exhausted or timeout
        """
        if self._closed:
            raise MCPConnectionError("Connection pool is closed")

        timeout = timeout if timeout is not None else self.connection_timeout
        start_time = time.time()

        try:
            # Try to get existing connection
            try:
                conn = self._available.get(timeout=timeout)
            except queue.Empty:
                # No available connections, try to create new one
                with self._lock:
                    if self._total_created < self.max_connections:
                        conn = self._create_new_connection()
                    else:
                        # Pool exhausted
                        self._metrics.pool_exhausted_count += 1
                        raise MCPConnectionError(
                            f"Connection pool exhausted for {self.server_name}. "
                            f"Max connections: {self.max_connections}. "
                            f"Try again later or increase max_connections.",
                            retry_after=5.0,
                        )

            # Validate connection is healthy
            if not conn.is_connected():
                logger.warning(f"Unhealthy connection discarded for {self.server_name}")
                conn.close()
                with self._lock:
                    self._total_created -= 1
                # Retry with remaining timeout
                remaining = timeout - (time.time() - start_time)
                if remaining > 0:
                    return self.acquire(timeout=remaining)
                else:
                    raise MCPConnectionError("Timeout acquiring healthy connection")

            # Mark as in use
            with self._lock:
                self._in_use.add(conn)
                self._metrics.total_acquires += 1

            # Record acquire time
            acquire_time = time.time() - start_time
            self._record_acquire_time(acquire_time)

            logger.debug(
                f"Acquired connection for {self.server_name} in {acquire_time:.3f}s"
            )

            return conn

        except Exception as e:
            logger.error(f"Failed to acquire connection for {self.server_name}: {e}")
            raise

    def release(self, conn: MCPClient) -> None:
        """
        Release connection back to pool

        Args:
            conn: MCPClient to release
        """
        with self._lock:
            if conn in self._in_use:
                self._in_use.remove(conn)
                self._metrics.total_releases += 1

            # Check if connection is still healthy
            if conn.is_connected():
                try:
                    self._available.put_nowait(conn)
                    logger.debug(f"Released connection for {self.server_name}")
                except queue.Full:
                    # Pool full, close connection
                    logger.debug(
                        f"Pool full, closing excess connection for {self.server_name}"
                    )
                    conn.close()
                    self._total_created -= 1
            else:
                # Connection unhealthy, close it
                logger.warning(f"Closing unhealthy connection for {self.server_name}")
                conn.close()
                self._total_created -= 1

    def close(self) -> None:
        """Close all connections in pool"""
        with self._lock:
            if self._closed:
                return

            self._closed = True

            # Close all available connections
            while not self._available.empty():
                try:
                    conn = self._available.get_nowait()
                    conn.close()
                except queue.Empty:
                    break

            # Close in-use connections
            for conn in self._in_use:
                conn.close()

            self._in_use.clear()
            self._total_created = 0

            logger.info(f"Closed connection pool for {self.server_name}")

    def get_metrics(self) -> ConnectionPoolMetrics:
        """Get current pool metrics"""
        with self._lock:
            self._metrics.total_connections = self._total_created
            self._metrics.active_connections = len(self._in_use)
            self._metrics.idle_connections = self._available.qsize()

        return self._metrics

    def _initialize_pool(self) -> None:
        """Pre-create minimum connections"""
        for _ in range(self.min_connections):
            try:
                conn = self._create_new_connection()
                self._available.put(conn)
            except Exception as e:
                logger.error(f"Failed to create initial connection: {e}")

    def _create_new_connection(self) -> MCPClient:
        """Create new connection (must be called with lock held)"""
        conn = self.create_connection()
        self._total_created += 1
        logger.debug(
            f"Created new connection for {self.server_name} (total: {self._total_created})"
        )
        return conn

    def _record_acquire_time(self, acquire_time: float) -> None:
        """Record connection acquire time for metrics"""
        self._acquire_times.append(acquire_time)

        # Keep only last 100 samples
        if len(self._acquire_times) > 100:
            self._acquire_times.pop(0)

        # Update average
        if self._acquire_times:
            self._metrics.average_acquire_time = sum(self._acquire_times) / len(
                self._acquire_times
            )

    def _start_health_monitor(self) -> None:
        """Start background health monitoring thread"""
        self._health_monitor_thread = threading.Thread(
            target=self._health_monitor_loop,
            daemon=True,
            name=f"MCP-health-{self.server_name}",
        )
        self._health_monitor_thread.start()

    def _health_monitor_loop(self) -> None:
        """Background health monitoring loop"""
        while not self._closed:
            try:
                time.sleep(self.health_check_interval)

                if self._closed:
                    break

                # Check connections in pool
                unhealthy = []
                temp_queue = queue.Queue()

                # Check all available connections
                while not self._available.empty():
                    try:
                        conn = self._available.get_nowait()
                        if conn.is_connected():
                            temp_queue.put(conn)
                        else:
                            unhealthy.append(conn)
                    except queue.Empty:
                        break

                # Put healthy connections back
                while not temp_queue.empty():
                    try:
                        conn = temp_queue.get_nowait()
                        self._available.put(conn)
                    except queue.Empty:
                        break

                # Close unhealthy connections
                if unhealthy:
                    logger.warning(
                        f"Found {len(unhealthy)} unhealthy connections for {self.server_name}"
                    )
                    for conn in unhealthy:
                        conn.close()
                        with self._lock:
                            self._total_created -= 1

                    # Replenish if below minimum
                    with self._lock:
                        while self._total_created < self.min_connections:
                            try:
                                conn = self._create_new_connection()
                                self._available.put(conn)
                            except Exception as e:
                                logger.error(f"Failed to replenish connection: {e}")
                                break

            except Exception as e:
                logger.error(f"Health monitor error for {self.server_name}: {e}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False
