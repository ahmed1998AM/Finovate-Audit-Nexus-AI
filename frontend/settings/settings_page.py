from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QFormLayout, QLineEdit, QComboBox, QSpinBox,
    QCheckBox, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from loguru import logger
import json
import os

from frontend.styles.design_system import DesignSystem, Color, Typography


SETTINGS_PATH = os.path.join(os.path.expanduser("~"), ".finovate_audit", "settings.json")


def load_settings_file():
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load settings: {e}")
    return {}


def save_settings_file(data: dict):
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class FormField(QWidget):
    def __init__(self, label, widget):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(12)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {Color.TEXT_PRIMARY}; font-size: 13px; font-weight: 500; min-width: 160px;")
        layout.addWidget(lbl)
        layout.addWidget(widget, stretch=1)


class SettingsPage(QWidget):
    settings_changed = Signal(dict)

    def __init__(self, parent=None, theme_manager=None):
        super().__init__(parent)
        self.setObjectName("SettingsPage")
        self.theme_manager = theme_manager
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Settings")
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {Color.TEXT_PRIMARY};")
        header.addWidget(title)
        header.addStretch()
        main_layout.addLayout(header)

        tabs = QTabWidget()


        general_tab = self._create_general_tab()
        general_tab.setStyleSheet("background: transparent;")
        tabs.addTab(general_tab, "General")

        ai_tab = self._create_ai_tab()
        ai_tab.setStyleSheet("background: transparent;")
        tabs.addTab(ai_tab, "AI")

        connector_tab = self._create_connector_tab()
        connector_tab.setStyleSheet("background: transparent;")
        tabs.addTab(connector_tab, "Connectors")

        security_tab = self._create_security_tab()
        security_tab.setStyleSheet("background: transparent;")
        tabs.addTab(security_tab, "Security")

        theme_tab = self._create_theme_tab()
        theme_tab.setStyleSheet("background: transparent;")
        tabs.addTab(theme_tab, "Appearance")

        main_layout.addWidget(tabs)

        buttons = QHBoxLayout()
        buttons.addStretch()
        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("successButton")
        save_btn.setFixedHeight(40)
        save_btn.setFixedWidth(180)
        save_btn.clicked.connect(self._on_save)
        buttons.addWidget(save_btn)
        main_layout.addLayout(buttons)

    def _input_style(self):
        return f"""
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
                background-color: {Color.BG_DARK};
                color: {Color.TEXT_PRIMARY};
                border: 1px solid {Color.BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                min-height: 20px;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
                border: 1px solid {Color.PRIMARY};
            }}
        """

    def _checkbox_style(self):
        return f"color: {Color.TEXT_PRIMARY}; font-size: 13px; spacing: 8px;"

    def _create_general_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(2)

        group = QGroupBox("General Configuration")
        group.setStyleSheet(f"""
            QGroupBox {{
                color: {Color.TEXT_PRIMARY}; font-weight: 600; font-size: 13px;
                border: 1px solid {Color.BORDER}; border-radius: 8px;
                padding: 20px; margin-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; left: 12px; padding: 0 6px;
            }}
        """)
        cl = QVBoxLayout(group)
        cl.setSpacing(2)

        self.company_input = QLineEdit("Finovate Audit Client")
        self.company_input.setStyleSheet(f"background: {Color.BG_DARK}; color: {Color.TEXT_PRIMARY}; border: 1px solid {Color.BORDER}; border-radius: 6px; padding: 8px 12px; font-size: 13px;")
        cl.addWidget(FormField("Company Name:", self.company_input))

        self.api_url_input = QLineEdit("http://localhost:8000")
        self.api_url_input.setStyleSheet(f"background: {Color.BG_DARK}; color: {Color.TEXT_PRIMARY}; border: 1px solid {Color.BORDER}; border-radius: 6px; padding: 8px 12px; font-size: 13px;")
        cl.addWidget(FormField("API Server URL:", self.api_url_input))

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "العربية"])
        self.lang_combo.setStyleSheet(f"background: {Color.BG_DARK}; color: {Color.TEXT_PRIMARY}; border: 1px solid {Color.BORDER}; border-radius: 6px; padding: 8px 12px; font-size: 13px;")
        cl.addWidget(FormField("Language:", self.lang_combo))

        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["USD", "EUR", "EGP", "SAR", "AED"])
        self.currency_combo.setStyleSheet(f"background: {Color.BG_DARK}; color: {Color.TEXT_PRIMARY}; border: 1px solid {Color.BORDER}; border-radius: 6px; padding: 8px 12px; font-size: 13px;")
        cl.addWidget(FormField("Currency:", self.currency_combo))

        self.fiscal_combo = QComboBox()
        self.fiscal_combo.addItems(["January", "February", "March", "April", "July"])
        self.fiscal_combo.setStyleSheet(f"background: {Color.BG_DARK}; color: {Color.TEXT_PRIMARY}; border: 1px solid {Color.BORDER}; border-radius: 6px; padding: 8px 12px; font-size: 13px;")
        cl.addWidget(FormField("Fiscal Year Start:", self.fiscal_combo))

        self.auto_refresh = QCheckBox("Auto-refresh every 30 seconds")
        self.auto_refresh.setChecked(True)
        self.auto_refresh.setStyleSheet(self._checkbox_style())
        cl.addWidget(self.auto_refresh)

        self.notifications_check = QCheckBox("Enable notifications")
        self.notifications_check.setChecked(True)
        self.notifications_check.setStyleSheet(self._checkbox_style())
        cl.addWidget(self.notifications_check)

        layout.addWidget(group)
        layout.addStretch()
        return w

    def _create_ai_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(2)

        group = QGroupBox("AI Configuration")
        group.setStyleSheet(f"""
            QGroupBox {{
                color: {Color.TEXT_PRIMARY}; font-weight: 600; font-size: 13px;
                border: 1px solid {Color.BORDER}; border-radius: 8px;
                padding: 20px; margin-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; left: 12px; padding: 0 6px;
            }}
        """)
        cl = QVBoxLayout(group)
        cl.setSpacing(2)

        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["OpenAI", "Anthropic", "Google Gemini", "DeepSeek", "Mistral AI", "Ollama (Local)"])
        self.provider_combo.setStyleSheet(f"background: {Color.BG_DARK}; color: {Color.TEXT_PRIMARY}; border: 1px solid {Color.BORDER}; border-radius: 6px; padding: 8px 12px; font-size: 13px;")
        cl.addWidget(FormField("AI Provider:", self.provider_combo))

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Enter API key")
        self.api_key_input.setStyleSheet(f"background: {Color.BG_DARK}; color: {Color.TEXT_PRIMARY}; border: 1px solid {Color.BORDER}; border-radius: 6px; padding: 8px 12px; font-size: 13px;")
        cl.addWidget(FormField("API Key:", self.api_key_input))

        self.model_combo = QComboBox()
        self.model_combo.addItems(["GPT-4", "GPT-3.5-turbo", "Claude-3", "Gemini Pro", "Llama 3", "Mistral Large"])
        self.model_combo.setStyleSheet(f"background: {Color.BG_DARK}; color: {Color.TEXT_PRIMARY}; border: 1px solid {Color.BORDER}; border-radius: 6px; padding: 8px 12px; font-size: 13px;")
        cl.addWidget(FormField("Model:", self.model_combo))

        self.temp_spin = QSpinBox()
        self.temp_spin.setRange(0, 100)
        self.temp_spin.setValue(70)
        self.temp_spin.setStyleSheet(f"background: {Color.BG_DARK}; color: {Color.TEXT_PRIMARY}; border: 1px solid {Color.BORDER}; border-radius: 6px; padding: 8px 12px; font-size: 13px;")
        cl.addWidget(FormField("Temperature:", self.temp_spin))

        self.tokens_spin = QSpinBox()
        self.tokens_spin.setRange(100, 16000)
        self.tokens_spin.setValue(2000)
        self.tokens_spin.setStyleSheet(f"background: {Color.BG_DARK}; color: {Color.TEXT_PRIMARY}; border: 1px solid {Color.BORDER}; border-radius: 6px; padding: 8px 12px; font-size: 13px;")
        cl.addWidget(FormField("Max Tokens:", self.tokens_spin))

        self.local_ai_check = QCheckBox("Enable local AI (Ollama)")
        self.local_ai_check.setChecked(True)
        self.local_ai_check.setStyleSheet(self._checkbox_style())
        cl.addWidget(self.local_ai_check)

        layout.addWidget(group)
        layout.addStretch()
        return w

    def _create_connector_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        group = QGroupBox("Connectors")
        group.setStyleSheet(f"""
            QGroupBox {{
                color: {Color.TEXT_PRIMARY}; font-weight: 600; font-size: 13px;
                border: 1px solid {Color.BORDER}; border-radius: 8px;
                padding: 20px; margin-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; left: 12px; padding: 0 6px;
            }}
        """)
        cl = QVBoxLayout(group)
        cl.setSpacing(4)

        self.connector_checks = {}
        for name in ["SAP", "Oracle ERP", "Microsoft Dynamics", "Odoo", "Zoho Books", "QuickBooks", "Xero", "SQL Database"]:
            cb = QCheckBox(name)
            cb.setChecked(True)
            cb.setStyleSheet(self._checkbox_style())
            self.connector_checks[name] = cb
            cl.addWidget(cb)

        layout.addWidget(group)
        layout.addStretch()
        return w

    def _create_security_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(2)

        group = QGroupBox("Security Settings")
        group.setStyleSheet(f"""
            QGroupBox {{
                color: {Color.TEXT_PRIMARY}; font-weight: 600; font-size: 13px;
                border: 1px solid {Color.BORDER}; border-radius: 8px;
                padding: 20px; margin-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; left: 12px; padding: 0 6px;
            }}
        """)
        cl = QVBoxLayout(group)
        cl.setSpacing(2)

        self.mfa_check = QCheckBox("Enable MFA (Multi-Factor Authentication)")
        self.mfa_check.setChecked(True)
        self.mfa_check.setStyleSheet(self._checkbox_style())
        cl.addWidget(self.mfa_check)

        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 480)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setStyleSheet(f"background: {Color.BG_DARK}; color: {Color.TEXT_PRIMARY}; border: 1px solid {Color.BORDER}; border-radius: 6px; padding: 8px 12px; font-size: 13px;")
        cl.addWidget(FormField("Session Timeout (min):", self.timeout_spin))

        encryption_check = QCheckBox("Enable AES-256 encryption")
        encryption_check.setChecked(True)
        encryption_check.setEnabled(False)
        encryption_check.setStyleSheet(self._checkbox_style())
        cl.addWidget(encryption_check)

        self.logging_check = QCheckBox("Enable audit logging")
        self.logging_check.setChecked(True)
        self.logging_check.setStyleSheet(self._checkbox_style())
        cl.addWidget(self.logging_check)

        self.session_check = QCheckBox("Logout on session timeout")
        self.session_check.setChecked(True)
        self.session_check.setStyleSheet(self._checkbox_style())
        cl.addWidget(self.session_check)

        layout.addWidget(group)
        layout.addStretch()
        return w

    def _create_theme_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(2)

        group = QGroupBox("Appearance")
        group.setStyleSheet(f"""
            QGroupBox {{
                color: {Color.TEXT_PRIMARY}; font-weight: 600; font-size: 13px;
                border: 1px solid {Color.BORDER}; border-radius: 8px;
                padding: 20px; margin-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; left: 12px; padding: 0 6px;
            }}
        """)
        cl = QVBoxLayout(group)
        cl.setSpacing(2)

        self.theme_combo = QComboBox()
        themes = list(self.theme_manager.THEMES.keys()) if self.theme_manager else ["Dark Professional", "Light Enterprise"]
        self.theme_combo.addItems(themes)
        self.theme_combo.setStyleSheet(f"background: {Color.BG_DARK}; color: {Color.TEXT_PRIMARY}; border: 1px solid {Color.BORDER}; border-radius: 6px; padding: 8px 12px; font-size: 13px;")
        cl.addWidget(FormField("Theme:", self.theme_combo))

        self.font_size = QComboBox()
        self.font_size.addItems(["Small (12px)", "Medium (14px)", "Large (16px)"])
        self.font_size.setCurrentIndex(1)
        self.font_size.setStyleSheet(f"background: {Color.BG_DARK}; color: {Color.TEXT_PRIMARY}; border: 1px solid {Color.BORDER}; border-radius: 6px; padding: 8px 12px; font-size: 13px;")
        cl.addWidget(FormField("Font Size:", self.font_size))

        self.compact_check = QCheckBox("Compact Mode")
        self.compact_check.setStyleSheet(self._checkbox_style())
        cl.addWidget(self.compact_check)

        self.animations_check = QCheckBox("Enable animations")
        self.animations_check.setChecked(True)
        self.animations_check.setStyleSheet(self._checkbox_style())
        cl.addWidget(self.animations_check)

        layout.addWidget(group)
        layout.addStretch()
        return w

    def _load_settings(self):
        saved = load_settings_file()
        if not saved:
            return
        if "company" in saved:
            self.company_input.setText(saved["company"])
        if "api_base_url" in saved:
            self.api_url_input.setText(saved["api_base_url"])
        idx = self.lang_combo.findText(saved.get("language", ""))
        if idx >= 0: self.lang_combo.setCurrentIndex(idx)
        idx = self.currency_combo.findText(saved.get("currency", ""))
        if idx >= 0: self.currency_combo.setCurrentIndex(idx)
        idx = self.theme_combo.findText(saved.get("theme", ""))
        if idx >= 0: self.theme_combo.setCurrentIndex(idx)
        idx = self.font_size.findText(saved.get("font_size", ""))
        if idx >= 0: self.font_size.setCurrentIndex(idx)
        idx = self.provider_combo.findText(saved.get("provider", ""))
        if idx >= 0: self.provider_combo.setCurrentIndex(idx)
        idx = self.model_combo.findText(saved.get("model", ""))
        if idx >= 0: self.model_combo.setCurrentIndex(idx)
        self.temp_spin.setValue(saved.get("temperature", 70))
        self.tokens_spin.setValue(saved.get("max_tokens", 2000))
        self.timeout_spin.setValue(saved.get("session_timeout", 30))
        self.local_ai_check.setChecked(saved.get("local_ai", True))
        self.mfa_check.setChecked(saved.get("mfa", True))
        self.auto_refresh.setChecked(saved.get("auto_refresh", True))
        self.notifications_check.setChecked(saved.get("notifications", True))
        self.compact_check.setChecked(saved.get("compact_mode", False))
        self.animations_check.setChecked(saved.get("animations", True))
        self.logging_check.setChecked(saved.get("logging", True))
        self.session_check.setChecked(saved.get("session_check", True))
        connector_states = saved.get("connectors", {})
        for name, cb in self.connector_checks.items():
            if name in connector_states:
                cb.setChecked(connector_states[name])
        logger.info("Settings loaded from disk")

    def _on_save(self):
        connectors = {name: cb.isChecked() for name, cb in self.connector_checks.items()}
        data = {
            "company": self.company_input.text(),
            "api_base_url": self.api_url_input.text().strip().rstrip("/"),
            "language": self.lang_combo.currentText(),
            "currency": self.currency_combo.currentText(),
            "fiscal_start": self.fiscal_combo.currentText(),
            "theme": self.theme_combo.currentText(),
            "font_size": self.font_size.currentText(),
            "compact_mode": self.compact_check.isChecked(),
            "animations": self.animations_check.isChecked(),
            "provider": self.provider_combo.currentText(),
            "model": self.model_combo.currentText(),
            "temperature": self.temp_spin.value(),
            "max_tokens": self.tokens_spin.value(),
            "local_ai": self.local_ai_check.isChecked(),
            "mfa": self.mfa_check.isChecked(),
            "session_timeout": self.timeout_spin.value(),
            "auto_refresh": self.auto_refresh.isChecked(),
            "notifications": self.notifications_check.isChecked(),
            "logging": self.logging_check.isChecked(),
            "session_check": self.session_check.isChecked(),
            "connectors": connectors,
        }
        save_settings_file(data)
        logger.info(f"Settings saved to {SETTINGS_PATH}")
        QMessageBox.information(self, "Saved", "Settings saved successfully")
        self.settings_changed.emit(data)
