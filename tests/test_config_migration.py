"""Configuration migrations for provider defaults."""

import yaml

from llmswap.config import LLMSwapConfig


def test_legacy_defaults_migrate_and_custom_choices_survive(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "provider": {
                    "default": "openai",
                    "fallback_order": ["anthropic", "openai", "gemini"],
                    "models": {
                        "openai": "gpt-4o-mini",
                        "gemini": "gemini-2.0-flash-exp",
                        "perplexity": "sonar",
                        "ollama": "granite-code:8b",
                        "sarvam": "sarvam-m",
                    },
                }
            }
        )
    )

    config = LLMSwapConfig(str(config_path))

    assert config.get("config_version") == 2
    assert config.get("provider.models.openai") == "gpt-5.6"
    assert config.get("provider.models.gemini") == "gemini-3.6-flash"
    assert config.get("provider.models.sarvam") == "sarvam-105b"
    assert config.get("provider.models.perplexity") == "sonar"
    assert config.get("provider.models.ollama") == "granite-code:8b"
    assert set(config.get("provider.fallback_order")) == {
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
    }
    assert (tmp_path / "config.yaml.pre-v2.bak").exists()


def test_current_config_is_not_rewritten(tmp_path):
    config_path = tmp_path / "config.yaml"
    original = {
        "config_version": 2,
        "provider": {"models": {"openai": "my-custom-model"}},
    }
    config_path.write_text(yaml.safe_dump(original))

    config = LLMSwapConfig(str(config_path))

    assert config.get("provider.models.openai") == "my-custom-model"
    assert not (tmp_path / "config.yaml.pre-v2.bak").exists()
