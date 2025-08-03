"""Basic usage examples for llmswap."""

from llmswap import LLMClient

def basic_example():
    """Simple usage with auto-detection."""
    print("=== Basic Example ===")
    
    # Auto-detect provider from environment variables
    client = LLMClient()
    
    print(f"Using provider: {client.get_current_provider()}")
    print(f"Using model: {client.get_current_model()}")
    
    # Simple query
    response = client.query("What is Python programming language?")
    
    print(f"Response: {response.content[:100]}...")
    print(f"Provider: {response.provider}")
    print(f"Latency: {response.latency:.2f}s")
    print()


def provider_switching_example():
    """Example of switching between providers."""
    print("=== Provider Switching Example ===")
    
    # Start with auto-detection
    client = LLMClient()
    print(f"Auto-detected provider: {client.get_current_provider()}")
    
    # List available providers
    available = client.list_available_providers()
    print(f"Available providers: {available}")
    
    # Try different providers
    for provider in available[:2]:  # Try first 2 available providers
        try:
            client.set_provider(provider)
            response = client.query("Say hello in a creative way")
            
            print(f"\n{provider.upper()}:")
            print(f"Response: {response.content[:80]}...")
            print(f"Latency: {response.latency:.2f}s")
            
        except Exception as e:
            print(f"Error with {provider}: {e}")
    
    print()


def custom_model_example():
    """Example with custom models."""
    print("=== Custom Model Example ===")
    
    # Use specific provider and model
    try:
        client = LLMClient(provider="anthropic", model="claude-3-sonnet-20240229")
        
        response = client.query("Explain machine learning in one sentence")
        
        print(f"Provider: {response.provider}")
        print(f"Model: {response.model}")
        print(f"Response: {response.content}")
        print(f"Metadata: {response.metadata}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure ANTHROPIC_API_KEY is set in environment")
    
    print()


def fallback_example():
    """Example of fallback behavior."""
    print("=== Fallback Example ===")
    
    # Enable fallback (default)
    client = LLMClient(fallback=True)
    
    print(f"Primary provider: {client.get_current_provider()}")
    
    # This will automatically fallback if primary provider fails
    try:
        response = client.query("What is artificial intelligence?")
        print(f"Success with: {response.provider}")
        print(f"Response: {response.content[:100]}...")
    except Exception as e:
        print(f"All providers failed: {e}")
    
    print()


def metadata_example():
    """Example of response metadata."""
    print("=== Metadata Example ===")
    
    client = LLMClient()
    
    queries = [
        "Hello",
        "What is the capital of France?",
        "Explain quantum computing",
        "Write a haiku about programming"
    ]
    
    for query in queries:
        try:
            response = client.query(query)
            
            print(f"Query: {query}")
            print(f"  Provider: {response.provider}")
            print(f"  Model: {response.model}")
            print(f"  Latency: {response.latency:.2f}s")
            print(f"  Metadata: {response.metadata}")
            print()
        except Exception as e:
            print(f"Error with query '{query}': {e}")
    
    print()


if __name__ == "__main__":
    print("llmswap Basic Usage Examples")
    print("=" * 40)
    
    try:
        basic_example()
        provider_switching_example() 
        custom_model_example()
        fallback_example()
        metadata_example()
        
    except Exception as e:
        print(f"Setup error: {e}")
        print("\nMake sure you have at least one API key set:")
        print("- ANTHROPIC_API_KEY")
        print("- OPENAI_API_KEY") 
        print("- GEMINI_API_KEY")
        print("Or run Ollama locally")
    
    print("Examples completed!")