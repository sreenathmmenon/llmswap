"""User-facing exception rendering regressions."""

from llmswap.exceptions import AuthenticationError


def test_authentication_help_renders_provider_name():
    message = str(AuthenticationError("openai"))

    assert "LLMClient(provider='openai', api_key='your-key')" in message
    assert "{self.provider}" not in message
