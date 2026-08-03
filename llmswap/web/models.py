"""
Dynamic model configuration for LLMSwap Web UI.

Allows users to customize available models via:
1. Default models (built-in, August 2026)
2. Config file (~/.llmswap/models.json)
3. Environment variable (LLMSWAP_CUSTOM_MODELS)

Copyright (c) 2025 Sreenath M Menon
Licensed under the MIT License
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any

# Audited against provider documentation on 2026-08-03. Prices are USD per
# million input/output tokens and exclude provider-specific search/tool fees.
DEFAULT_MODELS = {
    "openai": [
        {
            "id": "gpt-5.6",
            "name": "GPT-5.6 Sol",
            "description": "OpenAI • Frontier model",
            "featured": True,
            "pricing": {"input": 5.0, "output": 30.0},
            "status": "stable",
        },
        {
            "id": "gpt-5.6-terra",
            "name": "GPT-5.6 Terra",
            "description": "OpenAI • Balanced frontier model",
            "featured": True,
            "pricing": {"input": 2.5, "output": 15.0},
            "status": "stable",
        },
        {
            "id": "gpt-5.6-luna",
            "name": "GPT-5.6 Luna",
            "description": "OpenAI • Fast and economical",
            "featured": True,
            "pricing": {"input": 1.0, "output": 6.0},
            "status": "stable",
        },
        {
            "id": "gpt-5.5",
            "name": "GPT-5.5",
            "description": "OpenAI • Previous frontier generation",
            "pricing": {"input": 5.0, "output": 30.0},
            "status": "stable",
        },
        {
            "id": "gpt-5.4",
            "name": "GPT-5.4",
            "description": "OpenAI • General-purpose reasoning",
            "pricing": {"input": 2.5, "output": 15.0},
            "status": "stable",
        },
        {
            "id": "gpt-5.4-mini",
            "name": "GPT-5.4 Mini",
            "description": "OpenAI • Efficient reasoning",
            "pricing": {"input": 0.75, "output": 4.50},
            "status": "stable",
        },
        {
            "id": "gpt-4.1",
            "name": "GPT-4.1",
            "description": "OpenAI • Non-reasoning model",
            "pricing": {"input": 2.0, "output": 8.0},
            "status": "stable",
        },
    ],
    "anthropic": [
        {
            "id": "claude-sonnet-5",
            "name": "Claude Sonnet 5",
            "description": "Anthropic • Balanced frontier model",
            "featured": True,
            "pricing": {"input": 3.0, "output": 15.0},
            "status": "stable",
        },
        {
            "id": "claude-opus-5",
            "name": "Claude Opus 5",
            "description": "Anthropic • Most capable",
            "featured": True,
            "pricing": {"input": 5.0, "output": 25.0},
            "status": "stable",
        },
        {
            "id": "claude-fable-5",
            "name": "Claude Fable 5",
            "description": "Anthropic • Premium model",
            "pricing": {"input": 10.0, "output": 50.0},
            "status": "stable",
        },
        {
            "id": "claude-sonnet-4-6",
            "name": "Claude Sonnet 4.6",
            "description": "Anthropic • Previous Sonnet generation",
            "pricing": {"input": 3.0, "output": 15.0},
            "status": "stable",
        },
        {
            "id": "claude-haiku-4-5",
            "name": "Claude Haiku 4.5",
            "description": "Anthropic • Fast and economical",
            "pricing": {"input": 1.0, "output": 5.0},
            "status": "stable",
        },
    ],
    "google": [
        {
            "id": "gemini-3.6-flash",
            "name": "Gemini 3.6 Flash",
            "description": "Google • Recommended multimodal model",
            "featured": True,
            "pricing": {"input": 1.50, "output": 7.50},
            "status": "stable",
        },
        {
            "id": "gemini-3.5-flash",
            "name": "Gemini 3.5 Flash",
            "description": "Google • General-purpose multimodal",
            "featured": True,
            "pricing": {"input": 1.50, "output": 9.0},
            "status": "stable",
        },
        {
            "id": "gemini-3.5-flash-lite",
            "name": "Gemini 3.5 Flash-Lite",
            "description": "Google • Low-cost multimodal",
            "featured": True,
            "pricing": {"input": 0.30, "output": 2.50},
            "status": "stable",
        },
        {
            "id": "gemini-3.1-pro-preview",
            "name": "Gemini 3.1 Pro Preview",
            "description": "Google • Advanced reasoning preview",
            "pricing": {"input": 2.0, "output": 12.0},
            "status": "preview",
        },
    ],
    "xai": [
        {
            "id": "grok-4.5",
            "name": "Grok 4.5",
            "description": "xAI • Current flagship",
            "featured": True,
            "pricing": {"input": 2.0, "output": 6.0},
            "status": "stable",
        },
        {
            "id": "grok-4.3",
            "name": "Grok 4.3",
            "description": "xAI • Previous generation",
            "pricing": {"input": 1.25, "output": 2.50},
            "status": "stable",
        },
    ],
    "groq": [
        {
            "id": "openai/gpt-oss-120b",
            "name": "GPT-OSS 120B",
            "description": "Groq • Production Open-Weight",
            "featured": True,
            "pricing": {"input": 0.15, "output": 0.60},
            "status": "stable",
        },
        {
            "id": "openai/gpt-oss-20b",
            "name": "GPT-OSS 20B",
            "description": "Groq • Fast Open-Weight",
            "featured": True,
            "pricing": {"input": 0.075, "output": 0.30},
            "status": "stable",
        },
        {
            "id": "qwen/qwen3.6-27b",
            "name": "Qwen 3.6 27B",
            "description": "Groq • Fast preview model",
            "pricing": {"input": 0.60, "output": 3.0},
            "status": "preview",
        },
    ],
    "perplexity": [
        {
            "id": "sonar",
            "name": "Sonar",
            "description": "Perplexity • Search-enhanced",
            "pricing": {"input": 1.0, "output": 1.0},
            "status": "stable",
        },
        {
            "id": "sonar-pro",
            "name": "Sonar Pro",
            "description": "Perplexity • Advanced search",
            "featured": True,
            "pricing": {"input": 3.0, "output": 15.0},
            "status": "stable",
        },
        {
            "id": "sonar-reasoning-pro",
            "name": "Sonar Reasoning Pro",
            "description": "Perplexity • Search with reasoning",
            "pricing": {"input": 2.0, "output": 8.0},
            "status": "stable",
        },
        {
            "id": "sonar-deep-research",
            "name": "Sonar Deep Research",
            "description": "Perplexity • Multi-step research",
            "pricing": {"input": 2.0, "output": 8.0},
            "status": "stable",
        },
    ],
    "cohere": [
        {
            "id": "command-a-plus-05-2026",
            "name": "Command A+",
            "description": "Cohere • Agentic Multimodal",
            "featured": True,
            "pricing": {"input": 0, "output": 0},
            "status": "stable",
        },
        {
            "id": "command-a-03-2025",
            "name": "Command A",
            "description": "Cohere • Enterprise agentic model",
            "pricing": {"input": 2.5, "output": 10.0},
            "status": "stable",
        },
        {
            "id": "command-a-reasoning-08-2025",
            "name": "Command A Reasoning",
            "description": "Cohere • Reasoning model",
            "pricing": {"input": 2.5, "output": 10.0},
            "status": "stable",
        },
    ],
    "ollama": [
        {
            "id": "qwen3.5:9b",
            "name": "Qwen 3.5 9B (Local)",
            "description": "Ollama • Free, Self-hosted",
            "featured": True,
            "pricing": {"input": 0, "output": 0},
            "status": "local",
        },
        {
            "id": "gpt-oss:20b",
            "name": "GPT-OSS 20B (Local)",
            "description": "Ollama • Local open-weight model",
            "pricing": {"input": 0, "output": 0},
            "status": "local",
        },
        {
            "id": "deepseek-r1:8b",
            "name": "DeepSeek R1 8B (Local)",
            "description": "Ollama • Reasoning Model",
            "pricing": {"input": 0, "output": 0},
            "status": "local",
        },
    ],
    "watsonx": [
        {
            "id": "ibm/granite-4-h-small",
            "name": "Granite 4 H Small",
            "description": "IBM watsonx • Current IBM model",
            "featured": True,
            "pricing": {"input": 0.0636, "output": 0.265},
            "status": "stable",
        },
    ],
    "sarvam": [
        {
            "id": "sarvam-105b",
            "name": "Sarvam 105B",
            "description": "Sarvam AI • Indic Frontier",
            "featured": True,
            "pricing": {"input": 0.50, "output": 1.50},
            "status": "stable",
        },
        {
            "id": "sarvam-30b",
            "name": "Sarvam 30B",
            "description": "Sarvam AI • Efficient Indic model",
            "pricing": {"input": 0.25, "output": 0.75},
            "status": "stable",
        },
    ],
}


def get_model_provider(model_id: str) -> str:
    """Resolve a built-in model ID to the llmswap provider name.

    Exact catalog lookup is important for IDs such as ``openai/gpt-oss-120b``:
    the same model family can be served by Groq or watsonx, so substring-based
    routing alone is ambiguous. Custom models should be passed with an explicit
    provider.
    """
    matches = []
    for provider, models in DEFAULT_MODELS.items():
        if any(model["id"] == model_id for model in models):
            matches.append("gemini" if provider == "google" else provider)

    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        # Groq is the established default host for the shared GPT-OSS ID.
        return "groq" if "groq" in matches else matches[0]

    lowered = model_id.lower()
    prefixes = {
        "claude": "anthropic",
        "gemini": "gemini",
        "grok": "xai",
        "sonar": "perplexity",
        "command": "cohere",
        "sarvam": "sarvam",
        "ibm/": "watsonx",
        "gpt": "openai",
        "o1": "openai",
        "o3": "openai",
        "o4": "openai",
    }
    for prefix, provider in prefixes.items():
        if lowered.startswith(prefix):
            return provider
    return "ollama"


def get_config_path() -> Path:
    """Get path to user config file."""
    config_dir = Path.home() / ".llmswap"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "models.json"


def load_custom_models() -> Dict[str, List[Dict]]:
    """Load custom models from config file."""
    config_path = get_config_path()

    if not config_path.exists():
        return {}

    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not load custom models: {e}")
        return {}


def load_env_models() -> List[Dict]:
    """Load custom models from environment variable."""
    env_models = os.getenv("LLMSWAP_CUSTOM_MODELS")

    if not env_models:
        return []

    try:
        return json.loads(env_models)
    except json.JSONDecodeError as e:
        print(f"Warning: Invalid LLMSWAP_CUSTOM_MODELS format: {e}")
        return []


def merge_models(base: Dict, custom: Dict) -> Dict:
    """Merge custom models with base models."""
    result = base.copy()

    for provider, models in custom.items():
        if provider not in result:
            result[provider] = []

        # Add custom models with custom flag
        for model in models:
            model["custom"] = True
            result[provider].append(model)

    return result


def get_available_models() -> Dict[str, List[Dict]]:
    """
    Get all available models.

    Priority:
    1. Start with DEFAULT_MODELS (August 2026 audit)
    2. Load custom models from ~/.llmswap/models.json
    3. Load custom models from LLMSWAP_CUSTOM_MODELS env var
    4. Merge all together

    Returns:
        Dict mapping provider name to list of model configs
    """
    models = DEFAULT_MODELS.copy()

    # Load from config file
    custom_file = load_custom_models()
    if custom_file:
        models = merge_models(models, custom_file)

    # Load from environment
    env_models = load_env_models()
    if env_models:
        # Group env models by provider
        env_by_provider = {}
        for model in env_models:
            provider = model.get("provider", "custom")
            if provider not in env_by_provider:
                env_by_provider[provider] = []
            env_by_provider[provider].append(model)

        models = merge_models(models, env_by_provider)

    return models


def save_custom_model(provider: str, model: Dict):
    """
    Save a custom model to config file.

    Args:
        provider: Provider name (e.g., "openai", "custom")
        model: Model configuration dict
    """
    config_path = get_config_path()

    # Load existing
    if config_path.exists():
        with open(config_path, "r") as f:
            models = json.load(f)
    else:
        models = {}

    # Add new model
    if provider not in models:
        models[provider] = []

    # Mark as custom
    model["custom"] = True
    models[provider].append(model)

    # Save
    with open(config_path, "w") as f:
        json.dump(models, f, indent=2)


def remove_custom_model(provider: str, model_id: str) -> bool:
    """
    Remove a custom model from config file.

    Args:
        provider: Provider name
        model_id: Model ID to remove

    Returns:
        True if removed, False if not found
    """
    config_path = get_config_path()

    if not config_path.exists():
        return False

    with open(config_path, "r") as f:
        models = json.load(f)

    if provider not in models:
        return False

    # Remove model
    original_len = len(models[provider])
    models[provider] = [m for m in models[provider] if m.get("id") != model_id]

    if len(models[provider]) == original_len:
        return False  # Not found

    # Save
    with open(config_path, "w") as f:
        json.dump(models, f, indent=2)

    return True


def get_featured_models() -> List[Dict]:
    """Get list of featured models (shown by default in UI)."""
    all_models = get_available_models()
    featured = []

    for provider, models in all_models.items():
        for model in models:
            if model.get("featured"):
                model["provider"] = provider
                featured.append(model)

    return featured


def get_model_pricing(model_id: str) -> Dict[str, float]:
    """
    Get pricing for a specific model.

    Args:
        model_id: Model identifier

    Returns:
        Dict with 'input' and 'output' pricing per 1M tokens
    """
    all_models = get_available_models()

    for provider, models in all_models.items():
        for model in models:
            if model["id"] == model_id:
                return model.get("pricing", {"input": 0, "output": 0})

    # Default pricing if not found
    return {"input": 3.0, "output": 15.0}
