from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QGridLayout, QPushButton
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from loguru import logger
from frontend.api_client import get_client
from frontend.styles.design_system import DesignSystem, Color, Typography


AGENT_NAMES = {
    "chief_agent": "Chief Audit Agent", "journal_agent": "Journal Entry Agent",
    "ledger_agent": "General Ledger Agent", "tb_agent": "Trial Balance Agent",
    "fs_agent": "Financial Statements Agent", "tax_agent": "Tax Compliance Agent",
    "bank_agent": "Bank & Treasury Agent", "inventory_agent": "Inventory Agent",
    "assets_agent": "Fixed Assets Agent", "fraud_agent": "Fraud Detection Agent",
    "ocr_agent": "OCR Agent", "compliance_agent": "Compliance Agent",
    "behavior_agent": "Behavioral Agent", "risk_agent": "Risk Scoring Agent",
    "forensic_agent": "Forensic Agent", "xai_agent": "Explainable AI Agent",
    "qa_agent": "QA Agent", "executive_agent": "Executive Agent",
    "connector_agent": "Connector Agent", "monitoring_agent": "Monitoring Agent",
    "graph_agent": "Graph Agent", "copilot_agent": "Copilot Agent",
}

AGENT_DESCRIPTIONS = {
    "chief_agent": "Orchestrates the overall audit workflow across all agents",
    "journal_agent": "Reviews journal entries for compliance and accuracy",
    "ledger_agent": "Audits the general ledger for anomalies",
    "tb_agent": "Analyzes trial balance for discrepancies",
    "fs_agent": "Reviews financial statements for GAAP compliance",
    "tax_agent": "Ensures tax compliance and identifies exposures",
    "bank_agent": "Reconciles and audits banking transactions",
    "inventory_agent": "Verifies inventory records and counts",
    "assets_agent": "Audits fixed asset registers and depreciation",
    "fraud_agent": "Detects fraudulent patterns in financial data",
    "ocr_agent": "Extracts and processes document data",
    "compliance_agent": "Monitors regulatory compliance across standards",
    "behavior_agent": "Analyzes behavioral patterns for risk indicators",
    "risk_agent": "Calculates risk scores for transactions and entities",
    "forensic_agent": "Conducts deep forensic investigation on anomalies",
    "xai_agent": "Provides explainable AI insights for audit findings",
    "qa_agent": "Quality assurance and validation of audit results",
    "executive_agent": "Generates executive summaries and board reports",
    "connector_agent": "Manages ERP system connectors and data ingestion",
    "monitoring_agent": "Continuous monitoring of financial transactions",
    "graph_agent": "Network analysis of related parties and transactions",
    "copilot_agent": "Interactive AI assistant for audit professionals",
}

AGENT_ICONS = {
    "chief_agent": "C", "journal_agent": "J", "ledger_agent": "L", "tb_agent": "T",
    "fs_agent": "F", "tax_agent": "X", "bank_agent": "B", "inventory_agent": "I",
    "assets_agent": "A", "fraud_agent": "D", "ocr_agent": "O", "compliance_agent": "M",
    "behavior_agent": "H", "risk_agent": "R", "forensic_agent": "P", "xai_agent": "E",
    "qa_agent": "Q", "executive_agent": "V", "connector_agent": "N", "monitoring_agent": "W",
    "graph_agent": "G", "copilot_agent": "Y",
}


class AgentCard(QFrame):
    def __init__(self, name, display_name, description, icon):
        super().__init__()
        self.setObjectName("AgentCard")
        self.setStyleSheet(f"""
            QFrame#AgentCard {{
                background-color: {Color.BG_CARD};
                border: 1px solid {Color.BORDER};
                border-radius: 10px;
                padding: 16px;
            }}
            QFrame#AgentCard:hover {{
                border-color: {Color.PRIMARY};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            font-size: 18px; font-weight: 700; color: {Color.PRIMARY};
            background-color: {Color.PRIMARY}20;
            border-radius: 6px;
            padding: 6px 10px;
        """)
        icon_label.setFixedWidth(36)
        icon_label.setAlignment(Qt.AlignCenter)
        header.addWidget(icon_label)

        name_label = QLabel(display_name)
        name_label.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {Color.TEXT_PRIMARY};")
        header.addWidget(name_label)
        header.addStretch()

        status_label = QLabel("Registered")
        status_label.setObjectName("AgentStatus")
        status_label.setStyleSheet(f"font-size: 11px; color: {Color.INFO}; font-weight: 500;")
        header.addWidget(status_label)
        layout.addLayout(header)

        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"font-size: 12px; color: {Color.TEXT_SECONDARY};")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)


class AgentManagerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AgentManagerWidget")
        self.agent_cards = {}
        self._setup_ui()
        self._load_agents()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        title_label = QLabel("AI Agent Manager")
        title_label.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {Color.TEXT_PRIMARY};")
        main_layout.addWidget(title_label)

        status_bar = QHBoxLayout()
        self.total_label = QLabel("Loading...")
        self.total_label.setStyleSheet(f"color: {Color.TEXT_SECONDARY}; font-size: 13px;")
        status_bar.addWidget(self.total_label)
        status_bar.addStretch()
        main_layout.addLayout(status_bar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content_widget = QWidget()
        self.card_layout = QGridLayout(content_widget)
        self.card_layout.setSpacing(16)
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        refresh_timer = QTimer(self)
        refresh_timer.timeout.connect(self._load_agents)
        refresh_timer.start(30000)

    def _load_agents(self):
        try:
            client = get_client()
            data = client.get_agents()
            if isinstance(data, list):
                agents_data = {}
                for a in data:
                    name = a.get("agent_name", "unknown")
                    agents_data[name] = a
                total = len(agents_data)
            else:
                agents_data = data.get("agents", {})
                total = data.get("total", 0) or len(agents_data)
            self.total_label.setText(f"Total Agents: {total}")

            existing = set(self.agent_cards.keys())
            current = set(agents_data.keys())

            for name, info in agents_data.items():
                if name not in self.agent_cards:
                    card = self._create_agent_card(name)
                    self.agent_cards[name] = card
                    idx = len(self.agent_cards) - 1
                    self.card_layout.addWidget(card, idx // 2, idx % 2)
                self._update_card(name, info)

            for name in existing - current:
                card = self.agent_cards.pop(name, None)
                if card:
                    self.card_layout.removeWidget(card)
                    card.deleteLater()

        except Exception as e:
            logger.warning(f"Failed to load agents: {e}")
            self.total_label.setText("Offline - Unable to load agents")

            if not self.agent_cards:
                for i, (key, display_name) in enumerate(AGENT_NAMES.items()):
                    if i >= 6:
                        break
                    card = self._create_agent_card(key)
                    self.agent_cards[key] = card
                    self.card_layout.addWidget(card, i // 2, i % 2)
                    status_label = card.findChild(QLabel, "AgentStatus")
                    if status_label:
                        status_label.setText("Offline")
                        status_label.setStyleSheet(f"font-size: 11px; color: {Color.ERROR}; font-weight: 500;")

    def _create_agent_card(self, name):
        display_name = AGENT_NAMES.get(name, name.replace("_", " ").title())
        description = AGENT_DESCRIPTIONS.get(name, "")
        icon = AGENT_ICONS.get(name, "?")
        card = AgentCard(name, display_name, description, icon)
        return card

    def _update_card(self, name, info):
        card = self.agent_cards.get(name)
        if not card:
            return
        status_label = card.findChild(QLabel, "AgentStatus")
        if not status_label:
            return
        status = info.get("status", "registered")
        class_name = info.get("class_name", "")
        if status == "error":
            status_label.setText("Error")
            status_label.setStyleSheet(f"font-size: 11px; color: {Color.ERROR}; font-weight: 500;")
        elif status == "completed":
            status_label.setText(f"Ready ({class_name})")
            status_label.setStyleSheet(f"font-size: 11px; color: {Color.SUCCESS}; font-weight: 500;")
        else:
            status_label.setText(f"Registered ({class_name})")
            status_label.setStyleSheet(f"font-size: 11px; color: {Color.INFO}; font-weight: 500;")
