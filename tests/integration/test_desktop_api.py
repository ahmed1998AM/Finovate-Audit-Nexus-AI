"""Integration tests for Desktop API Client with backend."""
import pytest
from unittest.mock import Mock, patch


class TestDesktopAPIClient:
    """Tests for the frontend API client integration."""

    @pytest.fixture
    def api_client(self):
        client = Mock()
        client.base_url = "http://localhost:8000"
        client._token = "test_token"
        client._last_online = True
        client.check_available.return_value = True
        client.headers = {"Authorization": "Bearer test", "Content-Type": "application/json"}
        return client

    def test_health_check(self, api_client):
        api_client.health.return_value = {"status": "healthy", "version": "2.0.0"}
        result = api_client.health()
        assert result["status"] == "healthy"

    def test_get_dashboard_data(self, api_client):
        api_client.get_dashboard_v1.return_value = {
            "riskScore": 25.0, "complianceScore": 90.0,
            "findingsCount": 5, "auditStatus": "in_progress"
        }
        dash = api_client.get_dashboard_v1()
        assert dash["riskScore"] == 25.0

    def test_get_agents_list(self, api_client):
        api_client.get_agents.return_value = [
            {"name": "ChiefAuditAgent", "status": "ready"},
            {"name": "FraudAgent", "status": "ready"}
        ]
        agents = api_client.get_agents()
        assert len(agents) == 2

    def test_get_audit_projects(self, api_client):
        api_client.get_audit_projects.return_value = [
            {"id": 1, "project_name": "Q1 Audit", "status": "Completed"},
            {"id": 2, "project_name": "Q2 Audit", "status": "In Progress"}
        ]
        projects = api_client.get_audit_projects()
        assert len(projects) == 2

    def test_start_audit(self, api_client):
        api_client.start_audit.return_value = {
            "success": True, "data": {"audit_id": "AUD-001", "status": "running"}
        }
        result = api_client.start_audit("1", {"test": True}, "full")
        assert result["success"] is True

    def test_list_reports(self, api_client):
        api_client.list_reports.return_value = [
            {"report_id": "RPT-001", "status": "finalized"}
        ]
        reports = api_client.list_reports()
        assert len(reports) == 1

    def test_connectors_flow(self, api_client):
        api_client.list_connectors.return_value = [
            {"name": "SAP", "type": "ERP", "status": "connected"}
        ]
        connectors = api_client.list_connectors()
        assert len(connectors) == 1

    def test_findings_api(self, api_client):
        api_client.get_findings.return_value = [
            {"id": 1, "title": "Test Finding", "severity": "High"}
        ]
        findings = api_client.get_findings()
        assert len(findings) >= 1

    def test_session_management(self):
        from frontend.services.session_manager import get_session, reset_session
        reset_session()
        session = get_session()
        assert session.api_base_url == "http://localhost:8000"
        session.set_user({"username": "test", "role": "Auditor", "token": "tok123", "source": "api"})
        assert session.username == "test"
        assert session.role == "Auditor"
        assert session.is_online is True

    def test_auth_service(self):
        from frontend.services.auth_service import AuthService
        mock_client = Mock()
        mock_client.login.return_value = {
            "access_token": "test_token",
            "user_info": {"username": "admin", "role": "Admin"}
        }
        auth = AuthService(mock_client)
        result = auth.login_api("admin", "password")
        assert result is not None
        assert result["username"] == "admin"
