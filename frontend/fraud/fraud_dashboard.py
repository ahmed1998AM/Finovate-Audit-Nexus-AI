"""
Finovate Audit Nexus AI - Fraud Detection Dashboard
لوحة كشف الاحتيال والتحقيق الجنائي
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QGroupBox, QTabWidget, QTextEdit, QProgressBar,
    QHeaderView, QComboBox, QLineEdit, QDateEdit, QDialog, QDialogButtonBox,
    QFormLayout, QMessageBox
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont

class FraudAlertDialog(QDialog):
    """نافذة تفاصيل تنبيه احتيال"""
    def __init__(self, alert_data, parent=None):
        super().__init__(parent)
        self.alert_data = alert_data
        self.setWindowTitle(f"تفاصيل تنبيه احتيال - {alert_data.get('id', 'N/A')}")
        self.setMinimumSize(600, 500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        header = QLabel(f"🚨 تنبيه احتيال: {self.alert_data.get('type', 'Unknown')}")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header.setStyleSheet("color: #e74c3c;")
        layout.addWidget(header)
        
        details = QGroupBox("تفاصيل التنبيه")
        details_layout = QFormLayout(details)
        
        for key, value in self.alert_data.items():
            label = QLabel(str(key).replace('_', ' ').title())
            label.setFont(QFont("Segoe UI", 10, QFont.Bold))
            value_label = QLabel(str(value))
            value_label.setWordWrap(True)
            details_layout.addRow(label, value_label)
        
        layout.addWidget(details)

        actions = QGroupBox("إجراءات التحقيق")
        actions_layout = QVBoxLayout(actions)
        
        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "بدء تحقيق مفصل",
            "تجميد الحساب مؤقتاً",
            "إرسال تقرير للإدارة",
            "وضع في قائمة المراقبة",
            "إغلاق التنبيه (False Positive)"
        ])
        actions_layout.addWidget(self.action_combo)
        
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("أضف ملاحظات التحقيق هنا...")
        self.notes.setMaximumHeight(100)
        actions_layout.addWidget(self.notes)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        actions_layout.addWidget(buttons)
        
        layout.addWidget(actions)

class FraudDetectionDashboard(QWidget):
    """لوحة كشف الاحتيال"""
    investigation_started = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_alerts()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        header = QHBoxLayout()
        title = QLabel("🕵️ كشف الاحتيال والتحقيق الجنائي")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.addWidget(title)
        header.addStretch()
        
        self.export_btn = QPushButton("📤 تصدير التقرير")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white;
                padding: 10px 20px; border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        header.addWidget(self.export_btn)
        
        main_layout.addLayout(header)
        
        stats_layout = QHBoxLayout()
        stats_layout.addWidget(self.create_stat_card("🔴 عالي", "12", "#e74c3c"))
        stats_layout.addWidget(self.create_stat_card("🟠 متوسط", "28", "#f39c12"))
        stats_layout.addWidget(self.create_stat_card("🟡 منخفض", "45", "#f1c40f"))
        stats_layout.addWidget(self.create_stat_card("✅ تم التحقيق", "87", "#2ecc71"))
        main_layout.addLayout(stats_layout)
        
        tabs = QTabWidget()
        
        self.alerts_tab = self.create_alerts_table()
        tabs.addTab(self.alerts_tab, "التنبيهات الحية")
        
        self.cases_tab = self.create_cases_table()
        tabs.addTab(self.cases_tab, "قضايا التحقيق")
        
        self.patterns_tab = self.create_patterns_analysis()
        tabs.addTab(self.patterns_tab, "تحليل الأنماط")
        
        main_layout.addWidget(tabs)

    def create_stat_card(self, label, value, color):
        card = QGroupBox()
        card.setStyleSheet(f"""
            QGroupBox {{
                background-color: {color}20;
                border: 2px solid {color};
                border-radius: 10px;
                font-weight: bold;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)
        
        val_label = QLabel(value)
        val_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        val_label.setStyleSheet(f"color: {color};")
        val_label.setAlignment(Qt.AlignCenter)
        
        desc_label = QLabel(label)
        desc_label.setFont(QFont("Segoe UI", 12))
        desc_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(val_label)
        layout.addWidget(desc_label)
        
        return card

    def create_alerts_table(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        filters = QHBoxLayout()
        filters.addWidget(QLabel("تصفية حسب:"))
        
        type_filter = QComboBox()
        type_filter.addItems(["الكل", "قيود وهمية", "تكرار مشبوه", "توقيت غير طبيعي"])
        filters.addWidget(type_filter)
        
        risk_filter = QComboBox()
        risk_filter.addItems(["الكل", "عالي", "متوسط", "منخفض"])
        filters.addWidget(risk_filter)
        
        filters.addStretch()
        layout.addLayout(filters)
        
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "ID", "النوع", "المخاطر", "الوصف", "التاريخ", "الإجراء"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setAlternatingRowColors(True)
        
        layout.addWidget(table)
        return table

    def create_cases_table(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "رقم القضية", "النوع", "الحالة", "المحقق", "التقدم", "الأولوية", "تاريخ الفتح"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table)
        
        return table

    def create_patterns_analysis(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        info = QLabel("📊 تحليل أنماط الاحتيال المكتشفة")
        info.setFont(QFont("Segoe UI", 14))
        layout.addWidget(info)
        
        patterns = QGroupBox("الأنماط الشائعة")
        patterns_layout = QVBoxLayout(patterns)
        
        pattern_list = QTextEdit()
        pattern_list.setReadOnly(True)
        pattern_list.append("• قيود يومية متكررة بنفس المبلغ تماماً")
        pattern_list.append("• حركات بنكية في أوقات غير عمل رسمية")
        pattern_list.append("• فواتير من موردين جدد بمبالغ كبيرة")
        pattern_list.append("• تسويات يدوية متكررة في نهاية الفترة")
        pattern_list.append("• اختلافات منهجية في جرد المخزون")
        
        patterns_layout.addWidget(pattern_list)
        layout.addWidget(patterns)
        
        return widget

    def load_alerts(self):
        alerts = [
            {"id": "FR-001", "type": "قيود وهمية", "risk": "عالي", "desc": "كشف 15 قيد مكرر", "date": "2025-01-15"},
            {"id": "FR-002", "type": "تكرار مشبوه", "risk": "متوسط", "desc": "دفعات متكررة لمورد واحد", "date": "2025-01-14"},
            {"id": "FR-003", "type": "توقيت غير طبيعي", "risk": "عالي", "desc": "قيود بعد ساعات العمل", "date": "2025-01-13"},
        ]
        
        table = self.alerts_tab.findChild(QTableWidget)
        if table:
            for alert in alerts:
                row = table.rowCount()
                table.insertRow(row)
                table.setItem(row, 0, QTableWidgetItem(alert['id']))
                table.setItem(row, 1, QTableWidgetItem(alert['type']))
                
                risk_item = QTableWidgetItem(alert['risk'])
                if alert['risk'] == "عالي":
                    risk_item.setBackground(Qt.red)
                    risk_item.setForeground(Qt.white)
                elif alert['risk'] == "متوسط":
                    risk_item.setBackground(Qt.yellow)
                table.setItem(row, 2, risk_item)
                
                table.setItem(row, 3, QTableWidgetItem(alert['desc']))
                table.setItem(row, 4, QTableWidgetItem(alert['date']))
                
                action_btn = QPushButton("🔍 تحقيق")
                action_btn.clicked.connect(lambda checked, a=alert: self.show_alert_details(a))
                table.setCellWidget(row, 5, action_btn)

    def show_alert_details(self, alert_data):
        dialog = FraudAlertDialog(alert_data, self)
        if dialog.exec() == QDialog.Accepted:
            action = dialog.action_combo.currentText()
            notes = dialog.notes.toPlainText()
            QMessageBox.information(
                self, "تم التسجيل",
                f"الإجراء: {action}\nملاحظات: {notes}"
            )
            self.investigation_started.emit(alert_data)
