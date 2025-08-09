"""Basic tests for async functionality."""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llmswap import AsyncLLMClient


async def test_async_query():
    """Test basic async query."""
    print("Testing async query with Ollama...")
    
    try:
        client = AsyncLLMClient(provider="ollama", model="granite-code:8b")
        response = await client.query("Say hello in one word")
        print(f"Response: {response.content}")
        print(f"Provider: {response.provider}")
        print(f"Model: {response.model}")
        print(f"Latency: {response.latency:.2f}s")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


async def test_async_streaming():
    """Test async streaming."""
    print("\nTesting async streaming with Ollama...")
    
    try:
        client = AsyncLLMClient(provider="ollama", model="granite-code:8b")
        print("Streaming response: ", end="", flush=True)
        
        chunk_count = 0
        async for chunk in client.stream("Count from 1 to 5"):
            print(chunk, end="", flush=True)
            chunk_count += 1
        
        print(f"\n(Received {chunk_count} chunks)")
        return True
    except Exception as e:
        print(f"\nStreaming error: {e}")
        return False


async def test_logging():
    """Test logging functionality."""
    print("\nTesting logging...")
    
    log_file = "/tmp/llmswap_test.log"
    
    try:
        client = AsyncLLMClient(
            provider="ollama",
            model="granite-code:8b",
            log_file=log_file,
            log_level="info"
        )
        
        response = await client.query("What is 2+2?")
        print(f"Response: {response.content}")
        
        # Check if log file was created
        if os.path.exists(log_file):
            print(f"Log file created: {log_file}")
            with open(log_file, 'r') as f:
                logs = f.readlines()
                print(f"Log entries: {len(logs)}")
                if logs:
                    print("Sample log entry:", logs[0][:100] + "...")
            return True
        else:
            print("Log file not created")
            return False
            
    except Exception as e:
        print(f"Logging error: {e}")
        return False


async def test_provider_list():
    """Test listing available providers."""
    print("\nTesting provider detection...")
    
    try:
        client = AsyncLLMClient()
        providers = client.list_available_providers()
        print(f"Available providers: {providers}")
        
        current = client.get_current_provider()
        print(f"Current provider: {current}")
        return True
    except Exception as e:
        print(f"Provider detection error: {e}")
        return False


async def main():
    """Run all async tests."""
    print("=" * 50)
    print("Testing llmswap v2.0 Async Features")
    print("=" * 50)
    
    results = []
    
    # Test basic async query
    results.append(await test_async_query())
    
    # Test streaming
    results.append(await test_async_streaming())
    
    # Test logging
    results.append(await test_logging())
    
    # Test provider detection
    results.append(await test_provider_list())
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {sum(results)}/{len(results)}")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())