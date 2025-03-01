import time
import logging
from typing import Any, Optional, Dict, List, Union, Callable, TypeVar, Generic
from datetime import datetime, timedelta
from threading import Lock
from functools import wraps
import pickle
import hashlib
import json
from collections import OrderedDict
import asyncio
import zlib
from pydantic import BaseModel, Field

try:
    import redis
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class CacheConfig(BaseModel):
    ttl: int = Field(default=3600, description="Time to live in seconds")
    max_size: int = Field(default=1000, description="Maximum items in memory cache")
    redis_url: Optional[str] = Field(default=None, description="Redis connection URL")
    enable_memory_cache: bool = Field(default=True, description="Enable in-memory caching")
    enable_redis_cache: bool = Field(default=False, description="Enable Redis caching")
    compression: bool = Field(default=True, description="Enable data compression")
    namespace: str = Field(default="app", description="Cache namespace")
    
    class Config:
        validate_assignment = True

    @property
    def has_redis(self) -> bool:
        return REDIS_AVAILABLE and self.enable_redis_cache and self.redis_url is not None
    
    def validate_redis_connection(self) -> bool:
        if not self.has_redis:
            return False
            
        try:
            r = redis.Redis.from_url(self.redis_url)
            r.ping()
            return True
        except Exception as e:
            logging.error(f"Redis connection failed: {str(e)}")
            return False


class MemoryCache:
    def __init__(self, config: CacheConfig):
        self.config = config
        self.cache: OrderedDict = OrderedDict()
        self.lock = Lock()
        self.hits = 0
        self.misses = 0
    
    def _compress(self, data: Any) -> bytes:
        if not self.config.compression:
            return pickle.dumps(data)
        return zlib.compress(pickle.dumps(data))
    
    def _decompress(self, data: bytes) -> Any:
        if not self.config.compression:
            return pickle.loads(data)
        return pickle.loads(zlib.decompress(data))
    
    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None
                
            value, expiry = self.cache[key]
            
            if expiry and time.time() > expiry:
                del self.cache[key]
                self.misses += 1
                return None
                
            self.cache.move_to_end(key)
            self.hits += 1
            
            return self._decompress(value)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = ttl if ttl is not None else self.config.ttl
        expiry = time.time() + ttl if ttl > 0 else None
        
        with self.lock:
            if len(self.cache) >= self.config.max_size:
                self.cache.popitem(last=False)
                
            self.cache[key] = (self._compress(value), expiry)
    
    def delete(self, key: str) -> bool:
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> None:
        with self.lock:
            self.cache.clear()
    
    def stats(self) -> Dict[str, Any]:
        with self.lock:
            total = self.hits + self.misses
            hit_rate = self.hits / total if total > 0 else 0
            
            return {
                "size": len(self.cache),
                "max_size": self.config.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "compression": self.config.compression
            }


class RedisCache:
    def __init__(self, config: CacheConfig):
        self.config = config
        if not config.has_redis:
            raise ValueError("Redis is not available or not configured")
        self.client = redis.Redis.from_url(config.redis_url)
        self.hits = 0
        self.misses = 0
    
    def _get_key(self, key: str) -> str:
        return f"{self.config.namespace}:{key}"
    
    def _compress(self, data: Any) -> bytes:
        if not self.config.compression:
            return pickle.dumps(data)
        return zlib.compress(pickle.dumps(data))
    
    def _decompress(self, data: bytes) -> Any:
        if not self.config.compression:
            return pickle.loads(data)
        return pickle.loads(zlib.decompress(data))
    
    def get(self, key: str) -> Optional[Any]:
        redis_key = self._get_key(key)
        value = self.client.get(redis_key)
        
        if value is None:
            self.misses += 1
            return None
            
        self.hits += 1
        return self._decompress(value)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = ttl if ttl is not None else self.config.ttl
        redis_key = self._get_key(key)
        
        compressed_value = self._compress(value)
        if ttl > 0:
            self.client.setex(redis_key, ttl, compressed_value)
        else:
            self.client.set(redis_key, compressed_value)
    
    def delete(self, key: str) -> bool:
        redis_key = self._get_key(key)
        return bool(self.client.delete(redis_key))
    
    def clear(self) -> None:
        pattern = f"{self.config.namespace}:*"
        cursor = 0
        while True:
            cursor, keys = self.client.scan(cursor, pattern, 100)
            if keys:
                self.client.delete(*keys)
            if cursor == 0:
                break
    
    def stats(self) -> Dict[str, Any]:
        info = self.client.info()
        pattern = f"{self.config.namespace}:*"
        keys_count = len(self.client.keys(pattern))
        
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        
        return {
            "size": keys_count,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "redis_memory_used": info.get("used_memory_human", "N/A"),
            "redis_version": info.get("redis_version", "N/A"),
            "compression": self.config.compression
        }


class Cache:
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.memory_cache = MemoryCache(self.config) if self.config.enable_memory_cache else None
        
        if self.config.has_redis and self.config.enable_redis_cache:
            try:
                self.redis_cache = RedisCache(self.config)
            except Exception as e:
                logging.warning(f"Failed to initialize Redis cache: {str(e)}")
                self.redis_cache = None
        else:
            self.redis_cache = None
            
        if not self.memory_cache and not self.redis_cache:
            raise ValueError("No cache backends available. Enable at least one cache type.")
    
    def get(self, key: str) -> Optional[Any]:
        if self.redis_cache:
            value = self.redis_cache.get(key)
            if value is not None:
                return value
                
        if self.memory_cache:
            return self.memory_cache.get(key)
            
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if self.redis_cache:
            self.redis_cache.set(key, value, ttl)
            
        if self.memory_cache:
            self.memory_cache.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        result = False
        
        if self.redis_cache:
            result = self.redis_cache.delete(key) or result
            
        if self.memory_cache:
            result = self.memory_cache.delete(key) or result
            
        return result
    
    def clear(self) -> None:
        if self.redis_cache:
            self.redis_cache.clear()
            
        if self.memory_cache:
            self.memory_cache.clear()
    
    def stats(self) -> Dict[str, Any]:
        stats = {
            "config": {
                "ttl": self.config.ttl,
                "max_size": self.config.max_size,
                "namespace": self.config.namespace,
                "compression": self.config.compression
            },
            "backends": []
        }
        
        if self.memory_cache:
            stats["backends"].append({
                "type": "memory",
                "stats": self.memory_cache.stats()
            })
            
        if self.redis_cache:
            stats["backends"].append({
                "type": "redis",
                "stats": self.redis_cache.stats()
            })
            
        return stats


def cached(ttl: Optional[int] = None, key_prefix: Optional[str] = None, 
           cache_instance: Optional[Cache] = None):
    cache = cache_instance or Cache()
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key_parts = [key_prefix or func.__name__]
            
            for arg in args:
                key_parts.append(str(arg))
                
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}={v}")
                
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
                
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
            
        return wrapper
        
    return decorator


def async_cached(ttl: Optional[int] = None, key_prefix: Optional[str] = None,
                 cache_instance: Optional[Cache] = None):
    cache = cache_instance or Cache()
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key_parts = [key_prefix or func.__name__]
            
            for arg in args:
                key_parts.append(str(arg))
                
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}={v}")
                
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
                
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
            
        return wrapper
        
    return decorator