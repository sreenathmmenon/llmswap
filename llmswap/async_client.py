"""Async client for llmswap with streaming support."""

import asyncio
from typing import Optional, List, AsyncIterator, Dict, Any

from .async_providers import (
    AsyncAnthropicProvider, AsyncOpenAIProvider, AsyncGeminiProvider, 
    AsyncOllamaProvider, AsyncWatsonxProvider, AsyncGroqProvider, AsyncCoherProvider, AsyncPerplexityProvider
)
from .response import LLMResponse
from .exceptions import ConfigurationError, AllProvidersFailedError
from .logging_handler import LLMLogger
from .cache import InMemoryCache


class AsyncLLMClient:
    """Async client for any LLM provider with streaming support."""
    
    def __init__(self, 
                 provider: str = "auto",
                 model: Optional[str] = None,
                 api_key: Optional[str] = None,
                 fallback: bool = True,
                 log_file: Optional[str] = None,
                 log_level: str = "info",
                 cache_enabled: bool = False,
                 cache_ttl: int = 3600,
                 cache_max_size_mb: int = 100):
        """Initialize async LLM client.
        
        Args:
            provider: Provider name ("auto", "anthropic", "openai", "gemini", "cohere", "perplexity", "watsonx", "groq", "ollama")
            model: Model name (optional, uses provider defaults)
            api_key: API key (optional, uses environment variables)
            fallback: Enable fallback to other providers if primary fails
            log_file: Path to log file for request logging
            log_level: Logging level ("debug", "info", "warning", "error")
            cache_enabled: Enable response caching (default: False for security)
            cache_ttl: Default cache time-to-live in seconds (default: 3600)
            cache_max_size_mb: Maximum cache size in megabytes (default: 100)
        """
        self.fallback_enabled = fallback
        self.current_provider = None
        
        # Initialize logger if log_file is provided
        self.logger = LLMLogger(log_file, log_level) if log_file else None
        
        # Initialize cache if enabled
        self._cache = InMemoryCache(cache_max_size_mb, cache_ttl) if cache_enabled else None
        
        # Provider priority order for auto-detection and fallback
        self.provider_order = ["anthropic", "openai", "gemini", "cohere", "perplexity", "watsonx", "groq", "ollama"]
        
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
            "No LLM providers available. Set at least one API key:\\n"
            "- ANTHROPIC_API_KEY\\n"
            "- OPENAI_API_KEY\\n"
            "- GEMINI_API_KEY\\n"
            "- COHERE_API_KEY\\n"
            "- PERPLEXITY_API_KEY\\n"
            "- WATSONX_API_KEY and WATSONX_PROJECT_ID\\n"
            "- GROQ_API_KEY\\n"
            "Or run Ollama locally"
        )
    
    def _initialize_provider(self, provider_name: str, model: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize specific provider."""
        if provider_name == "anthropic":
            return AsyncAnthropicProvider(api_key, model)
        elif provider_name == "openai":
            return AsyncOpenAIProvider(api_key, model)
        elif provider_name == "gemini":
            return AsyncGeminiProvider(api_key, model)
        elif provider_name == "cohere":
            return AsyncCoherProvider(api_key, model)
        elif provider_name == "perplexity":
            return AsyncPerplexityProvider(api_key, model)
        elif provider_name == "groq":
            return AsyncGroqProvider(api_key, model)
        elif provider_name == "ollama":
            return AsyncOllamaProvider(model or "llama3")
        elif provider_name == "watsonx":
            import os
            project_id = os.getenv("WATSONX_PROJECT_ID")
            if not project_id:
                raise ConfigurationError("WATSONX_PROJECT_ID environment variable required")
            return AsyncWatsonxProvider(api_key, model, project_id)
        else:
            raise ConfigurationError(f"Unknown provider: {provider_name}")
    
    async def query(self, 
                    prompt: str,
                    cache_context: Optional[Dict[str, Any]] = None,
                    cache_ttl: Optional[int] = None,
                    cache_bypass: bool = False) -> LLMResponse:
        """Send query to current provider with optional fallback and caching.
        
        Args:
            prompt: Text prompt to send to LLM
            cache_context: Optional context dict (e.g., {"user_id": "123"}) for cache key
            cache_ttl: Override default cache TTL in seconds
            cache_bypass: Skip cache lookup and force fresh response
            
        Returns:
            LLMResponse with content, metadata, and usage info
        """
        if not self.current_provider:
            raise ConfigurationError("No provider initialized")
        
        # Check cache if enabled and not bypassed
        if self._cache and not cache_bypass:
            cache_key = InMemoryCache.create_cache_key(prompt, cache_context)
            cached_data = self._cache.get(cache_key)
            
            if cached_data:
                # Reconstruct response from cached data
                response = LLMResponse(
                    content=cached_data["content"],
                    provider=cached_data.get("provider"),
                    model=cached_data.get("model"),
                    usage=cached_data.get("usage"),
                    raw_response=cached_data.get("raw_response")
                )
                # Mark as from cache
                response.from_cache = True
                return response
        
        # Log request if logger is available
        if self.logger:
            self.logger.log_request(
                provider=self.current_provider.provider_name,
                model=self.current_provider.model,
                prompt_length=len(prompt)
            )
        
        try:
            response = await self.current_provider.query(prompt)
            
            # Store in cache if enabled
            if self._cache:
                cache_key = InMemoryCache.create_cache_key(prompt, cache_context)
                cache_data = {
                    "content": response.content,
                    "provider": response.provider,
                    "model": response.model,
                    "usage": response.usage,
                    "raw_response": response.raw_response
                }
                self._cache.set(cache_key, cache_data, cache_ttl)
            
            # Log response if logger is available
            if self.logger:
                self.logger.log_response(
                    provider=response.provider,
                    model=response.model,
                    response_length=len(response.content),
                    latency=response.latency,
                    metadata=response.metadata
                )
            
            return response
            
        except Exception as e:
            if not self.fallback_enabled:
                raise
            
            # Try fallback providers
            for provider_name in self.provider_order:
                if provider_name == self.get_current_provider():
                    continue
                    
                try:
                    fallback_provider = self._initialize_provider(provider_name)
                    if not fallback_provider.is_available():
                        continue
                        
                    # Switch to fallback provider
                    original_provider = self.current_provider
                    self.current_provider = fallback_provider
                    
                    response = await fallback_provider.query(prompt)
                    
                    # Log fallback if logger is available
                    if self.logger:
                        self.logger.log_response(
                            provider=response.provider,
                            model=response.model,
                            response_length=len(response.content),
                            latency=response.latency,
                            metadata={"fallback_from": original_provider.provider_name, **response.metadata}
                        )
                    
                    return response
                    
                except Exception:
                    continue
            
            raise AllProvidersFailedError(f"All providers failed. Last error: {e}")
    
    async def stream(self, prompt: str) -> AsyncIterator[str]:
        """Stream response from LLM provider.
        
        Args:
            prompt: Text prompt to send to LLM
            
        Yields:
            String chunks of the response
        """
        if not self.current_provider:
            raise ConfigurationError("No provider initialized")
        
        provider_name = self.get_current_provider()
        
        if not hasattr(self.current_provider, 'stream'):
            raise NotImplementedError(f"Provider {provider_name} doesn't support streaming yet")
        
        # Log streaming request if logger is available
        if self.logger:
            self.logger.log_request(
                provider=self.current_provider.provider_name,
                model=self.current_provider.model,
                prompt_length=len(prompt),
                metadata={"streaming": True}
            )
        
        try:
            chunk_count = 0
            async for chunk in self.current_provider.stream(prompt):
                chunk_count += 1
                yield chunk
            
            # Log streaming completion if logger is available
            if self.logger:
                self.logger.log_response(
                    provider=self.current_provider.provider_name,
                    model=self.current_provider.model,
                    response_length=0,  # Can't measure total length in streaming
                    latency=0,  # Can't measure total latency in streaming
                    metadata={"streaming": True, "chunks": chunk_count}
                )
                
        except Exception as e:
            raise
    
    def get_current_provider(self) -> str:
        """Get the name of the currently active provider."""
        if not self.current_provider:
            return "none"
        return self.current_provider.provider_name
    
    def set_provider(self, provider_name: str, model: Optional[str] = None, api_key: Optional[str] = None):
        """Switch to a different provider.
        
        Args:
            provider_name: Name of the provider to switch to
            model: Optional model name for the new provider
            api_key: Optional API key for the new provider
        """
        self.current_provider = self._initialize_provider(provider_name, model, api_key)
    
    def is_provider_available(self, provider_name: str) -> bool:
        """Check if a specific provider is available."""
        try:
            provider = self._initialize_provider(provider_name)
            return provider.is_available()
        except ConfigurationError:
            return False
    
    def list_available_providers(self) -> List[str]:
        """List all available and configured providers."""
        available = []
        for provider_name in self.provider_order:
            if self.is_provider_available(provider_name):
                available.append(provider_name)
        return available
    
    def clear_cache(self) -> None:
        """Clear all cached responses."""
        if self._cache:
            self._cache.clear()
    
    def invalidate_cache(self, prompt: str, cache_context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Invalidate a specific cached response.
        
        Args:
            prompt: The prompt to invalidate
            cache_context: Optional context used when caching
            
        Returns:
            True if entry was removed, False if not found
        """
        if not self._cache:
            return False
        
        cache_key = InMemoryCache.create_cache_key(prompt, cache_context)
        return self._cache.invalidate(cache_key)
    
    def get_cache_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats or None if cache disabled
        """
        if not self._cache:
            return None
        return self._cache.get_stats()