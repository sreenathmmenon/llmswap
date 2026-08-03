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
    assert DEFAULT_PROVIDER_MODELS["anthropic"] == "claude-sonnet-5"
    assert DEFAULT_PROVIDER_MODELS["openai"] == "gpt-5.6"
    assert DEFAULT_PROVIDER_MODELS["gemini"] == "gemini-3.6-flash"
    assert DEFAULT_PROVIDER_MODELS["watsonx"] == "ibm/granite-4-h-small"
    assert DEFAULT_PROVIDER_MODELS["ollama"] == "qwen3.5:9b"
    assert DEFAULT_PROVIDER_MODELS["xai"] == "grok-4.5"
    assert DEFAULT_PROVIDER_MODELS["sarvam"] == "sarvam-105b"
