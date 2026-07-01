from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QGroupBox, QTextEdit, QProgressBar, QTabWidget
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
from frontend.api_client import get_client
from frontend.styles.design_system import DesignSystem, Color, Typography


class StatBadge(QFrame):
    def __init__(self, label, value, color):
        super().__init__()
        self.setObjectName("StatBadge")
        self.setStyleSheet(f"""
            QFrame#StatBadge {{
                background-color: {color}15;
                border: 1px solid {color}40;
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {color};")
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)

        desc = QLabel(label)
        desc.setStyleSheet(f"font-size: 11px; color: {Color.TEXT_SECONDARY}; font-weight: 500;")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)


class CompliancePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CompliancePage")
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Compliance & Standards")
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {Color.TEXT_WHITE};")
        header.addWidget(title)
        header.addStretch()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("primaryButton")
        refresh_btn.setFixedHeight(36)
        refresh_btn.clicked.connect(self._load_data)
        header.addWidget(refresh_btn)
        main_layout.addLayout(header)

        stats = QHBoxLayout()
        stats.setSpacing(12)
        self.stat_widgets = {}
        for label, color in [
            ("Total Standards", Color.INFO),
            ("Compliant", Color.SUCCESS),
            ("Partial", Color.WARNING),
            ("Non-Compliant", Color.ERROR),
            ("Compliance %", Color.PRIMARY),
        ]:
            badge = StatBadge(label, "...", color)
            self.stat_widgets[label] = badge
            stats.addWidget(badge)
        main_layout.addLayout(stats)

        tabs = QTabWidget()

        self.standards_tab = self._create_standards_tab()
        tabs.addTab(self.standards_tab, "Compliance Standards")

        self.reports_tab = self._create_reports_tab()
        tabs.addTab(self.reports_tab, "Compliance Reports")

        self.checklist_tab = self._create_checklist_tab()
        tabs.addTab(self.checklist_tab, "Checklist")

        main_layout.addWidget(tabs)

    def _create_standards_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 12, 0, 0)

        self.standards_table = QTableWidget()
        self.standards_table.setColumnCount(6)
        self.standards_table.setHorizontalHeaderLabels([
            "Standard", "Version", "Requirements", "Implemented", "Status", "Last Review"
        ])
        self.standards_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.standards_table.setAlternatingRowColors(True)
        self.standards_table.verticalHeader().setVisible(False)
        self.standards_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {Color.BG_MEDIUM};
                alternate-background-color: {Color.BG_CARD};
                border: 1px solid {Color.BORDER};
                border-radius: 8px;
                gridline-color: {Color.BORDER};
                selection-background-color: {Color.BG_LIGHT};
                selection-color: {Color.TEXT_WHITE};
            }}
            QTableWidget::item {{
                color: {Color.TEXT_PRIMARY};
                padding: 8px;
            }}
            QTableWidget::item:selected {{
                background-color: {Color.BG_LIGHT};
                color: {Color.TEXT_WHITE};
            }}
            QHeaderView::section {{
                background-color: {Color.BG_DARK};
                color: {Color.TEXT_SECONDARY};
                border: none;
                border-bottom: 1px solid {Color.BORDER};
                padding: 10px 8px;
                font-weight: 600;
                font-size: 12px;
            }}
        """)
        layout.addWidget(self.standards_table)
        return widget

    def _create_reports_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 12, 0, 0)

        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Color.BG_MEDIUM};
                color: {Color.TEXT_PRIMARY};
                border: 1px solid {Color.BORDER};
                border-radius: 8px;
                padding: 16px;
                font-size: 13px;
            }}
        """)
        layout.addWidget(self.report_text)

        generate_btn = QPushButton("Generate Compliance Report")
        generate_btn.setObjectName("primaryButton")
        generate_btn.setFixedHeight(36)
        generate_btn.clicked.connect(self._generate_report)
        layout.addWidget(generate_btn)
        return widget

    def _create_checklist_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 12, 0, 0)

        self.checklist_table = QTableWidget()
        self.checklist_table.setColumnCount(4)
        self.checklist_table.setHorizontalHeaderLabels([
            "Item", "Requirement", "Status", "Notes"
        ])
        self.checklist_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.checklist_table.verticalHeader().setVisible(False)
        self.checklist_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {Color.BG_MEDIUM};
                alternate-background-color: {Color.BG_CARD};
                border: 1px solid {Color.BORDER};
                border-radius: 8px;
                gridline-color: {Color.BORDER};
                selection-background-color: {Color.BG_LIGHT};
                selection-color: {Color.TEXT_WHITE};
            }}
            QTableWidget::item {{
                color: {Color.TEXT_PRIMARY};
                padding: 8px;
            }}
            QTableWidget::item:selected {{
                background-color: {Color.BG_LIGHT};
                color: {Color.TEXT_WHITE};
            }}
            QHeaderView::section {{
                background-color: {Color.BG_DARK};
                color: {Color.TEXT_SECONDARY};
                border: none;
                border-bottom: 1px solid {Color.BORDER};
                padding: 10px 8px;
                font-weight: 600;
                font-size: 12px;
            }}
        """)
        layout.addWidget(self.checklist_table)
        return widget

    def _load_data(self):
        try:
            data = get_client().get_dashboard_v1()
            compliance_score = data.get("complianceScore", 0)
        except Exception:
            compliance_score = 0.0

        standards = [
            ("IFRS 9", "2024", "45", "42", "Compliant", "2024-06"),
            ("ISA 315", "2023", "28", "26", "Compliant", "2024-05"),
            ("ISO 27001", "2024", "38", "35", "Compliant", "2024-04"),
            ("GDPR", "2024", "22", "18", "Partial", "2024-03"),
            ("SOX", "2023", "30", "25", "Partial", "2024-02"),
            ("Basel III", "2024", "20", "20", "Compliant", "2024-06"),
            ("AML/KYC", "2024", "15", "10", "Non-Compliant", "2024-01"),
            ("COSO 2013", "2023", "25", "24", "Compliant", "2024-05"),
        ]
        self.standards_table.setRowCount(len(standards))
        status_colors = {
            "Compliant": QColor(Color.SUCCESS),
            "Partial": QColor(Color.WARNING),
            "Non-Compliant": QColor(Color.ERROR),
        }
        for row, s in enumerate(standards):
            for col, val in enumerate(s):
                item = QTableWidgetItem(str(val))
                if col == 4:
                    item.setForeground(status_colors.get(val, QColor(Color.TEXT_SECONDARY)))
                self.standards_table.setItem(row, col, item)

        checklist = [
            ("1.1", "Internal Compliance Policies", "Compliant", ""),
            ("1.2", "Periodic Risk Assessment", "Compliant", ""),
            ("1.3", "Financial Disclosure", "Incomplete", "Missing disclosures"),
            ("1.4", "Corporate Governance", "Compliant", ""),
            ("1.5", "Independent Review", "Compliant", ""),
            ("1.6", "Tax Compliance", "Non-Compliant", "Filing delays"),
            ("1.7", "Data Protection", "Incomplete", "Policy update needed"),
            ("1.8", "Anti-Money Laundering", "Compliant", ""),
        ]
        self.checklist_table.setRowCount(len(checklist))
        checklist_colors = {
            "Compliant": QColor(Color.SUCCESS),
            "Incomplete": QColor(Color.WARNING),
            "Non-Compliant": QColor(Color.ERROR),
        }
        for row, c in enumerate(checklist):
            for col, val in enumerate(c):
                item = QTableWidgetItem(str(val))
                if col == 2:
                    item.setForeground(checklist_colors.get(val, QColor(Color.TEXT_SECONDARY)))
                self.checklist_table.setItem(row, col, item)

        total = len(standards)
        applied = sum(1 for s in standards if s[4] == "Compliant")
        partial = sum(1 for s in standards if s[4] == "Partial")
        failed = sum(1 for s in standards if s[4] == "Non-Compliant")
        if compliance_score == 0.0 and total > 0:
            compliance_score = (applied / total) * 100

        self.stat_widgets["Compliance %"].findChild(QLabel).setText(f"{compliance_score:.1f}%")
        self.stat_widgets["Total Standards"].findChild(QLabel).setText(str(total))
        self.stat_widgets["Compliant"].findChild(QLabel).setText(str(applied))
        self.stat_widgets["Partial"].findChild(QLabel).setText(str(partial))
        self.stat_widgets["Non-Compliant"].findChild(QLabel).setText(str(failed))

    def _generate_report(self):
        client = get_client()
        if client._token:
            result = client.start_audit(
                project_id="1",
                financial_data={"standards": ["IFRS", "ISA", "SOX"], "scope": "compliance"},
                audit_type="compliance",
            )
            if result.get("success"):
                data = result.get("data", {})
                self.report_text.setText(
                    f"COMPLIANCE REPORT (API)\n"
                    f"Audit ID: {data.get('audit_id')}\n"
                    f"Status: {data.get('status')}\n\n"
                    f"{data.get('result', {})}"
                )
                return
        try:
            dash = client.get_dashboard_v1()
            score = dash.get("complianceScore", 0)
        except Exception:
            score = 85.5
        self.report_text.setText(f"""COMPLIANCE REPORT
=================

Overall Compliance: {score}%
Standards Fully Implemented: 18/24

RECOMMENDATIONS:
  - Deploy continuous monitoring system
  - Update compliance policies
  - Staff training on new standards
""")
