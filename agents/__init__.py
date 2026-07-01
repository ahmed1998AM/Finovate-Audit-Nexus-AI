"""Finovate Audit Nexus AI - Agents Package"""

from .assets_agent.agent import FixedAssetsAuditAgent
from .bank_agent.agent import BankAuditAgent
from .behavior_agent.agent import BehavioralIntelligenceAgent
from .chief_agent.agent import ChiefAuditAgent
from .compliance_agent.agent import ComplianceStandardsAgent
from .connector_agent.agent import ERPConnectorAgent
from .copilot_agent.agent import AICopilotAgent
from .executive_agent.agent import ExecutiveIntelligenceAgent
from .forensic_agent.agent import ForensicAccountingAgent
from .fraud_agent.agent import FraudDetectionAgent
from .fs_agent.agent import FinancialStatementsAuditAgent
from .graph_agent.agent import FinancialGraphIntelligenceAgent
from .inventory_agent.agent import InventoryAuditAgent
from .journal_agent.agent import JournalEntryAuditAgent
from .ledger_agent.agent import GeneralLedgerAuditAgent
from .monitoring_agent.agent import ContinuousAuditAgent
from .ocr_agent.agent import OCRDocumentIntelligenceAgent
from .qa_agent.agent import AIQualityAssuranceAgent
from .risk_agent.agent import RiskScoringAgent
from .tax_agent.agent import TaxComplianceAgent
from .tb_agent.agent import TrialBalanceAuditAgent
from .xai_agent.agent import ExplainableAIAgent

__version__ = "2.0.0"
__all__ = [
    "AICopilotAgent",
    "AIQualityAssuranceAgent",
    "BankAuditAgent",
    "BehavioralIntelligenceAgent",
    "ChiefAuditAgent",
    "ComplianceStandardsAgent",
    "ContinuousAuditAgent",
    "ERPConnectorAgent",
    "ExecutiveIntelligenceAgent",
    "ExplainableAIAgent",
    "FinancialGraphIntelligenceAgent",
    "FinancialStatementsAuditAgent",
    "FixedAssetsAuditAgent",
    "ForensicAccountingAgent",
    "FraudDetectionAgent",
    "GeneralLedgerAuditAgent",
    "InventoryAuditAgent",
    "JournalEntryAuditAgent",
    "OCRDocumentIntelligenceAgent",
    "RiskScoringAgent",
    "TaxComplianceAgent",
    "TrialBalanceAuditAgent",
]
