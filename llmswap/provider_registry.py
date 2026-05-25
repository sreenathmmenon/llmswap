"""Central provider metadata for llmswap."""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class ProviderSpec:
    """Metadata shared by clients, config, verification, and docs."""

    name: str
    default_model: str
    env_key: Optional[str]
    sync_class: str
    async_class: str
    supports_tools: bool = False
    supports_chat: bool = True
    optional_extra: Optional[str] = None


PROVIDER_SPECS: Dict[str, ProviderSpec] = {
    "anthropic": ProviderSpec(
        name="anthropic",
        default_model="claude-sonnet-4-20250514",
        env_key="ANTHROPIC_API_KEY",
        sync_class="AnthropicProvider",
        async_class="AsyncAnthropicProvider",
        supports_tools=True,
    ),
    "openai": ProviderSpec(
        name="openai",
        default_model="gpt-5.2",
        env_key="OPENAI_API_KEY",
        sync_class="OpenAIProvider",
        async_class="AsyncOpenAIProvider",
        supports_tools=True,
    ),
    "gemini": ProviderSpec(
        name="gemini",
        default_model="gemini-3-pro-preview",
        env_key="GEMINI_API_KEY",
        sync_class="GeminiProvider",
        async_class="AsyncGeminiProvider",
        supports_tools=True,
    ),
    "cohere": ProviderSpec(
        name="cohere",
        default_model="command-a-plus-05-2026",
        env_key="COHERE_API_KEY",
        sync_class="CoherProvider",
        async_class="AsyncCoherProvider",
    ),
    "perplexity": ProviderSpec(
        name="perplexity",
        default_model="sonar-pro",
        env_key="PERPLEXITY_API_KEY",
        sync_class="PerplexityProvider",
        async_class="AsyncPerplexityProvider",
    ),
    "watsonx": ProviderSpec(
        name="watsonx",
        default_model="ibm/granite-3-3-8b-instruct",
        env_key="WATSONX_API_KEY",
        sync_class="WatsonxProvider",
        async_class="AsyncWatsonxProvider",
        optional_extra="watsonx",
    ),
    "groq": ProviderSpec(
        name="groq",
        default_model="openai/gpt-oss-120b",
        env_key="GROQ_API_KEY",
        sync_class="GroqProvider",
        async_class="AsyncGroqProvider",
        supports_tools=True,
    ),
    "ollama": ProviderSpec(
        name="ollama",
        default_model="llama3.1",
        env_key=None,
        sync_class="OllamaProvider",
        async_class="AsyncOllamaProvider",
    ),
    "xai": ProviderSpec(
        name="xai",
        default_model="grok-4.3",
        env_key="XAI_API_KEY",
        sync_class="XAIProvider",
        async_class="AsyncXAIProvider",
        supports_tools=True,
    ),
    "sarvam": ProviderSpec(
        name="sarvam",
        default_model="sarvam-105b",
        env_key="SARVAM_API_KEY",
        sync_class="SarvamProvider",
        async_class="AsyncSarvamProvider",
    ),
}

PROVIDER_ORDER: List[str] = list(PROVIDER_SPECS.keys())
DEFAULT_PROVIDER_MODELS: Dict[str, str] = {
    name: spec.default_model for name, spec in PROVIDER_SPECS.items()
}


def get_provider_spec(provider_name: str) -> ProviderSpec:
    """Return provider metadata or raise KeyError for unknown providers."""
    return PROVIDER_SPECS[provider_name]


def get_provider_names() -> List[str]:
    """Return providers in fallback/auto-detection order."""
    return list(PROVIDER_ORDER)
