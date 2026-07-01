"""
Finovate Audit Nexus AI - Caching Layer
Multi-backend cache with Redis support and in-memory fallback
"""

import hashlib
import json
import logging
import time
from functools import wraps
from typing import Any, Callable, Optional

from backend.core.config import settings

logger = logging.getLogger(__name__)


class MemoryBackend:
    def __init__(self):
        self._store: dict = {}
        self._ttls: dict = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._ttls and time.time() > self._ttls[key]:
            self._store.pop(key, None)
            self._ttls.pop(key, None)
            return None
        return self._store.get(key)

    def set(self, key: str, value: Any, ttl: int = 300):
        self._store[key] = value
        if ttl > 0:
            self._ttls[key] = time.time() + ttl
        else:
            self._ttls.pop(key, None)

    def delete(self, key: str):
        self._store.pop(key, None)
        self._ttls.pop(key, None)

    def flush(self):
        self._store.clear()
        self._ttls.clear()

    def get_stats(self) -> dict:
        return {"items": len(self._store), "backend": "memory"}


class RedisBackend:
    def __init__(self):
        self._client = None
        self._available = False
        self._init_redis()

    def _init_redis(self):
        try:
            import redis as redis_lib
            self._client = redis_lib.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            self._client.ping()
            self._available = True
            logger.info("Redis cache connected")
        except Exception:
            self._available = False
            logger.warning("Redis unavailable, connect() for memory fallback")

    def get(self, key: str) -> Optional[Any]:
        if not self._available:
            return None
        try:
            val = self._client.get(key)
            if val:
                return json.loads(val)
            return None
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: int = 300):
        if not self._available:
            return
        try:
            self._client.setex(key, ttl, json.dumps(value))
        except Exception:
            pass

    def delete(self, key: str):
        if not self._available:
            return
        try:
            self._client.delete(key)
        except Exception:
            pass

    def flush(self):
        if not self._available:
            return
        try:
            self._client.flushdb()
        except Exception:
            pass

    def get_stats(self) -> dict:
        if not self._available:
            return {"backend": "redis", "available": False}
        try:
            info = self._client.info()
            return {
                "backend": "redis",
                "available": True,
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "uptime_days": info.get("uptime_in_days", 0),
            }
        except Exception:
            return {"backend": "redis", "available": True, "error": "stats_unavailable"}


class CacheManager:
    def __init__(self):
        self._memory = MemoryBackend()
        self._redis = RedisBackend()
        self._use_redis = self._redis._available
        logger.info(f"CacheManager initialized (redis={self._use_redis})")

    def _backend(self):
        return self._redis if self._use_redis else self._memory

    def get(self, key: str) -> Optional[Any]:
        return self._backend().get(key)

    def set(self, key: str, value: Any, ttl: int = 300):
        self._backend().set(key, value, ttl)

    def delete(self, key: str):
        self._backend().delete(key)

    def flush(self):
        self._backend().flush()

    def remember(self, key: str, ttl: int = 300):
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                cache_key = f"{key}:{hashlib.md5(f'{args}:{kwargs}'.encode()).hexdigest()}"
                cached = self.get(cache_key)
                if cached is not None:
                    return cached
                result = await func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                return result
            return wrapper
        return decorator

    def invalidate(self, pattern: str):
        if self._use_redis:
            try:
                for key in self._redis._client.scan_iter(match=pattern):
                    self._redis._client.delete(key)
            except Exception:
                pass

    def get_stats(self) -> dict:
        return self._backend().get_stats()


_cache_instance: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager()
    return _cache_instance
