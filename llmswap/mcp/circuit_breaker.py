"""
Circuit Breaker Pattern for MCP Connections

Prevents cascading failures by detecting and isolating failing services.
"""

import threading
import time
import logging
from enum import Enum
from typing import Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime

from .exceptions import MCPError, MCPConnectionError

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker monitoring"""

    state: CircuitState
    failure_count: int
    success_count: int
    total_calls: int
    last_failure_time: Optional[datetime]
    last_state_change: datetime

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "total_calls": self.total_calls,
            "last_failure_time": (
                self.last_failure_time.isoformat() if self.last_failure_time else None
            ),
            "last_state_change": self.last_state_change.isoformat(),
        }


class CircuitBreaker:
    """
    Circuit breaker for MCP connections

    Protects against cascading failures by monitoring operation success/failure
    and temporarily blocking requests when failure threshold is exceeded.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = MCPError,
        success_threshold: int = 2,
    ):
        """
        Initialize circuit breaker

        Args:
            name: Name for this circuit breaker (for logging)
            failure_threshold: Consecutive failures before opening circuit
            recovery_timeout: Seconds to wait before trying half-open state
            expected_exception: Exception type that counts as failure
            success_threshold: Successes needed in half-open to close circuit
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.success_threshold = success_threshold

        # State management
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._total_calls = 0
        self._last_failure_time: Optional[float] = None
        self._last_state_change = time.time()
        self._lock = threading.RLock()

        logger.info(
            f"Circuit breaker '{name}' initialized: "
            f"threshold={failure_threshold}, timeout={recovery_timeout}s"
        )

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            MCPConnectionError: If circuit is open
            Original exception: If function fails
        """
        with self._lock:
            self._total_calls += 1

            # Check if circuit is open
            if self._state == CircuitState.OPEN:
                # Check if recovery timeout has passed
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    # Circuit still open, reject request
                    time_until_retry = self.recovery_timeout - (
                        time.time() - (self._last_failure_time or 0)
                    )
                    raise MCPConnectionError(
                        f"Circuit breaker '{self.name}' is OPEN. "
                        f"Service is currently unavailable. "
                        f"Retry in {time_until_retry:.1f}s",
                        error_code="CIRCUIT_OPEN",
                        retry_after=time_until_retry,
                    )

        # Execute function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except self.expected_exception as e:
            self._on_failure()
            raise

    def _on_success(self) -> None:
        """Handle successful operation"""
        with self._lock:
            self._failure_count = 0

            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                logger.debug(
                    f"Circuit breaker '{self.name}': success in HALF_OPEN "
                    f"({self._success_count}/{self.success_threshold})"
                )

                # Check if we should close the circuit
                if self._success_count >= self.success_threshold:
                    self._transition_to_closed()

            elif self._state == CircuitState.CLOSED:
                self._success_count += 1

    def _on_failure(self) -> None:
        """Handle failed operation"""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            logger.warning(
                f"Circuit breaker '{self.name}': failure "
                f"({self._failure_count}/{self.failure_threshold})"
            )

            # Check if we should open the circuit
            if self._state == CircuitState.CLOSED:
                if self._failure_count >= self.failure_threshold:
                    self._transition_to_open()

            elif self._state == CircuitState.HALF_OPEN:
                # Any failure in half-open immediately opens circuit
                self._transition_to_open()

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit"""
        if self._last_failure_time is None:
            return False

        elapsed = time.time() - self._last_failure_time
        return elapsed >= self.recovery_timeout

    def _transition_to_open(self) -> None:
        """Transition to OPEN state"""
        self._state = CircuitState.OPEN
        self._last_state_change = time.time()
        logger.error(
            f"Circuit breaker '{self.name}': OPEN " f"(failures: {self._failure_count})"
        )

    def _transition_to_half_open(self) -> None:
        """Transition to HALF_OPEN state"""
        self._state = CircuitState.HALF_OPEN
        self._success_count = 0
        self._failure_count = 0
        self._last_state_change = time.time()
        logger.info(f"Circuit breaker '{self.name}': HALF_OPEN " f"(testing recovery)")

    def _transition_to_closed(self) -> None:
        """Transition to CLOSED state"""
        self._state = CircuitState.CLOSED
        self._success_count = 0
        self._failure_count = 0
        self._last_state_change = time.time()
        logger.info(f"Circuit breaker '{self.name}': CLOSED " f"(service recovered)")

    def get_state(self) -> CircuitState:
        """Get current circuit state"""
        with self._lock:
            return self._state

    def get_metrics(self) -> CircuitBreakerMetrics:
        """Get current metrics"""
        with self._lock:
            return CircuitBreakerMetrics(
                state=self._state,
                failure_count=self._failure_count,
                success_count=self._success_count,
                total_calls=self._total_calls,
                last_failure_time=(
                    datetime.fromtimestamp(self._last_failure_time)
                    if self._last_failure_time
                    else None
                ),
                last_state_change=datetime.fromtimestamp(self._last_state_change),
            )

    def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state"""
        with self._lock:
            self._transition_to_closed()
            logger.info(f"Circuit breaker '{self.name}': manually reset")
