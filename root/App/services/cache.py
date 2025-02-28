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
    
logger = logging.getLogger(__name__)

T = TypeVar('T')

class CacheConfig(BaseModel):
    """Configuration for cache behavior."""
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

class CacheEntry(BaseModel, Generic[T]):
    """Cache entry with metadata."""
    key: str
    value: T
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    access_count: int = Field(default=0)
    last_accessed: datetime = Field(default_factory=datetime.now)
    size_bytes: Optional[int] = None

    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at

    def update_access(self) -> None:
        self.access_count += 1
        self.last_accessed = datetime.now()

class CacheStats(BaseModel):
    """Cache statistics."""
    memory_items: int = 0
    redis_items: int = 0
    memory_size_bytes: int = 0
    hit_count: int = 0
    miss_count: int = 0
    eviction_count: int = 0

class CacheService:
    """Advanced caching service with multi-level caching support."""
    
    def __init__(self, config: CacheConfig):
        """Initialize cache service with configuration."""
        self.config = config
        self._memory_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._cache_lock = Lock()
        self._redis_client: Optional[redis.Redis] = None
        self._async_redis_client: Optional[aioredis.Redis] = None
        self._stats = CacheStats()
        
        if config.has_redis:
            self._initialize_redis()

    def _initialize_redis(self) -> None:
        """Initialize Redis connection if configured."""
        if not REDIS_AVAILABLE:
            logger.warning("Redis support not available. Install 'redis' and 'aioredis' packages.")
            return

        try:
            self._redis_client = redis.from_url(
                self.config.redis_url,
                decode_responses=False,
                socket_timeout=5
            )
            self._redis_client.ping()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            self.config.enable_redis_cache = False

    async def _initialize_async_redis(self) -> None:
        """Initialize async Redis connection."""
        if not REDIS_AVAILABLE:
            return

        try:
            self._async_redis_client = await aioredis.from_url(
                self.config.redis_url,
                decode_responses=False,
                socket_timeout=5
            )
            await self._async_redis_client.ping()
            logger.info("Async Redis cache initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize async Redis: {e}")
            self.config.enable_redis_cache = False

    def _generate_key(self, key: str) -> str:
        """Generate namespaced cache key."""
        return f"{self.config.namespace}:{key}"

    def _compress_value(self, value: Any) -> bytes:
        """Compress value for storage."""
        serialized = pickle.dumps(value)
        if self.config.compression:
            return zlib.compress(serialized)
        return serialized

    def _decompress_value(self, compressed_value: bytes) -> Any:
        """Decompress stored value."""
        try:
            if self.config.compression:
                serialized = zlib.decompress(compressed_value)
            else:
                serialized = compressed_value
            return pickle.loads(serialized)
        except Exception as e:
            logger.error(f"Failed to decompress/deserialize value: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL."""
        namespaced_key = self._generate_key(key)
        expires_at = datetime.now() + timedelta(seconds=ttl or self.config.ttl)
        
        try:
            compressed_value = self._compress_value(value)
            size_bytes = len(compressed_value)
            
            entry = CacheEntry(
                key=namespaced_key,
                value=value,
                expires_at=expires_at,
                size_bytes=size_bytes
            )

            success = True
            
            # Set in memory cache
            if self.config.enable_memory_cache:
                with self._cache_lock:
                    self._cleanup_memory_cache()
                    self._memory_cache[namespaced_key] = entry
                    self._stats.memory_size_bytes += size_bytes
            
            # Set in Redis cache
            if self.config.has_redis and self._redis_client:
                try:
                    self._redis_client.setex(
                        namespaced_key,
                        ttl or self.config.ttl,
                        compressed_value
                    )
                except Exception as e:
                    logger.error(f"Redis cache set error: {e}")
                    success = False
            
            return success
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache, checking memory first then Redis."""
        namespaced_key = self._generate_key(key)
        
        # Check memory cache first
        if self.config.enable_memory_cache:
            with self._cache_lock:
                if entry := self._memory_cache.get(namespaced_key):
                    if not entry.is_expired():
                        entry.update_access()
                        self._stats.hit_count += 1
                        return entry.value
                    else:
                        del self._memory_cache[namespaced_key]
                        self._stats.eviction_count += 1
        
        # Check Redis cache
        if self.config.has_redis and self._redis_client:
            try:
                if value := self._redis_client.get(namespaced_key):
                    decompressed_value = self._decompress_value(value)
                    if decompressed_value is not None:
                        # Update memory cache if enabled
                        if self.config.enable_memory_cache:
                            self.set(key, decompressed_value)
                        self._stats.hit_count += 1
                        return decompressed_value
            except Exception as e:
                logger.error(f"Redis cache get error: {e}")
        
        self._stats.miss_count += 1
        return None

    async def async_get(self, key: str) -> Optional[Any]:
        """Asynchronously get value from cache."""
        if not self._async_redis_client:
            await self._initialize_async_redis()
            
        namespaced_key = self._generate_key(key)
        
        if self.config.has_redis and self._async_redis_client:
            try:
                if value := await self._async_redis_client.get(namespaced_key):
                    return self._decompress_value(value)
            except Exception as e:
                logger.error(f"Async Redis cache get error: {e}")
        
        return None

    def delete(self, key: str) -> bool:
        """Delete value from all cache levels."""
        namespaced_key = self._generate_key(key)
        success = True
        
        # Delete from memory cache
        if self.config.enable_memory_cache:
            with self._cache_lock:
                if entry := self._memory_cache.pop(namespaced_key, None):
                    self._stats.memory_size_bytes -= entry.size_bytes or 0
        
        # Delete from Redis cache
        if self.config.has_redis and self._redis_client:
            try:
                self._redis_client.delete(namespaced_key)
            except Exception as e:
                logger.error(f"Redis cache delete error: {e}")
                success = False
        
        return success

    def _cleanup_memory_cache(self) -> None:
        """Clean up expired and overflow entries from memory cache."""
        with self._cache_lock:
            now = datetime.now()
            # Remove expired entries
            expired_keys = [
                k for k, v in self._memory_cache.items()
                if v.is_expired()
            ]
            for k in expired_keys:
                entry = self._memory_cache.pop(k)
                self._stats.memory_size_bytes -= entry.size_bytes or 0
                self._stats.eviction_count += 1
            
            # Remove overflow entries
            while len(self._memory_cache) > self.config.max_size:
                _, entry = self._memory_cache.popitem(last=False)
                self._stats.memory_size_bytes -= entry.size_bytes or 0
                self._stats.eviction_count += 1

    def clear(self) -> bool:
        """Clear all cache entries."""
        success = True
        
        # Clear memory cache
        with self._cache_lock:
            self._memory_cache.clear()
            self._stats.memory_size_bytes = 0
        
        # Clear Redis cache
        if self.config.has_redis and self._redis_client:
            try:
                self._redis_client.flushdb()
            except Exception as e:
                logger.error(f"Redis cache clear error: {e}")
                success = False
        
        return success

    def get_stats(self) -> CacheStats:
        """Get current cache statistics."""
        stats = self._stats.copy()
        stats.memory_items = len(self._memory_cache)
        
        if self.config.has_redis and self._redis_client:
            try:
                stats.redis_items = self._redis_client.dbsize()
            except Exception:
                pass
        
        return stats

    def __del__(self) -> None:
        """Cleanup Redis connections."""
        if self._redis_client:
            self._redis_client.close()
        if self._async_redis_client and not self._async_redis_client.closed:
            asyncio.create_task(self._async_redis_client.close())