"""
Finovate Audit Nexus AI - Sidebar Component
الشريط الجانبي للتنقل بين صفحات التطبيق
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFrame, 
    QLabel, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QFont


class Sidebar(QFrame):
    """الشريط الجانبي للتنقل"""
    
    page_requested = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(250)
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة الشريط الجانبي"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)
        
        # شعار التطبيق
        logo_label = QLabel("Finovate Audit\nNexus AI")
        logo_label.setObjectName("logoLabel")
        logo_font = QFont("Segoe UI", 14, QFont.Bold)
        logo_label.setFont(logo_font)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("separatorLine")
        layout.addWidget(line)
        
        # أزرار التنقل
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setObjectName("navScrollArea")
        
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(5)
        
        # تعريف عناصر التنقل
        nav_items = [
            ("dashboard", "📊 لوحة التحكم", "لوحة التحكم الرئيسية"),
            ("analytics", "📈 التحليلات", "التحليلات المالية"),
            ("agents", "🤖 الوكلاء", "إدارة الوكلاء الذكية"),
            ("reports", "📑 التقارير", "عرض التقارير"),
            ("ai_management", "🧠 الذكاء الاصطناعي", "إدارة مزودي AI"),
            ("connectors", "🔗 الموصلات", "إدارة الموصلات"),
            ("audit_projects", "📝 مشاريع المراجعة", "إدارة المشاريع"),
            ("fraud_detection", "🔍 كشف الاحتيال", "تحليل الاحتيال"),
            ("compliance", "⚖️ الامتثال", "الامتثال والمعايير"),
            ("settings", "⚙️ الإعدادات", "إعدادات النظام"),
        ]
        
        for page_id, title, tooltip in nav_items:
            btn = self.create_nav_button(title, tooltip)
            btn.clicked.connect(lambda checked, pid=page_id: self.page_requested.emit(pid))
            nav_layout.addWidget(btn)
            
        nav_layout.addStretch()
        scroll.setWidget(nav_widget)
        layout.addWidget(scroll)
        
        # معلومات الإصدار
        version_label = QLabel("v1.0.0")
        version_label.setObjectName("versionLabel")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
    def create_nav_button(self, text, tooltip) -> QPushButton:
        """إنشاء زر تنقل"""
        btn = QPushButton(text)
        btn.setObjectName("navButton")
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.setMinimumHeight(45)
        btn.setIconSize(QSize(20, 20))
        
        font = QFont("Segoe UI", 10)
        btn.setFont(font)
        
        return btn


class TopToolbar(QFrame):
    """الشريط العلوي للأدوات السريعة"""
    
    quick_action_requested = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("topToolbar")
        self.setFixedHeight(60)
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد شريط الأدوات"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)
        
        # عنوان الصفحة
        title_label = QLabel("لوحة التحكم الرئيسية")
        title_label.setObjectName("toolbarTitle")
        title_font = QFont("Segoe UI", 14, QFont.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # أزرار الإجراءات السريعة
        quick_actions = [
            ("new_audit", "➕ مراجعة جديدة", "بدء مراجعة جديدة"),
            ("import_file", "📥 استيراد ملف", "استيراد بيانات من ملف"),
            ("run_agents", "▶️ تشغيل الوكلاء", "تشغيل جميع الوكلاء"),
        ]
        
        for action_id, icon_text, tooltip in quick_actions:
            btn = QPushButton(f"{icon_text}")
            btn.setObjectName("quickActionButton")
            btn.setToolTip(tooltip)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedSize(40, 40)
            btn.clicked.connect(lambda checked, aid=action_id: self.quick_action_requested.emit(aid))
            layout.addWidget(btn)
            
        # زر المستخدم
        user_btn = QPushButton("👤 Admin")
        user_btn.setObjectName("userButton")
        user_btn.setFixedSize(100, 40)
        layout.addWidget(user_btn)
