"""
Finovate Audit Nexus AI - Rate Limiting Middleware
الحد من الطلبات للحماية من الإساءة
Supports both in-memory (single worker) and Redis-backed (multi-worker) modes.
"""
import time
from collections import defaultdict

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware


class InMemoryRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict = defaultdict(list)

    async def check(self, client_ip: str) -> None:
        now = time.time()
        window_start = now - self.window_seconds
        self.requests[client_ip] = [t for t in self.requests[client_ip] if t > window_start]
        if len(self.requests[client_ip]) >= self.max_requests:
            raise HTTPException(status_code=429, detail=f"Too many requests. Limit: {self.max_requests}/{self.window_seconds}s")
        self.requests[client_ip].append(now)


class RedisRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int, redis_client=None):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.redis = redis_client

    async def check(self, client_ip: str) -> None:
        if self.redis is None:
            return
        try:
            now = int(time.time())
            key = f"ratelimit:{client_ip}"
            pipeline = self.redis.pipeline()
            pipeline.zadd(key, {str(now + i): now for i in range(1)})
            pipeline.zremrangebyscore(key, 0, now - self.window_seconds)
            pipeline.zcard(key)
            pipeline.expire(key, self.window_seconds + 60)
            results = await pipeline.execute()
            count = results[2]
            if count > self.max_requests:
                raise HTTPException(status_code=429, detail=f"Too many requests. Limit: {self.max_requests}/{self.window_seconds}s")
        except HTTPException:
            raise
        except Exception:
            pass


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60, redis_client=None):
        super().__init__(app)
        if redis_client is not None:
            self.limiter = RedisRateLimiter(max_requests, window_seconds, redis_client)
        else:
            self.limiter = InMemoryRateLimiter(max_requests, window_seconds)

    async def dispatch(self, request: Request, call_next):
        if request.url.path in ("/api/health", "/api/docs", "/api/redoc", "/api/openapi.json"):
            return await call_next(request)
        client_ip = request.client.host if request.client else "unknown"
        await self.limiter.check(client_ip)
        return await call_next(request)
