"""
Memory-based caching for LLM responses with TTL and size limits.
"""

import hashlib
import json
import threading
import time
from typing import Any, Dict, Optional
import sys


class InMemoryCache:
    """Memory-based cache for LLM responses with TTL and size limits"""
    
    def __init__(self, max_memory_mb: int = 100, default_ttl: int = 3600):
        """
        Initialize the in-memory cache.
        
        Args:
            max_memory_mb: Maximum memory usage in megabytes
            default_ttl: Default time-to-live in seconds
        """
        # Response storage with hash keys
        self._responses = {}
        # Expiry timestamps for cached entries
        self._expiry_map = {}
        # Access count for statistics
        self._access_count = {}
        # Memory limit in bytes
        self._memory_limit = max_memory_mb * 1024 * 1024
        # Current memory usage
        self._current_size = 0
        # Default TTL
        self._default_ttl = default_ttl
        # Thread safety
        self._lock = threading.Lock()
        # Cache statistics
        self._hits = 0
        self._misses = 0
        
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a cached response if it exists and hasn't expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached response data or None if not found/expired
        """
        with self._lock:
            if key not in self._responses:
                self._misses += 1
                return None
                
            # Check expiry
            if time.time() > self._expiry_map[key]:
                # Entry has expired
                self._remove_entry(key)
                self._misses += 1
                return None
            
            # Valid cache hit
            self._hits += 1
            self._access_count[key] = self._access_count.get(key, 0) + 1
            return self._responses[key]
    
    def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Store a response in cache with TTL.
        
        Args:
            key: Cache key
            value: Response data to cache
            ttl: Time-to-live in seconds (uses default if not specified)
            
        Returns:
            True if stored successfully, False if size limit exceeded
        """
        ttl = ttl if ttl is not None else self._default_ttl
        
        # Estimate size of new entry
        entry_size = sys.getsizeof(key) + sys.getsizeof(value)
        
        with self._lock:
            # Check if adding this would exceed memory limit
            if self._current_size + entry_size > self._memory_limit:
                # Try to make room by removing least accessed entries
                self._evict_least_accessed()
                
                # Check again after eviction
                if self._current_size + entry_size > self._memory_limit:
                    return False
            
            # Remove old entry if it exists
            if key in self._responses:
                self._remove_entry(key)
            
            # Store new entry
            self._responses[key] = value
            self._expiry_map[key] = time.time() + ttl
            self._access_count[key] = 0
            self._current_size += entry_size
            
            return True
    
    def invalidate(self, key: str) -> bool:
        """
        Remove a specific entry from cache.
        
        Args:
            key: Cache key to invalidate
            
        Returns:
            True if entry was removed, False if not found
        """
        with self._lock:
            if key in self._responses:
                self._remove_entry(key)
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._responses.clear()
            self._expiry_map.clear()
            self._access_count.clear()
            self._current_size = 0
            self._hits = 0
            self._misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 2),
                "entries": len(self._responses),
                "memory_used_mb": round(self._current_size / (1024 * 1024), 2),
                "memory_limit_mb": self._memory_limit / (1024 * 1024)
            }
    
    def _remove_entry(self, key: str) -> None:
        """Remove an entry from cache (internal use only)."""
        if key in self._responses:
            entry_size = sys.getsizeof(key) + sys.getsizeof(self._responses[key])
            del self._responses[key]
            del self._expiry_map[key]
            if key in self._access_count:
                del self._access_count[key]
            self._current_size -= entry_size
    
    def _evict_least_accessed(self) -> None:
        """Evict least recently accessed entries to make room."""
        if not self._responses:
            return
        
        # Sort by access count and remove least accessed
        sorted_keys = sorted(self._access_count.keys(), key=lambda k: self._access_count[k])
        
        # Remove bottom 20% or at least one entry
        remove_count = max(1, len(sorted_keys) // 5)
        
        for key in sorted_keys[:remove_count]:
            self._remove_entry(key)
    
    @staticmethod
    def create_cache_key(prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a cache key from prompt and optional context.
        
        Args:
            prompt: The prompt text
            context: Optional context dictionary (e.g., user_id, session_id)
            
        Returns:
            SHA256 hash as cache key
        """
        if context:
            # Include context in cache key
            key_data = f"{prompt}:{json.dumps(context, sort_keys=True)}"
        else:
            key_data = prompt
        
        return hashlib.sha256(key_data.encode()).hexdigest()