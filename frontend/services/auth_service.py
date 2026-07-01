"""Authentication helpers for the desktop client."""

from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING

from loguru import logger

from frontend.services.session_manager import get_session

if TYPE_CHECKING:
    from frontend.api_client import APIClient


class AuthService:
    def __init__(self, client: Optional["APIClient"] = None):
        self._client = client
        self._session = get_session()

    def _get_client(self) -> "APIClient":
        if self._client is None:
            from frontend.api_client import get_client
            self._client = get_client()
        return self._client

    def login_api(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        client = self._get_client()
        resp = client.login(username, password)
        if not resp or not resp.get("access_token"):
            return None

        token = resp["access_token"]
        client.set_token(token)
        user_info = resp.get("user_info") or resp.get("user") or {}

        result = {
            "username": user_info.get("username", username),
            "role": user_info.get("role", "Auditor"),
            "token": token,
            "source": "api",
            "must_change_password": user_info.get("must_change_password", False),
            "full_name": user_info.get("full_name", username),
        }
        self._session.set_user(result)
        logger.info(f"API login successful for {username}")
        return result

    def apply_local_login(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        result = dict(user_info)
        result["source"] = "local"
        self._get_client().set_token(None)
        self._session.set_user(result)
        return result

    def logout(self) -> None:
        self._get_client().set_token(None)
        self._session.clear()
