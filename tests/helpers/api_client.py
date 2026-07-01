"""Test HTTP client compatible with httpx 0.28+ and Starlette apps."""

from __future__ import annotations

import asyncio
from typing import Any, Optional

import httpx
from httpx import ASGITransport


class SyncTestClient:
    """Minimal synchronous wrapper around httpx.AsyncClient + ASGITransport."""

    def __init__(self, app, base_url: str = "http://testserver"):
        self._transport = ASGITransport(app=app)
        self._client = httpx.AsyncClient(transport=self._transport, base_url=base_url)
        self._loop = asyncio.new_event_loop()

    def _run(self, coro):
        return self._loop.run_until_complete(coro)

    def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        return self._run(self._client.request(method, url, **kwargs))

    def get(self, url: str, **kwargs) -> httpx.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> httpx.Response:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs) -> httpx.Response:
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs) -> httpx.Response:
        return self.request("DELETE", url, **kwargs)

    def close(self) -> None:
        try:
            self._run(self._client.aclose())
        finally:
            self._loop.close()

    def __enter__(self) -> "SyncTestClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
