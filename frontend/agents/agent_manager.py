"""
Finovate Audit Nexus AI - Agent Manager Widget
واجهة إدارة الوكلاء الذكية
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QGridLayout, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class AgentManagerWidget(QWidget):
    """واجهة إدارة الوكلاء"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AgentManagerWidget")
        self._setup_ui()

    def _setup_ui(self):
        """إعداد الواجهة"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # العنوان الرئيسي
        title_label = QLabel("🤖 إدارة الوكلاء الذكية")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        main_layout.addWidget(title_label)

        # منطقة المحتوى
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content_widget = QWidget()
        content_layout = QGridLayout(content_widget)
        content_layout.setSpacing(15)

        # قائمة الوكلاء
        agents = [
            ("Chief Audit Agent", "🎯", "وكيل التدقيق الرئيسي"),
            ("Journal Entry Agent", "📝", "مراجعة قيود اليومية"),
            ("General Ledger Agent", "📒", "مراجعة الأستاذ العام"),
            ("Trial Balance Agent", "⚖️", "تحليل ميزان المراجعة"),
            ("Financial Statements Agent", "📊", "القوائم المالية"),
            ("Tax Compliance Agent", "💰", "الامتثال الضريبي"),
            ("Bank & Treasury Agent", "🏦", "المراجعة البنكية"),
            ("Inventory Agent", "📦", "مراجعة المخزون"),
            ("Fixed Assets Agent", "🏢", "الأصول الثابتة"),
            ("Fraud Detection Agent", "🔍", "كشف الاحتيال"),
            ("OCR Agent", "📷", "معالجة المستندات"),
            ("Compliance Agent", "✅", "الامتثال والمعايير"),
            ("Behavioral Agent", "🧠", "التحليل السلوكي"),
            ("Risk Scoring Agent", "⚠️", "تقييم المخاطر"),
            ("Forensic Agent", "🔬", "التحقيق الجنائي"),
            ("Explainable AI Agent", "💡", "شرح القرارات"),
            ("QA Agent", "✔️", "ضمان الجودة"),
            ("Executive Agent", "👔", "التقارير التنفيذية"),
            ("Connector Agent", "🔗", "إدارة الموصلات"),
            ("Monitoring Agent", "📡", "المراقبة المستمرة"),
            ("Graph Agent", "🕸️", "تحليل الشبكات"),
            ("Copilot Agent", "🤝", "المساعد الذكي"),
        ]

        row = 0
        col = 0
        max_cols = 2

        for agent_name, icon, description in agents:
            card = self._create_agent_card(agent_name, icon, description)
            content_layout.addWidget(card, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def _create_agent_card(self, name, icon, description):
        """إنشاء بطاقة وكيل"""
        card = QFrame()
        card.setObjectName("AgentCard")
        card.setStyleSheet("""
            QFrame#AgentCard {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #e0e0e0;
            }
            QFrame#AgentCard:hover {
                border: 2px solid #3498db;
                background-color: #f8f9fa;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(10)

        # الأيقونة والاسم
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Arial", 24))
        header_layout.addWidget(icon_label)

        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        name_label.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(name_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # الوصف
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(desc_label)

        # حالة الوكيل
        status_label = QLabel("✅ جاهز")
        status_label.setFont(QFont("Arial", 9))
        status_label.setStyleSheet("color: #27ae60;")
        layout.addWidget(status_label)

        return card


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    widget = AgentManagerWidget()
    widget.show()
    sys.exit(app.exec())
