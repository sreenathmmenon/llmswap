"""Async providers for different LLM services."""

import os
import time
import json
from typing import Optional, AsyncIterator
from abc import ABC, abstractmethod

from .response import LLMResponse
from .exceptions import ConfigurationError, ProviderError


class AsyncBaseProvider(ABC):
    """Base class for async LLM providers."""
    
    def __init__(self, api_key: Optional[str], model: Optional[str]):
        """Initialize provider with API key and model."""
        self.api_key = api_key
        self.model = model or self.default_model
        self.provider_name = self.__class__.__name__.replace("Async", "").replace("Provider", "").lower()
    
    @abstractmethod
    async def query(self, prompt: str) -> LLMResponse:
        """Send query to LLM provider."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass
    
    async def stream(self, prompt: str) -> AsyncIterator[str]:
        """Stream response from provider. Override in subclasses that support it."""
        raise NotImplementedError(f"{self.provider_name} doesn't support streaming yet")


class AsyncOpenAIProvider(AsyncBaseProvider):
    """Async provider for OpenAI models."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.default_model = "gpt-3.5-turbo"
        
        # Use provided key or get from environment
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ConfigurationError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
        
        super().__init__(api_key, model)
        
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=self.api_key)
        except ImportError:
            raise ConfigurationError("openai package not installed. Run: pip install openai")
    
    async def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000
            )
            
            latency = time.time() - start_time
            content = response.choices[0].message.content
            
            return LLMResponse(
                content=content,
                provider="openai", 
                model=self.model,
                latency=latency,
                metadata={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "finish_reason": response.choices[0].finish_reason,
                }
            )
        except Exception as e:
            raise ProviderError("openai", str(e))
    
    async def stream(self, prompt: str) -> AsyncIterator[str]:
        """Stream response from OpenAI."""
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise ProviderError("openai", f"Stream error: {str(e)}")
    
    def is_available(self) -> bool:
        return bool(self.api_key)


class AsyncAnthropicProvider(AsyncBaseProvider):
    """Async provider for Anthropic Claude models."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.default_model = "claude-3-sonnet-20240229"
        
        # Use provided key or get from environment
        if not api_key:
            api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not api_key:
            raise ConfigurationError("Anthropic API key required. Set ANTHROPIC_API_KEY environment variable.")
        
        super().__init__(api_key, model)
        
        try:
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=self.api_key)
        except ImportError:
            raise ConfigurationError("anthropic package not installed. Run: pip install anthropic")
    
    async def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            latency = time.time() - start_time
            content = response.content[0].text
            
            return LLMResponse(
                content=content,
                provider="anthropic",
                model=self.model,
                latency=latency,
                metadata={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "stop_reason": response.stop_reason,
                }
            )
        except Exception as e:
            raise ProviderError("anthropic", str(e))
    
    async def stream(self, prompt: str) -> AsyncIterator[str]:
        """Stream response from Anthropic."""
        try:
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            raise ProviderError("anthropic", f"Stream error: {str(e)}")
    
    def is_available(self) -> bool:
        return bool(self.api_key)


class AsyncGeminiProvider(AsyncBaseProvider):
    """Async provider for Google Gemini models."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.default_model = "gemini-1.5-flash"
        
        # Use provided key or get from environment
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ConfigurationError("Gemini API key required. Set GEMINI_API_KEY environment variable.")
        
        super().__init__(api_key, model)
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.genai = genai
            self.model_instance = genai.GenerativeModel(self.model)
        except ImportError:
            raise ConfigurationError("google-generativeai package not installed. Run: pip install google-generativeai")
    
    async def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            # Google's SDK doesn't have true async yet, so we run in executor
            import asyncio
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                self.model_instance.generate_content,
                prompt
            )
            
            latency = time.time() - start_time
            content = response.text
            
            return LLMResponse(
                content=content,
                provider="gemini",
                model=self.model,
                latency=latency,
                metadata={}
            )
        except Exception as e:
            raise ProviderError("gemini", str(e))
    
    def is_available(self) -> bool:
        return bool(self.api_key)


class AsyncOllamaProvider(AsyncBaseProvider):
    """Async provider for local Ollama models."""
    
    def __init__(self, model: str = "llama3", url: str = "http://localhost:11434"):
        super().__init__(None, model)
        self.url = url
        self.default_model = "llama3"
        
        try:
            import httpx
            self.httpx = httpx
        except ImportError:
            raise ConfigurationError("httpx package not installed. Run: pip install httpx")
    
    async def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            async with self.httpx.AsyncClient() as client:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                    }
                }
                
                response = await client.post(
                    f"{self.url}/api/generate",
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                
                latency = time.time() - start_time
                content = result.get('response', 'No response generated')
                
                return LLMResponse(
                    content=content,
                    provider="ollama",
                    model=self.model,
                    latency=latency,
                    metadata={
                        "total_duration": result.get("total_duration"),
                        "load_duration": result.get("load_duration"),
                    }
                )
        except Exception as e:
            raise ProviderError("ollama", str(e))
    
    async def stream(self, prompt: str) -> AsyncIterator[str]:
        """Stream response from Ollama."""
        try:
            async with self.httpx.AsyncClient() as client:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                }
                
                async with client.stream(
                    "POST",
                    f"{self.url}/api/generate",
                    json=payload,
                    timeout=60.0
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            data = json.loads(line)
                            if 'response' in data:
                                yield data['response']
                            if data.get('done', False):
                                break
                                
        except Exception as e:
            raise ProviderError("ollama", f"Stream error: {str(e)}")
    
    def is_available(self) -> bool:
        try:
            import httpx
            with httpx.Client() as client:
                response = client.get(f"{self.url}/api/tags", timeout=5.0)
                return response.status_code == 200
        except:
            return False


class AsyncWatsonxProvider(AsyncBaseProvider):
    """Async provider for IBM watsonx models."""
    
    def __init__(self, api_key: str, model: str = "ibm/granite-3-8b-instruct", 
                 project_id: str = None, url: str = "https://eu-de.ml.cloud.ibm.com"):
        super().__init__(api_key, model)
        self.project_id = project_id
        self.url = url
        self.default_model = "ibm/granite-3-8b-instruct"
        
        # Note: watsonx SDK doesn't have async support yet
        # We'll use sync in executor for now
        try:
            from ibm_watsonx_ai.foundation_models import ModelInference
            from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
            from ibm_watsonx_ai import Credentials
            self.ModelInference = ModelInference
            self.GenParams = GenParams
            self.Credentials = Credentials
        except ImportError:
            raise ConfigurationError("ibm-watsonx-ai package not installed. Run: pip install ibm-watsonx-ai")
    
    async def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            import asyncio
            
            # Run sync code in executor
            response_text = await asyncio.get_event_loop().run_in_executor(
                None,
                self._sync_query,
                prompt
            )
            
            latency = time.time() - start_time
            
            return LLMResponse(
                content=response_text,
                provider="watsonx",
                model=self.model,
                latency=latency,
                metadata={
                    "project_id": self.project_id,
                    "url": self.url
                }
            )
        except Exception as e:
            raise ProviderError("watsonx", str(e))
    
    def _sync_query(self, prompt: str) -> str:
        """Synchronous query for watsonx (used in executor)."""
        credentials = self.Credentials(
            url=self.url,
            api_key=self.api_key
        )
        
        parameters = {
            self.GenParams.DECODING_METHOD: "greedy",
            self.GenParams.MAX_NEW_TOKENS: 2000,
            self.GenParams.MIN_NEW_TOKENS: 1,
            self.GenParams.TEMPERATURE: 0.7,
            self.GenParams.TOP_P: 1,
            self.GenParams.STOP_SEQUENCES: []
        }
        
        model = self.ModelInference(
            model_id=self.model,
            params=parameters,
            credentials=credentials,
            project_id=self.project_id
        )
        
        return model.generate_text(prompt=prompt)
    
    def is_available(self) -> bool:
        try:
            credentials = self.Credentials(
                url=self.url,
                api_key=self.api_key
            )
            return True
        except:
            return False


def get_async_provider(provider_name: str, api_key: Optional[str] = None, model: Optional[str] = None):
    """Factory function to get the right async provider."""
    
    if provider_name == "anthropic":
        return AsyncAnthropicProvider(api_key, model)
    elif provider_name == "openai":
        return AsyncOpenAIProvider(api_key, model)
    elif provider_name == "gemini":
        return AsyncGeminiProvider(api_key, model)
    elif provider_name == "ollama":
        return AsyncOllamaProvider(model or "llama3")
    elif provider_name == "watsonx":
        project_id = os.getenv("WATSONX_PROJECT_ID")
        if not project_id:
            raise ConfigurationError("WATSONX_PROJECT_ID environment variable required")
        return AsyncWatsonxProvider(api_key, model, project_id)
    else:
        raise ConfigurationError(f"Unknown provider: {provider_name}")