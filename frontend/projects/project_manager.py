"""
Finovate Audit Nexus AI - Audit Project Management Window
إدارة مشاريع المراجعة الذكية
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QDateEdit, QDialog,
    QDialogButtonBox, QFormLayout, QMessageBox, QHeaderView, QProgressBar,
    QTabWidget, QTextEdit, QGroupBox
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont

class NewProjectDialog(QDialog):
    """نافذة إنشاء مشروع مراجعة جديد"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إنشاء مشروع مراجعة جديد")
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("اسم المشروع (مثال: مراجعة شركة XYZ 2025)")
        
        self.client_input = QLineEdit()
        self.client_input.setPlaceholderText("اسم العميل")
        
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "مراجعة شاملة (Full Audit)",
            "مراجعة ضريبية (Tax Audit)",
            "مراجعة اكتشاف احتيال (Fraud Investigation)",
            "مراجعة محدودة (Review Engagement)",
            "Due Diligence"
        ])
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addMonths(1))
        
        self.risk_level = QComboBox()
        self.risk_level.addItems(["منخفض", "متوسط", "مرتفع", "حرج"])
        
        layout.addRow("اسم المشروع:", self.name_input)
        layout.addRow("العميل:", self.client_input)
        layout.addRow("نوع المراجعة:", self.type_combo)
        layout.addRow("تاريخ البدء:", self.start_date)
        layout.addRow("تاريخ الانتهاء:", self.end_date)
        layout.addRow("مستوى المخاطر:", self.risk_level)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "client": self.client_input.text(),
            "type": self.type_combo.currentText(),
            "start_date": self.start_date.date().toString("yyyy-MM-dd"),
            "end_date": self.end_date.date().toString("yyyy-MM-dd"),
            "risk_level": self.risk_level.currentText()
        }

class AuditProjectManager(QWidget):
    """واجهة إدارة مشاريع المراجعة"""
    project_selected = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_projects()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("📂 إدارة مشاريع المراجعة")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.addWidget(title)
        header.addStretch()
        
        self.new_btn = QPushButton("➕ مشروع جديد")
        self.new_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; color: white; 
                padding: 10px 20px; border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #27ae60; }
        """)
        self.new_btn.clicked.connect(self.create_project)
        header.addWidget(self.new_btn)
        
        main_layout.addLayout(header)
        
        # Tabs
        tabs = QTabWidget()
        
        # Tab 1: Active Projects
        self.active_tab = self.create_projects_table()
        tabs.addTab(self.active_tab, "المشاريع النشطة")
        
        # Tab 2: Completed
        self.completed_tab = self.create_projects_table()
        tabs.addTab(self.completed_tab, "المشاريع المكتملة")
        
        # Tab 3: Risk Monitor
        self.risk_tab = self.create_risk_dashboard()
        tabs.addTab(self.risk_tab, "مراقبة المخاطر")
        
        main_layout.addWidget(tabs)

    def create_projects_table(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "ID", "اسم المشروع", "العميل", "النوع", "المخاطر", "التقدم", "الحالة"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(table)
        return table

    def create_risk_dashboard(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        info = QLabel("⚠️ لوحة مراقبة المخاطر الحية للمشاريع النشطة")
        info.setFont(QFont("Segoe UI", 14))
        layout.addWidget(info)
        
        placeholder = QGroupBox("تحليل توزيع المخاطر")
        placeholder_layout = QVBoxLayout(placeholder)
        placeholder_layout.addWidget(QLabel("📊 رسم بياني لتوزيع المخاطر (سيتم دمجه مع Plotly)"))
        layout.addWidget(placeholder)
        
        alerts = QGroupBox("تنبيهات المخاطر الحديثة")
        alerts_layout = QVBoxLayout(alerts)
        self.alerts_list = QTextEdit()
        self.alerts_list.setReadOnly(True)
        self.alerts_list.append("✅ لا توجد تنبيهات مخاطر حالية.")
        alerts_layout.addWidget(self.alerts_list)
        layout.addWidget(alerts)
        
        return widget

    def load_projects(self):
        projects = [
            (101, "مراجعة XYZ Corp", "XYZ Corp", "شاملة", "متوسط", 75, "نشط"),
            (102, "تحقيق ABC Ltd", "ABC Ltd", "احتيال", "مرتفع", 30, "نشط"),
            (103, "مراجعة ضريبية 2024", "Tech Sol", "ضريبية", "منخفض", 100, "مكتمل"),
        ]
        
        for proj in projects:
            if proj[5] < 100:
                self.add_project_row(self.active_tab, proj)
            else:
                self.add_project_row(self.completed_tab, proj)

    def add_project_row(self, table, proj):
        row_pos = table.rowCount()
        table.insertRow(row_pos)
        
        progress = QProgressBar()
        progress.setValue(proj[5])
        
        data = [
            str(proj[0]), proj[1], proj[2], proj[3], 
            self.get_risk_color(proj[4]), "", proj[6]
        ]
        
        for col, val in enumerate(data):
            if col == 5:
                table.setCellWidget(row_pos, col, progress)
            else:
                table.setItem(row_pos, col, QTableWidgetItem(val))

    def get_risk_color(self, risk):
        colors = {
            "منخفض": "🟢 منخفض",
            "متوسط": "🟡 متوسط",
            "مرتفع": "🟠 مرتفع",
            "حرج": "🔴 حرج"
        }
        return colors.get(risk, risk)

    def create_project(self):
        dialog = NewProjectDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            QMessageBox.information(self, "نجاح", f"تم إنشاء المشروع: {data['name']}")
            self.load_projects()
