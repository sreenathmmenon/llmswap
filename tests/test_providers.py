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
    provider = AnthropicProvider(api_key="test-key")
    assert provider.api_key == "test-key"
    assert provider.model is None  # No default when not specified


def test_openai_provider_initialization():
    """Test OpenAI provider initialization (Nov 2025 models)"""
    provider = OpenAIProvider(api_key="test-key")
    assert provider.api_key == "test-key"
    assert provider.model is None  # No default when not specified


def test_gemini_provider_initialization():
    """Test Gemini provider initialization (Nov 2025 models)"""
    provider = GeminiProvider(api_key="test-key")
    assert provider.api_key == "test-key"
    assert provider.model is None  # No default when not specified


def test_ollama_provider_initialization():
    """Test Ollama provider initialization"""
    provider = OllamaProvider()
    assert provider.model is None  # No default when not specified


def test_anthropic_provider_custom_model():
    """Test Anthropic provider with latest model (Nov 2025)"""
    provider = AnthropicProvider(api_key="test-key", model="claude-opus-4-5")
    assert provider.model == "claude-opus-4-5"


def test_openai_provider_custom_model():
    """Test OpenAI provider with latest model (Nov 2025)"""
    provider = OpenAIProvider(api_key="test-key", model="gpt-5.1")
    assert provider.model == "gpt-5.1"


def test_provider_query_method_exists():
    """Test that all providers have query method"""
    providers = [
        AnthropicProvider(api_key="test"),
        OpenAIProvider(api_key="test"),
        GeminiProvider(api_key="test"),
        OllamaProvider(),
    ]

    for provider in providers:
        assert hasattr(provider, "query")
        assert callable(provider.query)
