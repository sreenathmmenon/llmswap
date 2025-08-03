"""Main LLMClient class for llmswap."""

import os
from typing import Optional, List

from .providers import AnthropicProvider, OpenAIProvider, GeminiProvider, OllamaProvider
from .response import LLMResponse
from .exceptions import ConfigurationError, AllProvidersFailedError


class LLMClient:
    """Simple client for any LLM provider."""
    
    def __init__(self, 
                 provider: str = "auto",
                 model: Optional[str] = None,
                 api_key: Optional[str] = None,
                 fallback: bool = True):
        """Initialize LLM client.
        
        Args:
            provider: Provider name ("auto", "anthropic", "openai", "gemini", "ollama")
            model: Model name (optional, uses provider defaults)
            api_key: API key (optional, uses environment variables)
            fallback: Enable fallback to other providers if primary fails
        """
        self.fallback_enabled = fallback
        self.current_provider = None
        
        # Provider priority order for auto-detection and fallback
        self.provider_order = ["anthropic", "openai", "gemini", "ollama"]
        
        if provider == "auto":
            self.current_provider = self._detect_available_provider()
        else:
            self.current_provider = self._initialize_provider(provider, model, api_key)
    
    def _detect_available_provider(self):
        """Auto-detect first available provider based on environment variables."""
        for provider_name in self.provider_order:
            try:
                provider = self._initialize_provider(provider_name)
                if provider.is_available():
                    return provider
            except ConfigurationError:
                continue
        
        raise ConfigurationError(
            "No LLM providers available. Set at least one API key:\n"
            "- ANTHROPIC_API_KEY\n"
            "- OPENAI_API_KEY\n"
            "- GEMINI_API_KEY\n"
            "Or run Ollama locally"
        )
    
    def _initialize_provider(self, provider_name: str, model: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize specific provider."""
        if provider_name == "anthropic":
            return AnthropicProvider(api_key, model)
        elif provider_name == "openai":
            return OpenAIProvider(api_key, model)
        elif provider_name == "gemini":
            return GeminiProvider(api_key, model)
        elif provider_name == "ollama":
            return OllamaProvider(model or "llama3")
        else:
            raise ConfigurationError(f"Unknown provider: {provider_name}")
    
    def query(self, prompt: str) -> LLMResponse:
        """Send query to current provider with optional fallback.
        
        Args:
            prompt: Text prompt to send to LLM
            
        Returns:
            LLMResponse with content, metadata, and usage info
        """
        if not self.current_provider:
            raise ConfigurationError("No provider initialized")
        
        try:
            return self.current_provider.query(prompt)
        except Exception as e:
            if not self.fallback_enabled:
                raise
            
            # Try fallback providers
            current_provider_name = self.get_current_provider()
            for provider_name in self.provider_order:
                if provider_name == current_provider_name:
                    continue  # Skip current provider
                
                try:
                    provider = self._initialize_provider(provider_name)
                    if provider.is_available():
                        response = provider.query(prompt)
                        # Switch to working provider for future queries
                        self.current_provider = provider
                        return response
                except:
                    continue
            
            # All providers failed
            raise AllProvidersFailedError(f"All providers failed. Last error: {str(e)}")
    
    def set_provider(self, provider: str, model: Optional[str] = None, api_key: Optional[str] = None):
        """Switch to different provider.
        
        Args:
            provider: Provider name ("anthropic", "openai", "gemini", "ollama")
            model: Model name (optional)
            api_key: API key (optional)
        """
        self.current_provider = self._initialize_provider(provider, model, api_key)
    
    def get_current_provider(self) -> str:
        """Get name of current provider."""
        if not self.current_provider:
            return "none"
        return self.current_provider.__class__.__name__.replace("Provider", "").lower()
    
    def get_current_model(self) -> str:
        """Get current model name."""
        if not self.current_provider:
            return "none"
        return self.current_provider.model
    
    def is_provider_available(self, provider: str) -> bool:
        """Check if a provider is available and configured."""
        try:
            test_provider = self._initialize_provider(provider)
            return test_provider.is_available()
        except:
            return False
    
    def list_available_providers(self) -> List[str]:
        """List all available and configured providers."""
        available = []
        for provider_name in self.provider_order:
            if self.is_provider_available(provider_name):
                available.append(provider_name)
        return available