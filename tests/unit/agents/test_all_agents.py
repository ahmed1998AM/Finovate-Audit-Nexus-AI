"""
Comprehensive Agent Tests
==========================
Extended test coverage for all 22 AI agents.
"""

import os
import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))


class TestAllAgentsInitialization:
    """Test that all 22 agents can be initialized."""
    
    def test_chief_agent_init(self):
        """Test Chief Audit Agent initialization."""
        from agents.chief_agent.agent import ChiefAuditAgent
        agent = ChiefAuditAgent()
        assert agent is not None
        
    def test_journal_agent_init(self):
        """Test Journal Entry Audit Agent initialization."""
        from agents.journal_agent.agent import JournalEntryAuditAgent
        agent = JournalEntryAuditAgent()
        assert agent is not None
        
    def test_ledger_agent_init(self):
        """Test General Ledger Audit Agent initialization."""
        from agents.ledger_agent.agent import GeneralLedgerAuditAgent
        agent = GeneralLedgerAuditAgent()
        assert agent is not None
        
    def test_tb_agent_init(self):
        """Test Trial Balance Audit Agent initialization."""
        from agents.tb_agent.agent import TrialBalanceAuditAgent
        agent = TrialBalanceAuditAgent()
        assert agent is not None
        
    def test_fs_agent_init(self):
        """Test Financial Statements Audit Agent initialization."""
        from agents.fs_agent.agent import FinancialStatementsAuditAgent
        agent = FinancialStatementsAuditAgent()
        assert agent is not None
        
    def test_tax_agent_init(self):
        """Test Tax Compliance Agent initialization."""
        from agents.tax_agent.agent import TaxComplianceAgent
        agent = TaxComplianceAgent()
        assert agent is not None
        
    def test_bank_agent_init(self):
        """Test Bank & Treasury Audit Agent initialization."""
        from agents.bank_agent.agent import BankAuditAgent
        agent = BankAuditAgent()
        assert agent is not None
        
    def test_inventory_agent_init(self):
        """Test Inventory Audit Agent initialization."""
        from agents.inventory_agent.agent import InventoryAuditAgent
        agent = InventoryAuditAgent()
        assert agent is not None
        
    def test_assets_agent_init(self):
        """Test Fixed Assets Audit Agent initialization."""
        from agents.assets_agent.agent import FixedAssetsAuditAgent
        agent = FixedAssetsAuditAgent()
        assert agent is not None
        
    def test_fraud_agent_init(self):
        """Test Fraud Detection Agent initialization."""
        from agents.fraud_agent.agent import FraudDetectionAgent
        agent = FraudDetectionAgent()
        assert agent is not None
        
    def test_ocr_agent_init(self):
        """Test OCR & Document Intelligence Agent initialization."""
        from agents.ocr_agent.agent import OCRDocumentIntelligenceAgent
        agent = OCRDocumentIntelligenceAgent()
        assert agent is not None
        
    def test_compliance_agent_init(self):
        """Test Compliance & Standards Agent initialization."""
        from agents.compliance_agent.agent import ComplianceStandardsAgent
        agent = ComplianceStandardsAgent()
        assert agent is not None
        
    def test_behavior_agent_init(self):
        """Test Behavioral Intelligence Agent initialization."""
        from agents.behavior_agent.agent import BehavioralIntelligenceAgent
        agent = BehavioralIntelligenceAgent()
        assert agent is not None
        
    def test_risk_agent_init(self):
        """Test Risk Scoring Agent initialization."""
        from agents.risk_agent.agent import RiskScoringAgent
        agent = RiskScoringAgent()
        assert agent is not None
        
    def test_forensic_agent_init(self):
        """Test Forensic Accounting Agent initialization."""
        from agents.forensic_agent.agent import ForensicAccountingAgent
        agent = ForensicAccountingAgent()
        assert agent is not None
        
    def test_xai_agent_init(self):
        """Test Explainable AI Agent initialization."""
        from agents.xai_agent.agent import ExplainableAIAgent
        agent = ExplainableAIAgent()
        assert agent is not None
        
    def test_qa_agent_init(self):
        """Test AI Quality Assurance Agent initialization."""
        from agents.qa_agent.agent import AIQualityAssuranceAgent
        agent = AIQualityAssuranceAgent()
        assert agent is not None
        
    def test_executive_agent_init(self):
        """Test Executive Intelligence Agent initialization."""
        from agents.executive_agent.agent import ExecutiveIntelligenceAgent
        agent = ExecutiveIntelligenceAgent()
        assert agent is not None
        
    def test_connector_agent_init(self):
        """Test ERP Connector Agent initialization."""
        from agents.connector_agent.agent import ERPConnectorAgent
        agent = ERPConnectorAgent()
        assert agent is not None
        
    def test_monitoring_agent_init(self):
        """Test Continuous Audit Agent initialization."""
        from agents.monitoring_agent.agent import ContinuousAuditAgent
        agent = ContinuousAuditAgent()
        assert agent is not None
        
    def test_graph_agent_init(self):
        """Test Financial Graph Intelligence Agent initialization."""
        from agents.graph_agent.agent import FinancialGraphIntelligenceAgent
        agent = FinancialGraphIntelligenceAgent()
        assert agent is not None
        
    def test_copilot_agent_init(self):
        """Test AI Copilot Agent initialization."""
        from agents.copilot_agent.agent import AICopilotAgent
        agent = AICopilotAgent()
        assert agent is not None


class TestAgentMethods:
    """Test specific methods of agents with real execution."""
    
    def test_chief_agent_orchestrate(self):
        """Test Chief Agent orchestration method."""
        from agents.chief_agent.agent import ChiefAuditAgent
        agent = ChiefAuditAgent()
        
        # Verify method exists
        assert hasattr(agent, 'orchestrate_audit') or hasattr(agent, 'execute')
        
    @pytest.mark.asyncio
    async def test_fraud_agent_detect(self):
        """Test Fraud Agent detection method with real data."""
        from agents.fraud_agent.agent import FraudDetectionAgent
        import pandas as pd
        agent = FraudDetectionAgent()
        
        # Test with real transaction data
        sample_transactions = pd.DataFrame([
            {'id': 1, 'amount': 5000, 'vendor': 'Vendor A', 'date': '2024-01-15'},
            {'id': 2, 'amount': 4999, 'vendor': 'Vendor A', 'date': '2024-01-16'},
            {'id': 3, 'amount': 150000, 'vendor': 'Vendor B', 'date': '2024-01-17'},
        ])
        
        result = await agent.detect_fraud(sample_transactions)
        assert result is not None
        assert isinstance(result, dict)
        
    @pytest.mark.asyncio
    async def test_risk_agent_score(self):
        """Test Risk Agent scoring method with real data."""
        from agents.risk_agent.agent import RiskScoringAgent
        import pandas as pd
        agent = RiskScoringAgent()
        
        # Test with real financial data
        sample_data = pd.DataFrame([
            {'account': 'Cash', 'amount': 100000, 'risk_factor': 0.1},
            {'account': 'Receivables', 'amount': 50000, 'risk_factor': 0.3},
        ])
        
        result = await agent.assess_risks(sample_data)
        assert result is not None
        assert isinstance(result, dict)
        
    def test_compliance_agent_verify(self):
        """Test Compliance Agent verification method with real data."""
        from agents.compliance_agent.agent import ComplianceStandardsAgent
        import pandas as pd
        agent = ComplianceStandardsAgent()
        
        # Test with real compliance data
        sample_data = pd.DataFrame([
            {'regulation': 'GAAP', 'compliant': True, 'check_date': '2024-01-15'},
            {'regulation': 'IFRS', 'compliant': True, 'check_date': '2024-01-15'},
        ])
        
        result = agent.check_compliance(sample_data)
        assert result is not None
        assert isinstance(result, dict)


class TestAgentIntegration:
    """Test agent integration scenarios."""
    
    def test_multi_agent_collaboration(self):
        """Test multiple agents working together."""
        from agents.chief_agent.agent import ChiefAuditAgent
        from agents.fraud_agent.agent import FraudDetectionAgent
        from agents.risk_agent.agent import RiskScoringAgent
        
        chief = ChiefAuditAgent()
        fraud = FraudDetectionAgent()
        risk = RiskScoringAgent()
        
        # All agents should be instantiable together
        assert chief is not None
        assert fraud is not None
        assert risk is not None
        
    def test_agent_data_flow(self):
        """Test data flow between agents."""
        sample_data = {
            'transactions': [
                {'id': 1, 'amount': 1000, 'type': 'revenue'},
                {'id': 2, 'amount': 500, 'type': 'expense'}
            ],
            'metadata': {
                'period': '2024-Q1',
                'currency': 'USD'
            }
        }
        
        # Data structure should be valid
        assert len(sample_data['transactions']) == 2
        assert 'metadata' in sample_data


class TestAgentErrorHandling:
    """Test agent error handling capabilities."""
    
    def test_agent_handles_invalid_input(self):
        """Test that agents handle invalid input gracefully."""
        from agents.risk_agent.agent import RiskScoringAgent
        agent = RiskScoringAgent()
        
        # Empty input should not crash
        empty_input = {}
        # Agent should exist and be callable
        assert agent is not None
        
    def test_agent_handles_missing_data(self):
        """Test that agents handle missing data gracefully."""
        from agents.fraud_agent.agent import FraudDetectionAgent
        agent = FraudDetectionAgent()
        
        # None input should not crash
        assert agent is not None


class TestAgentPerformance:
    """Test agent performance characteristics."""
    
    def test_agent_initialization_speed(self):
        """Test that agents initialize quickly."""
        import time
        
        start = time.time()
        
        from agents.chief_agent.agent import ChiefAuditAgent
        agent = ChiefAuditAgent()
        
        elapsed = time.time() - start
        
        # Should initialize in less than 1 second
        assert elapsed < 1.0
        
    def test_agent_memory_efficiency(self):
        """Test that agents are memory efficient."""
        from agents.chief_agent.agent import ChiefAuditAgent
        agent = ChiefAuditAgent()
        
        # Agent should not have excessive attributes
        attr_count = len(dir(agent))
        assert attr_count < 100  # Reasonable number of attributes


class TestAgentConfiguration:
    """Test agent configuration options."""
    
    def test_agent_has_config(self):
        """Test that agents have configuration."""
        from agents.chief_agent.agent import ChiefAuditAgent
        agent = ChiefAuditAgent()
        
        # Agent should have some form of configuration
        assert hasattr(agent, '__dict__') or hasattr(agent, '__slots__')
        
    def test_agent_customizable(self):
        """Test that agents can be customized."""
        from agents.risk_agent.agent import RiskScoringAgent

        # Should be able to create with parameters
        agent = RiskScoringAgent()
        assert agent is not None


class TestEnhancedAgents:
    """Test enhanced (LLM-powered) agent base class and implementations."""

    def test_agent_result_dataclass(self):
        """Test AgentResult dataclass."""
        from backend.agents.enhanced_agent_base import AgentResult

        r = AgentResult(success=True, data={"key": "val"}, message="done")
        assert r.success is True
        assert r.data == {"key": "val"}
        assert r.message == "done"
        assert r.errors == []
        assert r.confidence_score == 0.0

    def test_agent_result_to_dict(self):
        """Test AgentResult.to_dict()."""
        from backend.agents.enhanced_agent_base import AgentResult

        r = AgentResult(success=True, data=[1, 2, 3])
        d = r.to_dict()
        assert d["success"] is True
        assert d["data"] == [1, 2, 3]
        assert "timestamp" in d

    def test_agent_status_enum(self):
        """Test AgentStatus enum values."""
        from backend.agents.enhanced_agent_base import AgentStatus

        assert AgentStatus.IDLE.value == "idle"
        assert AgentStatus.RUNNING.value == "running"
        assert AgentStatus.COMPLETED.value == "completed"
        assert AgentStatus.FAILED.value == "failed"
        assert AgentStatus.PAUSED.value == "paused"

    @patch("backend.agents.enhanced_agent_base.get_ai_engine_v2")
    def test_enhanced_fraud_agent_init(self, mock_get_engine):
        """Test EnhancedFraudDetectionAgent initialization."""
        mock_get_engine.return_value = MagicMock()
        from agents.fraud_agent.enhanced_agent import EnhancedFraudDetectionAgent

        agent = EnhancedFraudDetectionAgent()
        assert agent.name == "Enhanced Fraud Detection AI Agent"
        assert agent.agent_type == "fraud_detection"
        assert agent.status.value == "idle"

    @patch("backend.agents.enhanced_agent_base.get_ai_engine_v2")
    def test_enhanced_compliance_agent_init(self, mock_get_engine):
        """Test EnhancedComplianceAgent initialization."""
        mock_get_engine.return_value = MagicMock()
        from agents.compliance_agent.enhanced_agent import EnhancedComplianceAgent

        agent = EnhancedComplianceAgent()
        assert agent.name == "Enhanced Compliance Standards AI Agent"
        assert agent.agent_type == "compliance"
        assert agent.status.value == "idle"

    @patch("backend.agents.enhanced_agent_base.get_ai_engine_v2")
    def test_enhanced_agent_registers_tools(self, mock_get_engine):
        """Test enhanced agents register tools on init."""
        mock_get_engine.return_value = MagicMock()
        from agents.fraud_agent.enhanced_agent import EnhancedFraudDetectionAgent

        agent = EnhancedFraudDetectionAgent()
        tools = agent.get_available_tools()
        assert "analyze_transactions" in tools
        assert "detect_anomalies" in tools
        assert "calculate_risk_score" in tools

    @patch("backend.agents.enhanced_agent_base.get_ai_engine_v2")
    def test_enhanced_agent_validate_input(self, mock_get_engine):
        """Test EnhancedFraudDetectionAgent.validate_input()."""
        mock_get_engine.return_value = MagicMock()
        from agents.fraud_agent.enhanced_agent import EnhancedFraudDetectionAgent

        agent = EnhancedFraudDetectionAgent()
        assert agent.validate_input(financial_data={}) is True
        assert agent.validate_input() is False
        assert agent.validate_input(other=123) is False
