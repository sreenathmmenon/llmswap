"""
Security utilities for llmswap.
Original implementation for API key protection in error messages.
"""

import re
from typing import Optional


def remove_sensitive_data(text: str, key_to_hide: Optional[str] = None) -> str:
    """
    Clean sensitive information from text.

    Args:
        text: Text that might contain API keys
        key_to_hide: Specific key to remove if known

    Returns:
        Cleaned text with sensitive data replaced
    """
    if not text:
        return text

    result = str(text)

    # Remove Anthropic keys
    result = re.sub(r"sk-ant-api\d+-[\w-]+", "[HIDDEN]", result, flags=re.I)

    # Remove OpenAI keys
    result = re.sub(r"sk-proj-[\w-]+", "[HIDDEN]", result, flags=re.I)
    result = re.sub(r"sk-[\w]{20,}", "[HIDDEN]", result, flags=re.I)

    # Remove Groq keys
    result = re.sub(r"gsk_[\w-]+", "[HIDDEN]", result, flags=re.I)

    # Remove Google keys
    result = re.sub(r"AIza[\w-]+", "[HIDDEN]", result, flags=re.I)

    # Remove Perplexity keys
    result = re.sub(r"pplx-[\w-]+", "[HIDDEN]", result, flags=re.I)

    # Remove xAI keys
    result = re.sub(r"xai-[\w-]+", "[HIDDEN]", result, flags=re.I)

    # Remove Bearer tokens
    result = re.sub(r"Bearer\s+[\w.-]+", "Bearer [HIDDEN]", result, flags=re.I)

    # If specific key provided, remove it too
    if key_to_hide and len(key_to_hide) > 8:
        result = result.replace(key_to_hide, "[HIDDEN]")

    return result


def safe_error_string(error: Exception, api_key: Optional[str] = None) -> str:
    """
    Convert exception to safe string for display.

    Args:
        error: The exception
        api_key: API key to remove if present

    Returns:
        Safe error string
    """
    return remove_sensitive_data(str(error), api_key)
