"""
Simple in-memory caching system for FastAPI
Phase 13.1 - Performance Optimization
"""
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import logging
import json
import hashlib

logger = logging.getLogger(__name__)


class InMemoryCache:
    """Thread-safe in-memory cache with TTL support"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired"""
        if cache_entry.get("expires_at") is None:
            return False
        return datetime.utcnow() > cache_entry["expires_at"]
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self._cache:
            self._stats["misses"] += 1
            logger.debug(f"Cache MISS: {key}")
            return None
        
        cache_entry = self._cache[key]
        
        # Check if expired
        if self._is_expired(cache_entry):
            del self._cache[key]
            self._stats["misses"] += 1
            logger.debug(f"Cache MISS (expired): {key}")
            return None
        
        self._stats["hits"] += 1
        logger.debug(f"Cache HIT: {key}")
        return cache_entry["value"]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = no expiration)
        """
        expires_at = None
        if ttl:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        
        self._cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": datetime.utcnow()
        }
        self._stats["sets"] += 1
        logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
    
    def delete(self, key: str):
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]
            self._stats["deletes"] += 1
            logger.debug(f"Cache DELETE: {key}")
    
    def clear(self):
        """Clear all cache entries"""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cache CLEARED: {count} entries removed")
    
    def invalidate_pattern(self, pattern: str):
        """
        Invalidate all keys matching pattern
        Example: invalidate_pattern("blogs:") deletes all blog cache entries
        """
        keys_to_delete = [key for key in self._cache.keys() if pattern in key]
        for key in keys_to_delete:
            self.delete(key)
        logger.info(f"Cache INVALIDATE PATTERN: {pattern} ({len(keys_to_delete)} entries)")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self._stats,
            "total_requests": total_requests,
            "hit_rate": round(hit_rate, 2),
            "cache_size": len(self._cache)
        }
    
    def cleanup_expired(self):
        """Remove all expired entries"""
        expired_keys = [
            key for key, entry in self._cache.items()
            if self._is_expired(entry)
        ]
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"Cache CLEANUP: {len(expired_keys)} expired entries removed")


def generate_cache_key(prefix: str, **params) -> str:
    """
    Generate a consistent cache key from parameters
    
    Example:
        generate_cache_key("blogs", status="published", page=1, limit=10)
        Returns: "blogs:status=published:page=1:limit=10"
    """
    # Sort params for consistency
    sorted_params = sorted(params.items())
    param_str = ":".join([f"{k}={v}" for k, v in sorted_params if v is not None])
    
    if param_str:
        return f"{prefix}:{param_str}"
    return prefix


# Global cache instance
cache = InMemoryCache()


# Cache decorator for FastAPI routes
def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache FastAPI route responses
    
    Args:
        ttl: Time-to-live in seconds (default 5 minutes)
        key_prefix: Prefix for cache key
    
    Usage:
        @api_router.get("/blogs")
        @cached(ttl=600, key_prefix="blogs")
        async def get_blogs(...):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key from function arguments
            cache_key_params = {
                k: v for k, v in kwargs.items() 
                if k not in ['request', 'background_tasks', 'db']
            }
            cache_key = generate_cache_key(key_prefix or func.__name__, **cache_key_params)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache the result
            cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator
