"""Regression tests for the audited built-in model catalog."""

from llmswap.provider_registry import DEFAULT_PROVIDER_MODELS
from llmswap.web.models import DEFAULT_MODELS, get_model_provider


def _model_ids(provider):
    catalog_provider = "google" if provider == "gemini" else provider
    return {model["id"] for model in DEFAULT_MODELS[catalog_provider]}


def test_every_provider_default_is_in_web_catalog():
    for provider, model in DEFAULT_PROVIDER_MODELS.items():
        assert model in _model_ids(provider), (provider, model)


def test_retired_models_are_not_built_in():
    all_ids = {
        model["id"]
        for provider_models in DEFAULT_MODELS.values()
        for model in provider_models
    }
    retired = {
        "claude-sonnet-4-20250514",
        "claude-opus-4-20250514",
        "gemini-3-pro-preview",
        "ibm/granite-3-3-8b-instruct",
        "mixtral-8x7b-32768",
        "command-r",
        "sarvam-m",
    }
    assert all_ids.isdisjoint(retired)


def test_shared_gpt_oss_id_routes_to_groq():
    assert get_model_provider("openai/gpt-oss-120b") == "groq"


def test_current_model_families_route_correctly():
    assert get_model_provider("gpt-5.6") == "openai"
    assert get_model_provider("claude-sonnet-5") == "anthropic"
    assert get_model_provider("gemini-3.6-flash") == "gemini"
    assert get_model_provider("grok-4.5") == "xai"
    assert get_model_provider("ibm/granite-4-h-small") == "watsonx"
    assert get_model_provider("qwen3.5:9b") == "ollama"


def test_catalog_and_cost_estimator_pricing_match(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    from llmswap.metrics.cost_estimator import CostEstimator

    pricing = CostEstimator().pricing
    for provider, models in DEFAULT_MODELS.items():
        metric_provider = "gemini" if provider == "google" else provider
        if metric_provider == "ollama":
            continue
        for model in models:
            rates = pricing[metric_provider][model["id"]]
            assert rates["input"] * 1000 == model["pricing"]["input"]
            assert rates["output"] * 1000 == model["pricing"]["output"]
