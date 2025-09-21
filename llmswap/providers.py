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
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
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
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                metadata={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                }
            )
        except Exception as e:
            raise ProviderError("anthropic", str(e))
    
    def is_available(self) -> bool:
        return self.api_key is not None
    
    def chat(self, messages: list) -> LLMResponse:
        """Send conversation with full message history."""
        start_time = time.time()
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=messages
            )
            
            latency = time.time() - start_time
            content = response.content[0].text
            
            return LLMResponse(
                content=content,
                provider="anthropic",
                model=self.model,
                latency=latency,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                metadata={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                }
            )
        except Exception as e:
            raise ProviderError("anthropic", str(e))


class OpenAIProvider(BaseProvider):
    """Provider for OpenAI GPT models."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
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
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                },
                metadata={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "finish_reason": response.choices[0].finish_reason,
                }
            )
        except Exception as e:
            raise ProviderError("openai", str(e))
    
    def chat(self, messages: list) -> LLMResponse:
        """Send conversation with full message history."""
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=4000
            )
            
            latency = time.time() - start_time
            content = response.choices[0].message.content
            
            return LLMResponse(
                content=content,
                provider="openai", 
                model=self.model,
                latency=latency,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                },
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
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
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
            
            # Extract usage data if available (Gemini provides usage_metadata)
            usage_data = {}
            if hasattr(response, 'usage_metadata'):
                usage_data = {
                    "prompt_token_count": getattr(response.usage_metadata, 'prompt_token_count', None),
                    "candidates_token_count": getattr(response.usage_metadata, 'candidates_token_count', None),
                    "total_token_count": getattr(response.usage_metadata, 'total_token_count', None),
                }
                # Map to standard field names for analytics
                if usage_data.get("prompt_token_count"):
                    usage_data["input_tokens"] = usage_data["prompt_token_count"]
                if usage_data.get("candidates_token_count"):
                    usage_data["output_tokens"] = usage_data["candidates_token_count"]
            
            return LLMResponse(
                content=content,
                provider="gemini",
                model=self.model,
                latency=latency,
                usage=usage_data if usage_data else None,
                metadata={
                    "safety_ratings": getattr(response, 'safety_ratings', None),
                    "finish_reason": getattr(response, 'finish_reason', None),
                    "usage_metadata": usage_data,
                }
            )
        except Exception as e:
            raise ProviderError("gemini", str(e))
    
    def chat(self, messages: list) -> LLMResponse:
        """Send conversation with full message history."""
        start_time = time.time()
        try:
            # Convert message format for Gemini
            chat_history = []
            for msg in messages[:-1]:  # All except the last message
                role = "user" if msg["role"] == "user" else "model"
                chat_history.append({"role": role, "parts": [msg["content"]]})
            
            # Start chat with history
            chat = self.model_instance.start_chat(history=chat_history)
            
            # Send the current message
            current_message = messages[-1]["content"]
            response = chat.send_message(current_message)
            
            latency = time.time() - start_time
            content = response.text
            
            # Extract usage data if available (Gemini provides usage_metadata)
            usage_data = {}
            if hasattr(response, 'usage_metadata'):
                usage_data = {
                    "prompt_token_count": getattr(response.usage_metadata, 'prompt_token_count', None),
                    "candidates_token_count": getattr(response.usage_metadata, 'candidates_token_count', None),
                    "total_token_count": getattr(response.usage_metadata, 'total_token_count', None),
                }
                # Map to standard field names for analytics
                if usage_data.get("prompt_token_count"):
                    usage_data["input_tokens"] = usage_data["prompt_token_count"]
                if usage_data.get("candidates_token_count"):
                    usage_data["output_tokens"] = usage_data["candidates_token_count"]
            
            return LLMResponse(
                content=content,
                provider="gemini",
                model=self.model,
                latency=latency,
                usage=usage_data if usage_data else None,
                metadata={
                    "safety_ratings": getattr(response, 'safety_ratings', None),
                    "finish_reason": getattr(response, 'finish_reason', None),
                    "usage_metadata": usage_data,
                }
            )
        except Exception as e:
            raise ProviderError("gemini", str(e))
    
    def is_available(self) -> bool:
        return self.api_key is not None


class OllamaProvider(BaseProvider):
    """Provider for local Ollama models."""
    
    def __init__(self, model: Optional[str] = None, url: str = "http://localhost:11434"):
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
            
            # Extract usage data if available (Ollama provides token counts in response)
            usage_data = {}
            if "prompt_eval_count" in result or "eval_count" in result:
                usage_data = {
                    "input_tokens": result.get("prompt_eval_count"),
                    "output_tokens": result.get("eval_count"),
                }
                
            return LLMResponse(
                content=content,
                provider="ollama",
                model=self.model,
                latency=latency,
                usage=usage_data if usage_data else None,
                metadata={
                    "total_duration": result.get("total_duration"),
                    "load_duration": result.get("load_duration"),
                    "prompt_eval_count": result.get("prompt_eval_count"),
                    "eval_count": result.get("eval_count"),
                }
            )
        except Exception as e:
            raise ProviderError("ollama", str(e))
    
    def chat(self, messages: list) -> LLMResponse:
        """Send conversation with full message history."""
        start_time = time.time()
        try:
            # Convert messages to Ollama chat format
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 4000,
                }
            }
            
            response = self.requests.post(
                f"{self.url}/api/chat",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            latency = time.time() - start_time
            content = result.get('message', {}).get('content', 'No response generated')
            
            # Extract usage data if available (Ollama provides token counts in response)
            usage_data = {}
            if "prompt_eval_count" in result or "eval_count" in result:
                usage_data = {
                    "input_tokens": result.get("prompt_eval_count"),
                    "output_tokens": result.get("eval_count"),
                }
                
            return LLMResponse(
                content=content,
                provider="ollama",
                model=self.model,
                latency=latency,
                usage=usage_data if usage_data else None,
                metadata={
                    "total_duration": result.get("total_duration"),
                    "load_duration": result.get("load_duration"),
                    "prompt_eval_count": result.get("prompt_eval_count"),
                    "eval_count": result.get("eval_count"),
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


class GroqProvider(BaseProvider):
    """Provider for Groq high-performance inference models."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__(api_key or os.getenv("GROQ_API_KEY"), model)
        if not self.api_key:
            raise ConfigurationError("GROQ_API_KEY not found in environment variables")
        
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
        except ImportError:
            raise ConfigurationError("groq package not installed. Run: pip install groq")
    
    def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
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
            raise ProviderError("groq", str(e))
    
    def is_available(self) -> bool:
        return self.api_key is not None
    
    def chat(self, messages: list) -> LLMResponse:
        """Send conversation with full message history."""
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
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
            raise ProviderError("groq", str(e))


class CoherProvider(BaseProvider):
    """Provider for Cohere Command models."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__(api_key or os.getenv("COHERE_API_KEY"), model)
        if not self.api_key:
            raise ConfigurationError("COHERE_API_KEY not found in environment variables")
        
        try:
            import cohere
            self.client = cohere.ClientV2(api_key=self.api_key)
        except ImportError:
            raise ConfigurationError("cohere package not installed. Run: pip install cohere")
    
    def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            response = self.client.chat(
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
            raise ProviderError("cohere", str(e))
    
    def is_available(self) -> bool:
        return self.api_key is not None
    
    def chat(self, messages: list) -> LLMResponse:
        """Send conversation with full message history."""
        start_time = time.time()
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
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
            raise ProviderError("cohere", str(e))


class PerplexityProvider(BaseProvider):
    """Provider for Perplexity online models."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__(api_key or os.getenv("PERPLEXITY_API_KEY"), model)
        if not self.api_key:
            raise ConfigurationError("PERPLEXITY_API_KEY not found in environment variables")
        
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://api.perplexity.ai"
            )
        except ImportError:
            raise ConfigurationError("openai package not installed. Run: pip install openai")
    
    def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
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
            raise ProviderError("perplexity", str(e))
    
    def is_available(self) -> bool:
        return self.api_key is not None
    
    def chat(self, messages: list) -> LLMResponse:
        """Send conversation with full message history."""
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
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
            raise ProviderError("perplexity", str(e))


class WatsonxProvider(BaseProvider):
    """Provider for IBM watsonx models."""
    
    def __init__(self, api_key: str, model: Optional[str] = None, 
                 project_id: str = None, url: str = "https://eu-de.ml.cloud.ibm.com"):
        super().__init__(api_key, model)
        self.project_id = project_id
        self.url = url
        
        try:
            from ibm_watsonx_ai.foundation_models import ModelInference
            from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
            from ibm_watsonx_ai import APIClient
            self.Model = ModelInference
            self.GenParams = GenParams
            self.APIClient = APIClient
        except ImportError:
            raise ConfigurationError("ibm-watsonx-ai package not installed. Run: pip install ibm-watsonx-ai")
    
    def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            # Set up credentials
            credentials = {
                "url": self.url,
                "apikey": self.api_key
            }
            
            # Configure generation parameters
            parameters = {
                self.GenParams.DECODING_METHOD: "greedy",
                self.GenParams.MAX_NEW_TOKENS: 2000,
                self.GenParams.MIN_NEW_TOKENS: 1,
                self.GenParams.TEMPERATURE: 0.7,
                self.GenParams.TOP_P: 1,
                self.GenParams.STOP_SEQUENCES: []
            }
            
            # Initialize model
            model = self.Model(
                model_id=self.model,
                credentials=credentials,
                params=parameters,
                project_id=self.project_id
            )
            
            # Generate text
            response_text = model.generate_text(prompt=prompt)
            
            latency = time.time() - start_time
            
            # Extract usage data if available (watsonx provides token counts)
            usage_data = {}
            # Note: generate_text() returns just the text, not detailed usage info

            return LLMResponse(
                content=response_text,
                provider="watsonx",
                model=self.model,
                latency=latency,
                usage=usage_data if usage_data else None,
                metadata={
                    "project_id": self.project_id,
                    "url": self.url,
                    "usage_details": usage_data,
                }
            )
        except Exception as e:
            raise ProviderError("watsonx", str(e))
    
    def chat(self, messages: list) -> LLMResponse:
        """Send conversation with full message history."""
        start_time = time.time()
        try:
            # Convert messages to a single prompt for watsonx
            conversation_prompt = ""
            for msg in messages:
                role = msg["role"].capitalize()
                conversation_prompt += f"{role}: {msg['content']}\n\n"
            
            # Set up credentials
            credentials = {
                "url": self.url,
                "apikey": self.api_key
            }
            
            # Configure generation parameters
            parameters = {
                self.GenParams.DECODING_METHOD: "greedy",
                self.GenParams.MAX_NEW_TOKENS: 2000,
                self.GenParams.MIN_NEW_TOKENS: 1,
                self.GenParams.TEMPERATURE: 0.7,
                self.GenParams.TOP_P: 1,
                self.GenParams.STOP_SEQUENCES: []
            }
            
            # Initialize model
            model = self.Model(
                model_id=self.model,
                credentials=credentials,
                params=parameters,
                project_id=self.project_id
            )
            
            # Generate text
            response_text = model.generate_text(prompt=conversation_prompt)
            
            latency = time.time() - start_time
            
            # Extract usage data if available (watsonx provides token counts)
            usage_data = {}
            # Note: generate_text() returns just the text, not detailed usage info

            return LLMResponse(
                content=response_text,
                provider="watsonx",
                model=self.model,
                latency=latency,
                usage=usage_data if usage_data else None,
                metadata={
                    "project_id": self.project_id,
                    "url": self.url,
                    "usage_details": usage_data,
                }
            )
        except Exception as e:
            raise ProviderError("watsonx", str(e))
    
    def is_available(self) -> bool:
        return self.api_key is not None and self.project_id is not None