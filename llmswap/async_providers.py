"""Async provider implementations for llmswap."""

import asyncio
import os
import time
from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator

from .response import LLMResponse
from .exceptions import ProviderError, ConfigurationError


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
        """Check if provider is available and configured."""
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
            latency = time.time() - start_time
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
            raise ProviderError("openai", str(e))
    
    def is_available(self) -> bool:
        return self.api_key is not None


class AsyncAnthropicProvider(AsyncBaseProvider):
    """Async provider for Anthropic Claude models."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        
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
            latency = time.time() - start_time
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
            raise ProviderError("anthropic", str(e))
    
    def is_available(self) -> bool:
        return self.api_key is not None


class AsyncGeminiProvider(AsyncBaseProvider):
    """Async provider for Google Gemini models."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ConfigurationError("Gemini API key required. Set GEMINI_API_KEY environment variable.")
        
        super().__init__(api_key, model)
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model_instance = genai.GenerativeModel(self.model)
        except ImportError:
            raise ConfigurationError("google-generativeai package not installed. Run: pip install google-generativeai")
    
    async def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            # Run in executor since Gemini doesn't have native async support
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.model_instance.generate_content, prompt)
            
            latency = time.time() - start_time
            content = response.text
            
            return LLMResponse(
                content=content,
                provider="gemini",
                model=self.model,
                latency=latency,
                metadata={
                    "finish_reason": response.candidates[0].finish_reason.name if response.candidates else "unknown",
                }
            )
        except Exception as e:
            latency = time.time() - start_time
            raise ProviderError("gemini", str(e))
    
    def is_available(self) -> bool:
        return self.api_key is not None


class AsyncOllamaProvider(AsyncBaseProvider):
    """Async provider for local Ollama models."""
    
    def __init__(self, model: Optional[str] = None, url: str = "http://localhost:11434"):
        super().__init__(None, model)
        self.url = url
        
        try:
            import httpx
            self.httpx = httpx
        except ImportError:
            raise ConfigurationError("httpx package not installed. Run: pip install httpx")
    
    async def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            async with self.httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=120.0
                )
                response.raise_for_status()
                
                result = response.json()
                latency = time.time() - start_time
                
                return LLMResponse(
                    content=result["response"],
                    provider="ollama",
                    model=self.model,
                    latency=latency,
                    metadata={
                        "done": result.get("done", False),
                        "context": result.get("context", []),
                    }
                )
        except Exception as e:
            latency = time.time() - start_time
            raise ProviderError("ollama", str(e))
    
    async def stream(self, prompt: str) -> AsyncIterator[str]:
        """Stream response from Ollama."""
        try:
            async with self.httpx.AsyncClient() as client:
                async with client.stream(
                    'POST',
                    f"{self.url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": True
                    },
                    timeout=120.0
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                import json
                                data = json.loads(line)
                                if "response" in data:
                                    yield data["response"]
                                if data.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            raise ProviderError("ollama", str(e))
    
    def is_available(self) -> bool:
        try:
            import httpx
            with httpx.Client() as client:
                response = client.get(f"{self.url}/api/tags", timeout=5.0)
                return response.status_code == 200
        except:
            return False


class AsyncCoherProvider(AsyncBaseProvider):
    """Async provider for Cohere Command models."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        
        if not api_key:
            api_key = os.getenv("COHERE_API_KEY")
        
        if not api_key:
            raise ConfigurationError("Cohere API key required. Set COHERE_API_KEY environment variable.")
        
        super().__init__(api_key, model)
        
        try:
            import cohere
            self.client = cohere.AsyncClientV2(api_key=self.api_key)
        except ImportError:
            raise ConfigurationError("cohere package not installed. Run: pip install cohere")
    
    async def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            response = await self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.7
            )
            
            latency = time.time() - start_time
            content = response.message.content[0].text
            
            return LLMResponse(
                content=content,
                provider="cohere",
                model=self.model,
                latency=latency,
                usage={
                    "input_tokens": response.usage.billed_units.input_tokens if response.usage else 0,
                    "output_tokens": response.usage.billed_units.output_tokens if response.usage else 0,
                },
                metadata={
                    "input_tokens": response.usage.billed_units.input_tokens if response.usage else 0,
                    "output_tokens": response.usage.billed_units.output_tokens if response.usage else 0,
                }
            )
        except Exception as e:
            latency = time.time() - start_time
            raise ProviderError("cohere", str(e))
    
    def is_available(self) -> bool:
        return self.api_key is not None


class AsyncGroqProvider(AsyncBaseProvider):
    """Async provider for Groq high-performance inference models."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.default_model = "llama-3.1-8b-instant"
        
        if not api_key:
            api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ConfigurationError("Groq API key required. Set GROQ_API_KEY environment variable.")
        
        super().__init__(api_key, model)
        
        try:
            from groq import AsyncGroq
            self.client = AsyncGroq(api_key=self.api_key)
        except ImportError:
            raise ConfigurationError("groq package not installed. Run: pip install groq")
    
    async def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.7
            )
            
            latency = time.time() - start_time
            content = response.choices[0].message.content
            
            return LLMResponse(
                content=content,
                provider="groq",
                model=self.model,
                latency=latency,
                usage={
                    "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "output_tokens": response.usage.completion_tokens if response.usage else 0,
                },
                metadata={
                    "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "output_tokens": response.usage.completion_tokens if response.usage else 0,
                }
            )
        except Exception as e:
            latency = time.time() - start_time
            raise ProviderError("groq", str(e))
    
    def is_available(self) -> bool:
        return self.api_key is not None


class AsyncPerplexityProvider(AsyncBaseProvider):
    """Async provider for Perplexity online models."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.default_model = "sonar-pro"
        
        if not api_key:
            api_key = os.getenv("PERPLEXITY_API_KEY")
        
        if not api_key:
            raise ConfigurationError("Perplexity API key required. Set PERPLEXITY_API_KEY environment variable.")
        
        super().__init__(api_key, model)
        
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url="https://api.perplexity.ai"
            )
        except ImportError:
            raise ConfigurationError("openai package not installed. Run: pip install openai")
    
    async def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.7
            )
            
            latency = time.time() - start_time
            content = response.choices[0].message.content
            
            return LLMResponse(
                content=content,
                provider="perplexity",
                model=self.model,
                latency=latency,
                usage={
                    "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "output_tokens": response.usage.completion_tokens if response.usage else 0,
                },
                metadata={
                    "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "output_tokens": response.usage.completion_tokens if response.usage else 0,
                }
            )
        except Exception as e:
            latency = time.time() - start_time
            raise ProviderError("perplexity", str(e))
    
    def is_available(self) -> bool:
        return self.api_key is not None


class AsyncWatsonxProvider(AsyncBaseProvider):
    """Async provider for IBM watsonx models."""
    
    def __init__(self, api_key: str, model: Optional[str] = None, 
                 project_id: str = None, url: str = "https://eu-de.ml.cloud.ibm.com"):
        super().__init__(api_key, model)
        self.project_id = project_id
        self.url = url
        
        # Note: watsonx SDK doesn't have async support yet
        # Execute watsonx sync call in thread executor
        try:
            from ibm_watsonx_ai.foundation_models import ModelInference
            from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
            from ibm_watsonx_ai import Credentials
            
            credentials = Credentials(
                url=self.url,
                api_key=self.api_key
            )
            
            self.model_instance = ModelInference(
                model_id=self.model,
                params={
                    GenParams.DECODING_METHOD: "greedy",
                    GenParams.MAX_NEW_TOKENS: 1000,
                    GenParams.TEMPERATURE: 0.7,
                    GenParams.TOP_P: 1
                },
                credentials=credentials,
                project_id=self.project_id
            )
        except ImportError:
            raise ConfigurationError("ibm-watsonx-ai package not installed. Run: pip install ibm-watsonx-ai")
    
    async def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            # Run in executor since watsonx doesn't have native async support
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.model_instance.generate_text, prompt)
            
            latency = time.time() - start_time
            
            return LLMResponse(
                content=response,
                provider="watsonx",
                model=self.model,
                latency=latency,
                metadata={
                    "project_id": self.project_id,
                }
            )
        except Exception as e:
            latency = time.time() - start_time
            raise ProviderError("watsonx", str(e))
    
    def is_available(self) -> bool:
        return self.api_key is not None and self.project_id is not None