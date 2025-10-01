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
        
        # Provider-native conversation management (v5.0.0)
        # No local conversation storage - providers handle context natively
        self._chat_session_active = False
        self._current_chat_provider = None
        
        # Session-specific analytics (reset on provider switch)
        self._session_tokens = 0
        self._session_cost = 0.0
        self._session_start_time = None
        
        # Workspace detection and learning tracking (v5.1.0)
        self.workspace_dir = None
        self.workspace_manager = None
        self.learnings_tracker = None
        
        try:
            from .workspace.detector import WorkspaceDetector
            from .workspace.manager import WorkspaceManager
            from .workspace.learnings_tracker import LearningsTracker
            from .workspace.registry import WorkspaceRegistry
            from pathlib import Path
            
            self.workspace_dir = WorkspaceDetector.detect()
            
            if self.workspace_dir:
                workspace_id = self.workspace_dir.name
                registry = WorkspaceRegistry()
                all_workspaces = registry.list_workspaces()
                
                for ws in all_workspaces:
                    if ws["workspace_id"] == workspace_id:
                        project_path = Path(ws["project_path"])
                        self.workspace_manager = WorkspaceManager(project_path)
                        self.learnings_tracker = LearningsTracker(self.workspace_manager)
                        break
        except Exception:
            pass
        
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
        """Initialize specific provider with config-based model defaults."""
        
        # Load model from config if not specified
        if not model:
            try:
                from .config import get_config
                config = get_config()
                model = config.get(f'provider.models.{provider_name}')
                
                if not model:
                    raise ConfigurationError(f"No default model configured for {provider_name}. Check your config file or run: llmswap config set provider.models.{provider_name} <model>")
            except ImportError:
                raise ConfigurationError(f"Configuration system not available. Cannot determine default model for {provider_name}.")
        
        if provider_name == "anthropic":
            return AnthropicProvider(api_key, model)
        elif provider_name == "openai":
            return OpenAIProvider(api_key, model)
        elif provider_name == "gemini":
            return GeminiProvider(api_key, model)
        elif provider_name == "ollama":
            return OllamaProvider(model=model)
        elif provider_name == "watsonx":
            # Get required environment variables
            api_key = api_key or os.getenv("WATSONX_API_KEY")
            project_id = os.getenv("WATSONX_PROJECT_ID")
            url = os.getenv("WATSONX_URL", "https://eu-de.ml.cloud.ibm.com")
            
            if not api_key:
                raise ConfigurationError("WATSONX_API_KEY environment variable required")
            if not project_id:
                raise ConfigurationError("WATSONX_PROJECT_ID environment variable required")
            
            return WatsonxProvider(api_key=api_key, model=model, project_id=project_id, url=url)
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
            
            # Track learnings if workspace exists (v5.1.0)
            if self.learnings_tracker and not cache_hit:
                try:
                    self.learnings_tracker.extract_and_save(prompt, response.content)
                    if self.workspace_manager:
                        self.workspace_manager.increment_query_count()
                except Exception:
                    pass
            
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
            test_provider = self._initialize_provider(provider, None, None)
            return test_provider.is_available()
        except:
            return False
    
    def get_available_providers(self) -> List[str]:
        """Get list of available and configured providers."""
        available = []
        for provider_name in self.provider_order:
            if self.is_provider_available(provider_name):
                available.append(provider_name)
        return available
    
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
    
    def start_chat_session(self):
        """Start a provider-native chat session.
        
        No local conversation storage - provider handles all context.
        Session state only tracked for CLI UX purposes.
        """
        import time
        self._chat_session_active = True
        self._session_tokens = 0
        self._session_cost = 0.0
        self._session_start_time = time.time()
        
        # Get current provider safely
        try:
            self._current_chat_provider = self.get_current_provider()
        except:
            self._current_chat_provider = "none"
        
        # Initialize provider chat session if supported
        if hasattr(self, 'current_provider') and self.current_provider and hasattr(self.current_provider, 'start_chat_session'):
            self.current_provider.start_chat_session()
    
    def end_chat_session(self):
        """End llmswap chat session.
        
        Note: Conversation may continue to exist at provider level.
        """
        self._chat_session_active = False
        
        # End provider chat session if supported
        if hasattr(self, 'current_provider') and self.current_provider and hasattr(self.current_provider, 'end_chat_session'):
            self.current_provider.end_chat_session()
        
        self._current_chat_provider = None
    
    def is_chat_session_active(self) -> bool:
        """Check if chat session is active."""
        return self._chat_session_active
    
    def get_chat_session_info(self) -> Dict[str, Any]:
        """Get chat session information for CLI display."""
        import time
        session_id = None
        if hasattr(self, 'current_provider') and self.current_provider:
            session_id = id(self.current_provider)
        
        duration = 0
        if self._session_start_time:
            duration = int(time.time() - self._session_start_time)
            
        return {
            "active": self._chat_session_active,
            "provider": self._current_chat_provider,
            "session_id": session_id,
            "session_tokens": self._session_tokens,
            "session_cost": self._session_cost,
            "duration_seconds": duration
        }
    
    def get_session_cost(self) -> float:
        """Get cost for current chat session only."""
        return self._session_cost
    
    def get_session_tokens(self) -> int:
        """Get token count for current chat session only."""
        return self._session_tokens
    
    def switch_provider_safe(self, new_provider: str) -> Dict[str, Any]:
        """Safely switch providers without context transfer.
        
        LEGAL COMPLIANCE: This method ensures no conversation context
        is transferred between providers to comply with Terms of Service
        and avoid copyright/legal issues.
        
        Args:
            new_provider: Name of the new provider to switch to
            
        Returns:
            Dict with switch status and session info
        """
        try:
            # Step 1: Capture final stats from current provider session
            final_stats = None
            if self._chat_session_active and self._analytics_enabled:
                final_stats = {
                    'provider': self._current_chat_provider,
                    'model': self.get_current_model(),
                    'session_cost': self.get_session_cost() if hasattr(self, 'get_session_cost') else 0,
                    'session_tokens': self.get_session_tokens() if hasattr(self, 'get_session_tokens') else 0
                }
            
            # Step 2: End current chat session cleanly
            if self._chat_session_active:
                self.end_chat_session()
            
            # Step 3: Reset session-specific analytics
            if hasattr(self, '_session_tokens'):
                self._session_tokens = 0
            if hasattr(self, '_session_cost'):
                self._session_cost = 0
            
            # Step 4: Switch to new provider
            self.set_provider(new_provider)
            
            # Step 5: Start fresh chat session with new provider
            # NO context is transferred - completely fresh start
            self.start_chat_session()
            
            # Step 6: Update analytics with new provider info
            new_model = self.get_current_model()
            new_pricing = None
            # TODO: Re-enable pricing info when analytics module is ready
            # if self._analytics_enabled and self._cost_estimator:
            #     from .analytics.price_manager import PROVIDER_PRICING
            #     provider_key = new_provider.lower()
            #     if provider_key in PROVIDER_PRICING and new_model in PROVIDER_PRICING[provider_key]:
            #         new_pricing = PROVIDER_PRICING[provider_key][new_model]
            
            return {
                'success': True,
                'previous_session': final_stats,
                'new_provider': new_provider,
                'new_model': new_model,
                'new_pricing': new_pricing
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def chat(self, 
             message,  # Can be str or list of messages
             cache_context: Optional[Dict[str, Any]] = None,
             cache_ttl: Optional[int] = None,
             cache_bypass: bool = False) -> LLMResponse:
        """Send message with provider-native conversation context.
        
        Provider handles all conversation context and history.
        No local storage - completely privacy-first approach.
        
        Args:
            message: User message string OR list of conversation messages
            cache_context: Optional context dict for cache key
            cache_ttl: Override default cache TTL in seconds
            cache_bypass: Skip cache lookup and force fresh response
            
        Returns:
            LLMResponse with content, metadata, and usage info
        """
        # Handle both string messages and conversation history
        if isinstance(message, str):
            # Single message - convert to conversation format
            messages = [{"role": "user", "content": message}]
        elif isinstance(message, list):
            # Full conversation history provided
            messages = message
        else:
            raise ValueError("message must be either a string or list of messages")
        
        # Always use standard chat method with full conversation history
        if hasattr(self.current_provider, 'chat'):
            # Standard chat method - send full conversation history
            response = self.current_provider.chat(messages)
        else:
            # Fallback: single query (no conversation context)
            if isinstance(message, str):
                response = self.current_provider.query(message)
            else:
                # Extract last user message for query fallback
                last_user_msg = next((msg['content'] for msg in reversed(messages) if msg['role'] == 'user'), "")
                response = self.current_provider.query(last_user_msg)
        
        # Update session-specific analytics
        if self._chat_session_active and hasattr(response, 'usage') and response.usage:
            # Track tokens for this session
            tokens = response.usage.get('total_tokens', 0)
            self._session_tokens += tokens
            
            # Calculate and track cost for this session
            if self._analytics_enabled and self._cost_estimator:
                provider = self.get_current_provider()
                model = self.get_current_model()
                input_tokens = response.usage.get('prompt_tokens', 0)
                output_tokens = response.usage.get('completion_tokens', 0)
                
                if input_tokens and output_tokens:
                    cost_info = self._cost_estimator.estimate_cost(
                        provider, model, input_tokens, output_tokens
                    )
                    if cost_info and 'total' in cost_info:
                        self._session_cost += cost_info['total']
        
        # No local conversation storage - provider handles everything
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