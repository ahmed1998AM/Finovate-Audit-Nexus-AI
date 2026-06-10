"""
Finovate Audit Nexus AI - Main Application Window
نافذة التطبيق الرئيسية لنظام التدقيق المالي بالذكاء الاصطناعي
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QToolBar, QStatusBar, QLabel,
    QPushButton, QFrame, QSplitter, QGroupBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QAction, QIcon, QFont

from .dashboard.main_dashboard import MainDashboard
from .dashboard.web_view_page import WebViewDashboard
from .analytics.dashboard import AnalyticsDashboard
from .agents.agent_manager import AgentManagerWidget
from .reports.report_viewer import ReportViewerWidget
from .settings.config_dialog import SettingsDialog
from .ai_management.ai_provider_manager import AIProviderManager
from .components.sidebar import Sidebar
from .components.toolbar import TopToolbar


class MainWindow(QMainWindow):
    """النافذة الرئيسية للتطبيق"""
    
    # إشارات التنقل
    navigation_requested = Signal(str)
    audit_started = Signal(dict)
    report_generated = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Finovate Audit Nexus AI - Next-Generation Financial Audit")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        # ضبط الأيقونة
        self._set_app_icon()
        
        # تهيئة المكونات
        self._setup_ui()
        self._setup_toolbar()
        self._setup_statusbar()
        self._connect_signals()
        self._load_default_theme()
        
    def _setup_ui(self):
        """إعداد الواجهة الرئيسية"""
        # الويدجت المركزي
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # التخطيط الرئيسي
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # الشريط الجانبي
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)
        
        # منطقة المحتوى الرئيسية
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # الشريط العلوي
        self.top_toolbar = TopToolbar()
        content_layout.addWidget(self.top_toolbar)
        
        # مكدس الصفحات
        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)
        
        main_layout.addWidget(content_frame, 1)
        
        # إنشاء الصفحات
        self._create_pages()
        
    def _set_app_icon(self):
        """تحميل وضبط أيقونة التطبيق"""
        import os
        import sys
        
        def get_resource_path(relative_path):
            """الحصول على المسار الصحيح للموارد سواء في التطوير أو بعد التجميع"""
            if hasattr(sys, '_MEIPASS'):
                return os.path.join(sys._MEIPASS, relative_path)
            return os.path.join(os.path.abspath("."), relative_path)

        icon_paths = [
            get_resource_path("assets/icon.ico"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon.ico"),
            "assets/icon.ico"
        ]
        
        for path in icon_paths:
            if os.path.exists(path):
                self.setWindowIcon(QIcon(path))
                break

    def _create_pages(self):
        """إنشاء صفحات التطبيق"""
        try:
            # 1. لوحة التحكم الرئيسية
            self.dashboard_page = MainDashboard()
            self.stack.addWidget(self.dashboard_page)
            
            # 1.1 لوحة الويب الذكية
            self.web_dashboard_page = WebViewDashboard()
            self.stack.addWidget(self.web_dashboard_page)
            
            # 2. لوحة التحليلات
            self.analytics_page = AnalyticsDashboard()
            self.stack.addWidget(self.analytics_page)
            
            # 3. إدارة الوكلاء
            self.agents_page = AgentManagerWidget()
            self.stack.addWidget(self.agents_page)
            
            # 4. عرض التقارير
            self.reports_page = ReportViewerWidget()
            self.stack.addWidget(self.reports_page)
            
            # 5. إدارة مزودي الذكاء الاصطناعي
            self.ai_management_page = AIProviderManager()
            self.stack.addWidget(self.ai_management_page)
        except Exception as e:
            print(f"Error creating pages: {e}")
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel(f"❌ خطأ في تحميل مكونات الواجهة:\n{e}")
            error_label.setStyleSheet("color: red; font-size: 18px;")
            error_label.setAlignment(Qt.AlignCenter)
            error_layout.addWidget(error_label)
            self.stack.addWidget(error_widget)
        
        # 6. صفحة الإعدادات (ستُفتح كنافذة منبثقة)
        
    def _setup_toolbar(self):
        """إعداد شريط الأدوات"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(Qt.SizeF(24, 24))
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        
        # إجراءات شريط الأدوات
        self.action_new_audit = QAction("مراجعة جديدة", self)
        self.action_new_audit.triggered.connect(self._start_new_audit)
        toolbar.addAction(self.action_new_audit)
        
        self.action_import_data = QAction("استيراد بيانات", self)
        self.action_import_data.triggered.connect(self._import_data)
        toolbar.addAction(self.action_import_data)
        
        toolbar.addSeparator()
        
        self.action_export_report = QAction("تصدير تقرير", self)
        self.action_export_report.triggered.connect(self._export_report)
        toolbar.addAction(self.action_export_report)
        
        toolbar.addSeparator()
        
        self.action_settings = QAction("الإعدادات", self)
        self.action_settings.triggered.connect(self._open_settings)
        toolbar.addAction(self.action_settings)
        
    def _setup_statusbar(self):
        """إعداد شريط الحالة"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # معلومات الحالة
        self.status_label = QLabel("جاهز")
        self.statusbar.addWidget(self.status_label)
        
        self.agents_status = QLabel("الوكلاء: غير نشط")
        self.statusbar.addPermanentWidget(self.agents_status)
        
        self.connection_status = QLabel("الاتصال: غير متصل")
        self.statusbar.addPermanentWidget(self.connection_status)
        
    def _connect_signals(self):
        """ربط الإشارات"""
        # ربط إشارات الشريط الجانبي
        self.sidebar.page_requested.connect(self._navigate_to_page)
        
        # ربط إشارات الشريط العلوي
        self.top_toolbar.quick_action_requested.connect(self._handle_quick_action)
        
        # ربط إشارات الصفحات
        self.dashboard_page.audit_started.connect(self._on_audit_started)
        self.dashboard_page.report_ready.connect(self._on_report_ready)
        
    def _load_default_theme(self):
        """تحميل الثيم الافتراضي"""
        from .themes.theme_manager import ThemeManager
        theme_manager = ThemeManager()
        theme_manager.apply_theme("Dark Professional")
        
    @Slot(str)
    def _navigate_to_page(self, page_name: str):
        """الانتقال إلى صفحة محددة"""
        page_map = {
            "dashboard": 0,
            "web_dashboard": 1,
            "analytics": 2,
            "agents": 3,
            "reports": 4,
            "ai_management": 5,
        }
        
        if page_name in page_map:
            self.stack.setCurrentIndex(page_map[page_name])
            self.status_label.setText(f"الصفحة: {page_name}")
            
    @Slot(str)
    def _handle_quick_action(self, action: str):
        """التعامل مع الإجراءات السريعة"""
        if action == "new_audit":
            self._start_new_audit()
        elif action == "import_file":
            self._import_data()
        elif action == "run_agents":
            self._run_all_agents()
            
    def _start_new_audit(self):
        """بدء مراجعة جديدة"""
        self.navigation_requested.emit("new_audit")
        self.status_label.setText("جاري بدء مراجعة جديدة...")
        
    def _import_data(self):
        """استيراد بيانات"""
        self.navigation_requested.emit("import_data")
        self.status_label.setText("جاري استيراد البيانات...")
        
    def _export_report(self):
        """تصدير تقرير"""
        self.report_generated.emit("pdf")
        self.status_label.setText("جاري تصدير التقرير...")
        
    def _open_settings(self):
        """فتح نافذة الإعدادات"""
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec()
        
    def _run_all_agents(self):
        """تشغيل جميع الوكلاء"""
        self.status_label.setText("جاري تشغيل جميع الوكلاء...")
        # سيتم تنفيذ هذا عبر خدمة تنسيق الذكاء الاصطناعي
        
    @Slot(dict)
    def _on_audit_started(self, audit_info: dict):
        """عند بدء مراجعة"""
        self.status_label.setText(f"مراجعة جارية: {audit_info.get('name', 'غير معروف')}")
        self.agents_status.setText("الوكلاء: نشط")
        
    @Slot(str)
    def _on_report_ready(self, report_path: str):
        """عند جاهزية تقرير"""
        self.status_label.setText(f"تقرير جاهز: {report_path}")
        self.stack.setCurrentIndex(3)  # الانتقال لصفحة التقارير
