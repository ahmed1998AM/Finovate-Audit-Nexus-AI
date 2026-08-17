from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QFrame, QScrollArea, QGridLayout, QHBoxLayout,
    QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, Signal

from frontend.api_client import get_client
from frontend.styles.design_system import Color


class StatCard(QFrame):
    CARD_PALETTE = [
        Color.INFO, Color.ACCENT, Color.SUCCESS,
        Color.WARNING, Color.PRIMARY, Color.ERROR,
    ]

    def __init__(self, title, value="---", subtitle="", icon="", accent_color=None):
        super().__init__()
        self._accent = accent_color or Color.PRIMARY
        self.setObjectName("StatCard")
        self.setStyleSheet(f"""
            QFrame#StatCard {{
                background-color: {Color.BG_CARD};
                border: 1px solid {Color.BORDER};
                border-radius: 16px;
                padding: 24px;
            }}
            QFrame#StatCard:hover {{
                border: 1px solid {self._accent};
                background-color: {Color.BG_HOVER};
            }}
        """)
        self.setMinimumSize(200, 140)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(20, 16, 20, 16)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px;")
        layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 13px; color: {Color.TEXT_SECONDARY}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px;")
        layout.addWidget(title_label)

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"font-size: 32px; font-weight: 800; color: {Color.TEXT_WHITE}; margin-top: 4px;")
        layout.addWidget(self.value_label)

        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setStyleSheet(f"font-size: 11px; color: {Color.TEXT_MUTED};")
        layout.addWidget(self.subtitle_label)

    def set_value(self, value):
        self.value_label.setText(value)

    def set_subtitle(self, subtitle):
        self.subtitle_label.setText(subtitle)


class MainDashboard(QWidget):
    audit_started = Signal(dict)
    report_ready = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MainDashboard")
        self.cards = {}
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)

        title_label = QLabel("Dashboard")
        title_label.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {Color.TEXT_PRIMARY}; padding: 0;")
        main_layout.addWidget(title_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        self.card_layout = QGridLayout(content_widget)
        self.card_layout.setSpacing(16)

        self._create_stat_cards()

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        refresh_timer = QTimer(self)
        refresh_timer.timeout.connect(self._load_data)
        refresh_timer.start(30000)

    def _create_stat_cards(self):
        palette = StatCard.CARD_PALETTE
        cards_data = [
            ("companies", "Companies", "جارٍ التحميل...", "🏢", palette[0]),
            ("agents", "AI Agents", "جارٍ التحميل...", "🤖", palette[1]),
            ("projects", "Audit Projects", "جارٍ التحميل...", "📋", palette[2]),
            ("risks", "Risks Detected", "جارٍ التحميل...", "⚠️", palette[3]),
            ("tasks", "Tasks Completed", "جارٍ التحميل...", "✅", palette[4]),
            ("accuracy", "Accuracy Rate", "جارٍ التحميل...", "📊", palette[5]),
        ]
        positions = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
        for (key, title, subtitle, icon, color), (row, col) in zip(cards_data, positions):
            card = StatCard(title, "---", subtitle, icon, color)
            self.cards[key] = card
            self.card_layout.addWidget(card, row, col)

    def _load_data(self):
        try:
            client = get_client()
            online = client.check_available() and bool(client._token)
            dash = client.get_dashboard()
            health = dash.get("health", {})
            stats = dash.get("stats", {})
            ai = dash.get("ai", {})
            v1 = dash.get("v1", {})

            if not online:
                self._show_offline()
                return

            self.cards["companies"].set_value(str(stats.get("total_companies", v1.get("findingsCount", 0))))
            self.cards["companies"].set_subtitle("Active companies")

            agent_count = len(client.get_agents()) or ai.get("providers_available", 0)
            self.cards["agents"].set_value(str(agent_count))
            self.cards["agents"].set_subtitle("Ready agents")

            projects = client.get_audit_projects()
            self.cards["projects"].set_value(str(len(projects) or stats.get("total_audits", 0)))
            self.cards["projects"].set_subtitle("Audit projects")

            risk_score = v1.get("riskScore", ai.get("risk_score", 0))
            self.cards["risks"].set_value(str(risk_score))
            self.cards["risks"].set_subtitle("Risk score")

            findings = v1.get("findingsCount", 0)
            self.cards["tasks"].set_value(str(findings))
            self.cards["tasks"].set_subtitle("Findings logged")

            accuracy = health.get("status", "healthy")
            comp = v1.get("complianceScore")
            acc_text = f"{comp:.1f}%" if comp is not None else ("Online" if accuracy == "healthy" else "---")
            self.cards["accuracy"].set_value(acc_text)
            self.cards["accuracy"].set_subtitle("Compliance / status")

        except Exception as e:
            from loguru import logger
            logger.warning(f"Dashboard data load failed: {e}")
            self._show_offline()

    def _show_offline(self):
        for card in self.cards.values():
            card.set_value("---")
            card.set_subtitle("Offline — log in via API")
