import pytest
from unittest.mock import Mock, patch
from llmswap.providers import (
    AnthropicProvider,
    OpenAIProvider,
    GeminiProvider,
    OllamaProvider,
)


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
    provider = AnthropicProvider(api_key="a" * 32, model="claude-sonnet-4-20250514")
    assert provider.model == "claude-sonnet-4-20250514"


def test_openai_provider_custom_model():
    """Test OpenAI provider with current flagship model"""
    provider = OpenAIProvider(api_key="o" * 32, model="gpt-5.2")
    assert provider.model == "gpt-5.2"


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
