"""Test that v1.5 code still works with v2.0."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llmswap import LLMClient


def test_sync_client():
    """Test that synchronous client still works."""
    print("Testing backward compatibility...")
    
    try:
        # This is v1.5 style code - should still work
        client = LLMClient(provider="ollama", model="granite-code:8b")
        
        # Test basic query
        response = client.query("Say hello")
        print(f"Sync response: {response.content}")
        
        # Test provider switching
        current = client.get_current_provider()
        print(f"Current provider: {current}")
        
        # Test provider list
        available = client.list_available_providers()
        print(f"Available providers: {available}")
        
        print("Backward compatibility: PASSED")
        return True
        
    except Exception as e:
        print(f"Backward compatibility error: {e}")
        print("Backward compatibility: FAILED")
        return False


def test_imports():
    """Test that all exports are available."""
    print("\nTesting imports...")
    
    try:
        from llmswap import (
            LLMClient,
            AsyncLLMClient,
            LLMResponse,
            ConfigurationError,
            ProviderError
        )
        print("All imports successful")
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("Testing llmswap v2.0 Backward Compatibility")
    print("=" * 50)
    
    test_sync = test_sync_client()
    test_imp = test_imports()
    
    print("\n" + "=" * 50)
    if test_sync and test_imp:
        print("All backward compatibility tests PASSED")
    else:
        print("Some tests FAILED")
    print("=" * 50)