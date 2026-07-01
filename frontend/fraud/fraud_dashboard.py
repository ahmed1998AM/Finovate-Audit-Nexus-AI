from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QGroupBox, QTabWidget, QTextEdit, QProgressBar,
    QHeaderView, QComboBox, QLineEdit, QDateEdit, QDialog, QDialogButtonBox,
    QFormLayout, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont, QColor
from frontend.api_client import get_client
from frontend.styles.design_system import DesignSystem, Color, Typography


class FraudAlertDialog(QDialog):
    def __init__(self, alert_data, parent=None):
        super().__init__(parent)
        self.alert_data = alert_data
        self.setWindowTitle(f"Fraud Alert - {alert_data.get('id', 'N/A')}")
        self.setMinimumSize(600, 500)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Color.BG_DARK};
                color: {Color.TEXT_PRIMARY};
            }}
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        header = QLabel(f"Fraud Alert: {self.alert_data.get('type', 'Unknown')}")
        header.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {Color.ERROR};")
        layout.addWidget(header)

        details = QGroupBox("Alert Details")
        details.setStyleSheet(f"""
            QGroupBox {{
                color: {Color.TEXT_PRIMARY}; font-weight: 600; font-size: 13px;
                border: 1px solid {Color.BORDER}; border-radius: 8px;
                padding: 16px; margin-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; left: 12px; padding: 0 6px;
            }}
        """)
        details_layout = QFormLayout(details)
        details_layout.setSpacing(8)

        for key, value in self.alert_data.items():
            lbl = QLabel(str(key).replace('_', ' ').title())
            lbl.setStyleSheet(f"color: {Color.TEXT_SECONDARY}; font-weight: 500; font-size: 12px;")
            val = QLabel(str(value))
            val.setStyleSheet(f"color: {Color.TEXT_PRIMARY}; font-size: 13px;")
            val.setWordWrap(True)
            details_layout.addRow(lbl, val)

        layout.addWidget(details)

        actions = QGroupBox("Investigation Actions")
        actions.setStyleSheet(f"""
            QGroupBox {{
                color: {Color.TEXT_PRIMARY}; font-weight: 600; font-size: 13px;
                border: 1px solid {Color.BORDER}; border-radius: 8px;
                padding: 16px; margin-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; left: 12px; padding: 0 6px;
            }}
        """)
        actions_layout = QVBoxLayout(actions)
        actions_layout.setSpacing(10)

        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "Start detailed investigation",
            "Temporarily freeze account",
            "Send report to management",
            "Add to watchlist",
            "Close alert (False Positive)"
        ])
        self.action_combo.setStyleSheet(f"background: {Color.BG_DARK}; color: {Color.TEXT_PRIMARY}; border: 1px solid {Color.BORDER}; border-radius: 6px; padding: 8px 12px; font-size: 13px;")
        actions_layout.addWidget(self.action_combo)

        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Add investigation notes here...")
        self.notes.setMaximumHeight(100)
        self.notes.setStyleSheet(f"background: {Color.BG_DARK}; color: {Color.TEXT_PRIMARY}; border: 1px solid {Color.BORDER}; border-radius: 6px; padding: 10px; font-size: 13px;")
        actions_layout.addWidget(self.notes)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("ghostButton")
        cancel_btn.setFixedHeight(36)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("Confirm")
        ok_btn.setObjectName("primaryButton")
        ok_btn.setFixedHeight(36)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        actions_layout.addLayout(btn_layout)

        layout.addWidget(actions)


class FraudDetectionDashboard(QWidget):
    investigation_started = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setObjectName("FraudDetectionDashboard")
        self.setup_ui()
        self.load_alerts()
        self.load_stats()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Fraud Detection")
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {Color.TEXT_PRIMARY};")
        header.addWidget(title)
        header.addStretch()

        self.export_btn = QPushButton("Export Report")
        self.export_btn.setObjectName("primaryButton")
        self.export_btn.setFixedHeight(36)
        header.addWidget(self.export_btn)

        main_layout.addLayout(header)

        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(12)
        self.stat_cards = []
        for icon, lbl, color in [("High Risk", "...", Color.ERROR), ("Medium Risk", "...", Color.WARNING), ("Low Risk", "...", Color.INFO), ("Investigated", "...", Color.SUCCESS)]:
            card, val = self.create_stat_card(icon, lbl, color)
            self.stat_cards.append(val)
            self.stats_layout.addWidget(card)
        main_layout.addLayout(self.stats_layout)

        tabs = QTabWidget()

        self.alerts_tab = self.create_alerts_table()
        tabs.addTab(self.alerts_tab, "Live Alerts")

        self.cases_tab = self.create_cases_table()
        tabs.addTab(self.cases_tab, "Investigation Cases")

        self.patterns_tab = self.create_patterns_analysis()
        tabs.addTab(self.patterns_tab, "Pattern Analysis")

        main_layout.addWidget(tabs)

    def create_stat_card(self, label, value, color):
        card = QFrame()
        card.setObjectName("FraudStatCard")
        card.setStyleSheet(f"""
            QFrame#FraudStatCard {{
                background-color: {color}12;
                border: 1px solid {color}40;
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(4)

        val_label = QLabel(value)
        val_label.setStyleSheet(f"font-size: 26px; font-weight: 700; color: {color};")
        val_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(val_label)

        desc_label = QLabel(label)
        desc_label.setStyleSheet(f"font-size: 11px; color: {Color.TEXT_SECONDARY}; font-weight: 500;")
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)

        return card, val_label

    def create_alerts_table(self):
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 12, 0, 0)

        filters = QHBoxLayout()
        filters.setSpacing(8)
        filter_label = QLabel("Filter by:")
        filter_label.setStyleSheet(f"color: {Color.TEXT_SECONDARY}; font-size: 13px; font-weight: 500;")
        filters.addWidget(filter_label)

        type_filter = QComboBox()
        type_filter.addItems(["All", "Fake Entries", "Suspicious Duplicates", "Abnormal Timing"])
        type_filter.setStyleSheet(f"background: {Color.BG_DARK}; color: {Color.TEXT_PRIMARY}; border: 1px solid {Color.BORDER}; border-radius: 6px; padding: 6px 10px; font-size: 12px;")
        filters.addWidget(type_filter)

        risk_filter = QComboBox()
        risk_filter.addItems(["All", "High", "Medium", "Low"])
        risk_filter.setStyleSheet(f"background: {Color.BG_DARK}; color: {Color.TEXT_PRIMARY}; border: 1px solid {Color.BORDER}; border-radius: 6px; padding: 6px 10px; font-size: 12px;")
        filters.addWidget(risk_filter)

        filters.addStretch()
        layout.addLayout(filters)

        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(6)
        self.alerts_table.setHorizontalHeaderLabels([
            "ID", "Type", "Risk", "Description", "Date", "Action"
        ])
        self.alerts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.alerts_table.setAlternatingRowColors(True)
        self.alerts_table.verticalHeader().setVisible(False)
        self.alerts_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {Color.BG_MEDIUM};
                color: {Color.TEXT_PRIMARY};
                border: 1px solid {Color.BORDER};
                border-radius: 8px;
                gridline-color: {Color.BG_CARD};
                font-size: 13px;
            }}
            QHeaderView::section {{
                background-color: {Color.BG_CARD};
                color: {Color.TEXT_SECONDARY};
                font-weight: 600;
                font-size: 12px;
                padding: 10px 12px;
                border: none;
                border-bottom: 1px solid {Color.BORDER};
                text-transform: uppercase;
            }}
        """)

        layout.addWidget(self.alerts_table)
        return widget

    def create_cases_table(self):
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 12, 0, 0)

        self.cases_table = QTableWidget()
        self.cases_table.setColumnCount(7)
        self.cases_table.setHorizontalHeaderLabels([
            "Case #", "Type", "Status", "Investigator", "Progress", "Priority", "Opened"
        ])
        self.cases_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cases_table.verticalHeader().setVisible(False)
        self.cases_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {Color.BG_MEDIUM};
                color: {Color.TEXT_PRIMARY};
                border: 1px solid {Color.BORDER};
                border-radius: 8px;
                gridline-color: {Color.BG_CARD};
                font-size: 13px;
            }}
            QHeaderView::section {{
                background-color: {Color.BG_CARD};
                color: {Color.TEXT_SECONDARY};
                font-weight: 600;
                font-size: 12px;
                padding: 10px 12px;
                border: none;
                border-bottom: 1px solid {Color.BORDER};
                text-transform: uppercase;
            }}
        """)
        layout.addWidget(self.cases_table)

        return widget

    def create_patterns_analysis(self):
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 12, 0, 0)

        info = QLabel("Detected Fraud Patterns")
        info.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {Color.TEXT_PRIMARY}; padding-bottom: 8px;")
        layout.addWidget(info)

        patterns = QGroupBox("Common Patterns")
        patterns.setStyleSheet(f"""
            QGroupBox {{
                color: {Color.TEXT_PRIMARY}; font-weight: 600; font-size: 13px;
                border: 1px solid {Color.BORDER}; border-radius: 8px;
                padding: 16px; margin-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; left: 12px; padding: 0 6px;
            }}
        """)
        patterns_layout = QVBoxLayout(patterns)
        patterns_layout.setSpacing(6)

        pattern_list = QTextEdit()
        pattern_list.setReadOnly(True)
        pattern_list.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Color.BG_DARK};
                color: {Color.TEXT_PRIMARY};
                border: 1px solid {Color.BORDER};
                border-radius: 6px;
                padding: 12px;
                font-size: 13px;
            }}
        """)
        pattern_list.append("• Recurring daily entries with identical amounts")
        pattern_list.append("• Banking activity during non-official hours")
        pattern_list.append("• Invoices from new vendors with large amounts")
        pattern_list.append("• Frequent manual adjustments at period end")
        pattern_list.append("• Systematic inventory count discrepancies")

        patterns_layout.addWidget(pattern_list)
        layout.addWidget(patterns)

        return widget

    def load_stats(self):
        try:
            data = get_client().get_dashboard_v1()
            findings = data.get("findings", [])
            high = sum(1 for f in findings if f.get("severity") in ("high", "critical"))
            med = sum(1 for f in findings if f.get("severity") == "medium")
            low = sum(1 for f in findings if f.get("severity") == "low")
            done = sum(1 for f in findings if f.get("status") in ("Resolved", "Closed"))
            vals = [str(high), str(med), str(low), str(done)]
        except Exception:
            vals = ["N/A"] * 4
        for i, v in enumerate(vals):
            if i < len(self.stat_cards):
                self.stat_cards[i].setText(v)

    def load_alerts(self):
        try:
            data = get_client().get_dashboard_v1()
            raw = data.get("findings", [])
        except Exception:
            raw = []
        alerts = []
        for i, f in enumerate(raw):
            sev = f.get("severity", "low")
            risk_map = {"critical": "High", "high": "High", "medium": "Medium", "low": "Low"}
            alerts.append({
                "id": f"FND-{i+1:04d}",
                "type": f.get("description", "")[:25],
                "risk": risk_map.get(sev, "Low"),
                "desc": f.get("description", ""),
                "date": "",
                "severity": sev,
            })

        table = self.alerts_table if hasattr(self, 'alerts_table') else None
        if not table:
            return

        table.setRowCount(0)
        risk_colors = {
            "High": QColor(Color.ERROR),
            "Medium": QColor(Color.WARNING),
            "Low": QColor(Color.INFO),
        }

        for alert in alerts:
            row = table.rowCount()
            table.insertRow(row)
            table.setRowHeight(row, 44)
            table.setItem(row, 0, QTableWidgetItem(alert['id']))
            table.setItem(row, 1, QTableWidgetItem(alert['type']))

            risk_item = QTableWidgetItem(alert['risk'])
            risk_item.setForeground(risk_colors.get(alert['risk'], QColor(Color.TEXT_SECONDARY)))
            table.setItem(row, 2, risk_item)

            table.setItem(row, 3, QTableWidgetItem(alert['desc']))
            table.setItem(row, 4, QTableWidgetItem(alert['date']))

            action_btn = QPushButton("Investigate")
            action_btn.setObjectName("primaryButton")
            action_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Color.BG_CARD}; color: {Color.TEXT_PRIMARY};
                    border: 1px solid {Color.BORDER}; border-radius: 4px;
                    padding: 4px 12px; font-size: 11px;
                }}
                QPushButton:hover {{ background-color: {Color.BORDER}; border-color: {Color.INFO}; }}
            """)
            action_btn.clicked.connect(lambda a=alert: self.show_alert_details(a))
            table.setCellWidget(row, 5, action_btn)

    def show_alert_details(self, alert_data):
        dialog = FraudAlertDialog(alert_data, self)
        if dialog.exec() == QDialog.Accepted:
            action = dialog.action_combo.currentText()
            notes = dialog.notes.toPlainText()
            client = get_client()
            if client._token:
                result = client.execute_agent("fraud_agent", {
                    "task_type": "investigate",
                    "parameters": {
                        "alert_id": alert_data.get("id"),
                        "action": action,
                        "notes": notes,
                        "severity": alert_data.get("severity"),
                    },
                })
                if result:
                    QMessageBox.information(
                        self, "Investigation",
                        f"Action recorded via API.\n{result.get('message', '')}",
                    )
                else:
                    QMessageBox.information(self, "Recorded", f"Action: {action}\nNotes: {notes}")
            else:
                QMessageBox.information(self, "Recorded", f"Action: {action}\nNotes: {notes}")
            self.investigation_started.emit(alert_data)
