"""Provider verification regressions."""

from unittest.mock import Mock, patch

from llmswap.response import LLMResponse
from llmswap.verification import verify_provider


def test_provider_verification_disables_fallback(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "g" * 32)
    client = Mock()
    client.query.return_value = LLMResponse(
        content="OK", provider="gemini", model="gemini-3.6-flash"
    )

    with patch("llmswap.verification.LLMClient", return_value=client) as client_class:
        result = verify_provider("gemini")

    client_class.assert_called_once_with(
        provider="gemini",
        fallback=False,
        cache_enabled=False,
        workspace_enabled=False,
    )
    assert result["api_key_valid"] is True
    assert result["model"] == "gemini-3.6-flash"
