"""Main LLMClient class for llmswap."""

import os
import time
from typing import Optional, List, Dict, Any

from .providers import AnthropicProvider, OpenAIProvider, GeminiProvider, OllamaProvider, WatsonxProvider, GroqProvider, CoherProvider, PerplexityProvider
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
                 cache_max_size_mb: int = 100,
                 analytics_enabled: bool = False):
        """Initialize LLM client.
        
        Args:
            provider: Provider name ("auto", "anthropic", "openai", "gemini", "cohere", "perplexity", "watsonx", "groq", "ollama")
            model: Model name (optional, uses provider defaults)
            api_key: API key (optional, uses environment variables)
            fallback: Enable fallback to other providers if primary fails
            cache_enabled: Enable response caching (default: False for security)
            cache_ttl: Default cache time-to-live in seconds (default: 3600)
            cache_max_size_mb: Maximum cache size in megabytes (default: 100)
            analytics_enabled: Enable privacy-first usage analytics (default: False)
        """
        self.fallback_enabled = fallback
        self.current_provider = None
        
        # Provider priority order for auto-detection and fallback
        self.provider_order = ["anthropic", "openai", "gemini", "cohere", "perplexity", "watsonx", "groq", "ollama"]
        
        # Initialize cache if enabled
        self._cache = InMemoryCache(cache_max_size_mb, cache_ttl) if cache_enabled else None
        
        # Initialize analytics if enabled (NEW - optional feature)
        self._analytics_enabled = analytics_enabled
        self._usage_tracker = None
        self._cost_estimator = None
        
        if analytics_enabled:
            try:
                from .analytics.usage_tracker import UsageTracker
                from .metrics.cost_estimator import CostEstimator
                
                self._usage_tracker = UsageTracker()
                self._cost_estimator = CostEstimator()
            except ImportError:
                # Analytics modules not available - continue without them
                self._analytics_enabled = False
        
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
        elif provider_name == "groq":
            return GroqProvider(api_key, model)
        elif provider_name == "cohere":
            return CoherProvider(api_key, model)
        elif provider_name == "perplexity":
            return PerplexityProvider(api_key, model)
        else:
            raise ConfigurationError(f"Unknown provider: {provider_name}")
    
    def query(self, 
              prompt: str,
              cache_context: Optional[Dict[str, Any]] = None,
              cache_ttl: Optional[int] = None,
              cache_bypass: bool = False,
              use_local_knowledge: bool = False) -> LLMResponse:
        """Send query to current provider with optional fallback and caching.
        
        Args:
            prompt: Text prompt to send to LLM
            cache_context: Optional context dict (e.g., {"user_id": "123"}) for cache key
            cache_ttl: Override default cache TTL in seconds
            cache_bypass: Skip cache lookup and force fresh response
            use_local_knowledge: Use local knowledge base for context (future feature)
            
        Returns:
            LLMResponse with content, metadata, and usage info
        """
        if not self.current_provider:
            raise ConfigurationError("No provider initialized")
        
        # Start timing for analytics (if enabled)
        start_time = time.time()
        cache_hit = False
        fallback_used = False
        retry_count = 0
        
        # Pre-query setup (removed estimation features)
        
        # Check cache if enabled and not bypassed
        if self._cache and not cache_bypass:
            cache_key = InMemoryCache.create_cache_key(prompt, cache_context)
            cached_data = self._cache.get(cache_key)
            
            if cached_data:
                cache_hit = True
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
                
                # Record analytics for cached response (if enabled)
                self._record_analytics(
                    response, start_time, cache_hit, fallback_used, 
                    retry_count, success=True
                )
                
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
            
            # Record analytics for successful response (if enabled)
            self._record_analytics(
                response, start_time, cache_hit, fallback_used, 
                retry_count, success=True
            )
            
            return response
            
        except Exception as e:
            if not self.fallback_enabled:
                # Record analytics for failed response (if enabled)
                self._record_analytics(
                    None, start_time, cache_hit, fallback_used, 
                    retry_count, success=False, error=e
                )
                raise
            
            # Try fallback providers
            fallback_used = True
            current_provider_name = self.get_current_provider()
            for provider_name in self.provider_order:
                if provider_name == current_provider_name:
                    continue  # Skip current provider
                
                retry_count += 1
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
                        
                        # Record analytics for successful fallback (if enabled)
                        self._record_analytics(
                            response, start_time, cache_hit, fallback_used, 
                            retry_count, success=True
                        )
                        
                        return response
                except:
                    continue
            
            # All providers failed - record analytics
            self._record_analytics(
                None, start_time, cache_hit, fallback_used, 
                retry_count, success=False, error=e
            )
            
            # All providers failed
            raise AllProvidersFailedError(f"All providers failed. Last error: {str(e)}")
    
    def _record_analytics(self, response: Optional[LLMResponse], start_time: float,
                         cache_hit: bool, fallback_used: bool, retry_count: int,
                         success: bool, error: Optional[Exception] = None):
        """Record analytics data (privacy-first - no query content stored)."""
        if not self._analytics_enabled or not self._usage_tracker:
            return
        
        try:
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Extract token counts and costs from response
            input_tokens = None
            output_tokens = None
            actual_cost = None
            
            if response and response.usage:
                input_tokens = response.usage.get("input_tokens") or response.usage.get("prompt_tokens")
                output_tokens = response.usage.get("output_tokens") or response.usage.get("completion_tokens")
                
                # Calculate actual cost if we have token counts
                if input_tokens and output_tokens and self._cost_estimator:
                    cost_info = self._cost_estimator.estimate_cost(
                        input_tokens, output_tokens, 
                        response.provider, response.model
                    )
                    actual_cost = cost_info.get("total_cost")
            
            # Determine error category (general category only, no sensitive details)
            error_category = None
            if error:
                error_type = type(error).__name__
                if "Connection" in error_type or "Timeout" in error_type:
                    error_category = "connection"
                elif "Auth" in error_type or "Permission" in error_type:
                    error_category = "authentication"
                elif "Rate" in error_type or "Quota" in error_type:
                    error_category = "rate_limit"
                else:
                    error_category = "other"
            
            # Record the usage (NO query content stored)
            self._usage_tracker.record_usage(
                provider=response.provider if response else self.get_current_provider(),
                model=response.model if response else getattr(self.current_provider, 'model', None),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                actual_cost=actual_cost,
                response_time_ms=response_time_ms,
                cache_hit=cache_hit,
                fallback_used=fallback_used,
                retry_count=retry_count,
                success=success,
                error_category=error_category
            )
        except Exception as e:
            # Never let analytics break the main functionality
            pass
    
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
    
    def get_usage_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get usage analytics and statistics.
        
        Returns:
            Dict with usage stats or None if analytics disabled
        """
        if not self._analytics_enabled or not self._usage_tracker:
            return None
        
        try:
            return self._usage_tracker.get_usage_stats()
        except Exception:
            return None
    
    def get_cost_breakdown(self, days: int = 7) -> Optional[Dict[str, Any]]:
        """
        Get cost breakdown for recent usage.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with cost analysis or None if analytics disabled
        """
        if not self._analytics_enabled or not self._usage_tracker:
            return None
        
        try:
            result = self._usage_tracker.get_cost_analysis()
            if isinstance(result, dict) and "error" in result:
                return result  # Return the error dict instead of None
            return result
        except Exception:
            return None
    
    def get_provider_comparison(self, input_tokens: int = 1000, 
                              output_tokens: int = 500) -> Optional[Dict[str, Any]]:
        """
        Compare costs across providers for sample token counts.
        
        Args:
            input_tokens: Sample input tokens for comparison
            output_tokens: Sample output tokens for comparison
            
        Returns:
            Dict with provider comparison or None if analytics disabled
        """
        if not self._analytics_enabled or not self._cost_estimator:
            return None
        
        try:
            return self._cost_estimator.compare_provider_costs(input_tokens, output_tokens)
        except Exception:
            return None
    
    
    def get_pricing_trends(self, provider: str = None) -> Optional[Dict[str, Any]]:
        """
        Get pricing trends for current or specified provider.
        
        Args:
            provider: Provider to analyze (defaults to current)
            
        Returns:
            Dict with trend analysis or None if analytics disabled
        """
        if not self._analytics_enabled:
            return None
        
        try:
            from .analytics.price_manager import PriceManager
            price_manager = PriceManager()
            
            target_provider = provider or self.get_current_provider()
            target_model = self.get_current_model()
            
            return price_manager.analyze_price_trends(target_provider, target_model)
        except Exception:
            return None
    
    def export_analytics(self, output_file: str, format: str = "json", days: int = 30):
        """
        Export analytics data for external analysis.
        
        Args:
            output_file: Path to output file
            format: Export format ("json" or "csv")
            days: Number of days to include
            
        Returns:
            Success message or None if analytics disabled
        """
        if not self._analytics_enabled or not self._usage_tracker:
            return None
        
        try:
            return self._usage_tracker.export_data(output_file, format, days)
        except Exception:
            return None