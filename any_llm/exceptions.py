"""Exception classes for any-llm."""


class AnyLLMError(Exception):
    """Base exception for any-llm."""
    pass


class ProviderError(AnyLLMError):
    """Exception raised when a provider fails."""
    
    def __init__(self, provider: str, message: str):
        self.provider = provider
        super().__init__(f"Provider '{provider}' error: {message}")


class ConfigurationError(AnyLLMError):
    """Exception raised for configuration errors."""
    pass


class AllProvidersFailedError(AnyLLMError):
    """Exception raised when all providers fail."""
    pass