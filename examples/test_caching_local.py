"""
Test caching functionality locally without API keys
"""

import time
from llmswap import InMemoryCache

def test_cache_operations():
    """Test cache operations without API calls"""
    print("Testing InMemoryCache operations...")
    
    # Create cache instance
    cache = InMemoryCache(max_memory_mb=10, default_ttl=60)
    
    # Test set and get
    print("\n1. Testing set/get...")
    test_data = {"content": "Hello world", "provider": "test"}
    cache_key = InMemoryCache.create_cache_key("test prompt")
    
    # Store data
    stored = cache.set(cache_key, test_data)
    print(f"   Stored: {stored}")
    
    # Retrieve data
    retrieved = cache.get(cache_key)
    print(f"   Retrieved: {retrieved}")
    assert retrieved == test_data, "Retrieved data should match stored data"
    
    # Test cache hit/miss
    print("\n2. Testing cache statistics...")
    cache.get(cache_key)  # Hit
    cache.get("nonexistent")  # Miss
    stats = cache.get_stats()
    print(f"   Stats: {stats}")
    assert stats["hits"] == 2, "Should have 2 hits"
    assert stats["misses"] == 1, "Should have 1 miss"
    
    # Test context-aware keys
    print("\n3. Testing context-aware cache keys...")
    key1 = InMemoryCache.create_cache_key("prompt", {"user_id": "user1"})
    key2 = InMemoryCache.create_cache_key("prompt", {"user_id": "user2"})
    key3 = InMemoryCache.create_cache_key("prompt", {"user_id": "user1"})
    print(f"   Key1: {key1[:16]}...")
    print(f"   Key2: {key2[:16]}...")
    print(f"   Key3: {key3[:16]}...")
    assert key1 != key2, "Different contexts should produce different keys"
    assert key1 == key3, "Same context should produce same key"
    
    # Test TTL expiry
    print("\n4. Testing TTL expiry...")
    short_ttl_key = "short_ttl_test"
    cache.set(short_ttl_key, {"test": "data"}, ttl=1)
    
    # Should exist immediately
    assert cache.get(short_ttl_key) is not None, "Should exist immediately"
    print("   Data exists immediately after storage")
    
    # Wait for expiry
    time.sleep(1.5)
    assert cache.get(short_ttl_key) is None, "Should expire after TTL"
    print("   Data expired after TTL")
    
    # Test invalidation
    print("\n5. Testing cache invalidation...")
    test_key = "test_invalidate"
    cache.set(test_key, {"data": "test"})
    removed = cache.invalidate(test_key)
    print(f"   Removed: {removed}")
    assert cache.get(test_key) is None, "Should be removed after invalidation"
    
    # Test clear
    print("\n6. Testing cache clear...")
    cache.set("key1", {"a": 1})
    cache.set("key2", {"b": 2})
    cache.set("key3", {"c": 3})
    
    stats_before = cache.get_stats()
    print(f"   Entries before clear: {stats_before['entries']}")
    
    cache.clear()
    stats_after = cache.get_stats()
    print(f"   Entries after clear: {stats_after['entries']}")
    assert stats_after['entries'] == 0, "Cache should be empty after clear"
    
    # Test memory limit and eviction
    print("\n7. Testing memory limits...")
    small_cache = InMemoryCache(max_memory_mb=0.001, default_ttl=3600)  # Very small limit
    
    # Add entries until limit
    for i in range(100):
        small_cache.set(f"key_{i}", {"data": f"value_{i}" * 100})
    
    stats = small_cache.get_stats()
    print(f"   Memory used: {stats['memory_used_mb']:.3f} MB")
    print(f"   Memory limit: {stats['memory_limit_mb']:.3f} MB")
    assert stats['memory_used_mb'] <= stats['memory_limit_mb'], "Should not exceed memory limit"

if __name__ == "__main__":
    try:
        test_cache_operations()
        print("\nAll cache tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()