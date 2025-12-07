"""
Dynamic model configuration for LLMSwap Web UI.

Allows users to customize available models via:
1. Default models (built-in, December 2025)
2. Config file (~/.llmswap/models.json)
3. Environment variable (LLMSWAP_CUSTOM_MODELS)

Copyright (c) 2025 Sreenath M Menon
Licensed under the MIT License
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any


# December 2025 - Latest models across all providers
DEFAULT_MODELS = {
    "openai": [
        {
            "id": "gpt-5.1",
            "name": "GPT-5.1",
            "description": "OpenAI • Latest Flagship Dec 2025",
            "featured": True,
            "pricing": {"input": 5.0, "output": 20.0},
        },
        {
            "id": "gpt-4.5-turbo",
            "name": "GPT-4.5 Turbo",
            "description": "OpenAI • Fast & Smart",
            "featured": True,
            "pricing": {"input": 3.0, "output": 12.0},
        },
        {
            "id": "o1",
            "name": "o1",
            "description": "OpenAI • Advanced Reasoning",
            "featured": True,
            "pricing": {"input": 15.0, "output": 60.0},
        },
        {
            "id": "gpt-4o",
            "name": "GPT-4o",
            "description": "OpenAI • Fast & Multimodal",
            "pricing": {"input": 2.5, "output": 10.0},
        },
        {
            "id": "gpt-4o-mini",
            "name": "GPT-4o Mini",
            "description": "OpenAI • Fast & Cheap",
            "pricing": {"input": 0.15, "output": 0.60},
        },
        {
            "id": "o1-mini",
            "name": "o1 Mini",
            "description": "OpenAI • Fast Reasoning",
            "pricing": {"input": 3.0, "output": 12.0},
        },
    ],
    "anthropic": [
        {
            "id": "claude-opus-4-5",
            "name": "Claude Opus 4.5",
            "description": "Anthropic • Best Quality Dec 2025",
            "featured": True,
            "pricing": {"input": 15.0, "output": 75.0},
        },
        {
            "id": "claude-sonnet-4-5",
            "name": "Claude Sonnet 4.5",
            "description": "Anthropic • Best for Coding",
            "featured": True,
            "pricing": {"input": 3.0, "output": 15.0},
        },
        {
            "id": "claude-haiku-4-5",
            "name": "Claude Haiku 4.5",
            "description": "Anthropic • Fast & Cheap",
            "featured": True,
            "pricing": {"input": 1.0, "output": 5.0},
        },
        {
            "id": "claude-3-5-sonnet-20241022",
            "name": "Claude Sonnet 3.5",
            "description": "Anthropic • Previous Version",
            "pricing": {"input": 3.0, "output": 15.0},
        },
    ],
    "google": [
        {
            "id": "gemini-3-pro",
            "name": "Gemini 3 Pro",
            "description": "Google • Latest Flagship Dec 2025",
            "featured": True,
            "pricing": {"input": 2.5, "output": 10.0},
        },
        {
            "id": "gemini-3-deep-think",
            "name": "Gemini 3 Deep Think",
            "description": "Google • Advanced Reasoning",
            "featured": True,
            "pricing": {"input": 3.5, "output": 14.0},
        },
        {
            "id": "gemini-2.5-flash",
            "name": "Gemini 2.5 Flash",
            "description": "Google • Fast & Efficient",
            "featured": True,
            "pricing": {"input": 0.075, "output": 0.30},
        },
        {
            "id": "gemini-1.5-pro",
            "name": "Gemini 1.5 Pro",
            "description": "Google • Previous Generation",
            "pricing": {"input": 1.25, "output": 5.0},
        },
        {
            "id": "gemini-1.5-flash",
            "name": "Gemini 1.5 Flash",
            "description": "Google • Fast",
            "pricing": {"input": 0.075, "output": 0.30},
        },
    ],
    "xai": [
        {
            "id": "grok-4.1",
            "name": "Grok 4.1 🏆",
            "description": "xAI • #1 LMArena Dec 2025",
            "featured": True,
            "pricing": {"input": 5.0, "output": 15.0},
        },
        {
            "id": "grok-4-fast",
            "name": "Grok 4 Fast",
            "description": "xAI • Ultra Speed",
            "featured": True,
            "pricing": {"input": 2.5, "output": 10.0},
        },
        {
            "id": "grok-4",
            "name": "Grok 4",
            "description": "xAI • Balanced",
            "pricing": {"input": 5.0, "output": 15.0},
        },
    ],
    "groq": [
        {
            "id": "llama-4-70b",
            "name": "Llama 4 70B",
            "description": "Groq • Meta Latest Dec 2025",
            "featured": True,
            "pricing": {"input": 0.10, "output": 0.10},
        },
        {
            "id": "deepseek-v3",
            "name": "DeepSeek v3",
            "description": "Groq • GPT-5 Competitor",
            "featured": True,
            "pricing": {"input": 0.10, "output": 0.10},
        },
        {
            "id": "llama-3.3-70b-versatile",
            "name": "Llama 3.3 70B",
            "description": "Groq • Ultra Fast",
            "pricing": {"input": 0.10, "output": 0.10},
        },
        {
            "id": "llama-3.1-8b-instant",
            "name": "Llama 3.1 8B",
            "description": "Groq • Fastest",
            "pricing": {"input": 0.05, "output": 0.05},
        },
        {
            "id": "mixtral-8x7b-32768",
            "name": "Mixtral 8x7B",
            "description": "Groq • Balanced",
            "pricing": {"input": 0.10, "output": 0.10},
        },
    ],
    "perplexity": [
        {
            "id": "sonar-pro",
            "name": "Sonar Pro",
            "description": "Perplexity • Search-Enhanced",
            "featured": True,
            "pricing": {"input": 3.0, "output": 15.0},
        },
        {
            "id": "sonar",
            "name": "Sonar",
            "description": "Perplexity • Standard",
            "pricing": {"input": 1.0, "output": 5.0},
        },
    ],
    "cohere": [
        {
            "id": "command-r-plus",
            "name": "Command R+",
            "description": "Cohere • Latest Dec 2025",
            "featured": True,
            "pricing": {"input": 3.0, "output": 15.0},
        },
        {
            "id": "command-r",
            "name": "Command R",
            "description": "Cohere • Balanced",
            "pricing": {"input": 0.50, "output": 1.50},
        },
    ],
    "ollama": [
        {
            "id": "llama3.3",
            "name": "Llama 3.3 (Local)",
            "description": "Ollama • Free, Self-hosted",
            "featured": True,
            "pricing": {"input": 0, "output": 0},
        },
        {
            "id": "mistral",
            "name": "Mistral (Local)",
            "description": "Ollama • Free, Fast",
            "pricing": {"input": 0, "output": 0},
        },
        {
            "id": "deepseek-r1",
            "name": "DeepSeek R1 (Local)",
            "description": "Ollama • Reasoning Model",
            "pricing": {"input": 0, "output": 0},
        },
    ],
}


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
    1. Start with DEFAULT_MODELS (December 2025 latest)
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
