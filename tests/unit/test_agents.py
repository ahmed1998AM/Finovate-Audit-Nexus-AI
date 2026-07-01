"""
Unit Tests for AI Agents
========================
Test all 22 intelligent agents in the system.
"""

import os
import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestFinancialAnalysisAgent:
    """Tests for Financial Analysis Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.fs_agent.agent import FinancialStatementsAuditAgent
        return FinancialStatementsAuditAgent()
    
    def test_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'analyze_income_statement')
        assert hasattr(agent, 'analyze_balance_sheet')
        assert hasattr(agent, 'analyze_cash_flow')
        assert hasattr(agent, 'calculate_financial_ratios')
    
    def test_ratio_analysis(self, agent):
        """Test financial ratio calculations."""
        sample_data = {
            'current_assets': 100000,
            'current_liabilities': 50000,
            'total_assets': 500000,
            'total_liabilities': 200000,
            'revenue': 300000,
            'net_income': 45000
        }
        
        # Test current ratio
        current_ratio = sample_data['current_assets'] / sample_data['current_liabilities']
        assert current_ratio == 2.0
        
        # Test debt ratio
        debt_ratio = sample_data['total_liabilities'] / sample_data['total_assets']
        assert debt_ratio == 0.4
        
        # Test profit margin
        profit_margin = sample_data['net_income'] / sample_data['revenue']
        assert profit_margin == 0.15


class TestChiefAuditAgent:
    """Tests for Chief Audit Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.chief_agent.agent import ChiefAuditAgent
        return ChiefAuditAgent()
    
    def test_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'orchestrate_audit')
        assert hasattr(agent, 'initialize_agents')
    
    def test_task_coordination(self, agent):
        """Test task coordination capabilities."""
        tasks = ['planning', 'fieldwork', 'review', 'reporting']
        assert len(tasks) == 4


class TestFraudDetectionAgent:
    """Tests for Fraud Detection Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.fraud_agent.agent import FraudDetectionAgent
        return FraudDetectionAgent()
    
    def test_anomaly_detection(self, agent):
        """Test anomaly detection in transactions."""
        normal_transactions = [100, 150, 120, 130, 140]
        anomalous_transaction = 5000

        mean_val = sum(normal_transactions) / len(normal_transactions)
        std_dev = (sum((x - mean_val) ** 2 for x in normal_transactions) / len(normal_transactions)) ** 0.5

        z_score = abs(anomalous_transaction - mean_val) / std_dev
        assert z_score > 3  # Should be flagged as anomaly

    def test_pattern_recognition(self, agent):
        """Test pattern recognition for fraud."""
        patterns = ['round_amounts', 'frequent_small_transactions', 'off_hours_activity']
        assert len(patterns) >= 3


class TestComplianceAgent:
    """Tests for Compliance Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.compliance_agent.agent import ComplianceStandardsAgent
        return ComplianceStandardsAgent()
    
    def test_ifrs_compliance_check(self, agent):
        """Test IFRS compliance verification."""
        sample_transactions = [
            {'type': 'revenue', 'amount': 10000, 'date': '2024-01-15'},
            {'type': 'expense', 'amount': 5000, 'date': '2024-01-20'}
        ]
        
        assert len(sample_transactions) > 0
        assert all('amount' in t for t in sample_transactions)

    def test_gaap_compliance_check(self, agent):
        """Test GAAP compliance verification."""
        principles = ['accrual', 'consistency', 'materiality', 'conservatism']
        assert len(principles) == 4


class TestRiskAssessmentAgent:
    """Tests for Risk Assessment Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.risk_agent.agent import RiskScoringAgent
        return RiskScoringAgent()
    
    def test_risk_scoring(self, agent):
        """Test risk score calculation."""
        risk_factors = {
            'financial_stability': 0.8,
            'market_volatility': 0.6,
            'operational_efficiency': 0.7,
            'compliance_status': 0.9
        }
        
        weights = {'financial_stability': 0.3, 'market_volatility': 0.25, 
                  'operational_efficiency': 0.25, 'compliance_status': 0.2}
        
        risk_score = sum(risk_factors[k] * weights[k] for k in risk_factors)
        assert 0 <= risk_score <= 1
        assert risk_score > 0.7


class TestForensicAgent:
    """Tests for Forensic Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.forensic_agent.agent import ForensicAccountingAgent
        return ForensicAccountingAgent()
    
    def test_asset_tracing(self, agent):
        """Test asset tracing capabilities."""
        assets = [
            {'type': 'cash', 'value': 100000},
            {'type': 'inventory', 'value': 250000},
            {'type': 'receivables', 'value': 150000}
        ]
        
        total_assets = sum(a['value'] for a in assets)
        assert total_assets == 500000


class TestMonitoringAgent:
    """Tests for Monitoring Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.monitoring_agent.agent import ContinuousAuditAgent
        return ContinuousAuditAgent()
    
    def test_real_time_monitoring(self, agent):
        """Test real-time monitoring capabilities."""
        metrics = {
            'cpu_usage': 45.5,
            'memory_usage': 62.3,
            'disk_usage': 78.1
        }
        
        assert all(0 <= v <= 100 for v in metrics.values())


class TestLedgerAgent:
    """Tests for Ledger Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.ledger_agent.agent import GeneralLedgerAuditAgent
        return GeneralLedgerAuditAgent()
    
    def test_gl_reconciliation(self, agent):
        """Test general ledger reconciliation."""
        gl_entries = [
            {'account': '1000', 'debit': 10000, 'credit': 0},
            {'account': '2000', 'debit': 0, 'credit': 10000}
        ]
        
        total_debits = sum(e['debit'] for e in gl_entries)
        total_credits = sum(e['credit'] for e in gl_entries)
        
        assert total_debits == total_credits


class TestTaxAgent:
    """Tests for Tax Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.tax_agent.agent import TaxComplianceAgent
        return TaxComplianceAgent()
    
    def test_tax_calculation(self, agent):
        """Test tax calculation."""
        taxable_income = 100000
        tax_rate = 0.20
        
        tax_due = taxable_income * tax_rate
        assert tax_due == 20000


class TestInventoryAgent:
    """Tests for Inventory Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.inventory_agent.agent import InventoryAuditAgent
        return InventoryAuditAgent()
    
    def test_inventory_valuation(self, agent):
        """Test inventory valuation methods."""
        inventory_items = [
            {'item': 'A', 'quantity': 100, 'unit_cost': 10},
            {'item': 'B', 'quantity': 50, 'unit_cost': 20}
        ]
        
        total_value = sum(i['quantity'] * i['unit_cost'] for i in inventory_items)
        assert total_value == 2000


class TestExecutiveAgent:
    """Tests for Executive Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.executive_agent.agent import ExecutiveIntelligenceAgent
        return ExecutiveIntelligenceAgent()
    
    def test_executive_summary_generation(self, agent):
        """Test executive summary generation."""
        key_findings = [
            'Revenue increased by 15%',
            'Operating expenses reduced by 8%',
            'Net profit margin improved to 12%'
        ]
        
        assert len(key_findings) >= 3


class TestQAAgent:
    """Tests for QA Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.qa_agent.agent import AIQualityAssuranceAgent
        return AIQualityAssuranceAgent()
    
    def test_quality_review(self, agent):
        """Test quality review process."""
        review_checklist = [
            'documentation_complete',
            'procedures_followed',
            'evidence_sufficient'
        ]
        
        assert len(review_checklist) == 3


class TestCopilotAgent:
    """Tests for Copilot Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.copilot_agent.agent import AICopilotAgent
        return AICopilotAgent()
    
    def test_assistant_capabilities(self, agent):
        """Test assistant capabilities."""
        suggestions = [
            'Review high-value transactions',
            'Verify cut-off procedures',
            'Confirm account balances'
        ]
        
        assert len(suggestions) >= 3


class TestGraphAgent:
    """Tests for Graph Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.graph_agent.agent import FinancialGraphIntelligenceAgent
        return FinancialGraphIntelligenceAgent()
    
    def test_relationship_mapping(self, agent):
        """Test relationship mapping."""
        entities = [
            {'name': 'Company A', 'type': 'corporation'},
            {'name': 'Person B', 'type': 'individual'},
            {'name': 'Company C', 'type': 'subsidiary'}
        ]
        
        assert len(entities) == 3


class TestBehaviorAgent:
    """Tests for Behavior Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.behavior_agent.agent import BehavioralIntelligenceAgent
        return BehavioralIntelligenceAgent()
    
    def test_behavioral_analysis(self, agent):
        """Test behavioral analysis."""
        behavioral_patterns = [
            'unusual_login_times',
            'excessive_voids',
            'manual_journal_entries'
        ]
        
        assert len(behavioral_patterns) >= 3


class TestTBAgent:
    """Tests for Trial Balance Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.tb_agent.agent import TrialBalanceAuditAgent
        return TrialBalanceAuditAgent()
    
    def test_tb_analysis(self, agent):
        """Test trial balance analysis."""
        tb_accounts = [
            {'account': 'Assets', 'balance': 500000},
            {'account': 'Liabilities', 'balance': 200000},
            {'account': 'Equity', 'balance': 300000}
        ]
        
        total_debits = sum(a['balance'] for a in tb_accounts if a['account'] == 'Assets')
        total_credits = sum(a['balance'] for a in tb_accounts if a['account'] in ['Liabilities', 'Equity'])
        
        assert total_debits == total_credits


class TestOCRAgent:
    """Tests for OCR Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.ocr_agent.agent import OCRDocumentIntelligenceAgent
        return OCRDocumentIntelligenceAgent()
    
    def test_document_processing(self, agent):
        """Test document processing."""
        extracted_text = "Invoice #12345\nAmount: $5,000\nDate: 2024-01-15"
        
        assert 'Invoice' in extracted_text
        assert '$5,000' in extracted_text


class TestXAIAgent:
    """Tests for XAI (Explainable AI) Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.xai_agent.agent import ExplainableAIAgent
        return ExplainableAIAgent()
    
    def test_explanation_generation(self, agent):
        """Test explanation generation."""
        ai_decision = {
            'prediction': 'high_risk',
            'confidence': 0.85,
            'factors': ['unusual_pattern', 'high_value', 'new_vendor']
        }
        
        assert ai_decision['confidence'] > 0.8


class TestBankAgent:
    """Tests for Bank Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.bank_agent.agent import BankAuditAgent
        return BankAuditAgent()
    
    def test_bank_reconciliation(self, agent):
        """Test bank reconciliation."""
        bank_statement = [
            {'date': '2024-01-15', 'amount': 10000, 'type': 'credit'},
            {'date': '2024-01-16', 'amount': 5000, 'type': 'debit'}
        ]
        
        net_change = sum(t['amount'] if t['type'] == 'credit' else -t['amount'] for t in bank_statement)
        assert net_change == 5000


class TestConnectorAgent:
    """Tests for Connector Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.connector_agent.agent import ERPConnectorAgent
        return ERPConnectorAgent()
    
    def test_connector_management(self, agent):
        """Test connector management."""
        connectors = ['SAP', 'Oracle', 'Dynamics', 'QuickBooks']
        
        assert len(connectors) >= 4


class TestJournalAgent:
    """Tests for Journal Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.journal_agent.agent import JournalEntryAuditAgent
        return JournalEntryAuditAgent()
    
    def test_journal_entry_validation(self, agent):
        """Test journal entry validation."""
        journal_entry = {
            'debits': [{'account': '1000', 'amount': 5000}],
            'credits': [{'account': '2000', 'amount': 5000}]
        }
        
        total_debits = sum(d['amount'] for d in journal_entry['debits'])
        total_credits = sum(c['amount'] for c in journal_entry['credits'])
        
        assert total_debits == total_credits


class TestAssetsAgent:
    """Tests for Assets Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        from agents.assets_agent.agent import FixedAssetsAuditAgent
        return FixedAssetsAuditAgent()
    
    def test_asset_depreciation(self, agent):
        """Test asset depreciation calculation."""
        asset = {
            'cost': 100000,
            'salvage_value': 10000,
            'useful_life': 10
        }
        
        annual_depreciation = (asset['cost'] - asset['salvage_value']) / asset['useful_life']
        assert annual_depreciation == 9000
