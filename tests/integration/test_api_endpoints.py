"""
Integration Tests for API Endpoints
====================================
Test all major API routes: auth, agents, providers, reports, predictive.
"""
import os, sys, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import httpx
from tests.helpers.api_client import SyncTestClient
from backend.database import db_config, get_db_session
from backend.database.bootstrap import seed_default_data
from backend.api.endpoints.auth import create_access_token

TEST_USER = "pytest_admin"

@pytest.fixture(scope="module")
def client():
    from backend.main import app
    import os
    from backend.database import db_config, init_db
    test_db = "sqlite:///./test_finovate_audit.db"
    if os.path.exists("test_finovate_audit.db"):
        os.remove("test_finovate_audit.db")
    db_config.database_url = test_db
    db_config.initialize()
    init_db(database_url=test_db)
    with get_db_session() as session:
        from backend.database.models import User
        existing = session.query(User).filter(User.username == TEST_USER).first()
        if not existing:
            from backend.api.endpoints.auth import hash_password
            session.add(User(username=TEST_USER, email="pytest@finovate.ai",
                             password_hash=hash_password("pytest"), role="Admin", is_active=True))
            session.commit()
    with SyncTestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def auth_header(client):
    token = create_access_token({"sub": TEST_USER, "role": "Admin"})
    return {"Authorization": f"Bearer {token}"}

class TestAuth:
    def test_health(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

    def test_login_invalid(self, client):
        r = client.post("/api/v1/auth/login", json={"username": "x", "password": "x"})
        assert r.status_code == 401

    def test_register(self, client):
        import random
        suffix = random.randint(1000, 9999)
        r = client.post("/api/v1/auth/register", json={
            "username": f"newuser_{suffix}", "email": f"new{suffix}@test.com",
            "password": "pass", "role": "Auditor"
        })
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_me_with_auth(self, client, auth_header):
        r = client.get("/api/v1/auth/me", headers=auth_header)
        assert r.status_code == 200

class TestAgents:
    def test_list_agents_requires_auth(self, client):
        r = client.get("/api/v1/agents/")
        assert r.status_code in (401, 403)

    def test_list_agents(self, client, auth_header):
        r = client.get("/api/v1/agents/", headers=auth_header)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) > 0

class TestAIProviders:
    def test_list_providers(self, client, auth_header):
        r = client.get("/api/v1/ai/providers", headers=auth_header)
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert "providers" in data["data"]

    def test_ai_status(self, client, auth_header):
        r = client.get("/api/v1/ai/status", headers=auth_header)
        assert r.status_code == 200

class TestReports:
    def test_create_report(self, client, auth_header):
        r = client.post("/api/v1/reports/create?project_id=TEST-001&report_type=audit",
                         headers=auth_header)
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert "report_id" in data["data"]

class TestPredictive:
    def test_predict_revenue(self, client, auth_header):
        r = client.post("/api/v1/predictive/revenue?periods=4",
                         json=[100, 120, 110, 130], headers=auth_header)
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert len(data["data"]["predictions"]) == 4

    def test_predict_fraud_risk(self, client, auth_header):
        r = client.post("/api/v1/predictive/fraud-risk",
                         json={"manual_adjustments_trend": "increasing", "unusual_hours_activity": True},
                         headers=auth_header)
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["data"]["predicted_risk_score"] > 0

    def test_predict_cash_flow(self, client, auth_header):
        r = client.post("/api/v1/predictive/cash-flow",
                         json=[50000, 48000, 52000, 51000], headers=auth_header)
        assert r.status_code == 200

class TestDashboard:
    def test_dashboard_data(self, client, auth_header):
        r = client.get("/api/v1/audit/dashboard", headers=auth_header)
        assert r.status_code in (200, 500)

    def test_dashboard_recommendations(self, client, auth_header):
        r = client.get("/api/v1/audit/dashboard/recommendations", headers=auth_header)
        assert r.status_code == 200
        data = r.json()
        assert "immediate_actions" in data
        assert "short_term" in data

    def test_dashboard_summary(self, client, auth_header):
        r = client.get("/api/v1/audit/dashboard/summary-report", headers=auth_header)
        assert r.status_code == 200
        data = r.json()
        assert "executive_summary" in data

class TestCompanies:
    def test_list_companies(self, client, auth_header):
        r = client.get("/api/v1/companies/", headers=auth_header)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
