"""Main LLMClient class for llmswap."""

import os
import time
from typing import Optional, List, Dict, Any

from .response import LLMResponse
from .exceptions import ConfigurationError, AllProvidersFailedError
from .cache import InMemoryCache
from .security import safe_error_string


class LLMClient:
    """Simple client for any LLM provider."""

    def __init__(
        self,
        provider: str = "auto",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        fallback: bool = True,
        cache_enabled: bool = False,
        cache_ttl: int = 3600,
        cache_max_size_mb: int = 100,
        analytics_enabled: bool = False,
        workspace_enabled: bool = True,
    ):
        """Initialize LLM client.

        Args:
            provider: Provider name ("auto", "anthropic", "openai", "gemini", "cohere", "perplexity", "watsonx", "groq", "ollama", "xai", "sarvam")
            model: Model name (optional, uses provider defaults)
            api_key: API key (optional, uses environment variables)
            fallback: Enable fallback to other providers if primary fails
            cache_enabled: Enable response caching (default: False for security)
            cache_ttl: Default cache time-to-live in seconds (default: 3600)
            cache_max_size_mb: Maximum cache size in megabytes (default: 100)
            analytics_enabled: Enable privacy-first usage analytics (default: False)
            workspace_enabled: Enable workspace detection and learning tracking (default: True)
        """
        self.fallback_enabled = fallback
        self.current_provider = None

        # Provider priority order for auto-detection and fallback
        self.provider_order = [
            "anthropic",
            "openai",
            "gemini",
            "cohere",
            "perplexity",
            "watsonx",
            "groq",
            "ollama",
            "xai",
            "sarvam",
        ]

        # Initialize cache if enabled
        self._cache = (
            InMemoryCache(cache_max_size_mb, cache_ttl) if cache_enabled else None
        )

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

        # MCP integration (v5.3.0)
        self._mcp_servers = {}  # {server_name: MCPClient}
        self._mcp_tools = {}  # {tool_name: {server, definition, handler}}
        self._mcp_enabled = False

        # Workspace detection and learning tracking (v5.1.0)
        self.workspace_dir = None
        self.workspace_manager = None
        self.learnings_tracker = None

        if workspace_enabled:
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
                            self.learnings_tracker = LearningsTracker(
                                self.workspace_manager
                            )
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

    def _initialize_provider(
        self,
        provider_name: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """Initialize specific provider with config-based model defaults."""

        # Load model from config if not specified
        if not model:
            try:
                from .config import get_config

                config = get_config()
                model = config.get(f"provider.models.{provider_name}")

                if not model:
                    raise ConfigurationError(
                        f"No default model configured for {provider_name}. Check your config file or run: llmswap config set provider.models.{provider_name} <model>"
                    )
            except ImportError:
                raise ConfigurationError(
                    f"Configuration system not available. Cannot determine default model for {provider_name}."
                )

        # Lazy import - only import the provider we need
        if provider_name == "anthropic":
            from .providers import AnthropicProvider

            return AnthropicProvider(api_key, model)
        elif provider_name == "openai":
            from .providers import OpenAIProvider

            return OpenAIProvider(api_key, model)
        elif provider_name == "gemini":
            from .providers import GeminiProvider

            return GeminiProvider(api_key, model)
        elif provider_name == "ollama":
            from .providers import OllamaProvider

            return OllamaProvider(model=model)
        elif provider_name == "watsonx":
            from .providers import WatsonxProvider

            # Get required environment variables
            api_key = api_key or os.getenv("WATSONX_API_KEY")
            project_id = os.getenv("WATSONX_PROJECT_ID")
            url = os.getenv("WATSONX_URL", "https://eu-de.ml.cloud.ibm.com")

            if not api_key:
                raise ConfigurationError(
                    "WATSONX_API_KEY environment variable required"
                )
            if not project_id:
                raise ConfigurationError(
                    "WATSONX_PROJECT_ID environment variable required"
                )

            return WatsonxProvider(
                api_key=api_key, model=model, project_id=project_id, url=url
            )
        elif provider_name == "groq":
            from .providers import GroqProvider

            return GroqProvider(api_key, model)
        elif provider_name == "cohere":
            from .providers import CoherProvider

            return CoherProvider(api_key, model)
        elif provider_name == "perplexity":
            from .providers import PerplexityProvider

            return PerplexityProvider(api_key, model)
        elif provider_name == "xai":
            from .providers import XAIProvider

            return XAIProvider(api_key, model)
        elif provider_name == "sarvam":
            from .providers import SarvamProvider

            return SarvamProvider(api_key, model)
        else:
            raise ConfigurationError(f"Unknown provider: {provider_name}")

    def query(
        self,
        prompt: str,
        cache_context: Optional[Dict[str, Any]] = None,
        cache_ttl: Optional[int] = None,
        cache_bypass: bool = False,
        use_local_knowledge: bool = False,
        use_mcp: bool = False,
    ) -> LLMResponse:
        """Send query to current provider with optional fallback and caching.

        Args:
            prompt: Text prompt to send to LLM
            cache_context: Optional context dict (e.g., {"user_id": "123"}) for cache key
            cache_ttl: Override default cache TTL in seconds
            cache_bypass: Skip cache lookup and force fresh response
            use_local_knowledge: Use local knowledge base for context (future feature)
            use_mcp: Enable MCP tools (uses tools from connected MCP servers)

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
                    raw_response=cached_data.get("raw_response"),
                )
                # Mark as from cache
                response.from_cache = True

                # Record analytics for cached response (if enabled)
                self._record_analytics(
                    response,
                    start_time,
                    cache_hit,
                    fallback_used,
                    retry_count,
                    success=True,
                )

                return response

        try:
            # If MCP is enabled, use chat with tools instead of simple query
            if use_mcp and self._mcp_enabled:
                response = self.chat(
                    prompt, cache_context, cache_ttl, cache_bypass, use_mcp=True
                )
            else:
                response = self.current_provider.query(prompt)

            # Store in cache if enabled
            if self._cache:
                cache_key = InMemoryCache.create_cache_key(prompt, cache_context)
                cache_data = {
                    "content": response.content,
                    "provider": response.provider,
                    "model": response.model,
                    "usage": response.usage,
                    "raw_response": response.raw_response,
                }
                self._cache.set(cache_key, cache_data, cache_ttl)

            # Record analytics for successful response (if enabled)
            self._record_analytics(
                response,
                start_time,
                cache_hit,
                fallback_used,
                retry_count,
                success=True,
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
                    None,
                    start_time,
                    cache_hit,
                    fallback_used,
                    retry_count,
                    success=False,
                    error=e,
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
                            cache_key = InMemoryCache.create_cache_key(
                                prompt, cache_context
                            )
                            cache_data = {
                                "content": response.content,
                                "provider": response.provider,
                                "model": response.model,
                                "usage": response.usage,
                                "raw_response": response.raw_response,
                            }
                            self._cache.set(cache_key, cache_data, cache_ttl)

                        # Switch to working provider for future queries
                        self.current_provider = provider

                        # Record analytics for successful fallback (if enabled)
                        self._record_analytics(
                            response,
                            start_time,
                            cache_hit,
                            fallback_used,
                            retry_count,
                            success=True,
                        )

                        return response
                except:
                    continue

            # All providers failed - record analytics
            self._record_analytics(
                None,
                start_time,
                cache_hit,
                fallback_used,
                retry_count,
                success=False,
                error=e,
            )

            # All providers failed
            raise AllProvidersFailedError(
                f"All providers failed. Last error: {safe_error_string(e, None)}"
            )

    def _record_analytics(
        self,
        response: Optional[LLMResponse],
        start_time: float,
        cache_hit: bool,
        fallback_used: bool,
        retry_count: int,
        success: bool,
        error: Optional[Exception] = None,
    ):
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
                input_tokens = response.usage.get("input_tokens") or response.usage.get(
                    "prompt_tokens"
                )
                output_tokens = response.usage.get(
                    "output_tokens"
                ) or response.usage.get("completion_tokens")

                # Calculate actual cost if we have token counts
                if input_tokens and output_tokens and self._cost_estimator:
                    cost_info = self._cost_estimator.estimate_cost(
                        input_tokens, output_tokens, response.provider, response.model
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
                model=(
                    response.model
                    if response
                    else getattr(self.current_provider, "model", None)
                ),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                actual_cost=actual_cost,
                response_time_ms=response_time_ms,
                cache_hit=cache_hit,
                fallback_used=fallback_used,
                retry_count=retry_count,
                success=success,
                error_category=error_category,
            )
        except Exception as e:
            # Never let analytics break the main functionality
            pass

    def set_provider(
        self, provider: str, model: Optional[str] = None, api_key: Optional[str] = None
    ):
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

    def invalidate_cache(
        self, prompt: str, cache_context: Optional[Dict[str, Any]] = None
    ) -> bool:
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
        if (
            hasattr(self, "current_provider")
            and self.current_provider
            and hasattr(self.current_provider, "start_chat_session")
        ):
            self.current_provider.start_chat_session()

    def end_chat_session(self):
        """End llmswap chat session.

        Note: Conversation may continue to exist at provider level.
        """
        self._chat_session_active = False

        # End provider chat session if supported
        if (
            hasattr(self, "current_provider")
            and self.current_provider
            and hasattr(self.current_provider, "end_chat_session")
        ):
            self.current_provider.end_chat_session()

        self._current_chat_provider = None

    def is_chat_session_active(self) -> bool:
        """Check if chat session is active."""
        return self._chat_session_active

    def get_chat_session_info(self) -> Dict[str, Any]:
        """Get chat session information for CLI display."""
        import time

        session_id = None
        if hasattr(self, "current_provider") and self.current_provider:
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
            "duration_seconds": duration,
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
                    "provider": self._current_chat_provider,
                    "model": self.get_current_model(),
                    "session_cost": (
                        self.get_session_cost()
                        if hasattr(self, "get_session_cost")
                        else 0
                    ),
                    "session_tokens": (
                        self.get_session_tokens()
                        if hasattr(self, "get_session_tokens")
                        else 0
                    ),
                }

            # Step 2: End current chat session cleanly
            if self._chat_session_active:
                self.end_chat_session()

            # Step 3: Reset session-specific analytics
            if hasattr(self, "_session_tokens"):
                self._session_tokens = 0
            if hasattr(self, "_session_cost"):
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
                "success": True,
                "previous_session": final_stats,
                "new_provider": new_provider,
                "new_model": new_model,
                "new_pricing": new_pricing,
            }
        except Exception as e:
            return {"success": False, "error": safe_error_string(e, None)}

    def chat(
        self,
        message,  # Can be str or list of messages
        cache_context: Optional[Dict[str, Any]] = None,
        cache_ttl: Optional[int] = None,
        cache_bypass: bool = False,
        tools: Optional[List[Any]] = None,
        use_mcp: bool = False,
    ) -> LLMResponse:
        """Send message with provider-native conversation context.

        Provider handles all conversation context and history.
        No local storage - completely privacy-first approach.

        Args:
            message: User message string OR list of conversation messages
            cache_context: Optional context dict for cache key
            cache_ttl: Override default cache TTL in seconds
            cache_bypass: Skip cache lookup and force fresh response
            tools: Optional list of Tool objects for function calling
            use_mcp: Enable MCP tools (uses tools from connected MCP servers)

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

        # Merge tools: provided tools + MCP tools (if enabled)
        all_tools = tools or []
        if use_mcp and self._mcp_enabled:
            # Add MCP tools to available tools
            for tool_name, tool_info in self._mcp_tools.items():
                all_tools.append(tool_info["definition"])

        # Always use standard chat method with full conversation history
        if hasattr(self.current_provider, "chat"):
            # Standard chat method - send full conversation history
            if all_tools and hasattr(self.current_provider, "chat_with_tools"):
                # Provider supports tool calling
                response = self.current_provider.chat_with_tools(messages, all_tools)
            else:
                # Standard chat without tools
                response = self.current_provider.chat(messages)
        else:
            # Fallback: single query (no conversation context)
            if isinstance(message, str):
                response = self.current_provider.query(message)
            else:
                # Extract last user message for query fallback
                last_user_msg = next(
                    (
                        msg["content"]
                        for msg in reversed(messages)
                        if msg["role"] == "user"
                    ),
                    "",
                )
                response = self.current_provider.query(last_user_msg)

        # Extract tool calls from metadata and expose as direct attribute
        if hasattr(response, "metadata") and response.metadata:
            tool_calls = response.metadata.get("tool_calls")
            if tool_calls:
                # Move tool calls from metadata to direct attribute for easy access
                response.tool_calls = tool_calls

                # Execute MCP tools if requested and enabled
                if use_mcp and self._mcp_enabled:
                    self._handle_mcp_tool_calls(tool_calls, messages, all_tools)

        # Update session-specific analytics
        if self._chat_session_active and hasattr(response, "usage") and response.usage:
            # Track tokens for this session
            tokens = response.usage.get("total_tokens", 0)
            self._session_tokens += tokens

            # Calculate and track cost for this session
            if self._analytics_enabled and self._cost_estimator:
                provider = self.get_current_provider()
                model = self.get_current_model()
                input_tokens = response.usage.get("prompt_tokens", 0)
                output_tokens = response.usage.get("completion_tokens", 0)

                if input_tokens and output_tokens:
                    cost_info = self._cost_estimator.estimate_cost(
                        provider, model, input_tokens, output_tokens
                    )
                    if cost_info and "total" in cost_info:
                        self._session_cost += cost_info["total"]

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

    def get_provider_comparison(
        self, input_tokens: int = 1000, output_tokens: int = 500
    ) -> Optional[Dict[str, Any]]:
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
            return self._cost_estimator.compare_provider_costs(
                input_tokens, output_tokens
            )
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

    # ========================================================================
    # MCP Integration (v5.3.0)
    # ========================================================================

    def _handle_mcp_tool_calls(
        self, tool_calls: List[Any], messages: List[Dict[str, Any]], tools: List[Any]
    ) -> None:
        """
        Handle tool calls from LLM - execute MCP tools if applicable.

        Args:
            tool_calls: Tool calls from LLM response
            messages: Conversation messages
            tools: Available tools
        """
        for tool_call in tool_calls:
            tool_name = (
                tool_call.get("name")
                if isinstance(tool_call, dict)
                else getattr(tool_call, "name", None)
            )
            tool_args = (
                tool_call.get("arguments", {})
                if isinstance(tool_call, dict)
                else getattr(tool_call, "arguments", {})
            )

            # Check if this is an MCP tool
            if tool_name in self._mcp_tools:
                tool_info = self._mcp_tools[tool_name]

                try:
                    # Execute the MCP tool
                    result = tool_info["handler"](tool_args)

                    # Store result in metadata (optional - for future multi-turn conversations)
                    # The provider may handle this differently

                except Exception as e:
                    # Log error but don't fail the entire response
                    pass

    def add_mcp_server(
        self,
        name: str,
        url: Optional[str] = None,
        command: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        transport: str = "auto",
    ) -> None:
        """
        Add an MCP server for tool discovery and execution.

        Args:
            name: Unique name for this MCP server
            url: URL for remote MCP server (SSE or HTTP)
            command: Command to start local MCP server (stdio)
            headers: Optional HTTP headers (for remote servers)
            transport: Transport type ("auto", "stdio", "sse", "http")

        Raises:
            ValueError: If invalid configuration
            MCPConnectionError: If connection fails

        Example:
            # Remote MCP server
            client.add_mcp_server(
                "github",
                url="https://api.github.com/mcp",
                headers={"Authorization": "Bearer token"}
            )

            # Local MCP server
            client.add_mcp_server(
                "database",
                command=["python", "db_mcp_server.py"]
            )
        """
        from .mcp import MCPClient
        from .mcp.exceptions import MCPError

        # Validate inputs
        if name in self._mcp_servers:
            raise ValueError(f"MCP server '{name}' already exists")

        if not url and not command:
            raise ValueError("Must provide either 'url' or 'command'")

        if url and command:
            raise ValueError("Cannot provide both 'url' and 'command'")

        try:
            # Create MCP client
            mcp_client = MCPClient(client_name="llmswap", client_version="5.5.2")

            # Connect based on transport type
            if command:
                # stdio transport (local server)
                mcp_client.connect_stdio(command)

            elif url:
                # Determine transport from URL or use specified
                if transport == "auto":
                    if "/events" in url or "sse" in url.lower():
                        transport = "sse"
                    else:
                        transport = "http"

                if transport == "sse":
                    from .mcp.transports import SSETransport

                    mcp_transport = SSETransport(url, headers=headers)
                    mcp_transport.connect()
                    # Set transport on client
                    mcp_client.transport = mcp_transport
                    mcp_client._initialized = True

                elif transport == "http":
                    from .mcp.transports import HTTPTransport

                    mcp_transport = HTTPTransport(url, headers=headers)
                    mcp_transport.connect()
                    # Set transport on client
                    mcp_client.transport = mcp_transport
                    mcp_client._initialized = True

                else:
                    raise ValueError(f"Invalid transport: {transport}")

            # Store MCP client
            self._mcp_servers[name] = mcp_client

            # Discover and register tools from this server
            self._discover_mcp_tools(name)

            self._mcp_enabled = True

        except MCPError as e:
            raise
        except Exception as e:
            raise MCPError(f"Failed to add MCP server '{name}': {e}")

    def _discover_mcp_tools(self, server_name: str) -> None:
        """
        Discover tools from an MCP server and register them.

        Args:
            server_name: Name of the MCP server
        """
        from .tools.schema import Tool

        mcp_client = self._mcp_servers.get(server_name)
        if not mcp_client:
            return

        try:
            # Get tools from MCP server
            mcp_tools = mcp_client.list_tools()

            # Convert each MCP tool to llmswap Tool format
            for mcp_tool in mcp_tools:
                tool_name = mcp_tool.get("name")
                if not tool_name:
                    continue

                # Create Tool object
                tool = Tool(
                    name=tool_name,
                    description=mcp_tool.get("description", ""),
                    parameters=mcp_tool.get("inputSchema", {}).get("properties", {}),
                    required=mcp_tool.get("inputSchema", {}).get("required", []),
                )

                # Store tool with handler
                self._mcp_tools[tool_name] = {
                    "server": server_name,
                    "definition": tool,
                    "mcp_tool": mcp_tool,
                    "handler": lambda args, srv=server_name, tn=tool_name: self._execute_mcp_tool(
                        srv, tn, args
                    ),
                }

        except Exception as e:
            # Log but don't fail - partial tool discovery is okay
            pass

    def _execute_mcp_tool(
        self, server_name: str, tool_name: str, arguments: Dict[str, Any]
    ) -> Any:
        """
        Execute a tool on an MCP server.

        Args:
            server_name: Name of MCP server
            tool_name: Name of tool to execute
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        from .mcp.exceptions import MCPError

        mcp_client = self._mcp_servers.get(server_name)
        if not mcp_client:
            raise MCPError(f"MCP server '{server_name}' not found")

        try:
            result = mcp_client.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            raise MCPError(f"Tool execution failed: {e}")

    def list_mcp_servers(self) -> List[str]:
        """
        List all connected MCP servers.

        Returns:
            List of MCP server names
        """
        return list(self._mcp_servers.keys())

    def list_mcp_tools(self, server_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available MCP tools.

        Args:
            server_name: Optional server name to filter by

        Returns:
            List of tool definitions
        """
        tools = []

        for tool_name, tool_info in self._mcp_tools.items():
            if server_name and tool_info["server"] != server_name:
                continue

            tool = tool_info["definition"]
            tools.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "server": tool_info["server"],
                    "parameters": tool.parameters,
                    "required": tool.required,
                }
            )

        return tools

    def remove_mcp_server(self, name: str) -> None:
        """
        Remove an MCP server and its tools.

        Args:
            name: Name of MCP server to remove
        """
        if name not in self._mcp_servers:
            raise ValueError(f"MCP server '{name}' not found")

        # Close connection
        mcp_client = self._mcp_servers[name]
        try:
            mcp_client.close()
        except:
            pass

        # Remove server
        del self._mcp_servers[name]

        # Remove associated tools
        tools_to_remove = [
            tool_name
            for tool_name, tool_info in self._mcp_tools.items()
            if tool_info["server"] == name
        ]

        for tool_name in tools_to_remove:
            del self._mcp_tools[tool_name]

        # Disable MCP if no servers left
        if not self._mcp_servers:
            self._mcp_enabled = False

    def format_tool_results(
        self,
        tool_calls: List[Any],
        tool_results: List[Dict[str, Any]],
        original_response: Optional[LLMResponse] = None,
    ) -> List[Dict[str, Any]]:
        """
        Format tool results for conversation history based on current provider.

        Different providers require different message formats for tool results.
        This method handles the provider-specific formatting automatically.

        Args:
            tool_calls: Original tool calls from LLM response
            tool_results: Executed tool results as list of dicts with 'content' key
            original_response: Original LLM response (optional, used for some providers)

        Returns:
            List of messages to append to conversation history

        Example:
            tool_calls = response.tool_calls
            results = [{"content": execute_tool(tc)} for tc in tool_calls]
            messages = client.format_tool_results(tool_calls, results, response)
            conversation_history.extend(messages)
        """
        provider = self.get_current_provider()
        messages = []

        if provider == "anthropic":
            # Anthropic requires content blocks format
            # 1. Add assistant message with tool_use blocks
            raw_response = None
            if original_response:
                # Try to get raw_response from attribute or metadata
                if (
                    hasattr(original_response, "raw_response")
                    and original_response.raw_response
                ):
                    raw_response = original_response.raw_response
                elif (
                    hasattr(original_response, "metadata")
                    and original_response.metadata
                ):
                    raw_response = original_response.metadata.get("raw_response")

            if raw_response and hasattr(raw_response, "content"):
                messages.append({"role": "assistant", "content": raw_response.content})
            else:
                # Fallback: construct tool_use blocks manually
                tool_use_blocks = []
                for i, tool_call in enumerate(tool_calls):
                    if isinstance(tool_call, dict):
                        tool_use_blocks.append(
                            {
                                "type": "tool_use",
                                "id": tool_call.get("id", f"tool_{i}"),
                                "name": tool_call.get("name", "unknown"),
                                "input": tool_call.get("arguments", {}),
                            }
                        )
                    else:
                        tool_use_blocks.append(
                            {
                                "type": "tool_use",
                                "id": getattr(tool_call, "id", f"tool_{i}"),
                                "name": getattr(tool_call, "name", "unknown"),
                                "input": getattr(tool_call, "arguments", {}),
                            }
                        )

                messages.append({"role": "assistant", "content": tool_use_blocks})

            # 2. Add user message with tool_result blocks
            tool_result_blocks = []
            for i, (tool_call, result) in enumerate(zip(tool_calls, tool_results)):
                if isinstance(tool_call, dict):
                    tool_id = tool_call.get("id", f"tool_{i}")
                else:
                    tool_id = getattr(tool_call, "id", f"tool_{i}")

                result_content = (
                    result.get("content", result)
                    if isinstance(result, dict)
                    else result
                )

                tool_result_blocks.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": str(result_content),
                    }
                )

            messages.append({"role": "user", "content": tool_result_blocks})

        elif provider in ["openai", "groq", "xai"]:
            # OpenAI-compatible format: tool role messages
            # 1. Add assistant message with tool_calls
            openai_tool_calls = []
            for i, tool_call in enumerate(tool_calls):
                if isinstance(tool_call, dict):
                    openai_tool_calls.append(tool_call)
                else:
                    # Convert ToolCall object to dict
                    import json

                    args_str = json.dumps(getattr(tool_call, "arguments", {}))
                    openai_tool_calls.append(
                        {
                            "id": getattr(tool_call, "id", f"call_{i}"),
                            "type": "function",
                            "function": {
                                "name": getattr(tool_call, "name", "unknown"),
                                "arguments": args_str,
                            },
                        }
                    )

            messages.append(
                {"role": "assistant", "content": None, "tool_calls": openai_tool_calls}
            )

            # 2. Add tool messages with results
            for i, (tool_call, result) in enumerate(zip(tool_calls, tool_results)):
                if isinstance(tool_call, dict):
                    tool_id = tool_call.get("id", f"call_{i}")
                else:
                    tool_id = getattr(tool_call, "id", f"call_{i}")

                result_content = (
                    result.get("content", result)
                    if isinstance(result, dict)
                    else result
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_id,
                        "content": str(result_content),
                    }
                )

        elif provider == "gemini":
            # Gemini format: function role with parts
            # 1. Add model message with function_call
            function_calls = []
            for tool_call in tool_calls:
                if isinstance(tool_call, dict):
                    function_calls.append(
                        {
                            "function_call": {
                                "name": tool_call.get("name", "unknown"),
                                "args": tool_call.get("arguments", {}),
                            }
                        }
                    )
                else:
                    function_calls.append(
                        {
                            "function_call": {
                                "name": getattr(tool_call, "name", "unknown"),
                                "args": getattr(tool_call, "arguments", {}),
                            }
                        }
                    )

            messages.append({"role": "model", "parts": function_calls})

            # 2. Add function messages with results
            for tool_call, result in zip(tool_calls, tool_results):
                if isinstance(tool_call, dict):
                    tool_name = tool_call.get("name", "unknown")
                else:
                    tool_name = getattr(tool_call, "name", "unknown")

                result_content = (
                    result.get("content", result)
                    if isinstance(result, dict)
                    else result
                )

                # Gemini expects object, not string
                if isinstance(result_content, str):
                    try:
                        import json

                        result_obj = json.loads(result_content)
                    except:
                        result_obj = {"result": result_content}
                else:
                    result_obj = result_content

                messages.append(
                    {
                        "role": "function",
                        "parts": [
                            {
                                "function_response": {
                                    "name": tool_name,
                                    "response": result_obj,
                                }
                            }
                        ],
                    }
                )

        else:
            # Unknown provider - use OpenAI format as fallback
            import json

            openai_tool_calls = []
            for i, tool_call in enumerate(tool_calls):
                if isinstance(tool_call, dict):
                    openai_tool_calls.append(tool_call)
                else:
                    args_str = json.dumps(getattr(tool_call, "arguments", {}))
                    openai_tool_calls.append(
                        {
                            "id": getattr(tool_call, "id", f"call_{i}"),
                            "type": "function",
                            "function": {
                                "name": getattr(tool_call, "name", "unknown"),
                                "arguments": args_str,
                            },
                        }
                    )

            messages.append(
                {"role": "assistant", "content": None, "tool_calls": openai_tool_calls}
            )

            for i, (tool_call, result) in enumerate(zip(tool_calls, tool_results)):
                if isinstance(tool_call, dict):
                    tool_id = tool_call.get("id", f"call_{i}")
                else:
                    tool_id = getattr(tool_call, "id", f"call_{i}")

                result_content = (
                    result.get("content", result)
                    if isinstance(result, dict)
                    else result
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_id,
                        "content": str(result_content),
                    }
                )

        return messages

        try:
            return self._usage_tracker.export_data(output_file, format, days)
        except Exception:
            return None
