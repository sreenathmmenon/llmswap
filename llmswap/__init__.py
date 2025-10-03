"""
llmswap: Simple interface for any LLM provider

Use any LLM provider with one simple interface.
Perfect for chatbots, applications, and scripts.

Basic usage:
    from llmswap import LLMClient
    
    client = LLMClient()  # Auto-detects provider
    response = client.query("Hello, world!")
    print(response.content)

Advanced usage:
    # Specify provider
    client = LLMClient(provider="anthropic")
    
    # Switch providers
    client.set_provider("openai")
    
    # With custom model
    client = LLMClient(provider="anthropic", model="claude-3-opus-20240229")
"""

__version__ = "5.1.2"
__author__ = "Sreenath Menon"
__description__ = "Universal AI Platform: CLI + Python SDK | Multi-Provider LLM Interface for Any Use Case"

from .client import LLMClient
from .async_client import AsyncLLMClient
from .response import LLMResponse
from .cache import InMemoryCache
from .exceptions import (
    LLMSwapError,
    ProviderError, 
    ConfigurationError,
    AllProvidersFailedError
)

__all__ = [
    "LLMClient",
    "AsyncLLMClient",
    "LLMResponse",
    "InMemoryCache",
    "LLMSwapError",
    "ProviderError",
    "ConfigurationError", 
    "AllProvidersFailedError"
]