"""
Finovate Audit Nexus AI - Settings Dialog
Enterprise AI Financial Audit & Intelligence Platform
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                                QLineEdit, QPushButton, QLabel, QComboBox, 
                                QTabWidget, QWidget, QSpinBox, QCheckBox)
from PySide6.QtCore import Qt

class SettingsDialog(QDialog):
    """Main Settings Dialog for Application Configuration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(600, 500)
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the settings dialog UI"""
        layout = QVBoxLayout(self)
        
        # Tab Widget
        tabs = QTabWidget()
        
        # General Settings Tab
        general_tab = self.create_general_tab()
        tabs.addTab(general_tab, "General")
        
        # AI Settings Tab
        ai_tab = self.create_ai_settings_tab()
        tabs.addTab(ai_tab, "AI Configuration")
        
        # Connector Settings Tab
        connector_tab = self.create_connector_tab()
        tabs.addTab(connector_tab, "Connectors")
        
        # Security Settings Tab
        security_tab = self.create_security_tab()
        tabs.addTab(security_tab, "Security")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2E86AB;
                color: white;
                padding: 10px 30px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1E5F7A;
            }
        """)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                padding: 10px 30px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #545B62;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def create_general_tab(self):
        """Create General Settings Tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        layout.addRow("Company Name:", QLineEdit())
        layout.addRow("Language:", QComboBox())
        layout.addRow("Currency:", QComboBox())
        layout.addRow("Fiscal Year Start:", QComboBox())
        
        return widget
    
    def create_ai_settings_tab(self):
        """Create AI Configuration Tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # AI Provider Selection
        provider_combo = QComboBox()
        provider_combo.addItems(["OpenAI", "Anthropic", "Google", "DeepSeek", "Mistral AI", "Ollama (Local)"])
        layout.addRow("AI Provider:", provider_combo)
        
        # API Key
        api_key_input = QLineEdit()
        api_key_input.setEchoMode(QLineEdit.Password)
        layout.addRow("API Key:", api_key_input)
        
        # Model Selection
        model_combo = QComboBox()
        model_combo.addItems(["GPT-4", "GPT-3.5-turbo", "Claude-3", "Gemini Pro", "Llama 3"])
        layout.addRow("Model:", model_combo)
        
        # Temperature
        temp_spin = QSpinBox()
        temp_spin.setRange(0, 100)
        temp_spin.setValue(70)
        layout.addRow("Temperature:", temp_spin)
        
        # Max Tokens
        tokens_spin = QSpinBox()
        tokens_spin.setRange(100, 8000)
        tokens_spin.setValue(2000)
        layout.addRow("Max Tokens:", tokens_spin)
        
        # Enable Local AI
        local_ai_check = QCheckBox("Enable Local AI (Ollama)")
        layout.addRow(local_ai_check)
        
        return widget
    
    def create_connector_tab(self):
        """Create Connectors Settings Tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        connectors = ["SAP", "Oracle ERP", "Microsoft Dynamics", "Odoo", 
                     "Zoho Books", "QuickBooks", "Xero", "SQL Database"]
        
        for connector in connectors:
            check = QCheckBox(f"Enable {connector}")
            layout.addRow(check)
        
        return widget
    
    def create_security_tab(self):
        """Create Security Settings Tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # MFA
        mfa_check = QCheckBox("Enable Multi-Factor Authentication")
        layout.addRow(mfa_check)
        
        # Session Timeout
        timeout_spin = QSpinBox()
        timeout_spin.setRange(5, 480)
        timeout_spin.setValue(30)
        layout.addRow("Session Timeout (minutes):", timeout_spin)
        
        # Encryption
        encryption_check = QCheckBox("Enable AES-256 Encryption")
        encryption_check.setChecked(True)
        encryption_check.setEnabled(False)
        layout.addRow(encryption_check)
        
        # Audit Logging
        logging_check = QCheckBox("Enable Audit Logging")
        logging_check.setChecked(True)
        layout.addRow(logging_check)
        
        return widget
