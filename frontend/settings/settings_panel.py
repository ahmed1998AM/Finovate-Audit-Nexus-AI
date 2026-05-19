"""
Finovate Audit Nexus AI - Settings Panel Component
مكون لوحة الإعدادات

Provides comprehensive settings panel for application configuration.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QFrame, QPushButton, QScrollArea,
    QCheckBox, QComboBox, QLineEdit, QSpinBox,
    QDoubleSpinBox, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class SettingsPanel(QWidget):
    """
    Settings Panel Component
    Provides comprehensive application settings
    """
    
    settings_changed = Signal(str, object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("الإعدادات")
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self.create_general_tab(), "📋 عام")
        tabs.addTab(self.create_appearance_tab(), "🎨 المظهر")
        tabs.addTab(self.create_ai_tab(), "🤖 الذكاء الاصطناعي")
        tabs.addTab(self.create_security_tab(), "🔐 الأمان")
        tabs.addTab(self.create_notifications_tab(), "🔔 الإشعارات")
        tabs.addTab(self.create_integrations_tab(), "🔗 التكاملات")
        
        main_layout.addWidget(tabs)
        
    def create_header(self) -> QWidget:
        """Create header"""
        header = QWidget()
        layout = QHBoxLayout(header)
        
        title = QLabel("⚙️ إعدادات التطبيق")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        
        save_btn = QPushButton("💾 حفظ التغييرات")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(save_btn)
        
        return header
    
    def create_general_tab(self) -> QWidget:
        """Create general settings tab"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Language
        lang_group = QGroupBox("🌐 اللغة")
        lang_layout = QFormLayout(lang_group)
        lang_combo = QComboBox()
        lang_combo.addItems(["العربية", "English"])
        lang_layout.addRow("لغة الواجهة:", lang_combo)
        
        # Theme
        theme_group = QGroupBox("🎨 السمة")
        theme_layout = QFormLayout(theme_group)
        theme_combo = QComboBox()
        theme_combo.addItems(["فاتح", "داكن", "تلقائي"])
        theme_layout.addRow("السمة:", theme_combo)
        
        # Date Format
        date_group = QGroupBox("📅 تنسيق التاريخ")
        date_layout = QFormLayout(date_group)
        date_combo = QComboBox()
        date_combo.addItems(["هجري", "ميلادي", "كلاهما"])
        date_layout.addRow("تنسيق التاريخ:", date_combo)
        
        # Currency
        currency_group = QGroupBox("💰 العملة")
        currency_layout = QFormLayout(currency_group)
        currency_combo = QComboBox()
        currency_combo.addItems(["ر.س", "د.إ", "د.ك", "USD", "EUR"])
        currency_layout.addRow("العملة الافتراضية:", currency_combo)
        
        layout.addWidget(lang_group)
        layout.addWidget(theme_group)
        layout.addWidget(date_group)
        layout.addWidget(currency_group)
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(tab)
        main_layout.addWidget(scroll)
        
        return tab
    
    def create_appearance_tab(self) -> QWidget:
        """Create appearance settings tab"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Font Size
        font_group = QGroupBox("📝 حجم الخط")
        font_layout = QFormLayout(font_group)
        font_spin = QSpinBox()
        font_spin.setRange(8, 24)
        font_spin.setValue(12)
        font_layout.addRow("حجم الخط:", font_spin)
        
        # Density
        density_group = QGroupBox("📊 كثافة العرض")
        density_layout = QFormLayout(density_group)
        density_combo = QComboBox()
        density_combo.addItems(["مريح", "عادي", "مضغوط"])
        density_layout.addRow("كثافة العرض:", density_combo)
        
        # Animations
        anim_group = QGroupBox("✨ الرسوم المتحركة")
        anim_layout = QVBoxLayout(anim_group)
        anim_checkbox = QCheckBox("تفعيل الرسوم المتحركة")
        anim_checkbox.setChecked(True)
        anim_layout.addWidget(anim_checkbox)
        
        layout.addWidget(font_group)
        layout.addWidget(density_group)
        layout.addWidget(anim_group)
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(tab)
        main_layout.addWidget(scroll)
        
        return tab
    
    def create_ai_tab(self) -> QWidget:
        """Create AI settings tab"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Model Selection
        model_group = QGroupBox("🤖 نموذج الذكاء الاصطناعي")
        model_layout = QFormLayout(model_group)
        model_combo = QComboBox()
        model_combo.addItems(["GPT-4", "Claude-3", "Llama-3", "Gemini Pro"])
        model_layout.addRow("النموذج الأساسي:", model_combo)
        
        # Temperature
        temp_group = QGroupBox("🌡️ درجة الحرارة")
        temp_layout = QFormLayout(temp_group)
        temp_spin = QDoubleSpinBox()
        temp_spin.setRange(0.0, 1.0)
        temp_spin.setSingleStep(0.1)
        temp_spin.setValue(0.7)
        temp_layout.addRow("درجة الحرارة:", temp_spin)
        
        # Auto-save
        auto_group = QGroupBox("💾 الحفظ التلقائي")
        auto_layout = QVBoxLayout(auto_group)
        auto_checkbox = QCheckBox("تفعيل الحفظ التلقائي للنتائج")
        auto_checkbox.setChecked(True)
        auto_layout.addWidget(auto_checkbox)
        
        layout.addWidget(model_group)
        layout.addWidget(temp_group)
        layout.addWidget(auto_group)
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(tab)
        main_layout.addWidget(scroll)
        
        return tab
    
    def create_security_tab(self) -> QWidget:
        """Create security settings tab"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 2FA
        twofa_group = QGroupBox("🔐 المصادقة الثنائية")
        twofa_layout = QVBoxLayout(twofa_group)
        twofa_checkbox = QCheckBox("تفعيل المصادقة الثنائية (2FA)")
        twofa_layout.addWidget(twofa_checkbox)
        
        # Session Timeout
        session_group = QGroupBox("⏱️ مهلة الجلسة")
        session_layout = QFormLayout(session_group)
        session_spin = QSpinBox()
        session_spin.setRange(5, 480)
        session_spin.setValue(30)
        session_spin.setSuffix(" دقيقة")
        session_layout.addRow("مهلة الجلسة:", session_spin)
        
        # Audit Log
        audit_group = QGroupBox("📋 سجل التدقيق")
        audit_layout = QVBoxLayout(audit_group)
        audit_checkbox = QCheckBox("تفعيل تسجيل جميع الأنشطة")
        audit_checkbox.setChecked(True)
        audit_layout.addWidget(audit_checkbox)
        
        layout.addWidget(twofa_group)
        layout.addWidget(session_group)
        layout.addWidget(audit_group)
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(tab)
        main_layout.addWidget(scroll)
        
        return tab
    
    def create_notifications_tab(self) -> QWidget:
        """Create notifications settings tab"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Email Notifications
        email_group = QGroupBox("📧 إشعارات البريد الإلكتروني")
        email_layout = QVBoxLayout(email_group)
        email_checkbox = QCheckBox("تفعيل إشعارات البريد الإلكتروني")
        email_checkbox.setChecked(True)
        email_layout.addWidget(email_checkbox)
        
        # Desktop Notifications
        desktop_group = QGroupBox("🖥️ إشعارات سطح المكتب")
        desktop_layout = QVBoxLayout(desktop_group)
        desktop_checkbox = QCheckBox("تفعيل إشعارات سطح المكتب")
        desktop_checkbox.setChecked(True)
        desktop_layout.addWidget(desktop_checkbox)
        
        # Sound
        sound_group = QGroupBox("🔔 الأصوات")
        sound_layout = QVBoxLayout(sound_group)
        sound_checkbox = QCheckBox("تفعيل الأصوات للإشعارات")
        sound_checkbox.setChecked(False)
        sound_layout.addWidget(sound_checkbox)
        
        layout.addWidget(email_group)
        layout.addWidget(desktop_group)
        layout.addWidget(sound_group)
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(tab)
        main_layout.addWidget(scroll)
        
        return tab
    
    def create_integrations_tab(self) -> QWidget:
        """Create integrations settings tab"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ERP Systems
        erp_group = QGroupBox("🏢 أنظمة ERP")
        erp_layout = QVBoxLayout(erp_group)
        
        sap_checkbox = QCheckBox("SAP")
        oracle_checkbox = QCheckBox("Oracle")
        odoo_checkbox = QCheckBox("Odoo")
        
        erp_layout.addWidget(sap_checkbox)
        erp_layout.addWidget(oracle_checkbox)
        erp_layout.addWidget(odoo_checkbox)
        
        # Cloud Storage
        cloud_group = QGroupBox("☁️ التخزين السحابي")
        cloud_layout = QVBoxLayout(cloud_group)
        
        drive_checkbox = QCheckBox("Google Drive")
        dropbox_checkbox = QCheckBox("Dropbox")
        onedrive_checkbox = QCheckBox("OneDrive")
        
        cloud_layout.addWidget(drive_checkbox)
        cloud_layout.addWidget(dropbox_checkbox)
        cloud_layout.addWidget(onedrive_checkbox)
        
        layout.addWidget(erp_group)
        layout.addWidget(cloud_group)
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(tab)
        main_layout.addWidget(scroll)
        
        return tab
    
    def setup_styles(self):
        """Apply styles"""
        self.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-size: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QCheckBox {
                spacing: 10px;
            }
            QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
        """)
    
    def save_settings(self):
        """Save all settings"""
        print("Saving settings...")
        self.settings_changed.emit("all", True)
