"""Response object for LLM queries."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class LLMResponse:
    """Response from LLM query."""
    
    content: str
    provider: Optional[str] = None
    model: Optional[str] = None
    latency: float = 0.0
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    usage: Optional[Dict[str, Any]] = None
    raw_response: Optional[Any] = None
    from_cache: bool = False
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    def __str__(self):
        return f"LLMResponse(provider={self.provider}, model={self.model})"