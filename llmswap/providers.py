"""LLM provider implementations."""

import os
import time
from abc import ABC, abstractmethod
from typing import Optional

from .response import LLMResponse
from .exceptions import (
    ProviderError,
    ConfigurationError,
    RateLimitError,
    AuthenticationError,
    TimeoutError,
    InvalidRequestError,
    QuotaExceededError,
)
from .security import safe_error_string


def clean_api_key(api_key: Optional[str]) -> Optional[str]:
    """Clean API key by removing quotes, whitespace, and invalid characters."""
    if not api_key:
        return api_key

    # Strip whitespace
    api_key = api_key.strip()

    # Remove all non-ASCII characters (API keys are ASCII only)
    # This removes Unicode quotes and any other invalid characters
    api_key = api_key.encode("ascii", errors="ignore").decode("ascii")

    # Remove any remaining ASCII quotes and whitespace
    api_key = api_key.strip().strip('"').strip("'").strip()

    return api_key


def classify_and_raise_error(
    provider_name: str, error: Exception, api_key: Optional[str] = None
):
    """
    Classify error and raise appropriate specific exception.

    Works for ALL providers (Anthropic, OpenAI, Gemini, Groq, Cohere,
    Perplexity, WatsonX, xAI, Ollama, Sarvam).

    Args:
        provider_name: Name of the provider (e.g., "anthropic", "openai")
        error: The original exception from any provider
        api_key: API key to remove from error messages (security)
    """
    error_text = str(error).lower()

    # Extract retry-after from rate limit responses (if present)
    retry_after = None
    if "retry-after" in error_text or "retry after" in error_text:
        import re

        match = re.search(r"retry[- ]after[:\s]+(\d+)", error_text)
        if match:
            retry_after = int(match.group(1))

    # Check for authentication errors (401, invalid key, unauthorized)
    if any(
        word in error_text
        for word in [
            "401",
            "unauthorized",
            "invalid",
            "authentication",
            "api key",
            "forbidden",
            "403",
        ]
    ):
        raise AuthenticationError(
            provider_name,
            "Authentication failed. Check your API key is valid and active.",
        )

    # Check for rate limits (429, too many requests, quota)
    if any(
        word in error_text
        for word in ["429", "rate limit", "too many requests", "requests per"]
    ):
        raise RateLimitError(
            provider_name,
            "Rate limit exceeded. Wait before retrying or switch providers.",
            retry_after=retry_after,
        )

    # Check for quota exceeded (different from rate limit)
    if any(
        word in error_text for word in ["quota", "exceeded", "insufficient", "credits"]
    ):
        raise QuotaExceededError(
            provider_name, "API quota exceeded. Check your account limits."
        )

    # Check for timeout/network errors
    if any(
        word in error_text
        for word in ["timeout", "connection", "network", "unreachable", "timed out"]
    ):
        raise TimeoutError(
            provider_name, "Request timed out. Check your network or try again."
        )

    # Check for invalid request (400, bad request, validation)
    if any(
        word in error_text
        for word in [
            "400",
            "bad request",
            "invalid request",
            "validation",
            "invalid parameter",
        ]
    ):
        safe_msg = safe_error_string(error, api_key)
        raise InvalidRequestError(provider_name, f"Invalid request: {safe_msg}")

    # Unknown error - use safe generic ProviderError
    safe_msg = safe_error_string(error, api_key)
    raise ProviderError(
        provider_name, f"Request failed: {safe_msg}", error_type="unknown"
    )


class BaseProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = clean_api_key(api_key)
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
            raise ConfigurationError(
                "ANTHROPIC_API_KEY not found in environment variables"
            )

        try:
            import anthropic

            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ConfigurationError(
                "anthropic package not installed. Run: pip install anthropic"
            )

    def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}],
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
                },
            )
        except Exception as e:
            classify_and_raise_error("anthropic", e, self.api_key)

    def is_available(self) -> bool:
        return self.api_key is not None

    def chat(self, messages: list) -> LLMResponse:
        """Send conversation with full message history."""
        start_time = time.time()
        try:
            response = self.client.messages.create(
                model=self.model, max_tokens=4000, messages=messages
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
                },
            )
        except Exception as e:
            classify_and_raise_error("anthropic", e, self.api_key)

    def chat_with_tools(self, messages: list, tools: list) -> LLMResponse:
        """Send conversation with tool calling support."""
        from .tools.response import create_enhanced_response

        start_time = time.time()
        try:
            # Convert Tool objects to Anthropic format
            anthropic_tools = [tool.to_anthropic_format() for tool in tools]

            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=messages,
                tools=anthropic_tools,
            )

            latency = time.time() - start_time

            # Use enhanced response to extract tool calls
            enhanced = create_enhanced_response(response, "anthropic")

            return LLMResponse(
                content=enhanced.content,
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
                    "tool_calls": enhanced.tool_calls,
                    "finish_reason": enhanced.finish_reason,
                    "raw_response": response,
                },
            )
        except Exception as e:
            classify_and_raise_error("anthropic", e, self.api_key)


class OpenAIProvider(BaseProvider):
    """Provider for OpenAI GPT models."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__(api_key or os.getenv("OPENAI_API_KEY"), model)
        if not self.api_key:
            raise ConfigurationError(
                "OPENAI_API_KEY not found in environment variables"
            )

        try:
            import openai

            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ConfigurationError(
                "openai package not installed. Run: pip install openai"
            )

    def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
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
                },
            )
        except Exception as e:
            classify_and_raise_error("openai", e, self.api_key)

    def chat(self, messages: list) -> LLMResponse:
        """Send conversation with full message history."""
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, max_tokens=4000
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
                },
            )
        except Exception as e:
            classify_and_raise_error("openai", e, self.api_key)

    def chat_with_tools(self, messages: list, tools: list) -> LLMResponse:
        """Send conversation with tool calling support."""
        from .tools.response import create_enhanced_response

        start_time = time.time()
        try:
            # Convert Tool objects to OpenAI format
            openai_tools = [tool.to_openai_format() for tool in tools]

            response = self.client.chat.completions.create(
                model=self.model, messages=messages, max_tokens=4000, tools=openai_tools
            )

            latency = time.time() - start_time

            # Use enhanced response to extract tool calls
            enhanced = create_enhanced_response(response, "openai")

            return LLMResponse(
                content=enhanced.content,
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
                    "tool_calls": enhanced.tool_calls,
                    "finish_reason": enhanced.finish_reason,
                    "raw_response": response,
                },
            )
        except Exception as e:
            classify_and_raise_error("openai", e, self.api_key)

    def is_available(self) -> bool:
        return self.api_key is not None


class GeminiProvider(BaseProvider):
    """Provider for Google Gemini models."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__(api_key or os.getenv("GEMINI_API_KEY"), model)
        if not self.api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY not found in environment variables"
            )

        self.model_instance = None
        self._genai = None

    def _initialize(self):
        """Lazy initialization of Gemini client."""
        if self.model_instance is not None:
            return

        try:
            import google.generativeai as genai

            self._genai = genai
            # Set environment variable to cleaned key (Google SDK may read from env)
            os.environ["GEMINI_API_KEY"] = self.api_key
            self._genai.configure(api_key=self.api_key)
            self.model_instance = self._genai.GenerativeModel(self.model)
        except ImportError:
            raise ConfigurationError(
                "google-generativeai package not installed. Run: pip install google-generativeai"
            )

    def query(self, prompt: str) -> LLMResponse:
        self._initialize()
        start_time = time.time()
        try:
            response = self.model_instance.generate_content(prompt)

            latency = time.time() - start_time
            content = response.text

            # Extract usage data if available (Gemini provides usage_metadata)
            usage_data = {}
            if hasattr(response, "usage_metadata"):
                usage_data = {
                    "prompt_token_count": getattr(
                        response.usage_metadata, "prompt_token_count", None
                    ),
                    "candidates_token_count": getattr(
                        response.usage_metadata, "candidates_token_count", None
                    ),
                    "total_token_count": getattr(
                        response.usage_metadata, "total_token_count", None
                    ),
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
                    "safety_ratings": getattr(response, "safety_ratings", None),
                    "finish_reason": getattr(response, "finish_reason", None),
                    "usage_metadata": usage_data,
                },
            )
        except Exception as e:
            classify_and_raise_error("gemini", e, self.api_key)

    def chat(self, messages: list) -> LLMResponse:
        """Send conversation with full message history."""
        self._initialize()
        start_time = time.time()
        try:
            # Convert message format for Gemini
            chat_history = []
            for msg in messages[:-1]:  # All except the last message
                role = "user" if msg["role"] == "user" else "model"
                # Handle messages that already have parts (from format_tool_results)
                if "parts" in msg:
                    # Message already formatted for Gemini
                    if msg["role"] == "function":
                        # Function role stays as is
                        chat_history.append({"role": "function", "parts": msg["parts"]})
                    else:
                        chat_history.append({"role": role, "parts": msg["parts"]})
                else:
                    # Standard message with content
                    chat_history.append({"role": role, "parts": [msg["content"]]})

            # Start chat with history
            chat = self.model_instance.start_chat(history=chat_history)

            # Send the current message
            last_msg = messages[-1]
            if "parts" in last_msg:
                # Message already has parts
                response = chat.send_message(last_msg["parts"])
            else:
                # Standard message with content
                response = chat.send_message(last_msg["content"])

            latency = time.time() - start_time
            content = response.text

            # Extract usage data if available (Gemini provides usage_metadata)
            usage_data = {}
            if hasattr(response, "usage_metadata"):
                usage_data = {
                    "prompt_token_count": getattr(
                        response.usage_metadata, "prompt_token_count", None
                    ),
                    "candidates_token_count": getattr(
                        response.usage_metadata, "candidates_token_count", None
                    ),
                    "total_token_count": getattr(
                        response.usage_metadata, "total_token_count", None
                    ),
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
                    "safety_ratings": getattr(response, "safety_ratings", None),
                    "finish_reason": getattr(response, "finish_reason", None),
                    "usage_metadata": usage_data,
                },
            )
        except Exception as e:
            classify_and_raise_error("gemini", e, self.api_key)

    def chat_with_tools(self, messages: list, tools: list) -> LLMResponse:
        """Send conversation with tool calling support."""
        from .tools.response import create_enhanced_response

        self._initialize()
        start_time = time.time()
        try:
            # Convert Tool objects to Gemini format
            gemini_tool_defs = []
            for tool in tools:
                tool_dict = tool.to_gemini_format()
                # Create FunctionDeclaration
                func_decl = self._genai.protos.FunctionDeclaration(
                    name=tool_dict["name"],
                    description=tool_dict["description"],
                    parameters=tool_dict["parameters"],
                )
                gemini_tool_defs.append(func_decl)

            # Create Tool wrapper
            gemini_tools = self._genai.protos.Tool(
                function_declarations=gemini_tool_defs
            )

            # Convert message format for Gemini
            chat_history = []
            for msg in messages[:-1]:  # All except the last message
                role = "user" if msg["role"] == "user" else "model"
                # Handle messages that already have parts (from format_tool_results)
                if "parts" in msg:
                    # Message already formatted for Gemini
                    if msg["role"] == "function":
                        # Function role stays as is
                        chat_history.append({"role": "function", "parts": msg["parts"]})
                    else:
                        chat_history.append({"role": role, "parts": msg["parts"]})
                else:
                    # Standard message with content
                    chat_history.append({"role": role, "parts": [msg["content"]]})

            # Start chat with history and tools
            chat = self.model_instance.start_chat(history=chat_history)

            # Send the current message with tools
            last_msg = messages[-1]
            if "parts" in last_msg:
                # Message already has parts
                response = chat.send_message(last_msg["parts"], tools=[gemini_tools])
            else:
                # Standard message with content
                response = chat.send_message(last_msg["content"], tools=[gemini_tools])

            latency = time.time() - start_time

            # Use enhanced response to extract tool calls
            enhanced = create_enhanced_response(response, "gemini")

            # Extract usage data
            usage_data = {}
            if hasattr(response, "usage_metadata"):
                usage_data = {
                    "prompt_token_count": getattr(
                        response.usage_metadata, "prompt_token_count", None
                    ),
                    "candidates_token_count": getattr(
                        response.usage_metadata, "candidates_token_count", None
                    ),
                    "total_token_count": getattr(
                        response.usage_metadata, "total_token_count", None
                    ),
                }
                if usage_data.get("prompt_token_count"):
                    usage_data["input_tokens"] = usage_data["prompt_token_count"]
                if usage_data.get("candidates_token_count"):
                    usage_data["output_tokens"] = usage_data["candidates_token_count"]

            return LLMResponse(
                content=enhanced.content,
                provider="gemini",
                model=self.model,
                latency=latency,
                usage=usage_data if usage_data else None,
                metadata={
                    "safety_ratings": getattr(response, "safety_ratings", None),
                    "finish_reason": enhanced.finish_reason,
                    "usage_metadata": usage_data,
                    "tool_calls": enhanced.tool_calls,
                    "raw_response": response,
                },
            )
        except Exception as e:
            classify_and_raise_error("gemini", e, self.api_key)

    def is_available(self) -> bool:
        return self.api_key is not None


class OllamaProvider(BaseProvider):
    """Provider for local Ollama models."""

    def __init__(
        self, model: Optional[str] = None, url: str = "http://localhost:11434"
    ):
        super().__init__(None, model)
        self.url = url

        try:
            import requests

            self.requests = requests
        except ImportError:
            raise ConfigurationError(
                "requests package not installed. Run: pip install requests"
            )

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
                },
            }

            response = self.requests.post(
                f"{self.url}/api/generate", json=payload, timeout=60
            )
            response.raise_for_status()
            result = response.json()

            latency = time.time() - start_time
            content = result.get("response", "No response generated")

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
                },
            )
        except Exception as e:
            classify_and_raise_error("ollama", e, self.api_key)

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
                },
            }

            response = self.requests.post(
                f"{self.url}/api/chat", json=payload, timeout=60
            )
            response.raise_for_status()
            result = response.json()

            latency = time.time() - start_time
            content = result.get("message", {}).get("content", "No response generated")

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
                },
            )
        except Exception as e:
            classify_and_raise_error("ollama", e, self.api_key)

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
            raise ConfigurationError(
                "groq package not installed. Run: pip install groq"
            )

    def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.7,
            )

            latency = time.time() - start_time
            content = response.choices[0].message.content

            return LLMResponse(
                content=content,
                provider="groq",
                model=self.model,
                latency=latency,
                usage={
                    "input_tokens": (
                        response.usage.prompt_tokens if response.usage else 0
                    ),
                    "output_tokens": (
                        response.usage.completion_tokens if response.usage else 0
                    ),
                },
                metadata={
                    "input_tokens": (
                        response.usage.prompt_tokens if response.usage else 0
                    ),
                    "output_tokens": (
                        response.usage.completion_tokens if response.usage else 0
                    ),
                },
            )
        except Exception as e:
            classify_and_raise_error("groq", e, self.api_key)

    def is_available(self) -> bool:
        return self.api_key is not None

    def chat(self, messages: list) -> LLMResponse:
        """Send conversation with full message history."""
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, max_tokens=4000, temperature=0.7
            )

            latency = time.time() - start_time
            content = response.choices[0].message.content

            return LLMResponse(
                content=content,
                provider="groq",
                model=self.model,
                latency=latency,
                usage={
                    "input_tokens": (
                        response.usage.prompt_tokens if response.usage else 0
                    ),
                    "output_tokens": (
                        response.usage.completion_tokens if response.usage else 0
                    ),
                },
                metadata={
                    "input_tokens": (
                        response.usage.prompt_tokens if response.usage else 0
                    ),
                    "output_tokens": (
                        response.usage.completion_tokens if response.usage else 0
                    ),
                },
            )
        except Exception as e:
            classify_and_raise_error("groq", e, self.api_key)

    def chat_with_tools(self, messages: list, tools: list) -> LLMResponse:
        """Send conversation with tool calling support."""
        from .tools.response import create_enhanced_response

        start_time = time.time()
        try:
            # Convert Tool objects to OpenAI format (Groq is OpenAI-compatible)
            groq_tools = [tool.to_openai_format() for tool in tools]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=4000,
                temperature=0.7,
                tools=groq_tools,
            )

            latency = time.time() - start_time

            # Use enhanced response to extract tool calls
            enhanced = create_enhanced_response(response, "groq")

            return LLMResponse(
                content=enhanced.content,
                provider="groq",
                model=self.model,
                latency=latency,
                usage={
                    "input_tokens": (
                        response.usage.prompt_tokens if response.usage else 0
                    ),
                    "output_tokens": (
                        response.usage.completion_tokens if response.usage else 0
                    ),
                },
                metadata={
                    "input_tokens": (
                        response.usage.prompt_tokens if response.usage else 0
                    ),
                    "output_tokens": (
                        response.usage.completion_tokens if response.usage else 0
                    ),
                    "tool_calls": enhanced.tool_calls,
                    "finish_reason": enhanced.finish_reason,
                    "raw_response": response,
                },
            )
        except Exception as e:
            classify_and_raise_error("groq", e, self.api_key)


class CoherProvider(BaseProvider):
    """Provider for Cohere Command models."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__(api_key or os.getenv("COHERE_API_KEY"), model)
        if not self.api_key:
            raise ConfigurationError(
                "COHERE_API_KEY not found in environment variables"
            )

        try:
            import cohere

            self.client = cohere.ClientV2(api_key=self.api_key)
        except ImportError:
            raise ConfigurationError(
                "cohere package not installed. Run: pip install cohere"
            )

    def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.7,
            )

            latency = time.time() - start_time
            content = response.message.content[0].text

            return LLMResponse(
                content=content,
                provider="cohere",
                model=self.model,
                latency=latency,
                usage={
                    "input_tokens": (
                        response.usage.billed_units.input_tokens
                        if response.usage
                        else 0
                    ),
                    "output_tokens": (
                        response.usage.billed_units.output_tokens
                        if response.usage
                        else 0
                    ),
                },
                metadata={
                    "input_tokens": (
                        response.usage.billed_units.input_tokens
                        if response.usage
                        else 0
                    ),
                    "output_tokens": (
                        response.usage.billed_units.output_tokens
                        if response.usage
                        else 0
                    ),
                },
            )
        except Exception as e:
            classify_and_raise_error("cohere", e, self.api_key)

    def is_available(self) -> bool:
        return self.api_key is not None

    def chat(self, messages: list) -> LLMResponse:
        """Send conversation with full message history."""
        start_time = time.time()
        try:
            response = self.client.chat(
                model=self.model, messages=messages, max_tokens=4000, temperature=0.7
            )

            latency = time.time() - start_time
            content = response.message.content[0].text

            return LLMResponse(
                content=content,
                provider="cohere",
                model=self.model,
                latency=latency,
                usage={
                    "input_tokens": (
                        response.usage.billed_units.input_tokens
                        if response.usage
                        else 0
                    ),
                    "output_tokens": (
                        response.usage.billed_units.output_tokens
                        if response.usage
                        else 0
                    ),
                },
                metadata={
                    "input_tokens": (
                        response.usage.billed_units.input_tokens
                        if response.usage
                        else 0
                    ),
                    "output_tokens": (
                        response.usage.billed_units.output_tokens
                        if response.usage
                        else 0
                    ),
                },
            )
        except Exception as e:
            classify_and_raise_error("cohere", e, self.api_key)


class PerplexityProvider(BaseProvider):
    """Provider for Perplexity online models."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__(api_key or os.getenv("PERPLEXITY_API_KEY"), model)
        if not self.api_key:
            raise ConfigurationError(
                "PERPLEXITY_API_KEY not found in environment variables"
            )

        try:
            import openai

            self.client = openai.OpenAI(
                api_key=self.api_key, base_url="https://api.perplexity.ai"
            )
        except ImportError:
            raise ConfigurationError(
                "openai package not installed. Run: pip install openai"
            )

    def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.7,
            )

            latency = time.time() - start_time
            content = response.choices[0].message.content

            return LLMResponse(
                content=content,
                provider="perplexity",
                model=self.model,
                latency=latency,
                usage={
                    "input_tokens": (
                        response.usage.prompt_tokens if response.usage else 0
                    ),
                    "output_tokens": (
                        response.usage.completion_tokens if response.usage else 0
                    ),
                },
                metadata={
                    "input_tokens": (
                        response.usage.prompt_tokens if response.usage else 0
                    ),
                    "output_tokens": (
                        response.usage.completion_tokens if response.usage else 0
                    ),
                },
            )
        except Exception as e:
            classify_and_raise_error("perplexity", e, self.api_key)

    def is_available(self) -> bool:
        return self.api_key is not None

    def chat(self, messages: list) -> LLMResponse:
        """Send conversation with full message history."""
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, max_tokens=4000, temperature=0.7
            )

            latency = time.time() - start_time
            content = response.choices[0].message.content

            return LLMResponse(
                content=content,
                provider="perplexity",
                model=self.model,
                latency=latency,
                usage={
                    "input_tokens": (
                        response.usage.prompt_tokens if response.usage else 0
                    ),
                    "output_tokens": (
                        response.usage.completion_tokens if response.usage else 0
                    ),
                },
                metadata={
                    "input_tokens": (
                        response.usage.prompt_tokens if response.usage else 0
                    ),
                    "output_tokens": (
                        response.usage.completion_tokens if response.usage else 0
                    ),
                },
            )
        except Exception as e:
            classify_and_raise_error("perplexity", e, self.api_key)


class WatsonxProvider(BaseProvider):
    """Provider for IBM watsonx models."""

    def __init__(
        self,
        api_key: str,
        model: Optional[str] = None,
        project_id: str = None,
        url: str = "https://eu-de.ml.cloud.ibm.com",
    ):
        super().__init__(api_key, model)
        self.project_id = project_id
        self.url = url

        # Check Python version - watsonx requires 3.10+
        import sys

        if sys.version_info < (3, 10):
            raise ConfigurationError(
                f"IBM watsonx requires Python 3.10+ (you have {sys.version_info.major}.{sys.version_info.minor}). "
                "Please upgrade Python or use a different provider."
            )

        try:
            from ibm_watsonx_ai.foundation_models import ModelInference
            from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
            from ibm_watsonx_ai import APIClient

            self.Model = ModelInference
            self.GenParams = GenParams
            self.APIClient = APIClient
        except ImportError:
            raise ConfigurationError(
                "ibm-watsonx-ai package not installed. Run: pip install 'llmswap[watsonx]'"
            )

    def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            # Set up credentials
            credentials = {"url": self.url, "apikey": self.api_key}

            # Configure generation parameters
            parameters = {
                self.GenParams.DECODING_METHOD: "greedy",
                self.GenParams.MAX_NEW_TOKENS: 2000,
                self.GenParams.MIN_NEW_TOKENS: 1,
                self.GenParams.TEMPERATURE: 0.7,
                self.GenParams.TOP_P: 1,
                self.GenParams.STOP_SEQUENCES: [],
            }

            # Initialize model
            model = self.Model(
                model_id=self.model,
                credentials=credentials,
                params=parameters,
                project_id=self.project_id,
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
                },
            )
        except Exception as e:
            classify_and_raise_error("watsonx", e, self.api_key)

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
            credentials = {"url": self.url, "apikey": self.api_key}

            # Configure generation parameters
            parameters = {
                self.GenParams.DECODING_METHOD: "greedy",
                self.GenParams.MAX_NEW_TOKENS: 2000,
                self.GenParams.MIN_NEW_TOKENS: 1,
                self.GenParams.TEMPERATURE: 0.7,
                self.GenParams.TOP_P: 1,
                self.GenParams.STOP_SEQUENCES: [],
            }

            # Initialize model
            model = self.Model(
                model_id=self.model,
                credentials=credentials,
                params=parameters,
                project_id=self.project_id,
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
                },
            )
        except Exception as e:
            classify_and_raise_error("watsonx", e, self.api_key)

    def is_available(self) -> bool:
        return self.api_key is not None and self.project_id is not None


class XAIProvider(BaseProvider):
    """Provider for xAI Grok models."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        # Support both XAI_API_KEY and GROK_X_AI_API_KEY for backwards compatibility
        api_key = api_key or os.getenv("XAI_API_KEY") or os.getenv("GROK_X_AI_API_KEY")
        super().__init__(api_key, model)
        if not self.api_key:
            raise ConfigurationError(
                "XAI_API_KEY or GROK_X_AI_API_KEY not found in environment variables. "
                "Set one of these environment variables with your X.AI API key."
            )

        try:
            import openai

            self.client = openai.OpenAI(
                api_key=self.api_key, base_url="https://api.x.ai/v1", timeout=20.0
            )
        except ImportError:
            raise ConfigurationError(
                "openai package not installed. Run: pip install openai"
            )

    def query(self, prompt: str) -> LLMResponse:
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
            )

            latency = time.time() - start_time
            content = response.choices[0].message.content or ""

            return LLMResponse(
                content=content,
                provider="xai",
                model=self.model,
                latency=latency,
                usage={
                    "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(
                        response.usage, "completion_tokens", 0
                    ),
                },
                metadata={},
            )
        except Exception as e:
            classify_and_raise_error("xai", e, self.api_key)

    def chat(self, messages: list) -> LLMResponse:
        """Send conversation with full message history."""
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, max_tokens=1000
            )

            latency = time.time() - start_time
            content = response.choices[0].message.content or ""

            return LLMResponse(
                content=content,
                provider="xai",
                model=self.model,
                latency=latency,
                usage={
                    "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(
                        response.usage, "completion_tokens", 0
                    ),
                },
                metadata={},
            )
        except Exception as e:
            classify_and_raise_error("xai", e, self.api_key)

    def chat_with_tools(self, messages: list, tools: list) -> LLMResponse:
        """Send conversation with tool calling support."""
        from .tools.response import create_enhanced_response

        start_time = time.time()
        try:
            # Convert Tool objects to OpenAI format (XAI is OpenAI-compatible)
            xai_tools = [tool.to_openai_format() for tool in tools]

            response = self.client.chat.completions.create(
                model=self.model, messages=messages, max_tokens=1000, tools=xai_tools
            )

            latency = time.time() - start_time

            # Use enhanced response to extract tool calls (use openai extraction)
            enhanced = create_enhanced_response(response, "openai")

            return LLMResponse(
                content=enhanced.content,
                provider="xai",
                model=self.model,
                latency=latency,
                usage={
                    "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(
                        response.usage, "completion_tokens", 0
                    ),
                },
                metadata={
                    "tool_calls": enhanced.tool_calls,
                    "finish_reason": enhanced.finish_reason,
                    "raw_response": response,
                },
            )
        except Exception as e:
            classify_and_raise_error("xai", e, self.api_key)

    def is_available(self) -> bool:
        return self.api_key is not None


class SarvamProvider(BaseProvider):
    """Provider for Sarvam AI models."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__(api_key or os.getenv("SARVAM_API_KEY"), model)
        if not self.api_key:
            raise ConfigurationError(
                "SARVAM_API_KEY not found in environment variables"
            )

        self.base_url = "https://api.sarvam.ai/v1"

    def query(self, prompt: str, **kwargs) -> LLMResponse:
        """Query Sarvam AI models.

        Supports:
        - sarvam-m (Sarvam-M): Chat model (24B parameter)
        - mayura: Translation model
        - sarvam-translate: Translation service
        """
        start_time = time.time()

        try:
            import requests

            # Determine endpoint based on model
            if self.model in ["mayura", "sarvam-translate"]:
                # Translation models
                endpoint = f"{self.base_url}/translate"
                payload = {
                    "input": prompt,
                    "source_language_code": kwargs.get("source_language", "en-IN"),
                    "target_language_code": kwargs.get("target_language", "hi-IN"),
                    "model": self.model,
                    "enable_preprocessing": kwargs.get("enable_preprocessing", True),
                }
            else:
                # Chat model (sarvam-2b / Sarvam-M)
                endpoint = f"{self.base_url}/chat/completions"
                payload = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": kwargs.get("max_tokens", 4000),
                }

            headers = {
                "api-subscription-key": self.api_key,
                "Content-Type": "application/json",
            }

            response = requests.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()

            latency = time.time() - start_time
            result = response.json()

            # Extract content based on model type
            if self.model in ["mayura", "sarvam-translate"]:
                content = result.get("translated_text", "")
            else:
                content = (
                    result.get("choices", [{}])[0].get("message", {}).get("content", "")
                )

            # Extract usage info if available
            usage = {}
            if "usage" in result:
                usage = result["usage"]

            return LLMResponse(
                content=content,
                provider="sarvam",
                model=self.model,
                latency=latency,
                usage=usage,
                metadata={
                    "endpoint": endpoint,
                    "model_type": (
                        "translation"
                        if self.model in ["mayura", "sarvam-translate"]
                        else "chat"
                    ),
                },
            )
        except Exception as e:
            classify_and_raise_error("sarvam", e, self.api_key)

    def chat(self, messages: list, **kwargs) -> LLMResponse:
        """Send conversation with full message history (for chat models only)."""
        start_time = time.time()

        try:
            import requests

            if self.model in ["mayura", "sarvam-translate"]:
                raise ProviderError(
                    "sarvam", "Translation models do not support chat method"
                )

            endpoint = f"{self.base_url}/chat/completions"
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 4000),
            }

            headers = {
                "api-subscription-key": self.api_key,
                "Content-Type": "application/json",
            }

            response = requests.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()

            latency = time.time() - start_time
            result = response.json()

            content = (
                result.get("choices", [{}])[0].get("message", {}).get("content", "")
            )
            usage = result.get("usage", {})

            return LLMResponse(
                content=content,
                provider="sarvam",
                model=self.model,
                latency=latency,
                usage=usage,
                metadata={"endpoint": endpoint, "model_type": "chat"},
            )
        except Exception as e:
            classify_and_raise_error("sarvam", e, self.api_key)

    def is_available(self) -> bool:
        return self.api_key is not None
