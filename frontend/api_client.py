"""
Finovate Audit Nexus AI - Desktop API Client
Unified HTTP client for /api/v1/* backend routes.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime

import os
import requests
from loguru import logger

from frontend.services.session_manager import get_session, DEFAULT_API_BASE


class APIConnectionError(Exception):
    """Raised when the API server is unreachable."""


class APIResponseError(Exception):
    """Raised when the API returns a non-2xx status."""


class APIClient:
    """Shared HTTP client for all desktop widgets."""

    def __init__(self, base_url: str = DEFAULT_API_BASE):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self._timeout = (2, 8)
        self._token: Optional[str] = None
        self._last_online: Optional[bool] = None

    def configure_from_session(self) -> None:
        sess = get_session()
        self.base_url = sess.api_base_url.rstrip("/")
        if sess.token:
            self._token = sess.token

    @property
    def headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json", "Accept": "application/json"}
        if self._token:
            h["Authorization"] = f"Bearer {self._token}"
        return h

    def set_token(self, token: Optional[str]) -> None:
        self._token = token
        get_session().token = token

    @property
    def is_online(self) -> bool:
        return bool(self._last_online)

    def check_available(self) -> bool:
        try:
            r = self.session.get(
                f"{self.base_url}/api/health",
                timeout=(1, 2),
            )
            self._last_online = r.status_code == 200
            return self._last_online
        except Exception:
            self._last_online = False
            return False

    def _request(self, method: str, path: str, *, require_auth: bool = False, **kwargs) -> Any:
        self.configure_from_session()
        url = f"{self.base_url}{path}"
        if require_auth and not self._token:
            raise APIResponseError("Authentication required — please log in via API")

        try:
            r = self.session.request(
                method,
                url,
                headers=self.headers,
                timeout=self._timeout,
                **kwargs,
            )
            self._last_online = True
            r.raise_for_status()
            return r.json() if r.text else None
        except requests.ConnectionError as e:
            self._last_online = False
            raise APIConnectionError(f"Cannot reach {url}") from e
        except requests.Timeout as e:
            self._last_online = False
            raise APIConnectionError(f"Request timed out: {url}") from e
        except requests.HTTPError as e:
            resp = e.response
            status = resp.status_code if resp is not None else "?"
            body = resp.text[:200] if resp is not None else ""
            raise APIResponseError(f"HTTP {status}: {body}") from e

    def _safe_get(self, path: str, default=None, *, require_auth: bool = False) -> Any:
        if not self.check_available():
            return default
        try:
            return self._request("GET", path, require_auth=require_auth)
        except Exception as e:
            logger.debug(f"GET {path} failed: {e}")
            return default

    def _safe_post(self, path: str, data: dict = None, *, require_auth: bool = False) -> Any:
        if not self.check_available():
            return None
        try:
            return self._request("POST", path, json=data or {}, require_auth=require_auth)
        except Exception as e:
            logger.debug(f"POST {path} failed: {e}")
            return None

    # ── Public endpoints ──────────────────────────────────────────────

    def health(self) -> dict:
        return self._safe_get("/api/health") or {
            "status": "offline",
            "database": "disconnected",
            "ai_engine": {"status": "unknown"},
        }

    def login(self, username: str, password: str) -> dict:
        self.configure_from_session()
        try:
            return self._request(
                "POST",
                "/api/v1/auth/login",
                json={"username": username, "password": password},
            )
        except Exception as e:
            logger.debug(f"Login failed: {e}")
            return {}

    # ── Audits ────────────────────────────────────────────────────────

    def get_audits(self) -> list:
        data = self._safe_get("/api/v1/audits", require_auth=True)
        if isinstance(data, dict):
            return data.get("data", data.get("audits", []))
        return data or []

    def get_audit_stats(self) -> dict:
        return self._safe_get("/api/v1/audits/stats/summary", require_auth=True) or {}

    def start_audit(
        self,
        project_id: str,
        financial_data: dict,
        audit_type: str = "full",
    ) -> dict:
        if not self.check_available():
            return {}
        try:
            return self._request(
                "POST",
                f"/api/v1/audits/start?project_id={project_id}&audit_type={audit_type}",
                json=financial_data,
                require_auth=True,
            ) or {}
        except Exception as e:
            logger.debug(f"start_audit failed: {e}")
            return {}

    def upload_document(
        self,
        file_path: str,
        document_type: str = "General",
        company_id: int = 1,
    ) -> dict:
        self.configure_from_session()
        if not self.check_available() or not self._token:
            return {}
        url = f"{self.base_url}/api/v1/documents/upload"
        headers = {"Authorization": f"Bearer {self._token}"}
        try:
            with open(file_path, "rb") as f:
                r = self.session.post(
                    url,
                    files={"file": (os.path.basename(file_path), f)},
                    params={"document_type": document_type, "company_id": company_id},
                    headers=headers,
                    timeout=(5, 30),
                )
            r.raise_for_status()
            self._last_online = True
            return r.json() if r.text else {}
        except Exception as e:
            logger.debug(f"upload_document failed: {e}")
            return {}

    def test_ai_provider(self, provider_name: str) -> dict:
        return self._safe_post(
            f"/api/v1/ai/providers/{provider_name}/test",
            {},
            require_auth=True,
        ) or {}

    def get_audit_project(self, project_id: int) -> dict:
        return self._safe_get(f"/api/v1/audit-projects/{project_id}", require_auth=True) or {}

    # ── AI ────────────────────────────────────────────────────────────

    def ai_status(self) -> dict:
        data = self._safe_get("/api/v1/ai/status", require_auth=True)
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data or {"status": "offline", "providers_available": 0}

    def ai_providers(self) -> dict:
        data = self._safe_get("/api/v1/ai/providers", require_auth=True)
        if isinstance(data, dict):
            inner = data.get("data", data)
            if isinstance(inner, dict) and "providers" in inner:
                return inner
            if "providers" in data:
                return data
        return {"providers": []}

    # ── Agents ────────────────────────────────────────────────────────

    def get_agents(self) -> list:
        data = self._safe_get("/api/v1/agents/", require_auth=True)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("agents", data.get("data", []))
        return []

    def get_agent_status(self) -> list:
        data = self._safe_get("/api/v1/agent-status", require_auth=True)
        if isinstance(data, dict):
            return data.get("agents", data.get("data", []))
        return data or []

    def execute_agent(self, agent_name: str, payload: dict) -> dict:
        body = {"agent_name": agent_name, **payload}
        return self._safe_post("/api/v1/agents/execute", body, require_auth=True) or {}

    # ── Dashboard ─────────────────────────────────────────────────────

    def get_dashboard_v1(self) -> dict:
        return self._safe_get("/api/v1/audit/dashboard", require_auth=True) or {}

    def get_summary_report(self) -> dict:
        return self._safe_get("/api/v1/audit/dashboard/summary-report", require_auth=True) or {}

    def get_dashboard_recommendations(self) -> dict:
        return self._safe_get("/api/v1/audit/dashboard/recommendations", require_auth=True) or {}

    def get_dashboard(self) -> dict:
        """Composite dashboard data for the main dashboard page."""
        if not self._token:
            return {
                "health": self.health(),
                "stats": {},
                "ai": {},
                "online": self.check_available(),
                "timestamp": datetime.now().isoformat(),
            }
        return {
            "health": self.health(),
            "stats": self.get_audit_stats(),
            "ai": self.ai_status(),
            "v1": self.get_dashboard_v1(),
            "online": self.is_online,
            "timestamp": datetime.now().isoformat(),
        }

    # ── Projects ──────────────────────────────────────────────────────

    def get_audit_projects(self) -> list:
        data = self._safe_get("/api/v1/audit-projects/", require_auth=True)
        if isinstance(data, list):
            return data
        return data.get("data", []) if isinstance(data, dict) else []

    def create_audit_project(self, data: dict) -> dict:
        return self._safe_post("/api/v1/audit-projects/", data, require_auth=True) or {}

    # ── Findings ──────────────────────────────────────────────────────

    def get_findings(self) -> list:
        data = self._safe_get("/api/v1/findings/", require_auth=True)
        return data if isinstance(data, list) else []

    # ── Reports ───────────────────────────────────────────────────────

    def list_reports(self, project_id: str = None) -> list:
        path = "/api/v1/reports"
        if project_id:
            path += f"?project_id={project_id}"
        data = self._safe_get(path, require_auth=True)
        if isinstance(data, dict):
            return data.get("data", [])
        return data or []

    def create_report(self, project_id: str, report_type: str = "audit") -> dict:
        return self._safe_post(
            f"/api/v1/reports/create?project_id={project_id}&report_type={report_type}",
            {},
            require_auth=True,
        ) or {}

    def generate_report_summary(self, report_id: str) -> dict:
        return self._safe_post(f"/api/v1/reports/{report_id}/summary", {}, require_auth=True) or {}

    def export_report(self, report_id: str, fmt: str = "pdf") -> dict:
        return self._safe_post(
            f"/api/v1/reports/{report_id}/export?format={fmt}",
            {},
            require_auth=True,
        ) or {}

    # ── Connectors ────────────────────────────────────────────────────

    def list_connectors(self) -> list:
        data = self._safe_get("/api/v1/connectors", require_auth=True)
        if isinstance(data, dict):
            return data.get("data", [])
        return data or []

    def register_connector(self, payload: dict) -> dict:
        return self._safe_post("/api/v1/connectors", payload, require_auth=True) or {}

    def test_connector(self, connector_id: str) -> dict:
        return self._safe_post(f"/api/v1/connectors/{connector_id}/test", {}, require_auth=True) or {}

    def delete_connector(self, connector_id: str) -> dict:
        self.configure_from_session()
        try:
            return self._request("DELETE", f"/api/v1/connectors/{connector_id}", require_auth=True)
        except Exception as e:
            logger.debug(f"DELETE connector failed: {e}")
            return {}


_client: Optional[APIClient] = None


def get_client() -> APIClient:
    global _client
    if _client is None:
        _client = APIClient()
        _client.configure_from_session()
    return _client


def reset_client() -> None:
    global _client
    _client = None
