import pytest
import os
from llmswap import LLMClient
from llmswap.exceptions import ConfigurationError
from llmswap.response import LLMResponse


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
    client = LLMClient(provider="openai", api_key="o" * 32)
    assert client.get_current_provider() == "openai"


def test_client_provider_detection(setup_anthropic_env):
    """Test automatic provider detection"""
    client = LLMClient()
    assert client.get_current_provider() == "anthropic"


def test_client_provider_switching():
    """Test switching between providers"""
    client = LLMClient(provider="openai", api_key="o" * 32)
    assert client.get_current_provider() == "openai"

    client.set_provider("gemini", api_key="g" * 32)
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
    client = LLMClient(provider="openai", api_key="o" * 32)
    assert client.is_provider_available("openai") == True


def test_no_providers_error(mock_env_vars, monkeypatch):
    """Test error when no providers available"""
    monkeypatch.setattr(
        "llmswap.providers.OllamaProvider.is_available", lambda self: False
    )
    with pytest.raises(ConfigurationError):
        client = LLMClient()
        client.query("test")


def test_client_with_custom_model():
    """Test client with custom model"""
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OpenAI API key not available")
    client = LLMClient(provider="openai", api_key="o" * 32, model="gpt-4")
    # Client created successfully with custom model
    assert client is not None


def test_chat_session_cost_uses_estimator_argument_order(monkeypatch, tmp_path):
    """Regression: token counts must not be passed as the provider name."""
    monkeypatch.setenv("HOME", str(tmp_path))

    class OpenAIProvider:
        model = "gpt-5.6"

        def chat(self, messages):
            return LLMResponse(
                content="answer",
                provider="openai",
                model=self.model,
                usage={"prompt_tokens": 100, "completion_tokens": 50},
            )

    client = LLMClient(
        provider="openai",
        api_key="o" * 32,
        model="gpt-5.6",
        analytics_enabled=True,
        workspace_enabled=False,
    )
    client.current_provider = OpenAIProvider()
    client.start_chat_session()

    response = client.chat("hello")

    assert response.content == "answer"
    assert client.get_session_tokens() == 150
    assert client._session_cost > 0
