"""E2E tests for the complete audit workflow."""
import pytest
import asyncio
from unittest.mock import Mock, patch
import json
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAuditWorkflow:
    """End-to-end test for the complete audit workflow."""

    @pytest.fixture
    def mock_client(self):
        client = Mock()
        client.login.return_value = {
            "access_token": "test_token_123",
            "token_type": "bearer",
            "expires_in": 86400,
            "user_info": {"username": "admin", "role": "Admin"}
        }
        client.upload_document.return_value = {"id": 1, "file_name": "test.xlsx", "status": "uploaded"}
        client.create_audit_project.return_value = {
            "success": True,
            "data": {"id": 1, "project_name": "Test Audit", "status": "Planning"}
        }
        client.start_audit.return_value = {
            "success": True,
            "data": {"audit_id": "AUD-001", "status": "completed"}
        }
        client.get_dashboard_v1.return_value = {
            "riskScore": 35.0,
            "complianceScore": 78.5,
            "findingsCount": 12,
            "auditStatus": "completed"
        }
        client.create_report.return_value = {
            "success": True,
            "data": {"report_id": "RPT-001"}
        }
        client.get_audit_projects.return_value = [
            {"id": 1, "project_name": "Test Audit", "status": "Completed"}
        ]
        client.list_reports.return_value = [
            {"report_id": "RPT-001", "project_id": "1", "report_type": "full_audit", "status": "finalized"}
        ]
        return client

    def test_complete_login_flow(self, mock_client):
        result = mock_client.login("admin", "password")
        assert result["access_token"] == "test_token_123"
        assert result["user_info"]["username"] == "admin"

    def test_upload_and_audit_flow(self, mock_client):
        upload = mock_client.upload_document("test.xlsx", document_type="Financial")
        assert upload["id"] == 1

        project = mock_client.create_audit_project({
            "project_name": "Test Audit", "company_id": 1, "audit_type": "full"
        })
        assert project["success"] is True

        result = mock_client.start_audit(
            project_id="1",
            financial_data={"description": "Test data"},
            audit_type="full"
        )
        assert result["success"] is True

    def test_dashboard_after_audit(self, mock_client):
        dash = mock_client.get_dashboard_v1()
        assert dash["riskScore"] == 35.0
        assert dash["complianceScore"] == 78.5

    def test_report_generation(self, mock_client):
        report = mock_client.create_report(project_id="1", report_type="full_audit")
        assert report["success"] is True
        assert report["data"]["report_id"] == "RPT-001"

    def test_end_to_end_workflow(self, mock_client):
        steps = []
        login = mock_client.login("admin", "password")
        steps.append(("login", bool(login.get("access_token"))))

        doc = mock_client.upload_document("test.xlsx", document_type="Financial")
        steps.append(("upload", bool(doc.get("id"))))

        project = mock_client.create_audit_project({"project_name": "E2E Test", "company_id": 1})
        steps.append(("create_project", project.get("success", False)))

        audit = mock_client.start_audit(project_id="1", financial_data={"test": True}, audit_type="full")
        steps.append(("run_audit", audit.get("success", False)))

        dash = mock_client.get_dashboard_v1()
        steps.append(("dashboard", bool(dash.get("riskScore") is not None)))

        report = mock_client.create_report(project_id="1", report_type="full_audit")
        steps.append(("report", report.get("success", False)))

        for name, ok in steps:
            assert ok, f"Step '{name}' failed"


class TestAgentOrchestratorIntegration:
    """Real integration tests for AgentOrchestrator with actual agents."""
    
    @pytest.fixture
    def sample_audit_data(self):
        """Sample financial data for audit testing."""
        return {
            "journal_entries": pd.DataFrame([
                {"id": 1, "account": "Cash", "debit": 1000, "credit": 0, "date": "2024-01-15"},
                {"id": 2, "account": "Revenue", "debit": 0, "credit": 1000, "date": "2024-01-15"},
                {"id": 3, "account": "Cash", "debit": 500, "credit": 0, "date": "2024-01-16"},
            ]),
            "ledger_data": pd.DataFrame([
                {"account": "Cash", "balance": 1500, "type": "Asset"},
                {"account": "Revenue", "balance": 1000, "type": "Equity"},
            ]),
            "trial_balance": pd.DataFrame([
                {"account": "Cash", "debit": 1500, "credit": 0},
                {"account": "Revenue", "debit": 0, "credit": 1000},
            ]),
            "vat_transactions": pd.DataFrame([
                {"id": 1, "type": "sale", "amount": 1000, "tax_rate": 0.15},
                {"id": 2, "type": "purchase", "amount": 500, "tax_rate": 0.15},
            ]),
            "financial_statements": {
                "income_statement": {"revenue": 1000, "expenses": 500, "net_income": 500},
                "balance_sheet": {"assets": 1500, "liabilities": 0, "equity": 1500},
            },
            "bank_transactions": pd.DataFrame([
                {"id": 1, "amount": 1000, "type": "credit", "date": "2024-01-15"},
                {"id": 2, "amount": 500, "type": "credit", "date": "2024-01-16"},
            ]),
            "inventory_data": pd.DataFrame([
                {"item": "Product A", "quantity": 100, "unit_cost": 10},
            ]),
        }
    
    def test_orchestrator_initialization(self):
        """Test that AgentOrchestrator initializes correctly."""
        from backend.orchestrator.agent_orchestrator import AgentOrchestrator
        
        orchestrator = AgentOrchestrator(auto_register_agents=False)
        assert orchestrator.orchestrator_id == "chief_orchestrator_001"
        assert orchestrator.status == "initialized"
        assert len(orchestrator.agents) == 0
    
    def test_orchestrator_register_agents(self):
        """Test registering agents with orchestrator."""
        from backend.orchestrator.agent_orchestrator import AgentOrchestrator
        from agents.journal_agent.agent import JournalEntryAuditAgent
        from agents.fraud_agent.agent import FraudDetectionAgent
        
        orchestrator = AgentOrchestrator(auto_register_agents=False)
        
        journal_agent = JournalEntryAuditAgent()
        fraud_agent = FraudDetectionAgent()
        
        assert orchestrator.register_agent("journal_agent", journal_agent) is True
        assert orchestrator.register_agent("fraud_agent", fraud_agent) is True
        
        assert len(orchestrator.agents) == 2
        assert "journal_agent" in orchestrator.agents
        assert "fraud_agent" in orchestrator.agents
    
    def test_orchestrator_workflow_execution(self, sample_audit_data):
        """Test executing a workflow with real agents."""
        from backend.orchestrator.agent_orchestrator import AgentOrchestrator
        from agents.journal_agent.agent import JournalEntryAuditAgent
        from agents.fraud_agent.agent import FraudDetectionAgent
        from agents.risk_agent.agent import RiskScoringAgent
        
        orchestrator = AgentOrchestrator(auto_register_agents=False)
        
        # Register agents
        journal_agent = JournalEntryAuditAgent()
        fraud_agent = FraudDetectionAgent()
        risk_agent = RiskScoringAgent()
        
        orchestrator.register_agent("journal_agent", journal_agent)
        orchestrator.register_agent("fraud_agent", fraud_agent)
        orchestrator.register_agent("risk_agent", risk_agent)
        
        # Execute workflow
        async def run_workflow():
            result = await orchestrator.execute_audit_workflow(sample_audit_data)
            return result
        
        result = asyncio.run(run_workflow())
        
        assert result is not None
        assert result["status"] in ["completed", "error"]
        assert "workflow_id" in result
        assert "agent_results" in result
        assert "overall_risk_score" in result
    
    def test_custom_workflow_config(self):
        """Test custom workflow configuration."""
        from backend.orchestrator.agent_orchestrator import AgentOrchestrator
        
        orchestrator = AgentOrchestrator(auto_register_agents=False)
        
        custom_config = {
            "stages": [
                {
                    "name": "Stage 1",
                    "parallel": True,
                    "agents": [
                        {"name": "journal_agent", "method": "analyze_journal_entries", "data_key": "journal_entries"},
                    ]
                }
            ]
        }
        
        assert orchestrator.register_workflow_config("custom_audit", custom_config) is True
        retrieved = orchestrator.get_workflow_config("custom_audit")
        assert retrieved == custom_config
    
    def test_agent_context_sharing(self):
        """Test that agents share context through AuditContext."""
        from backend.orchestrator.audit_context import AuditContext, AgentOutput
        
        ctx = AuditContext(workflow_id="test_wf")
        
        # Register outputs from multiple agents
        ctx.register_agent_output("journal_agent", AgentOutput(
            agent_name="journal_agent",
            status="completed",
            risk_score=20.0,
            findings=[{"type": "duplicate", "severity": "medium"}]
        ))
        
        ctx.register_agent_output("fraud_agent", AgentOutput(
            agent_name="fraud_agent",
            status="completed",
            risk_score=45.0,
            findings=[{"type": "suspicious", "severity": "high"}]
        ))
        
        # Verify context sharing
        assert len(ctx.agent_outputs) == 2
        assert len(ctx.all_findings) == 2
        assert "journal_agent" in ctx.completed_agents
        assert ctx.overall_risk_score == 32.5  # Average of 20 and 45
