"""Async client for llmswap with streaming support."""

import os
import time
from typing import Optional, List, AsyncIterator
import asyncio

from .response import LLMResponse
from .exceptions import ConfigurationError, AllProvidersFailedError
from .logging_handler import LLMLogger


class AsyncLLMClient:
    """Async client for any LLM provider with streaming support."""
    
    def __init__(self, 
                 provider: str = "auto",
                 model: Optional[str] = None,
                 api_key: Optional[str] = None,
                 fallback: bool = True,
                 log_file: Optional[str] = None,
                 log_level: str = "info"):
        """Initialize async LLM client.
        
        Args:
            provider: Provider name ("auto", "anthropic", "openai", "gemini", "watsonx", "ollama")
            model: Model name (optional, uses provider defaults)
            api_key: API key (optional, uses environment variables)
            fallback: Enable fallback to other providers if primary fails
            log_file: Path to log file (optional)
            log_level: Logging level (debug, info, warning, error)
        """
        self.fallback_enabled = fallback
        self.current_provider = None
        self.model = model
        self.api_key = api_key
        
        # Initialize logging if requested
        self.logger = LLMLogger(log_file, log_level) if log_file else None
        
        # Provider priority order for auto-detection and fallback
        self.provider_order = ["anthropic", "openai", "gemini", "watsonx", "ollama"]
        
        # Import async providers lazily to avoid circular imports
        from .async_providers import get_async_provider
        self.get_async_provider = get_async_provider
        
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
        """Initialize specific async provider."""
        return self.get_async_provider(provider_name, api_key, model)
    
    async def query(self, prompt: str) -> LLMResponse:
        """Send async query to current provider with optional fallback.
        
        Args:
            prompt: Text prompt to send to LLM
            
        Returns:
            LLMResponse with content, metadata, and usage info
        """
        if not self.current_provider:
            raise ConfigurationError("No provider initialized")
        
        provider_name = self.current_provider.provider_name
        model = self.current_provider.model
        
        # Log request if logging enabled
        if self.logger:
            self.logger.log_request(provider_name, model, prompt)
        
        start_time = time.time()
        
        try:
            response = await self.current_provider.query(prompt)
            
            # Log successful response
            if self.logger:
                latency = time.time() - start_time
                self.logger.log_response(
                    provider_name, 
                    model, 
                    response.content,
                    latency
                )
            
            return response
            
        except Exception as e:
            # Log error
            if self.logger:
                self.logger.log_error(provider_name, str(e))
            
            if not self.fallback_enabled:
                raise
            
            # Try fallback providers
            for fallback_name in self.provider_order:
                if fallback_name == provider_name:
                    continue  # Skip current provider
                
                try:
                    fallback_provider = self._initialize_provider(fallback_name)
                    if not fallback_provider.is_available():
                        continue
                    
                    # Log fallback attempt
                    if self.logger:
                        self.logger.log_request(fallback_name, fallback_provider.model, prompt)
                    
                    start_time = time.time()
                    response = await fallback_provider.query(prompt)
                    
                    # Log successful fallback
                    if self.logger:
                        latency = time.time() - start_time
                        self.logger.log_response(
                            fallback_name,
                            fallback_provider.model,
                            response.content,
                            latency
                        )
                    
                    # Update current provider for next request
                    self.current_provider = fallback_provider
                    return response
                    
                except Exception:
                    continue
            
            raise AllProvidersFailedError(f"All providers failed. Last error: {e}")
    
    async def stream(self, prompt: str) -> AsyncIterator[str]:
        """Stream response from LLM provider.
        
        Args:
            prompt: Text prompt to send to LLM
            
        Yields:
            Chunks of response text as they arrive
        """
        if not self.current_provider:
            raise ConfigurationError("No provider initialized")
        
        provider_name = self.current_provider.provider_name
        model = self.current_provider.model
        
        # Check if provider supports streaming
        if not hasattr(self.current_provider, 'stream'):
            raise NotImplementedError(f"Provider {provider_name} doesn't support streaming yet")
        
        # Log stream start
        if self.logger:
            self.logger.log_stream_start(provider_name, model)
        
        start_time = time.time()
        chunk_count = 0
        
        try:
            async for chunk in self.current_provider.stream(prompt):
                chunk_count += 1
                yield chunk
            
            # Log stream completion
            if self.logger:
                latency = time.time() - start_time
                self.logger.log_stream_end(provider_name, model, chunk_count, latency)
                
        except Exception as e:
            # Log error
            if self.logger:
                self.logger.log_error(provider_name, f"Stream error: {str(e)}")
            raise
    
    def set_provider(self, provider: str, model: Optional[str] = None, api_key: Optional[str] = None):
        """Switch to a different provider.
        
        Args:
            provider: Provider name
            model: Optional model override
            api_key: Optional API key override
        """
        self.current_provider = self._initialize_provider(provider, model, api_key)
        self.model = model
    
    def get_current_provider(self) -> Optional[str]:
        """Get name of current provider."""
        if self.current_provider:
            return self.current_provider.provider_name
        return None
    
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