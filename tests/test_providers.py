import pytest
from unittest.mock import Mock, patch
from llmswap.providers import (
    AnthropicProvider, 
    OpenAIProvider, 
    GeminiProvider,
    OllamaProvider
)

def test_anthropic_provider_initialization():
    """Test Anthropic provider initialization"""
    provider = AnthropicProvider(api_key="test-key")
    assert provider.api_key == "test-key"
    assert provider.default_model == "claude-3-sonnet-20240229"

def test_openai_provider_initialization():
    """Test OpenAI provider initialization"""
    provider = OpenAIProvider(api_key="test-key")
    assert provider.api_key == "test-key"
    assert provider.default_model == "gpt-3.5-turbo"

def test_gemini_provider_initialization():
    """Test Gemini provider initialization"""
    provider = GeminiProvider(api_key="test-key")
    assert provider.api_key == "test-key"
    assert provider.default_model == "gemini-1.5-flash"

def test_ollama_provider_initialization():
    """Test Ollama provider initialization"""
    provider = OllamaProvider()
    assert provider.base_url == "http://localhost:11434"
    assert provider.default_model == "llama2"

def test_anthropic_provider_custom_model():
    """Test Anthropic provider with custom model"""
    provider = AnthropicProvider(api_key="test-key", model="claude-3-opus-20240229")
    assert provider.model == "claude-3-opus-20240229"

def test_openai_provider_custom_model():
    """Test OpenAI provider with custom model"""
    provider = OpenAIProvider(api_key="test-key", model="gpt-4")
    assert provider.model == "gpt-4"

def test_provider_query_method_exists():
    """Test that all providers have query method"""
    providers = [
        AnthropicProvider(api_key="test"),
        OpenAIProvider(api_key="test"),
        GeminiProvider(api_key="test"),
        OllamaProvider()
    ]
    
    for provider in providers:
        assert hasattr(provider, 'query')
        assert callable(provider.query)