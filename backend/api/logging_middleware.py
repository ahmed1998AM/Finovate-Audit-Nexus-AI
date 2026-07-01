"""
Finovate Audit Nexus AI - Request Logging Middleware
تسجيل جميع طلبات API للتدقيق والمتابعة
"""
import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api.requests")

class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        if request.url.path.startswith("/api/") or request.url.path in ("/health", "/"):
            logger.info(
                "%s %s %s %.0fms",
                request.method, request.url.path, response.status_code, duration * 1000,
            )
        return response
