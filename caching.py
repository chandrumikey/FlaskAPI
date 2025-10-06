import time
from typing import Any, Optional
from functools import wraps

class MemoryCache:
    def __init__(self):
        self._cache = {}
    
    def get(self, key: str) -> Any:
        if key in self._cache:
            data, expiry = self._cache[key]
            if expiry is None or time.time() < expiry:
                return data
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        expiry = time.time() + ttl if ttl else None
        self._cache[key] = (value, expiry)
    
    def delete(self, key: str):
        if key in self._cache:
            del self._cache[key]
    
    def clear(self):
        self._cache.clear()

class RedisCache:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        try:
            import redis
            self.redis = redis.from_url(redis_url)
        except ImportError:
            raise RuntimeError("Redis required: pip install redis")
    
    def get(self, key: str) -> Any:
        return self.redis.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        self.redis.set(key, value, ex=ttl)
    
    def delete(self, key: str):
        self.redis.delete(key)

def cache(ttl: int = 300, key_func: Optional[callable] = None):
    """Caching decorator for route handlers"""
    def decorator(handler):
        @wraps(handler)
        async def wrapper(request, *args, **kwargs):
            cache_instance = request.app.cache
            if not cache_instance:
                return await handler(request, *args, **kwargs)
            
            # Generate cache key
            if key_func:
                cache_key = key_func(request, *args, **kwargs)
            else:
                cache_key = f"{request.path}:{request.method}:{str(request.query_params)}"
            
            # Try cache first
            cached_result = cache_instance.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute handler and cache result
            result = await handler(request, *args, **kwargs)
            cache_instance.set(cache_key, result, ttl=ttl)
            
            return result
        return wrapper
    return decorator