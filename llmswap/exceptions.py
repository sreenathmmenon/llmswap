"""Exception classes for llmswap."""


class LLMSwapError(Exception):
    """Base exception for llmswap."""

    pass


class ProviderError(LLMSwapError):
    """Exception raised when a provider fails."""

    def __init__(
        self,
        provider: str,
        message: str,
        error_type: str = "unknown",
        status_code: int = None,
        context: dict = None,
    ):
        self.provider = provider
        self.error_type = error_type
        self.safe_message = message
        self.status_code = status_code
        self.context = context or {}
        super().__init__(f"Provider '{provider}' error: {message}")

    def __str__(self):
        """Enhanced error message with helpful context."""
        msg = f"\n❌ {self.error_type.replace('_', ' ').title()} ({self.provider})\n"
        msg += f"   {self.safe_message}\n"

        # Add helpful hints based on error type
        if self.error_type == "rate_limit":
            msg += "\n💡 Quick fixes:\n"
            msg += "   • Wait a few seconds and retry\n"
            msg += "   • Switch provider: client.set_provider('openai')\n"
            msg += "   • Enable fallback: LLMClient(fallback=True)\n"
        elif self.error_type == "authentication":
            msg += "\n💡 Fix authentication:\n"
            msg += (
                f"   • Set API key: export {self.provider.upper()}_API_KEY=your-key\n"
            )
            msg += (
                "   • Or: LLMClient(provider='{self.provider}', api_key='your-key')\n"
            )
        elif self.error_type == "timeout":
            msg += "\n💡 Try:\n"
            msg += "   • Retry the request\n"
            msg += "   • Use a different model\n"
            msg += "   • Reduce prompt length\n"

        return msg


class RateLimitError(ProviderError):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, provider: str, message: str = None, retry_after: int = None):
        msg = message or f"Rate limit exceeded"
        if retry_after:
            msg += f". Retry after {retry_after} seconds"
        super().__init__(provider, msg, error_type="rate_limit")
        self.retry_after = retry_after


class AuthenticationError(ProviderError):
    """Exception raised for authentication failures."""

    def __init__(self, provider: str, message: str = None):
        msg = message or "Authentication failed. Check your API key"
        super().__init__(provider, msg, error_type="authentication")


class TimeoutError(ProviderError):
    """Exception raised when request times out."""

    def __init__(self, provider: str, message: str = None):
        msg = message or "Request timed out"
        super().__init__(provider, msg, error_type="timeout")


class InvalidRequestError(ProviderError):
    """Exception raised for invalid requests."""

    def __init__(self, provider: str, message: str):
        super().__init__(provider, message, error_type="invalid_request")


class QuotaExceededError(ProviderError):
    """Exception raised when quota is exceeded."""

    def __init__(self, provider: str, message: str = None):
        msg = message or "API quota exceeded"
        super().__init__(provider, msg, error_type="quota_exceeded")


class ConfigurationError(LLMSwapError):
    """Exception raised for configuration errors."""

    pass


class AllProvidersFailedError(LLMSwapError):
    """Exception raised when all providers fail."""

    pass
