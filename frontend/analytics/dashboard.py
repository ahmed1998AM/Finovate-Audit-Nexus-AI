from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from frontend.api_client import get_client
from frontend.styles.design_system import Color


class AnalyticsDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Analytics Dashboard")
        self.setup_ui()
        self.load_data()

    def load_data(self):
        try:
            data = get_client().get_dashboard_v1()
            kpis = [
                ("Risk Score", f'{data.get("riskScore", 0):.1f}', ""),
                ("Findings", str(data.get("findingsCount", 0)), ""),
                ("Compliance Rate", f'{data.get("complianceScore", 0):.1f}%', ""),
                ("Audit Status", data.get("auditStatus", ""), ""),
            ]
            risk_dist = data.get("riskDistribution", [0, 0, 0, 0])
            kpis.append(("Critical Risk", str(risk_dist[0] if len(risk_dist) > 0 else 0), ""))
            kpis.append(("High Risk", str(risk_dist[1] if len(risk_dist) > 1 else 0), ""))
        except Exception:
            kpis = [
                ("Risk Score", "N/A", ""),
                ("Findings", "N/A", ""),
                ("Compliance Rate", "N/A", ""),
                ("Audit Status", "Unavailable", ""),
                ("Critical Risk", "N/A", ""),
                ("High Risk", "N/A", ""),
            ]
        for i, (title, value, change) in enumerate(kpis):
            card = self.create_kpi_card(title, value, change)
            row = i // 3
            col = i % 3
            self.grid.addWidget(card, row, col)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)

        header = QLabel("Financial Analytics")
        header.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {Color.TEXT_PRIMARY}; padding-bottom: 8px;")
        main_layout.addWidget(header)

        self.grid = QGridLayout()
        self.grid.setSpacing(16)
        main_layout.addLayout(self.grid)

    def create_kpi_card(self, title, value, change):
        card = QFrame()
        card.setObjectName("KpiCard")
        card.setStyleSheet(f"""
            QFrame#KpiCard {{
                background-color: {Color.BG_CARD};
                border: 1px solid {Color.BORDER};
                border-radius: 10px;
                padding: 20px;
            }}
            QFrame#KpiCard:hover {{
                border-color: {Color.INFO};
            }}
        """)
        card.setMinimumSize(200, 120)

        layout = QVBoxLayout(card)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 11px; color: {Color.TEXT_SECONDARY}; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;")
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {Color.PRIMARY};")
        layout.addWidget(value_label)

        if change:
            change_color = Color.SUCCESS if change.startswith('+') else Color.ERROR
            change_label = QLabel(change)
            change_label.setStyleSheet(f"font-size: 13px; color: {change_color};")
            layout.addWidget(change_label)

        return card
