"""Application session state for the desktop client."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from frontend.settings.settings_page import load_settings_file


DEFAULT_API_BASE = "http://localhost:8000"


@dataclass
class AppSession:
    """Shared session: user, token, API base URL, connectivity."""

    api_base_url: str = DEFAULT_API_BASE
    token: Optional[str] = None
    user_info: Dict[str, Any] = field(default_factory=dict)
    is_online: bool = False

    def load_from_settings(self) -> None:
        saved = load_settings_file()
        self.api_base_url = saved.get("api_base_url", DEFAULT_API_BASE).rstrip("/")

    def set_user(self, user_info: Dict[str, Any]) -> None:
        self.user_info = dict(user_info)
        self.token = user_info.get("token")
        self.is_online = user_info.get("source") == "api"

    def clear(self) -> None:
        self.token = None
        self.user_info = {}
        self.is_online = False

    @property
    def username(self) -> str:
        return self.user_info.get("username", "")

    @property
    def role(self) -> str:
        return self.user_info.get("role", "Viewer")


_session: Optional[AppSession] = None


def get_session() -> AppSession:
    global _session
    if _session is None:
        _session = AppSession()
        _session.load_from_settings()
    return _session


def reset_session() -> None:
    global _session
    _session = None
