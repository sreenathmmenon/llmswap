"""Exception classes for llmswap."""


class LLMSwapError(Exception):
    """Base exception for llmswap."""
    pass


class ProviderError(LLMSwapError):
    """Exception raised when a provider fails."""
    
    def __init__(self, provider: str, message: str):
        self.provider = provider
        super().__init__(f"Provider '{provider}' error: {message}")


class ConfigurationError(LLMSwapError):
    """Exception raised for configuration errors."""
    pass


class AllProvidersFailedError(LLMSwapError):
    """Exception raised when all providers fail."""
    pass