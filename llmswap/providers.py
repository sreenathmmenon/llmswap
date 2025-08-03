"""LLM provider implementations."""

import os
import time
from abc import ABC, abstractmethod
from typing import Optional

from .response import LLMResponse
from .exceptions import ProviderError, ConfigurationError


class BaseProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        
    @abstractmethod
    def query(self, prompt: str) -> LLMResponse:
        """Send query to the LLM provider."""
        pass
        
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available and configured."""
        pass


class AnthropicProvider(BaseProvider):
    """Provider for Anthropic Claude models."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        super().__init__(api_key or os.getenv("ANTHROPIC_API_KEY"), model)
        if not self.api_key:
            raise ConfigurationError("ANTHROPIC_API_KEY not found in environment variables")
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ConfigurationError("anthropic package not installed. Run: pip install anthropic")
    
    def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            response = self.client.messages.create(
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
                }
            )
        except Exception as e:
            raise ProviderError("anthropic", str(e))
    
    def is_available(self) -> bool:
        return self.api_key is not None


class OpenAIProvider(BaseProvider):
    """Provider for OpenAI GPT models."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        super().__init__(api_key or os.getenv("OPENAI_API_KEY"), model)
        if not self.api_key:
            raise ConfigurationError("OPENAI_API_KEY not found in environment variables")
        
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ConfigurationError("openai package not installed. Run: pip install openai")
    
    def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
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
    
    def is_available(self) -> bool:
        return self.api_key is not None


class GeminiProvider(BaseProvider):
    """Provider for Google Gemini models."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        super().__init__(api_key or os.getenv("GEMINI_API_KEY"), model)
        if not self.api_key:
            raise ConfigurationError("GEMINI_API_KEY not found in environment variables")
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model_instance = genai.GenerativeModel(self.model)
        except ImportError:
            raise ConfigurationError("google-generativeai package not installed. Run: pip install google-generativeai")
    
    def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            response = self.model_instance.generate_content(prompt)
            
            latency = time.time() - start_time
            content = response.text
            
            return LLMResponse(
                content=content,
                provider="gemini",
                model=self.model,
                latency=latency,
                metadata={
                    "safety_ratings": getattr(response, 'safety_ratings', None),
                    "finish_reason": getattr(response, 'finish_reason', None),
                }
            )
        except Exception as e:
            raise ProviderError("gemini", str(e))
    
    def is_available(self) -> bool:
        return self.api_key is not None


class OllamaProvider(BaseProvider):
    """Provider for local Ollama models."""
    
    def __init__(self, model: str = "llama3", url: str = "http://localhost:11434"):
        super().__init__(None, model)
        self.url = url
        
        try:
            import requests
            self.requests = requests
        except ImportError:
            raise ConfigurationError("requests package not installed. Run: pip install requests")
    
    def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 4000,
                }
            }
            
            response = self.requests.post(
                f"{self.url}/api/generate",
                json=payload,
                timeout=60
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
    
    def is_available(self) -> bool:
        try:
            response = self.requests.get(f"{self.url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False