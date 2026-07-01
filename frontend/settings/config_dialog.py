"""
Finovate Audit Nexus AI - Settings Dialog
Enterprise AI Financial Audit & Intelligence Platform
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QLineEdit, QPushButton, QLabel, QComboBox,
                               QTabWidget, QWidget, QSpinBox, QCheckBox,
                               QMessageBox, QFrame, QGroupBox)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont
from loguru import logger

from frontend.styles.design_system import DesignSystem


class SettingsDialog(QDialog):
    """Professional Settings Dialog for Application Configuration"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("الإعدادات - Settings")
        self.setMinimumSize(720, 580)
        self.setModal(True)
        self.setStyleSheet(DesignSystem.get_dialog_style())
        self.setup_ui()
        self._load_settings()
        self._apply_entry_animation()

    def _apply_entry_animation(self):
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(250)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("dialogHeader")
        header.setFixedHeight(90)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(30, 18, 30, 18)

        title = QLabel("الإعدادات")
        title.setObjectName("dialogTitle")
        header_layout.addWidget(title)

        subtitle = QLabel("تخصيص إعدادات المنصة حسب احتياجاتك")
        subtitle.setObjectName("dialogSubtitle")
        header_layout.addWidget(subtitle)

        main_layout.addWidget(header)

        content = QWidget()
        content.setObjectName("dialogContent")

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(25, 20, 25, 20)

        tabs = QTabWidget()
        tabs.setObjectName("settingsTabs")
        tabs.addTab(self.create_general_tab(), "عام General")
        tabs.addTab(self.create_ai_settings_tab(), "الذكاء الاصطناعي AI")
        tabs.addTab(self.create_connector_tab(), "الموصلات Connectors")
        tabs.addTab(self.create_security_tab(), "الأمان Security")
        content_layout.addWidget(tabs)

        main_layout.addWidget(content, 1)

        button_frame = QFrame()
        button_frame.setObjectName("dialogButtonFrame")
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(25, 12, 25, 16)

        self.reset_all_btn = QPushButton("استعادة الإفتراضي")
        self.reset_all_btn.setObjectName("resetButton")
        self.reset_all_btn.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(self.reset_all_btn)

        button_layout.addStretch()

        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("cancelButton")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("حفظ الإعدادات")
        self.save_btn.setObjectName("createButton")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setDefault(True)
        button_layout.addWidget(self.save_btn)

        main_layout.addWidget(button_frame)

        self.save_btn.clicked.connect(self._on_save)
        self.cancel_btn.clicked.connect(self.reject)
        self.reset_all_btn.clicked.connect(self._on_reset)

    def _on_save(self):
        logger.info("Settings saved successfully")
        QMessageBox.information(
            self,
            "تم الحفظ",
            "تم حفظ الإعدادات بنجاح"
        )
        self.accept()

    def _on_cancel(self):
        self.reject()

    def _on_reset(self):
        reply = QMessageBox.question(
            self, "تأكيد",
            "هل أنت متأكد من استعادة الإعدادات الافتراضية؟",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._load_settings(reset=True)

    def _load_settings(self, reset=False):
        if reset:
            self.company_input.setText("")
            self.api_key_input.clear()
            self.lang_combo.setCurrentIndex(0)
            self.currency_combo.setCurrentIndex(0)
            self.fiscal_combo.setCurrentIndex(0)
            self.provider_combo.setCurrentIndex(0)
            self.temp_spin.setValue(70)
            self.tokens_spin.setValue(2000)
            self.local_ai_check.setChecked(True)
            self.timeout_spin.setValue(30)
            self.mfa_check.setChecked(False)

    def _create_section_group(self, title):
        group = QGroupBox(title)
        group.setObjectName("settingsGroup")
        return group

    def create_general_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        group = self._create_section_group("معلومات الشركة")
        form = QFormLayout(group)
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self.company_input = QLineEdit("Finovate Audit Client")
        self.company_input.setObjectName("settingsInput")
        form.addRow("اسم الشركة:", self.company_input)

        self.lang_combo = QComboBox()
        self.lang_combo.setObjectName("settingsCombo")
        self.lang_combo.addItems(["العربية (Arabic)", "English"])
        form.addRow("اللغة:", self.lang_combo)

        self.currency_combo = QComboBox()
        self.currency_combo.setObjectName("settingsCombo")
        self.currency_combo.addItems(["EGP", "USD", "EUR", "SAR", "GBP", "AED"])
        form.addRow("العملة:", self.currency_combo)

        self.fiscal_combo = QComboBox()
        self.fiscal_combo.setObjectName("settingsCombo")
        self.fiscal_combo.addItems([
            "يناير", "فبراير", "مارس", "أبريل",
            "مايو", "يونيو", "يوليو", "أغسطس",
            "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
        ])
        form.addRow("بداية السنة المالية:", self.fiscal_combo)

        layout.addWidget(group)
        layout.addStretch()
        return widget

    def create_ai_settings_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        group = self._create_section_group("إعدادات الذكاء الاصطناعي")
        form = QFormLayout(group)
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self.provider_combo = QComboBox()
        self.provider_combo.setObjectName("settingsCombo")
        self.provider_combo.addItems([
            "OpenAI", "Anthropic", "Google", "DeepSeek",
            "Mistral AI", "Cohere", "Ollama (Local)"
        ])
        form.addRow("مزود AI:", self.provider_combo)

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("أدخل مفتاح API")
        self.api_key_input.setObjectName("settingsInput")
        form.addRow("مفتاح API:", self.api_key_input)

        self.model_combo = QComboBox()
        self.model_combo.setObjectName("settingsCombo")
        self.model_combo.addItems([
            "GPT-4", "GPT-4 Turbo", "GPT-3.5-turbo",
            "Claude-3 Opus", "Claude-3 Sonnet",
            "Gemini Pro", "Gemini Ultra",
            "DeepSeek V3", "Llama 3", "Mistral Large"
        ])
        form.addRow("النموذج:", self.model_combo)

        self.temp_spin = QSpinBox()
        self.temp_spin.setRange(0, 100)
        self.temp_spin.setValue(70)
        self.temp_spin.setSuffix("%")
        form.addRow("الحرارة (Temperature):", self.temp_spin)

        self.tokens_spin = QSpinBox()
        self.tokens_spin.setRange(100, 32000)
        self.tokens_spin.setValue(4000)
        self.tokens_spin.setSingleStep(500)
        form.addRow("الحد الأقصى للرموز:", self.tokens_spin)

        self.local_ai_check = QCheckBox("تفعيل الذكاء الاصطناعي المحلي (Ollama)")
        self.local_ai_check.setChecked(True)
        form.addRow(self.local_ai_check)

        layout.addWidget(group)
        layout.addStretch()
        return widget

    def create_connector_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        group = self._create_section_group("موصلات الأنظمة")
        form = QFormLayout(group)
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        connectors = [
            ("SAP", "نظام SAP ERP"),
            ("Oracle ERP", "نظام Oracle Financials"),
            ("Microsoft Dynamics", "Microsoft Dynamics 365"),
            ("Odoo", "نظام Odoo ERP"),
            ("Zoho Books", "Zoho Books"),
            ("QuickBooks", "QuickBooks Online"),
            ("Xero", "Xero Accounting"),
            ("SQL Database", "SQL Database مباشر"),
        ]
        self.connector_checks = {}
        for key, label in connectors:
            check = QCheckBox(label)
            self.connector_checks[key] = check
            form.addRow(check)

        layout.addWidget(group)
        layout.addStretch()
        return widget

    def create_security_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        group = self._create_section_group("إعدادات الأمان")
        form = QFormLayout(group)
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self.mfa_check = QCheckBox("تفعيل المصادقة متعددة العوامل (MFA)")
        form.addRow(self.mfa_check)

        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 480)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setSuffix(" دقيقة")
        form.addRow("مهلة الجلسة:", self.timeout_spin)

        encryption_check = QCheckBox("تفعيل تشفير AES-256 للبيانات")
        encryption_check.setChecked(True)
        encryption_check.setEnabled(False)
        form.addRow(encryption_check)

        audit_check = QCheckBox("تفعيل سجل التدقيق (Audit Trail)")
        audit_check.setChecked(True)
        form.addRow(audit_check)

        layout.addWidget(group)
        layout.addStretch()
        return widget
