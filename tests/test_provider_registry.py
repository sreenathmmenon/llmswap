from llmswap.provider_registry import (
    DEFAULT_PROVIDER_MODELS,
    PROVIDER_SPECS,
    get_provider_names,
)


def test_registry_contains_all_supported_providers():
    assert get_provider_names() == [
        "anthropic",
        "openai",
        "gemini",
        "cohere",
        "perplexity",
        "watsonx",
        "groq",
        "ollama",
        "xai",
        "sarvam",
    ]


def test_default_models_are_defined_for_every_provider():
    assert set(DEFAULT_PROVIDER_MODELS) == set(PROVIDER_SPECS)
    assert DEFAULT_PROVIDER_MODELS["anthropic"] == "claude-sonnet-4-20250514"
    assert DEFAULT_PROVIDER_MODELS["openai"] == "gpt-5.2"
    assert DEFAULT_PROVIDER_MODELS["gemini"] == "gemini-3-pro-preview"
    assert DEFAULT_PROVIDER_MODELS["xai"] == "grok-4.3"
    assert DEFAULT_PROVIDER_MODELS["sarvam"] == "sarvam-105b"
