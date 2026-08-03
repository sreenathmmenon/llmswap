import pytest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from llmswap.providers import (
    AnthropicProvider,
    OpenAIProvider,
    GeminiProvider,
    OllamaProvider,
    classify_and_raise_error,
)
from llmswap.exceptions import InvalidRequestError
from llmswap.tools import Tool


def test_anthropic_provider_initialization():
    """Test Anthropic provider initialization (Nov 2025 models)"""
    provider = AnthropicProvider(api_key="a" * 32)
    assert provider.api_key == "a" * 32
    assert provider.model is None  # No default when not specified


def test_openai_provider_initialization():
    """Test OpenAI provider initialization (Nov 2025 models)"""
    provider = OpenAIProvider(api_key="o" * 32)
    assert provider.api_key == "o" * 32
    assert provider.model is None  # No default when not specified


def test_gemini_provider_initialization():
    """Test Gemini provider initialization (Nov 2025 models)"""
    provider = GeminiProvider(api_key="g" * 32)
    assert provider.api_key == "g" * 32
    assert provider.model is None  # No default when not specified


def test_ollama_provider_initialization():
    """Test Ollama provider initialization"""
    provider = OllamaProvider()
    assert provider.model is None  # No default when not specified


def test_anthropic_provider_custom_model():
    """Test Anthropic provider with current Sonnet model"""
    provider = AnthropicProvider(api_key="a" * 32, model="claude-sonnet-5")
    assert provider.model == "claude-sonnet-5"


def test_openai_provider_custom_model():
    """Test OpenAI provider with current flagship model"""
    provider = OpenAIProvider(api_key="o" * 32, model="gpt-5.6")
    assert provider.model == "gpt-5.6"


def test_provider_query_method_exists():
    """Test that all providers have query method"""
    providers = [
        AnthropicProvider(api_key="a" * 32),
        OpenAIProvider(api_key="o" * 32),
        GeminiProvider(api_key="g" * 32),
        OllamaProvider(),
    ]

    for provider in providers:
        assert hasattr(provider, "query")
        assert callable(provider.query)


def test_openai_current_models_use_completion_token_parameter():
    provider = OpenAIProvider(api_key="o" * 32, model="gpt-5.6")
    provider.client = Mock()
    provider.client.chat.completions.create.return_value = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content="ok"), finish_reason="stop"
            )
        ],
        usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
    )

    provider.query("hello")

    kwargs = provider.client.chat.completions.create.call_args.kwargs
    assert kwargs["max_completion_tokens"] == 4000
    assert "max_tokens" not in kwargs


def test_openai_gpt5_tool_calls_disable_reasoning_for_chat_completions():
    provider = OpenAIProvider(api_key="o" * 32, model="gpt-5.6")
    provider.client = Mock()
    provider.client.chat.completions.create.return_value = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content="ok", tool_calls=[]),
                finish_reason="stop",
            )
        ],
        usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
    )
    tool = Tool(
        name="list_files",
        description="List files",
        parameters={},
    )

    provider.chat_with_tools([{"role": "user", "content": "list files"}], [tool])

    kwargs = provider.client.chat.completions.create.call_args.kwargs
    assert kwargs["reasoning_effort"] == "none"


def test_invalid_request_error_is_not_misclassified_as_authentication():
    error = Exception(
        "Error code: 400 - {'error': {'type': 'invalid_request_error', "
        "'message': 'Function tools are not supported'}}"
    )

    with pytest.raises(InvalidRequestError):
        classify_and_raise_error("openai", error, "o" * 32)


def test_gemini_uses_google_genai_models_api():
    provider = GeminiProvider(api_key="g" * 32, model="gemini-3.6-flash")
    provider.client = Mock()
    provider.client.models.generate_content.return_value = SimpleNamespace(
        text="ok", usage_metadata=None
    )

    response = provider.query("hello")

    assert response.content == "ok"
    provider.client.models.generate_content.assert_called_once_with(
        model="gemini-3.6-flash", contents="hello"
    )
