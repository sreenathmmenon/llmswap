"""
Test caching functionality in llmswap v2.1.0
"""

import time
import os
from llmswap import LLMClient

def test_basic_caching():
    """Test basic caching functionality"""
    print("Testing basic caching...")
    
    # Create client with caching enabled
    client = LLMClient(cache_enabled=True, cache_ttl=60)
    
    # First query - should hit API
    print("\nFirst query (API call)...")
    start = time.time()
    response1 = client.query("What is 2+2?")
    time1 = time.time() - start
    print(f"Response: {response1.content[:50]}...")
    print(f"From cache: {response1.from_cache}")
    print(f"Time: {time1:.2f}s")
    
    # Second query - should be from cache
    print("\nSecond query (from cache)...")
    start = time.time()
    response2 = client.query("What is 2+2?")
    time2 = time.time() - start
    print(f"Response: {response2.content[:50]}...")
    print(f"From cache: {response2.from_cache}")
    print(f"Time: {time2:.2f}s")
    
    # Verify cache is working
    assert response2.from_cache == True, "Second query should be from cache"
    assert time2 < time1, "Cached response should be faster"
    print(f"\nCache speedup: {time1/time2:.1f}x faster")
    
    # Get cache stats
    stats = client.get_cache_stats()
    print(f"\nCache stats: {stats}")

def test_cache_context():
    """Test context-aware caching"""
    print("\n\nTesting context-aware caching...")
    
    client = LLMClient(cache_enabled=True)
    
    # Query with user context
    print("\nUser 1 query...")
    response1 = client.query(
        "Hello",
        cache_context={"user_id": "user1"}
    )
    print(f"Response: {response1.content[:50]}...")
    
    # Same query, different user - should not hit cache
    print("\nUser 2 query (different context)...")
    response2 = client.query(
        "Hello",
        cache_context={"user_id": "user2"}
    )
    print(f"From cache: {response2.from_cache}")
    
    # Same query, same user - should hit cache
    print("\nUser 1 query again (same context)...")
    response3 = client.query(
        "Hello",
        cache_context={"user_id": "user1"}
    )
    print(f"From cache: {response3.from_cache}")

def test_cache_bypass():
    """Test cache bypass functionality"""
    print("\n\nTesting cache bypass...")
    
    client = LLMClient(cache_enabled=True)
    
    # Initial query
    print("\nInitial query...")
    response1 = client.query("What time is it?")
    print(f"From cache: {response1.from_cache}")
    
    # Query with bypass
    print("\nQuery with cache bypass...")
    response2 = client.query("What time is it?", cache_bypass=True)
    print(f"From cache: {response2.from_cache}")
    
    # Normal query - should hit cache
    print("\nNormal query (should hit cache)...")
    response3 = client.query("What time is it?")
    print(f"From cache: {response3.from_cache}")

def test_cache_management():
    """Test cache management functions"""
    print("\n\nTesting cache management...")
    
    client = LLMClient(cache_enabled=True)
    
    # Add some cached responses
    client.query("Test 1")
    client.query("Test 2")
    client.query("Test 3")
    
    # Check stats
    stats = client.get_cache_stats()
    print(f"\nCache entries: {stats['entries']}")
    
    # Invalidate specific entry
    removed = client.invalidate_cache("Test 2")
    print(f"Removed 'Test 2': {removed}")
    
    # Clear all cache
    client.clear_cache()
    stats = client.get_cache_stats()
    print(f"After clear - entries: {stats['entries']}")

if __name__ == "__main__":
    # Check if any API key is available
    has_key = any([
        os.getenv("ANTHROPIC_API_KEY"),
        os.getenv("OPENAI_API_KEY"),
        os.getenv("GEMINI_API_KEY")
    ])
    
    if not has_key:
        print("No API key found. Set one of:")
        print("  export ANTHROPIC_API_KEY=...")
        print("  export OPENAI_API_KEY=...")
        print("  export GEMINI_API_KEY=...")
        exit(1)
    
    try:
        test_basic_caching()
        test_cache_context()
        test_cache_bypass()
        test_cache_management()
        print("\n\nAll caching tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()