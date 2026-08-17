"""
Finovate Audit Nexus AI - Comprehensive API Integration Tests for ALL Endpoints
اختبارات شاملة لجميع نقاط نهاية API
"""
import os
import sys
import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, PropertyMock, patch, ANY

import asyncio
import httpx
from httpx import ASGITransport
from jose import jwt, JWTError
import pytest
from fastapi import APIRouter, Depends, FastAPI

os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["ENCRYPTION_KEY"] = "test-encryption-key-32char!"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.database import get_db
from backend.api.auth_middleware import get_current_user
from backend.database.models import (
    User, AuditFinding, AuditProject, FraudCase, TaxCompliance,
    Company, ChartOfAccount, JournalEntry, Document as DocumentModel
)

from backend.api.endpoints import auth, agents, audit_projects, backups, companies
from backend.api.endpoints import connectors, dashboard, documents, findings
from backend.api.endpoints import notifications, predictive, reports
from backend.api.endpoints import tasks as task_endpoints
from backend.api.endpoints import webhooks_api
from backend.api.routes import audits, ai_providers

app = FastAPI()

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

protected = APIRouter(dependencies=[Depends(get_current_user)])
protected.include_router(audits.router)
protected.include_router(ai_providers.router)
protected.include_router(agents.router, prefix="/api/v1/agents")
protected.include_router(reports.router, prefix="/api/v1")
protected.include_router(predictive.router, prefix="/api/v1")
protected.include_router(companies.router, prefix="/api/v1/companies")
protected.include_router(audit_projects.router, prefix="/api/v1/audit-projects")
protected.include_router(findings.router, prefix="/api/v1/findings")
protected.include_router(documents.router, prefix="/api/v1/documents")
protected.include_router(dashboard.router, prefix="/api/v1/audit")
protected.include_router(notifications.router, prefix="/api/v1/notifications")
protected.include_router(connectors.router, prefix="/api/v1")
protected.include_router(webhooks_api.router, prefix="/api/v1/webhooks")
protected.include_router(task_endpoints.router, prefix="/api/v1/tasks")
protected.include_router(backups.router)
app.include_router(protected)

_loop = asyncio.new_event_loop()


def _sync_request(method, url, **kwargs):
    async def _req():
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as ac:
            r = await ac.request(method, url, **kwargs)
            return r
    return _loop.run_until_complete(_req())


client = type("SyncClient", (), {
    "get": lambda self, url, **kw: _sync_request("GET", url, **kw),
    "post": lambda self, url, **kw: _sync_request("POST", url, **kw),
    "put": lambda self, url, **kw: _sync_request("PUT", url, **kw),
    "delete": lambda self, url, **kw: _sync_request("DELETE", url, **kw),
    "request": lambda self, method, url, **kw: _sync_request(method, url, **kw),
})()


def _make_token(username="test_admin", role="Admin"):
    return jwt.encode(
        {"sub": username, "role": role, "exp": datetime.utcnow() + timedelta(hours=1)},
        "test-secret-key-for-testing-only",
        algorithm="HS256",
    )


@pytest.fixture
def auth_header():
    return {"Authorization": f"Bearer {_make_token()}"}


def _make_mock_user(overrides=None):
    attrs = dict(
        id=1, username="test_admin", email="admin@test.com",
        role="Admin", is_active=True, must_change_password=False,
        password_hash="$2b$12$fakehash",
        last_login=None,
    )
    if overrides:
        attrs.update(overrides)
    u = MagicMock(spec=User)
    for k, v in attrs.items():
        setattr(u, k, v)
    return u


def _make_mock_finding(overrides=None):
    attrs = dict(
        id=1, project_id=1, finding_number="F-2026-0001",
        title="Test Finding", description="A test",
        category="Error", severity="Critical", status="Open",
        financial_impact=10000.0, recommendation="Fix it",
        created_at=datetime.utcnow(),
    )
    if overrides:
        attrs.update(overrides)
    f = MagicMock(spec=AuditFinding)
    for k, v in attrs.items():
        setattr(f, k, v)
    return f


def _make_mock_project(overrides=None):
    attrs = dict(
        id=1, company_id=1, project_name="Audit 2026",
        audit_type="Financial", status="Planning", risk_level="Medium",
        scope="Full audit", objectives="Verify",
        start_date=datetime.utcnow(), end_date=datetime.utcnow(),
        created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
    )
    if overrides:
        attrs.update(overrides)
    p = MagicMock(spec=AuditProject)
    for k, v in attrs.items():
        setattr(p, k, v)
    return p


def _make_mock_company(overrides=None):
    attrs = dict(
        id=1, name="Test Corp", tax_id="TX-12345",
        commercial_registration="CR-001", address="Cairo",
        phone="0100000000", email="corp@test.com",
        fiscal_year_start=1, currency="EGP",
        is_active=True, created_at=datetime.utcnow(),
    )
    if overrides:
        attrs.update(overrides)
    c = MagicMock(spec=Company)
    for k, v in attrs.items():
        setattr(c, k, v)
    return c


def _make_mock_document(overrides=None):
    attrs = dict(
        id=1, company_id=1, document_type="invoice",
        file_name="inv.pdf", file_path="/tmp/test.pdf",
        file_size=1024, mime_type="application/pdf",
        file_hash="abc123", is_processed=False,
        ocr_text=None, extracted_data={},
        upload_date=datetime.utcnow(),
    )
    if overrides:
        attrs.update(overrides)
    d = MagicMock(spec=DocumentModel)
    for k, v in attrs.items():
        setattr(d, k, v)
    return d


class MockDB:
    def __init__(self):
        self._query_model = None
        self._filters = {}
        self._result = None
        self._all_result = []
        self._first_result = None
        self._count_result = 0
        self._order_by_result = None
        self._added_objects = []
        self._deleted_objects = []
        self.committed = False

    def query(self, model):
        self._query_model = model
        return self

    def filter(self, *args, **kwargs):
        return self

    def filter_by(self, **kwargs):
        return self

    def order_by(self, *args):
        return self

    def limit(self, n):
        return self

    def offset(self, n):
        return self

    def all(self):
        return self._all_result

    def first(self):
        return self._first_result

    def count(self):
        return self._count_result

    def add(self, obj):
        self._added_objects.append(obj)

    def delete(self, obj):
        self._deleted_objects.append(obj)

    def commit(self):
        self.committed = True

    _refresh_counter = 0

    def refresh(self, obj):
        self._refresh_counter += 1
        if hasattr(obj, 'id') and getattr(obj, 'id', None) is None:
            obj.id = self._refresh_counter
        if hasattr(obj, 'created_at') and getattr(obj, 'created_at', None) is None:
            obj.created_at = datetime.utcnow()
        if hasattr(obj, 'upload_date') and getattr(obj, 'upload_date', None) is None:
            obj.upload_date = datetime.utcnow()
        if hasattr(obj, 'is_active') and getattr(obj, 'is_active', None) is None:
            obj.is_active = True
        if hasattr(obj, 'finding_number') and getattr(obj, 'finding_number', None) is None:
            obj.finding_number = f"F-{datetime.now().year}-0001"
        if hasattr(obj, 'status') and getattr(obj, 'status', None) is None:
            obj.status = "Open"
        if hasattr(obj, 'risk_level') and getattr(obj, 'risk_level', None) is None:
            obj.risk_level = "Medium"
        if hasattr(obj, 'is_processed') and getattr(obj, 'is_processed', None) is None:
            obj.is_processed = False
        if hasattr(obj, 'file_size') and getattr(obj, 'file_size', None) is None:
            obj.file_size = 0
        if hasattr(obj, 'is_posted') and getattr(obj, 'is_posted', None) is None:
            obj.is_posted = True
        if hasattr(obj, 'ocr_text') and getattr(obj, 'ocr_text', None) is None:
            obj.ocr_text = None

    def rollback(self):
        pass

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


@pytest.fixture
def mock_db():
    return MockDB()


@pytest.fixture
def mock_task_queue():
    with patch("backend.api.endpoints.tasks.get_task_queue") as m:
        queue = MagicMock()
        queue.submit.return_value = "task-001"
        queue.get_task.return_value = MagicMock(
            task_id="task-001", name="test", status=MagicMock(value="success"),
            created_at=datetime.utcnow(), started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(), error=None,
        )
        queue.get_result.return_value = {"processed": True}
        queue.cancel.return_value = True
        queue.list_tasks.return_value = [{"task_id": "task-001", "name": "test"}]
        m.return_value = queue
        yield m


@pytest.fixture(autouse=True)
def _override_all(mock_db, mock_task_queue):
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: _make_mock_user()
    yield
    app.dependency_overrides.clear()


# =============================================================================
# AUTH
# =============================================================================

class TestAuth:
    """اختبارات نقاط نهاية المصادقة"""

    def test_login_success(self, mock_db):
        with patch("backend.api.endpoints.auth.verify_password", return_value=True):
            mock_db._first_result = _make_mock_user()
            r = client.post("/api/v1/auth/login", json={"username": "test_admin", "password": "correct"})
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_info"]["username"] == "test_admin"

    def test_login_wrong_password(self, mock_db):
        with patch("backend.api.endpoints.auth.verify_password", return_value=False):
            mock_db._first_result = _make_mock_user()
            r = client.post("/api/v1/auth/login", json={"username": "test_admin", "password": "wrong"})
        assert r.status_code == 401
        assert "Invalid credentials" in r.json()["detail"]

    def test_login_inactive_user(self, mock_db):
        mock_db._first_result = None
        r = client.post("/api/v1/auth/login", json={"username": "disabled", "password": "x"})
        assert r.status_code == 401

    def test_login_missing_fields(self):
        r = client.post("/api/v1/auth/login", json={"username": "x"})
        assert r.status_code == 422

    def test_login_empty_json(self):
        r = client.post("/api/v1/auth/login", json={})
        assert r.status_code == 422

    def test_register_success(self, mock_db):
        with patch("backend.api.endpoints.auth.hash_password", return_value="hashed"):
            mock_db._first_result = None
            r = client.post("/api/v1/auth/register", json={
                "username": "newuser", "email": "new@test.com",
                "password": "Str0ng!pass", "role": "Auditor"
            })
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_register_duplicate_username(self, mock_db):
        mock_db._first_result = _make_mock_user()
        r = client.post("/api/v1/auth/register", json={
            "username": "test_admin", "email": "other@test.com",
            "password": "Str0ng!pass"
        })
        assert r.status_code == 400
        assert "already exists" in r.json()["detail"]

    def test_me_valid_token(self, mock_db):
        mock_db._first_result = _make_mock_user()
        token = _make_token()
        r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["username"] == "test_admin"

    def test_me_without_token(self):
        r = client.get("/api/v1/auth/me")
        assert r.status_code in (401, 403)

    def test_me_invalid_token(self):
        r = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalidtoken"})
        assert r.status_code == 401

    def test_change_password_success(self, mock_db):
        with patch("backend.api.endpoints.auth.verify_password", return_value=True):
            with patch("backend.api.endpoints.auth.hash_password", return_value="newhash"):
                mock_db._first_result = _make_mock_user()
                token = _make_token()
                r = client.post("/api/v1/auth/change-password",
                    json={"old_password": "oldpass", "new_password": "NewStr0ng!"},
                    headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_change_password_wrong_old(self, mock_db):
        with patch("backend.api.endpoints.auth.verify_password", return_value=False):
            mock_db._first_result = _make_mock_user()
            token = _make_token()
            r = client.post("/api/v1/auth/change-password",
                json={"old_password": "wrong", "new_password": "NewStr0ng!"},
                headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 400

    def test_change_password_short(self, mock_db):
        with patch("backend.api.endpoints.auth.verify_password", return_value=True):
            mock_db._first_result = _make_mock_user()
            token = _make_token()
            r = client.post("/api/v1/auth/change-password",
                json={"old_password": "oldpass", "new_password": "short"},
                headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 400

    def test_logout(self, mock_db):
        mock_db._first_result = _make_mock_user()
        token = _make_token()
        r = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_refresh_token(self, mock_db):
        mock_db._first_result = _make_mock_user()
        token = _make_token()
        r = client.post("/api/v1/auth/refresh-token", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert "access_token" in r.json()


# =============================================================================
# AGENTS
# =============================================================================

class TestAgents:
    """اختبارات نقاط نهاية الوكلاء"""

    def test_list_agents(self, auth_header):
        with patch("backend.api.endpoints.agents._get_orchestrator") as m:
            orch = MagicMock()
            orch.agents = {
                "fraud_agent": {"status": "active", "instance": MagicMock(tasks_completed=5, success_rate=95.0)},
                "compliance_agent": {"status": "active", "instance": MagicMock(tasks_completed=3, success_rate=100.0)},
            }
            m.return_value = orch
            r = client.get("/api/v1/agents/", headers=auth_header)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_list_agents_empty_register(self, auth_header):
        with patch("backend.api.endpoints.agents._get_orchestrator") as m_orch:
            orch = MagicMock()
            orch.agents = {}
            m_orch.return_value = orch
            with patch("backend.orchestrator.agent_registry.register_agents_in_orchestrator") as reg:
                orch.agents = {"new_agent": {"status": "registered", "instance": None}}
                r = client.get("/api/v1/agents/", headers=auth_header)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_agent_status_found(self, auth_header):
        with patch("backend.api.endpoints.agents._get_orchestrator") as m:
            orch = MagicMock()
            orch.agents = {
                "fraud_agent": {"status": "active", "instance": MagicMock()},
            }
            m.return_value = orch
            r = client.get("/api/v1/agents/fraud_agent/status", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["agent_name"] == "fraud_agent"

    def test_get_agent_status_not_found(self, auth_header):
        with patch("backend.api.endpoints.agents._get_orchestrator") as m:
            orch = MagicMock()
            orch.agents = {}
            m.return_value = orch
            r = client.get("/api/v1/agents/nonexistent/status", headers=auth_header)
        assert r.status_code == 404

    def test_execute_agent_task(self, auth_header):
        with patch("backend.api.endpoints.agents._get_orchestrator") as m:
            inst = MagicMock()
            inst.execute.return_value = {"result": "done"}
            orch = MagicMock()
            orch.agents = {"fraud_agent": {"status": "active", "instance": inst}}
            m.return_value = orch
            r = client.post("/api/v1/agents/execute",
                json={"agent_name": "fraud_agent", "task_type": "analyze", "parameters": {"data": "x"}},
                headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_execute_agent_not_found(self, auth_header):
        with patch("backend.api.endpoints.agents._get_orchestrator") as m:
            orch = MagicMock()
            orch.agents = {}
            m.return_value = orch
            with patch("backend.orchestrator.agent_registry.register_agents_in_orchestrator", return_value=None):
                r = client.post("/api/v1/agents/execute",
                    json={"agent_name": "ghost", "task_type": "x"},
                    headers=auth_header)
        assert r.status_code == 404

    def test_get_agent_logs(self, auth_header):
        with patch("backend.api.endpoints.agents._get_orchestrator") as m:
            orch = MagicMock()
            orch.agents = {"fraud_agent": {"status": "active"}}
            m.return_value = orch
            r = client.get("/api/v1/agents/fraud_agent/logs?limit=10", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["agent_name"] == "fraud_agent"

    def test_get_agent_logs_not_found(self, auth_header):
        with patch("backend.api.endpoints.agents._get_orchestrator") as m:
            orch = MagicMock()
            orch.agents = {}
            m.return_value = orch
            r = client.get("/api/v1/agents/ghost/logs", headers=auth_header)
        assert r.status_code == 404

    def test_stop_agent(self, auth_header):
        with patch("backend.api.endpoints.agents._get_orchestrator") as m:
            orch = MagicMock()
            orch.agents = {"fraud_agent": {"status": "active"}}
            m.return_value = orch
            r = client.post("/api/v1/agents/fraud_agent/stop", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_start_agent(self, auth_header):
        with patch("backend.api.endpoints.agents._get_orchestrator") as m:
            orch = MagicMock()
            orch.agents = {"fraud_agent": {"status": "stopped"}}
            m.return_value = orch
            r = client.post("/api/v1/agents/fraud_agent/start", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True


# =============================================================================
# AUDIT PROJECTS
# =============================================================================

class TestAuditProjects:
    """اختبارات نقاط نهاية مشاريع المراجعة"""

    def test_list_projects(self, mock_db, auth_header):
        mock_db._all_result = [_make_mock_project()]
        r = client.get("/api/v1/audit-projects/", headers=auth_header)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_projects_with_status_filter(self, mock_db, auth_header):
        mock_db._all_result = [_make_mock_project()]
        r = client.get("/api/v1/audit-projects/?status_filter=Planning", headers=auth_header)
        assert r.status_code == 200

    def test_create_project(self, mock_db, auth_header):
        mock_db._added_objects = []
        r = client.post("/api/v1/audit-projects/", json={
            "company_id": 1, "project_name": "New Audit",
            "audit_type": "Financial",
        }, headers=auth_header)
        assert r.status_code == 201
        assert r.json()["project_name"] == "New Audit"

    def test_get_project_found(self, mock_db, auth_header):
        mock_db._first_result = _make_mock_project()
        r = client.get("/api/v1/audit-projects/1", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["project_name"] == "Audit 2026"

    def test_get_project_not_found(self, mock_db, auth_header):
        mock_db._first_result = None
        r = client.get("/api/v1/audit-projects/999", headers=auth_header)
        assert r.status_code == 404

    def test_get_project_findings(self, mock_db, auth_header):
        mock_db._all_result = [_make_mock_finding()]
        r = client.get("/api/v1/audit-projects/1/findings", headers=auth_header)
        assert r.status_code == 200
        assert "findings" in r.json()

    def test_get_project_workpapers(self, mock_db, auth_header):
        mock_db._all_result = []
        r = client.get("/api/v1/audit-projects/1/workpapers", headers=auth_header)
        assert r.status_code == 200
        assert "workpapers" in r.json()


# =============================================================================
# COMPANIES
# =============================================================================

class TestCompanies:
    """اختبارات نقاط نهاية الشركات"""

    def test_list_companies(self, mock_db, auth_header):
        mock_db._all_result = [_make_mock_company()]
        r = client.get("/api/v1/companies/", headers=auth_header)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_create_company(self, mock_db, auth_header):
        r = client.post("/api/v1/companies/", json={
            "name": "NewCo", "tax_id": "TX-NEW",
        }, headers=auth_header)
        assert r.status_code == 201
        assert r.json()["name"] == "NewCo"

    def test_get_company_found(self, mock_db, auth_header):
        mock_db._first_result = _make_mock_company()
        r = client.get("/api/v1/companies/1", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["name"] == "Test Corp"

    def test_get_company_not_found(self, mock_db, auth_header):
        mock_db._first_result = None
        r = client.get("/api/v1/companies/999", headers=auth_header)
        assert r.status_code == 404

    def test_update_company(self, mock_db, auth_header):
        mock_db._first_result = _make_mock_company()
        r = client.put("/api/v1/companies/1", json={"name": "Updated Corp"}, headers=auth_header)
        assert r.status_code == 200
        assert r.json()["name"] == "Updated Corp"

    def test_update_company_not_found(self, mock_db, auth_header):
        mock_db._first_result = None
        r = client.put("/api/v1/companies/999", json={"name": "Nope"}, headers=auth_header)
        assert r.status_code == 404

    def test_delete_company(self, mock_db, auth_header):
        mock_db._first_result = _make_mock_company()
        r = client.delete("/api/v1/companies/1", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_delete_company_nonexistent(self, mock_db, auth_header):
        mock_db._first_result = None
        r = client.delete("/api/v1/companies/999", headers=auth_header)
        assert r.status_code == 200

    def test_chart_of_accounts(self, mock_db, auth_header):
        mock_db._all_result = []
        r = client.get("/api/v1/companies/1/chart-of-accounts", headers=auth_header)
        assert r.status_code == 200
        assert "accounts" in r.json()

    def test_chart_of_accounts_with_data(self, mock_db, auth_header):
        acct = MagicMock(spec=ChartOfAccount)
        acct.id = 10
        acct.account_code = "1000"
        acct.account_name_ar = "نقد"
        acct.account_name_en = "Cash"
        acct.account_type = "Asset"
        acct.level = 1
        acct.is_active = True
        mock_db._all_result = [acct]
        r = client.get("/api/v1/companies/1/chart-of-accounts", headers=auth_header)
        assert r.status_code == 200
        assert len(r.json()["accounts"]) == 1

    def test_journal_entries(self, mock_db, auth_header):
        mock_db._all_result = []
        r = client.get("/api/v1/companies/1/journal-entries", headers=auth_header)
        assert r.status_code == 200
        assert "entries" in r.json()

    def test_journal_entries_with_filters(self, mock_db, auth_header):
        entry = MagicMock(spec=JournalEntry)
        entry.id = 1
        entry.entry_number = "JE-001"
        entry.entry_date = datetime.utcnow()
        entry.description = "Test"
        entry.source_system = "Manual"
        entry.is_posted = True
        entry.fiscal_year = 2026
        entry.fiscal_period = 1
        mock_db._all_result = [entry]
        r = client.get("/api/v1/companies/1/journal-entries?year=2026&period=1", headers=auth_header)
        assert r.status_code == 200
        assert len(r.json()["entries"]) == 1


# =============================================================================
# CONNECTORS
# =============================================================================

class TestConnectors:
    """اختبارات نقاط نهاية الموصلات"""

    def test_list_connectors(self, auth_header):
        with patch("backend.api.endpoints.connectors._get_service") as m:
            svc = MagicMock()
            svc.list_connectors.return_value = [{"id": "c1", "name": "SAP", "type": "sap"}]
            m.return_value = svc
            r = client.get("/api/v1/connectors", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_register_connector(self, auth_header):
        with patch("backend.api.endpoints.connectors._get_service") as m:
            svc = MagicMock()
            svc.register_connector.return_value = {"id": "c1", "name": "MyERP"}
            m.return_value = svc
            r = client.post("/api/v1/connectors", json={
                "connector_name": "MyERP", "connector_type": "sap",
                "company_id": 1, "config": {"host": "localhost"}
            }, headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_register_connector_value_error(self, auth_header):
        with patch("backend.api.endpoints.connectors._get_service") as m:
            svc = MagicMock()
            svc.register_connector.side_effect = ValueError("Invalid type")
            m.return_value = svc
            r = client.post("/api/v1/connectors", json={
                "connector_name": "Bad", "connector_type": "unknown",
            }, headers=auth_header)
        assert r.status_code == 400

    def test_test_connector_ok(self, auth_header):
        with patch("backend.api.endpoints.connectors._get_service") as m:
            svc = MagicMock()
            svc.connect.return_value = True
            m.return_value = svc
            r = client.post("/api/v1/connectors/c1/test", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "connected"

    def test_test_connector_fail(self, auth_header):
        with patch("backend.api.endpoints.connectors._get_service") as m:
            svc = MagicMock()
            svc.connect.return_value = False
            m.return_value = svc
            r = client.post("/api/v1/connectors/c1/test", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "failed"

    def test_sync_connector(self, auth_header):
        with patch("backend.api.endpoints.connectors._get_service") as m:
            svc = MagicMock()
            svc.registered_connectors = {"c1": MagicMock()}
            svc.sync_data.return_value = {"synced": True}
            m.return_value = svc
            r = client.post("/api/v1/connectors/c1/sync", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_sync_connector_not_found(self, auth_header):
        with patch("backend.api.endpoints.connectors._get_service") as m:
            svc = MagicMock()
            svc.registered_connectors = {}
            m.return_value = svc
            r = client.post("/api/v1/connectors/c999/sync", headers=auth_header)
        assert r.status_code == 404

    def test_delete_connector(self, auth_header):
        with patch("backend.api.endpoints.connectors._get_service") as m:
            svc = MagicMock()
            svc.registered_connectors = {"c1": MagicMock()}
            m.return_value = svc
            r = client.delete("/api/v1/connectors/c1", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["data"]["deleted"] is True

    def test_delete_connector_not_found(self, auth_header):
        with patch("backend.api.endpoints.connectors._get_service") as m:
            svc = MagicMock()
            svc.registered_connectors = {}
            m.return_value = svc
            r = client.delete("/api/v1/connectors/c999", headers=auth_header)
        assert r.status_code == 404


# =============================================================================
# DASHBOARD
# =============================================================================

class TestDashboard:
    """اختبارات نقاط نهاية لوحة التحكم"""

    def test_dashboard_main(self, mock_db, auth_header):
        mock_db._all_result = []
        r = client.get("/api/v1/audit/dashboard", headers=auth_header)
        assert r.status_code == 200
        data = r.json()
        assert "riskScore" in data
        assert "findingsCount" in data

    def test_dashboard_risk_details(self, mock_db, auth_header):
        mock_db._all_result = []
        r = client.get("/api/v1/audit/dashboard/risk-details", headers=auth_header)
        assert r.status_code == 200
        assert "financial_risk" in r.json()

    def test_dashboard_compliance_details(self, mock_db, auth_header):
        mock_db._all_result = []
        r = client.get("/api/v1/audit/dashboard/compliance-details", headers=auth_header)
        assert r.status_code == 200
        assert "overall_compliance" in r.json()

    def test_dashboard_audit_progress(self, mock_db, auth_header):
        mock_db._all_result = []
        r = client.get("/api/v1/audit/dashboard/audit-progress", headers=auth_header)
        assert r.status_code == 200
        assert "overall_progress" in r.json()

    def test_dashboard_recommendations(self, mock_db, auth_header):
        mock_db._all_result = []
        r = client.get("/api/v1/audit/dashboard/recommendations", headers=auth_header)
        assert r.status_code == 200
        assert "immediate_actions" in r.json()

    def test_dashboard_summary_report(self, mock_db, auth_header):
        mock_db._all_result = []
        r = client.get("/api/v1/audit/dashboard/summary-report", headers=auth_header)
        assert r.status_code == 200
        assert "executive_summary" in r.json()

    def test_dashboard_with_findings(self, mock_db, auth_header):
        mock_db._all_result = [_make_mock_finding()]
        mock_db._count_result = 1
        r = client.get("/api/v1/audit/dashboard", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["findingsCount"] == 1

    def test_dashboard_recommendations_critical(self, mock_db, auth_header):
        mock_db._all_result = [_make_mock_finding({"severity": "Critical"})]
        mock_db._count_result = 1
        r = client.get("/api/v1/audit/dashboard/recommendations", headers=auth_header)
        assert r.status_code == 200
        recs = r.json()
        assert any("URGENT" in a for a in recs["immediate_actions"])


# =============================================================================
# DOCUMENTS
# =============================================================================

class TestDocuments:
    """اختبارات نقاط نهاية المستندات"""

    def test_list_documents(self, mock_db, auth_header):
        mock_db._all_result = [_make_mock_document()]
        r = client.get("/api/v1/documents/", headers=auth_header)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_documents_filtered(self, mock_db, auth_header):
        mock_db._all_result = []
        r = client.get("/api/v1/documents/?document_type=invoice&company_id=1", headers=auth_header)
        assert r.status_code == 200

    def test_upload_document(self, mock_db, auth_header):
        with patch("builtins.open", MagicMock()):
            r = client.post("/api/v1/documents/upload?document_type=invoice&company_id=1",
                files={"file": ("test.pdf", b"dummy content", "application/pdf")},
                headers=auth_header)
        assert r.status_code == 200
        data = r.json()
        assert data["file_name"] == "test.pdf"

    def test_get_document_found(self, mock_db, auth_header):
        mock_db._first_result = _make_mock_document()
        r = client.get("/api/v1/documents/1", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["file_name"] == "inv.pdf"

    def test_get_document_not_found(self, mock_db, auth_header):
        mock_db._first_result = None
        r = client.get("/api/v1/documents/999", headers=auth_header)
        assert r.status_code == 404

    def test_delete_document(self, mock_db, auth_header):
        mock_db._first_result = _make_mock_document()
        with patch("os.path.exists", return_value=True), patch("os.remove"):
            r = client.delete("/api/v1/documents/1", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_delete_document_nonexistent(self, mock_db, auth_header):
        mock_db._first_result = None
        r = client.delete("/api/v1/documents/999", headers=auth_header)
        assert r.status_code == 200

    def test_process_ocr(self, mock_db, auth_header):
        mock_db._first_result = _make_mock_document()
        r = client.post("/api/v1/documents/1/ocr", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_process_ocr_not_found(self, mock_db, auth_header):
        mock_db._first_result = None
        r = client.post("/api/v1/documents/999/ocr", headers=auth_header)
        assert r.status_code == 404

    def test_download_document_found(self, mock_db, auth_header, tmp_path):
        tmp_file = tmp_path / "test_download.pdf"
        tmp_file.write_bytes(b"dummy pdf content")
        mock_db._first_result = _make_mock_document({"file_path": str(tmp_file)})
        r = client.get("/api/v1/documents/1/download", headers=auth_header)
        assert r.status_code == 200

    def test_download_document_not_found(self, mock_db, auth_header):
        mock_db._first_result = None
        r = client.get("/api/v1/documents/999/download", headers=auth_header)
        assert r.status_code == 404


# =============================================================================
# FINDINGS
# =============================================================================

class TestFindings:
    """اختبارات نقاط نهاية النتائج"""

    def test_list_findings(self, mock_db, auth_header):
        mock_db._all_result = []
        r = client.get("/api/v1/findings/", headers=auth_header)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_findings_filtered(self, mock_db, auth_header):
        mock_db._all_result = [_make_mock_finding()]
        r = client.get("/api/v1/findings/?project_id=1&severity=Critical", headers=auth_header)
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_create_finding(self, mock_db, auth_header):
        mock_db._count_result = 0
        r = client.post("/api/v1/findings/", json={
            "project_id": 1, "title": "Error found",
            "description": "Test", "category": "Error",
            "severity": "High",
        }, headers=auth_header)
        assert r.status_code == 201
        assert r.json()["severity"] == "High"

    def test_update_finding_status(self, mock_db, auth_header):
        mock_db._first_result = _make_mock_finding()
        r = client.put("/api/v1/findings/1/status?status=Resolved", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_update_finding_status_not_found(self, mock_db, auth_header):
        mock_db._first_result = None
        r = client.put("/api/v1/findings/999/status?status=Resolved", headers=auth_header)
        assert r.status_code == 404

    def test_delete_finding(self, mock_db, auth_header):
        mock_db._first_result = _make_mock_finding()
        r = client.delete("/api/v1/findings/1", headers=auth_header)
        assert r.status_code == 200

    def test_delete_finding_nonexistent(self, mock_db, auth_header):
        mock_db._first_result = None
        r = client.delete("/api/v1/findings/999", headers=auth_header)
        assert r.status_code == 200


# =============================================================================
# NOTIFICATIONS
# =============================================================================

class TestNotifications:
    """اختبارات نقاط نهاية الإشعارات"""

    def test_send_notification_email(self, auth_header):
        with patch("backend.api.endpoints.notifications._service") as svc:
            svc.send_email.return_value = (True, "sent")
            r = client.post("/api/v1/notifications/send", json={
                "channel": "email", "title": "Test", "message": "Hello",
                "recipients": ["a@b.com"], "alert_type": "info"
            }, headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_send_notification_slack(self, auth_header):
        with patch("backend.api.endpoints.notifications._service") as svc:
            svc.send_slack.return_value = (True, "sent")
            r = client.post("/api/v1/notifications/send", json={
                "channel": "slack", "title": "Test", "message": "Hello",
                "recipients": ["https://hooks.slack.com/x"], "alert_type": "info"
            }, headers=auth_header)
        assert r.status_code == 200

    def test_send_notification_teams(self, auth_header):
        with patch("backend.api.endpoints.notifications._service") as svc:
            svc.send_teams.return_value = (True, "sent")
            r = client.post("/api/v1/notifications/send", json={
                "channel": "teams", "title": "Test", "message": "Hello",
                "recipients": ["https://teams.webhook/x"], "alert_type": "info"
            }, headers=auth_header)
        assert r.status_code == 200

    def test_send_notification_inapp(self, auth_header):
        with patch("backend.api.endpoints.notifications._service") as svc:
            r = client.post("/api/v1/notifications/send", json={
                "channel": "inapp", "title": "Test", "message": "Hello",
                "recipients": ["user1"], "alert_type": "info"
            }, headers=auth_header)
        assert r.status_code == 200

    def test_send_notification_unknown_channel(self, auth_header):
        with patch("backend.api.endpoints.notifications._service") as svc:
            svc.send_email.return_value = (True, "sent")
            r = client.post("/api/v1/notifications/send", json={
                "channel": "sms", "title": "Test", "message": "Hello",
                "recipients": ["+123"], "alert_type": "info"
            }, headers=auth_header)
        assert r.status_code == 200
        assert r.json()["results"][0]["success"] is False

    def test_fraud_alert(self, auth_header):
        with patch("backend.api.endpoints.notifications._service") as svc:
            svc.send_email.return_value = (True, "sent")
            r = client.post("/api/v1/notifications/fraud-alert"
                "?project_id=PROJ-1&risk_level=high&description=Suspicious",
                json=["a@b.com"],
                headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_audit_reminder(self, auth_header):
        with patch("backend.api.endpoints.notifications._service") as svc:
            svc.send_email.return_value = (True, "sent")
            r = client.post("/api/v1/notifications/audit-reminder"
                "?project_id=PROJ-1&days_overdue=5",
                json=["a@b.com"],
                headers=auth_header)
        assert r.status_code == 200

    def test_notification_history(self, auth_header):
        with patch("backend.api.endpoints.notifications._service") as svc:
            svc.get_notification_history.return_value = [{"id": 1, "event": "sent"}]
            r = client.get("/api/v1/notifications/history", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_available_channels(self, auth_header):
        with patch("backend.api.endpoints.notifications._service") as svc:
            svc.get_channel_status.return_value = {"email": True, "slack": False}
            r = client.get("/api/v1/notifications/channels", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True


# =============================================================================
# PREDICTIVE
# =============================================================================

class TestPredictive:
    """اختبارات نقاط نهاية التحليل التنبؤي"""

    def test_predict_revenue(self, auth_header):
        with patch("backend.api.endpoints.predictive._service") as svc:
            svc.predict_revenue.return_value = {"predictions": [110, 115, 120], "trend": "صاعد", "growth_rate": 0.05}
            r = client.post("/api/v1/predictive/revenue?periods=3",
                json=[100, 105, 110], headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_predict_fraud_risk(self, auth_header):
        with patch("backend.api.endpoints.predictive._service") as svc:
            svc.predict_fraud_risk.return_value = {"predicted_risk_score": 45, "indicators": ["التعديلات اليدوية"]}
            r = client.post("/api/v1/predictive/fraud-risk",
                json={"manual_adjustments_trend": "increasing"},
                headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_predict_cash_flow(self, auth_header):
        with patch("backend.api.endpoints.predictive._service") as svc:
            svc.predict_cash_flow_issues.return_value = {"risk": "low", "forecast": [100, 200]}
            r = client.post("/api/v1/predictive/cash-flow",
                json=[50000, 48000, 52000], headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True


# =============================================================================
# REPORTS
# =============================================================================

class TestReports:
    """اختبارات نقاط نهاية التقارير"""

    def test_create_report(self, mock_db, auth_header):
        mock_db._all_result = [_make_mock_finding()]
        with patch("backend.api.endpoints.reports.get_reporting_service") as svc_cls:
            svc = MagicMock()
            svc.create_audit_report.return_value = {"report_id": "RPT-001", "status": "created"}
            svc_cls.return_value = lambda: svc
            r = client.post("/api/v1/reports/create?project_id=1&report_type=audit", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_create_report_non_digit_project(self, mock_db, auth_header):
        with patch("backend.api.endpoints.reports.get_reporting_service") as svc_cls:
            svc = MagicMock()
            svc.create_audit_report.return_value = {"report_id": "RPT-002"}
            svc_cls.return_value = lambda: svc
            r = client.post("/api/v1/reports/create?project_id=PROJ-X&report_type=financial", headers=auth_header)
        assert r.status_code == 200

    def test_generate_summary(self, auth_header):
        with patch("backend.api.endpoints.reports.get_reporting_service") as svc_cls:
            svc = MagicMock()
            svc.generate_executive_summary.return_value = {"summary": "Executive overview"}
            svc_cls.return_value = lambda: svc
            r = client.post("/api/v1/reports/RPT-001/summary", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_generate_summary_not_found(self, auth_header):
        with patch("backend.api.endpoints.reports.get_reporting_service") as svc_cls:
            svc = MagicMock()
            svc.generate_executive_summary.return_value = None
            svc_cls.return_value = lambda: svc
            r = client.post("/api/v1/reports/RPT-999/summary", headers=auth_header)
        assert r.status_code == 404

    def test_export_report(self, auth_header):
        with patch("backend.api.endpoints.reports.get_reporting_service") as svc_cls:
            svc = MagicMock()
            svc.export_report.return_value = {"success": True, "url": "/exports/rpt.pdf"}
            svc_cls.return_value = lambda: svc
            r = client.post("/api/v1/reports/RPT-001/export?format=pdf", headers=auth_header)
        assert r.status_code == 200

    def test_export_report_not_found(self, auth_header):
        with patch("backend.api.endpoints.reports.get_reporting_service") as svc_cls:
            svc = MagicMock()
            svc.export_report.return_value = {"success": False}
            svc_cls.return_value = lambda: svc
            r = client.post("/api/v1/reports/RPT-999/export?format=pdf", headers=auth_header)
        assert r.status_code == 404

    def test_list_reports(self, auth_header):
        with patch("backend.api.endpoints.reports.get_reporting_service") as svc_cls:
            svc = MagicMock()
            svc.list_reports.return_value = [{"id": "RPT-001", "type": "audit"}]
            svc_cls.return_value = lambda: svc
            r = client.get("/api/v1/reports", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_list_reports_filtered(self, auth_header):
        with patch("backend.api.endpoints.reports.get_reporting_service") as svc_cls:
            svc = MagicMock()
            svc.list_reports.return_value = []
            svc_cls.return_value = lambda: svc
            r = client.get("/api/v1/reports?project_id=1", headers=auth_header)
        assert r.status_code == 200


# =============================================================================
# TASKS
# =============================================================================

class TestTasks:
    """اختبارات نقاط نهاية المهام"""

    def test_submit_task(self, auth_header):
        with patch("backend.api.endpoints.tasks.get_task_queue") as m:
            q = MagicMock()
            q.submit.return_value = "task-001"
            m.return_value = q
            r = client.post("/api/v1/tasks/submit?name=test_task", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["data"]["task_id"] == "task-001"

    def test_get_task_found(self, auth_header):
        with patch("backend.api.endpoints.tasks.get_task_queue") as m:
            q = MagicMock()
            task = MagicMock(
                task_id="task-001", name="test",
                status=MagicMock(value="success"),
                created_at=datetime.utcnow(),
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                error=None,
            )
            q.get_task.return_value = task
            m.return_value = q
            r = client.get("/api/v1/tasks/task-001", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["data"]["task_id"] == "task-001"

    def test_get_task_not_found(self, auth_header):
        with patch("backend.api.endpoints.tasks.get_task_queue") as m:
            q = MagicMock()
            q.get_task.return_value = None
            m.return_value = q
            r = client.get("/api/v1/tasks/task-999", headers=auth_header)
        assert r.status_code == 404

    def test_get_task_result(self, auth_header):
        with patch("backend.api.endpoints.tasks.get_task_queue") as m:
            q = MagicMock()
            q.get_result.return_value = {"processed": True}
            m.return_value = q
            r = client.get("/api/v1/tasks/task-001/result", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["data"]["result"]["processed"] is True

    def test_get_task_result_not_found(self, auth_header):
        from backend.core.tasks import TaskStatus
        with patch("backend.api.endpoints.tasks.get_task_queue") as m:
            q = MagicMock()
            q.get_result.return_value = None
            task = MagicMock()
            task.status = TaskStatus.FAILED
            task.error = "Something broke"
            q.get_task.return_value = task
            m.return_value = q
            r = client.get("/api/v1/tasks/task-999/result", headers=auth_header)
        assert r.status_code == 422

    def test_get_task_result_still_running(self, auth_header):
        from backend.core.tasks import TaskStatus
        with patch("backend.api.endpoints.tasks.get_task_queue") as m:
            q = MagicMock()
            q.get_result.return_value = None
            task = MagicMock()
            task.status = TaskStatus.RUNNING
            q.get_task.return_value = task
            m.return_value = q
            r = client.get("/api/v1/tasks/task-001/result", headers=auth_header)
        assert r.status_code == 202

    def test_cancel_task(self, auth_header):
        with patch("backend.api.endpoints.tasks.get_task_queue") as m:
            q = MagicMock()
            q.cancel.return_value = True
            m.return_value = q
            r = client.post("/api/v1/tasks/task-001/cancel", headers=auth_header)
        assert r.status_code == 200
        assert "cancelled" in r.json()["message"].lower()

    def test_cancel_task_not_found(self, auth_header):
        with patch("backend.api.endpoints.tasks.get_task_queue") as m:
            q = MagicMock()
            q.cancel.return_value = False
            m.return_value = q
            r = client.post("/api/v1/tasks/task-999/cancel", headers=auth_header)
        assert r.status_code == 404

    def test_list_tasks(self, auth_header):
        with patch("backend.api.endpoints.tasks.get_task_queue") as m:
            q = MagicMock()
            q.list_tasks.return_value = [{"task_id": "task-001", "name": "test"}]
            m.return_value = q
            r = client.get("/api/v1/tasks", headers=auth_header)
        assert r.status_code == 200
        assert len(r.json()["data"]) == 1

    def test_list_tasks_filtered(self, auth_header):
        with patch("backend.api.endpoints.tasks.get_task_queue") as m:
            q = MagicMock()
            q.list_tasks.return_value = []
            m.return_value = q
            r = client.get("/api/v1/tasks?status=running&limit=10", headers=auth_header)
        assert r.status_code == 200


# =============================================================================
# WEBHOOKS
# =============================================================================

class TestWebhooks:
    """اختبارات نقاط نهاية Webhook"""

    def test_register_webhook(self, auth_header):
        r = client.post("/api/v1/webhooks/register", json={
            "url": "https://example.com/webhook", "events": ["audit.completed"],
            "secret": "sec123", "retry_count": 3, "timeout": 30,
        }, headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True
        assert "subscription_id" in r.json()["data"]

    def test_list_webhooks(self, auth_header):
        r = client.get("/api/v1/webhooks", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_unregister_webhook_found(self, auth_header):
        reg = client.post("/api/v1/webhooks/register", json={
            "url": "https://example.com/wh", "events": ["*"],
        }, headers=auth_header)
        sub_id = reg.json()["data"]["subscription_id"]
        r = client.delete(f"/api/v1/webhooks/{sub_id}", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_unregister_webhook_not_found(self, auth_header):
        r = client.delete("/api/v1/webhooks/nonexistent", headers=auth_header)
        assert r.status_code == 404

    def test_delivery_log(self, auth_header):
        r = client.get("/api/v1/webhooks/delivery-log?limit=5", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True


# =============================================================================
# BACKUPS
# =============================================================================

class TestBackups:
    """اختبارات نقاط نهاية النسخ الاحتياطي"""

    def test_list_backups(self, auth_header):
        with patch("backend.api.endpoints.backups.list_backups", return_value=[]):
            r = client.get("/api/v1/backups/", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True
        assert "backups" in r.json()

    def test_create_backup(self, auth_header):
        with patch("backend.api.endpoints.backups.create_backup", return_value="/tmp/backup.zip"):
            r = client.post("/api/v1/backups/create", headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_create_backup_fail(self, auth_header):
        with patch("backend.api.endpoints.backups.create_backup", return_value=None):
            r = client.post("/api/v1/backups/create", headers=auth_header)
        assert r.status_code == 500

    def test_restore_backup(self, auth_header):
        with patch("backend.api.endpoints.backups.restore_backup", return_value=True):
            r = client.post("/api/v1/backups/restore", json={"filename": "backup.zip"}, headers=auth_header)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_restore_backup_fail(self, auth_header):
        with patch("backend.api.endpoints.backups.restore_backup", return_value=False):
            r = client.post("/api/v1/backups/restore", json={"filename": "bad.zip"}, headers=auth_header)
        assert r.status_code == 500


# =============================================================================
# AUTH GUARD (protected endpoints require token)
# =============================================================================

class TestAuthGuard:
    """اختبارات حماية نقاط النهاية"""

    ENDPOINTS = [
        ("GET", "/api/v1/audit-projects/"),
        ("POST", "/api/v1/audit-projects/"),
        ("GET", "/api/v1/companies/"),
        ("GET", "/api/v1/audit/dashboard"),
        ("GET", "/api/v1/findings/"),
        ("GET", "/api/v1/documents/"),
        ("GET", "/api/v1/notifications/channels"),
        ("POST", "/api/v1/predictive/revenue"),
        ("GET", "/api/v1/reports"),
        ("GET", "/api/v1/tasks"),
        ("GET", "/api/v1/webhooks"),
        ("GET", "/api/v1/backups/"),
        ("GET", "/api/v1/agents/"),
    ]

    @pytest.mark.parametrize("method,path", ENDPOINTS)
    def test_unauthenticated_access(self, method, path):
        app.dependency_overrides.pop(get_current_user, None)
        r = client.request(method, path)
        assert r.status_code in (401, 403), f"{method} {path} returned {r.status_code}"
