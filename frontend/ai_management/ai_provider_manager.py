"""
Finovate Audit Nexus AI - AI Provider Manager Widget
واجهة إدارة مزودي الذكاء الاصطناعي
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QGridLayout, QPushButton,
    QComboBox, QLineEdit, QFormLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class AIProviderManager(QWidget):
    """واجهة إدارة مزودي الذكاء الاصطناعي"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AIProviderManager")
        self._setup_ui()

    def _setup_ui(self):
        """إعداد الواجهة"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # العنوان الرئيسي
        title_label = QLabel("🧠 إدارة مزودي الذكاء الاصطناعي")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        main_layout.addWidget(title_label)

        # منطقة المحتوى
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)

        # قائمة مزودي AI
        providers = [
            ("OpenAI GPT-4", "✅ متصل", "نموذج اللغة المتقدم"),
            ("Anthropic Claude", "✅ متصل", "الذكاء الاصطناعي الآمن"),
            ("Google Gemini", "⚠️ غير مهيأ", "نموذج جوجل متعدد الوسائط"),
            ("Local LLM", "❌ غير متصل", "النموذج المحلي"),
            ("Azure OpenAI", "✅ متصل", "سحابة مايكروسوفت"),
        ]

        for provider_name, status, description in providers:
            card = self._create_provider_card(provider_name, status, description)
            content_layout.addWidget(card)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def _create_provider_card(self, name, status, description):
        """إنشاء بطاقة مزود AI"""
        card = QFrame()
        card.setObjectName("ProviderCard")
        card.setStyleSheet("""
            QFrame#ProviderCard {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                border: 1px solid #e0e0e0;
            }
            QFrame#ProviderCard:hover {
                border: 2px solid #3498db;
                background-color: #f8f9fa;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(15)

        # الرأس
        header_layout = QHBoxLayout()

        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 16, QFont.Bold))
        name_label.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(name_label)

        header_layout.addStretch()

        status_label = QLabel(status)
        status_color = "#27ae60" if "✅" in status else ("#f39c12" if "⚠️" in status else "#e74c3c")
        status_label.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        header_layout.addWidget(status_label)

        layout.addLayout(header_layout)

        # الوصف
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(desc_label)

        # نموذج الإعدادات
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        api_key_input = QLineEdit()
        api_key_input.setPlaceholderText("أدخل مفتاح API")
        api_key_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("مفتاح API:", api_key_input)

        model_combo = QComboBox()
        model_combo.addItems(["gpt-4", "gpt-3.5-turbo", "claude-3", "gemini-pro"])
        form_layout.addRow("النموذج:", model_combo)

        layout.addLayout(form_layout)

        # أزرار الإجراءات
        btn_layout = QHBoxLayout()

        save_btn = QPushButton("💾 حفظ")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_layout.addWidget(save_btn)

        test_btn = QPushButton("🧪 اختبار")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        btn_layout.addWidget(test_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        return card


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    widget = AIProviderManager()
    widget.show()
    sys.exit(app.exec())
