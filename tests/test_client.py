import pytest
import os
from llmswap import LLMClient
from llmswap.exceptions import ConfigurationError


def test_client_initialization():
    """Test that client can be initialized"""
    if not any(
        [
            os.getenv("ANTHROPIC_API_KEY"),
            os.getenv("OPENAI_API_KEY"),
            os.getenv("GEMINI_API_KEY"),
        ]
    ):
        pytest.skip("No API keys available")
    client = LLMClient()
    assert client is not None


def test_client_with_specific_provider():
    """Test client with specific provider"""
    client = LLMClient(provider="openai", api_key="test-key")
    assert client.get_current_provider() == "openai"


def test_client_provider_detection(setup_anthropic_env):
    """Test automatic provider detection"""
    client = LLMClient()
    assert client.get_current_provider() == "anthropic"


def test_client_provider_switching():
    """Test switching between providers"""
    client = LLMClient(provider="openai", api_key="test-key")
    assert client.get_current_provider() == "openai"

    client.set_provider("gemini", api_key="test-gemini-key")
    assert client.get_current_provider() == "gemini"


def test_client_fallback_disabled():
    """Test client with fallback disabled"""
    if not any(
        [
            os.getenv("ANTHROPIC_API_KEY"),
            os.getenv("OPENAI_API_KEY"),
            os.getenv("GEMINI_API_KEY"),
        ]
    ):
        pytest.skip("No API keys available")
    client = LLMClient(fallback=False)
    assert client.fallback == False


def test_list_available_providers(setup_anthropic_env, setup_openai_env):
    """Test listing available providers"""
    client = LLMClient()
    providers = client.list_available_providers()
    assert "anthropic" in providers
    assert "openai" in providers


def test_is_provider_available():
    """Test checking provider availability"""
    if not any(
        [
            os.getenv("ANTHROPIC_API_KEY"),
            os.getenv("OPENAI_API_KEY"),
            os.getenv("GEMINI_API_KEY"),
        ]
    ):
        pytest.skip("No API keys available")
    client = LLMClient(provider="openai", api_key="test-key")
    assert client.is_provider_available("openai") == True


def test_no_providers_error(mock_env_vars):
    """Test error when no providers available"""
    with pytest.raises(ConfigurationError):
        client = LLMClient()
        client.query("test")


def test_client_with_custom_model():
    """Test client with custom model"""
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OpenAI API key not available")
    client = LLMClient(provider="openai", api_key="test-key", model="gpt-4")
    # Client created successfully with custom model
    assert client is not None
