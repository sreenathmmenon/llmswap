"""Main LLMClient class for llmswap."""

import os
from typing import Optional, List, Dict, Any

from .providers import AnthropicProvider, OpenAIProvider, GeminiProvider, OllamaProvider, WatsonxProvider
from .response import LLMResponse
from .exceptions import ConfigurationError, AllProvidersFailedError
from .cache import InMemoryCache


class LLMClient:
    """Simple client for any LLM provider."""
    
    def __init__(self, 
                 provider: str = "auto",
                 model: Optional[str] = None,
                 api_key: Optional[str] = None,
                 fallback: bool = True,
                 cache_enabled: bool = False,
                 cache_ttl: int = 3600,
                 cache_max_size_mb: int = 100):
        """Initialize LLM client.
        
        Args:
            provider: Provider name ("auto", "anthropic", "openai", "gemini", "watsonx", "ollama")
            model: Model name (optional, uses provider defaults)
            api_key: API key (optional, uses environment variables)
            fallback: Enable fallback to other providers if primary fails
            cache_enabled: Enable response caching (default: False for security)
            cache_ttl: Default cache time-to-live in seconds (default: 3600)
            cache_max_size_mb: Maximum cache size in megabytes (default: 100)
        """
        self.fallback_enabled = fallback
        self.current_provider = None
        
        # Provider priority order for auto-detection and fallback
        self.provider_order = ["anthropic", "openai", "gemini", "watsonx", "ollama"]
        
        # Initialize cache if enabled
        self._cache = InMemoryCache(cache_max_size_mb, cache_ttl) if cache_enabled else None
        
        # Conversation history for chat mode
        self._conversation_history = []
        self._max_history_length = 50  # Limit conversation length
        
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
            "- WATSONX_API_KEY and WATSONX_PROJECT_ID\n"
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
        elif provider_name == "watsonx":
            project_id = os.getenv("WATSONX_PROJECT_ID")
            if not project_id:
                raise ConfigurationError("WATSONX_PROJECT_ID environment variable required")
            return WatsonxProvider(api_key, model, project_id)
        else:
            raise ConfigurationError(f"Unknown provider: {provider_name}")
    
    def query(self, 
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
        
        try:
            response = self.current_provider.query(prompt)
            
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
            
            return response
            
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
    
    def start_conversation(self):
        """Start a new conversation by clearing history."""
        self._conversation_history = []
    
    def add_to_conversation(self, user_message: str, assistant_response: str):
        """Add message pair to conversation history."""
        self._conversation_history.append({"role": "user", "content": user_message})
        self._conversation_history.append({"role": "assistant", "content": assistant_response})
        
        # Trim conversation if too long
        if len(self._conversation_history) > self._max_history_length:
            # Remove oldest pair (user + assistant)
            self._conversation_history = self._conversation_history[2:]
    
    def get_conversation_length(self) -> int:
        """Get number of messages in conversation."""
        return len(self._conversation_history)
    
    def clear_conversation(self):
        """Clear conversation history."""
        self._conversation_history = []
    
    def chat(self, 
             message: str,
             cache_context: Optional[Dict[str, Any]] = None,
             cache_ttl: Optional[int] = None,
             cache_bypass: bool = False) -> LLMResponse:
        """Send message with conversation context.
        
        This method maintains conversation history for chat-like interactions.
        Use this for conversational AI where context matters.
        
        Args:
            message: User message to send
            cache_context: Optional context dict for cache key
            cache_ttl: Override default cache TTL in seconds
            cache_bypass: Skip cache lookup and force fresh response
            
        Returns:
            LLMResponse with content, metadata, and usage info
        """
        # Build messages with conversation history
        messages = list(self._conversation_history)
        messages.append({"role": "user", "content": message})
        
        # Use the provider's new chat method if available, fallback to query
        response = None
        if hasattr(self.current_provider, 'chat'):
            response = self.current_provider.chat(messages)
        else:
            # Fallback: send just the message (backward compatibility)
            response = self.current_provider.query(message)
        
        # Add to conversation history
        self.add_to_conversation(message, response.content)
        
        return response