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

__version__ = "1.0.3"
__author__ = "Sreenath Menon"
__description__ = "Simple interface for any LLM provider"

from .client import LLMClient
from .response import LLMResponse
from .exceptions import (
    LLMSwapError,
    ProviderError, 
    ConfigurationError,
    AllProvidersFailedError
)

__all__ = [
    "LLMClient",
    "LLMResponse", 
    "LLMSwapError",
    "ProviderError",
    "ConfigurationError", 
    "AllProvidersFailedError"
]