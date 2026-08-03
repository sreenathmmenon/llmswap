"""Provider defaults audited for llmswap 5.7.0 on 2026-08-03."""

from llmswap import LLMClient
from llmswap.provider_registry import DEFAULT_PROVIDER_MODELS


def show_defaults():
    """Print the exact defaults shipped by the installed llmswap version."""
    for provider, model in DEFAULT_PROVIDER_MODELS.items():
        print(f"{provider:12} {model}")


def ask(provider: str, prompt: str):
    """Use the current default for a configured provider."""
    client = LLMClient(provider=provider)
    response = client.chat(prompt)
    print(f"[{provider} / {response.model}]\n{response.content}")


if __name__ == "__main__":
    show_defaults()
    # Uncomment after configuring the provider's API key:
    # ask("openai", "Explain why provider abstraction is useful in three bullets.")
