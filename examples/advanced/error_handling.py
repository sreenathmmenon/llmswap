"""
Error Handling Example

Demonstrates comprehensive error handling with LLMSwap's enhanced exceptions.

Before running:
    # Intentionally use wrong API key to see errors
    export ANTHROPIC_API_KEY=wrong-key
"""

from llmswap import LLMClient
from llmswap import (
    RateLimitError,
    AuthenticationError,
    TimeoutError,
    InvalidRequestError,
    QuotaExceededError,
    ProviderError,
    AllProvidersFailedError
)
import time


def main():
    """Demonstrate error handling patterns."""
    
    # Example 1: Handle authentication errors
    print("=== Example 1: Authentication Error Handling ===")
    try:
        # This will fail if API key is wrong
        client = LLMClient(provider="anthropic", api_key="wrong-key")
        response = client.query("Hello")
    except AuthenticationError as e:
        print(f"Auth failed: {e}")
        print("Switching to another provider...")
        # Fallback to another provider
        client = LLMClient(provider="openai")
    
    print()
    
    # Example 2: Handle rate limits with retry
    print("=== Example 2: Rate Limit Handling ===")
    
    def query_with_retry(client, prompt, max_retries=3):
        """Retry on rate limits with exponential backoff."""
        for attempt in range(max_retries):
            try:
                return client.query(prompt)
            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = e.retry_after or (2 ** attempt)
                    print(f"Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                raise
        return None
    
    try:
        response = query_with_retry(client, "What is 2+2?")
        print(response)
    except RateLimitError as e:
        print(f"Still rate limited after retries: {e}")
    
    print()
    
    # Example 3: Catch all provider errors
    print("=== Example 3: General Provider Error Handling ===")
    try:
        client = LLMClient(provider="anthropic")
        response = client.query("Test query")
    except ProviderError as e:
        print(f"Provider error: {e}")
        print(f"Error type: {e.error_type}")
        print(f"Provider: {e.provider}")
        if e.status_code:
            print(f"Status code: {e.status_code}")
    
    print()
    
    # Example 4: Multiple providers with fallback
    print("=== Example 4: Automatic Fallback ===")
    try:
        # Enable automatic fallback
        client = LLMClient(fallback=True)
        response = client.query("Hello!")
        print(f"Success with {client.current_provider}")
    except AllProvidersFailedError as e:
        print(f"All providers failed: {e}")
        print("Check your API keys!")
    
    print()
    
    # Example 5: Specific error handling
    print("=== Example 5: Specific Error Types ===")
    
    providers = ["anthropic", "openai", "gemini"]
    
    for provider in providers:
        try:
            print(f"Trying {provider}...")
            client = LLMClient(provider=provider)
            response = client.query("Quick test")
            print(f"✓ {provider} works!")
            break
        except AuthenticationError:
            print(f"✗ {provider}: Authentication failed")
        except RateLimitError:
            print(f"✗ {provider}: Rate limited")
        except TimeoutError:
            print(f"✗ {provider}: Timeout")
        except ProviderError as e:
            print(f"✗ {provider}: {e.error_type}")
    
    print()
    
    # Example 6: Error context
    print("=== Example 6: Error Context ===")
    try:
        client = LLMClient(provider="anthropic")
        response = client.query("Test")
    except ProviderError as e:
        print(f"Error: {e.safe_message}")
        if e.context:
            print(f"Context: {e.context}")
    
    print("\n✅ Error handling examples complete!")


if __name__ == "__main__":
    main()
