"""
Finovate Audit Nexus AI - Frontend Package
Desktop UI components and windows for the financial audit platform.
"""

from .components.theme_manager import ThemeManager
from .components.audit_card import AuditCard
from .components.risk_gauge import RiskGauge
from .components.financial_chart import FinancialChart
from .components.agent_status_widget import AgentStatusWidget, AgentsDashboard
from .dashboard.main_window import MainWindow

__all__ = [
    'ThemeManager',
    'AuditCard',
    'RiskGauge',
    'FinancialChart',
    'AgentStatusWidget',
    'AgentsDashboard',
    'MainWindow'
]
