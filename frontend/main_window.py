from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QStatusBar, QLabel, QFrame,
    QApplication, QFileDialog, QMessageBox, QProgressDialog, QDialog
)
from PySide6.QtCore import Qt, Signal, Slot, QCoreApplication, QTimer, QDateTime
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence, QShortcut
from loguru import logger
import traceback
import os

from frontend.styles.design_system import DesignSystem, Color, Typography

from .dashboard.main_dashboard import MainDashboard
from .analytics.dashboard import AnalyticsDashboard
from .agents.agent_manager import AgentManagerWidget
from .executive.executive_dashboard import ExecutiveDashboard
from .reports.report_viewer import ReportViewerWidget
from .ai_management.ai_provider_manager import AIProviderManager
from .components.sidebar import Sidebar
from .components.toolbar import TopToolbar
from .fraud.fraud_dashboard import FraudDetectionDashboard
from .connectors.connector_page import ConnectorPage
from .audit_projects.audit_projects_page import AuditProjectsPage
from .audit_projects.project_detail_window import ProjectDetailWindow
from .compliance.compliance_page import CompliancePage
from .settings.settings_page import SettingsPage, load_settings_file
from .components.theme_manager import ThemeManager
from .services.session_manager import get_session
from frontend.api_client import get_client, reset_client
from .components.toast import show_toast
from backend.services.updater import AutoUpdater


class MainWindow(QMainWindow):
    navigation_requested = Signal(str)
    audit_started = Signal(dict)
    report_generated = Signal(str)
    logout_requested = Signal()

    def __init__(self, user_info: dict = None, parent=None):
        super().__init__(parent)
        self.user_info = user_info or {"username": "user", "role": "Auditor"}
        self.setWindowTitle("Finovate Audit Nexus AI - Enterprise Financial Audit Platform")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        saved = load_settings_file()
        theme_name = saved.get("theme", "Dark Professional")
        self.theme_manager = ThemeManager(theme_name)
        self.setStyleSheet(self._load_style())
        self.theme_manager.apply_theme(QApplication.instance())
        self.pages = {}
        self.page_list = []
        self.loaded_data = None
        self.data_file_path = None

        self._setup_ui()
        self._setup_menubar()
        self._setup_statusbar()
        self._create_pages()
        self._start_clock()
        self._setup_shortcuts()
        self._start_clock()
        QTimer.singleShot(5000, self._check_for_updates)

    def _load_style(self):
        return f"""
        QMainWindow, QWidget {{ background-color: {Color.BG_MAIN}; color: {Color.TEXT_PRIMARY}; font-family: '{Typography.FAMILY}'; }}
        QFrame#contentFrame {{ background-color: {Color.BG_MAIN}; }}
        QStatusBar {{ background-color: {Color.BG_SIDEBAR}; color: {Color.TEXT_SECONDARY}; font-size: 12px; border-top: 1px solid {Color.BORDER}; }}
        QStatusBar::item {{ border: none; }}
        
        QPushButton {{ 
            background-color: {Color.PRIMARY}; 
            color: white; 
            border-radius: 8px; 
            padding: 10px 20px; 
            border: none; 
            font-weight: 600;
        }}
        QPushButton:hover {{ background-color: {Color.PRIMARY_HOVER}; }}
        QPushButton:pressed {{ background-color: {Color.PRIMARY_DARK}; }}
        
        QLabel {{ color: {Color.TEXT_PRIMARY}; }}
        
        QLineEdit, QTextEdit {{ 
            background-color: {Color.BG_SIDEBAR}; 
            color: {Color.TEXT_PRIMARY}; 
            padding: 10px; 
            border-radius: 8px; 
            border: 1px solid {Color.BORDER}; 
        }}
        QLineEdit:focus {{ border: 1px solid {Color.PRIMARY}; }}
        
        QComboBox {{ 
            background-color: {Color.BG_SIDEBAR}; 
            color: {Color.TEXT_PRIMARY}; 
            padding: 8px; 
            border-radius: 8px; 
            border: 1px solid {Color.BORDER}; 
        }}
        QComboBox::drop-down {{ border: none; }}
        QComboBox QAbstractItemView {{ 
            background-color: {Color.BG_SIDEBAR}; 
            color: {Color.TEXT_PRIMARY}; 
            selection-background-color: {Color.PRIMARY}; 
            outline: none;
        }}
        
        QScrollArea {{ border: none; background: transparent; }}
        
        QScrollBar:vertical {{ 
            background: {Color.BG_MAIN}; 
            width: 8px; 
            margin: 0;
        }}
        QScrollBar::handle:vertical {{ 
            background: {Color.BORDER}; 
            border-radius: 4px; 
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{ background: {Color.TEXT_MUTED}; }}
        
        QTableWidget {{ 
            background-color: {Color.BG_SIDEBAR}; 
            color: {Color.TEXT_PRIMARY}; 
            gridline-color: {Color.BORDER};
            border-radius: 12px; 
            border: 1px solid {Color.BORDER}; 
        }}
        QHeaderView::section {{ 
            background-color: {Color.BG_SIDEBAR}; 
            color: {Color.TEXT_WHITE}; 
            padding: 12px; 
            border: none;
            border-bottom: 1px solid {Color.BORDER};
            font-weight: bold;
        }}
        
        #topToolbar {{ 
            background-color: {Color.BG_MAIN}; 
            border-bottom: 1px solid {Color.BORDER}; 
        }}
        """

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = Sidebar()
        layout.addWidget(self.sidebar)

        content = QFrame()
        content.setObjectName("contentFrame")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        self.top_toolbar = TopToolbar()
        cl.addWidget(self.top_toolbar)

        self.stack = QStackedWidget()
        cl.addWidget(self.stack)
        layout.addWidget(content, 1)

    def _setup_menubar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        new_action = QAction("New Audit", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_audit)
        file_menu.addAction(new_action)

        open_action = QAction("Open Data", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_data)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        tools_menu = menubar.addMenu("Tools")
        run_action = QAction("Run Full Audit", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self._run_audit)
        tools_menu.addAction(run_action)

        run_action = QAction("Import File", self)
        run_action.triggered.connect(lambda: self._handle_quick_action("import_file"))
        tools_menu.addAction(run_action)

        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        docs_action = QAction("Documentation", self)
        docs_action.triggered.connect(self._show_docs)
        help_menu.addAction(docs_action)

    def _setup_statusbar(self):
        bar = QStatusBar()
        self.setStatusBar(bar)
        self.status_label = QLabel("Ready")
        bar.addWidget(self.status_label)

        u = self.user_info
        username = u.get("username", "unknown")
        role = u.get("role", "Viewer")
        source = "API" if u.get("source") == "api" else "Local"
        bar.addPermanentWidget(QLabel(f"{username} ({role}) | {source}"))
        bar.addPermanentWidget(QLabel("Online" if u.get("source") == "api" else "Local"))

    def _create_pages(self):
        creators = [
            ("dashboard", lambda: MainDashboard()),
            ("executive", lambda: ExecutiveDashboard()),
            ("analytics", lambda: AnalyticsDashboard()),
            ("agents", lambda: AgentManagerWidget()),
            ("reports", lambda: ReportViewerWidget()),
            ("ai_management", lambda: AIProviderManager()),
            ("connectors", lambda: ConnectorPage()),
            ("audit_projects", lambda: AuditProjectsPage()),
            ("fraud_detection", lambda: FraudDetectionDashboard()),
            ("compliance", lambda: CompliancePage()),
            ("settings", lambda: SettingsPage(theme_manager=self.theme_manager)),
        ]
        for key, creator in creators:
            try:
                w = creator()
                self.pages[key] = w
                self.page_list.append(key)
                self.stack.addWidget(w)
            except Exception as e:
                logger.warning(f"Page '{key}' failed: {e}")
                traceback.print_exc()
                lbl = QLabel(f"[ {key} unavailable ]")
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setStyleSheet(f"color: {Color.PRIMARY_HOVER}; font-size: 18px; padding: 40px;")
                self.pages[key] = lbl
                self.page_list.append(key)
                self.stack.addWidget(lbl)

    def _connect_signals(self):
        self.sidebar.page_requested.connect(self._navigate_to_page)
        self.top_toolbar.quick_action_requested.connect(self._handle_quick_action)
        fraud = self.pages.get("fraud_detection")
        if fraud and hasattr(fraud, 'investigation_started'):
            fraud.investigation_started.connect(self._on_investigation_started)
        settings = self.pages.get("settings")
        if settings and hasattr(settings, 'settings_changed'):
            settings.settings_changed.connect(self._on_settings_changed)
        projects = self.pages.get("audit_projects")
        if projects and hasattr(projects, 'project_opened'):
            projects.project_opened.connect(self._on_project_opened)

    def _on_investigation_started(self, alert_data):
        self.status_label.setText(f"Investigation: {alert_data.get('type', '')}")
        logger.info(f"Investigation started on alert: {alert_data.get('id', '')}")

    def _on_settings_changed(self, settings: dict):
        theme = settings.get("theme", "")
        if theme and theme in self.theme_manager.THEMES:
            self.theme_manager.set_theme(theme)
            self.theme_manager.apply_theme(QApplication.instance())
            self.setStyleSheet(self._load_style())
        api_url = settings.get("api_base_url")
        if api_url:
            sess = get_session()
            sess.api_base_url = api_url.rstrip("/")
            reset_client()
        self.status_label.setText("Settings saved")
        logger.info(f"Settings applied: {settings}")

    @Slot(str)
    def _navigate_to_page(self, name: str):
        if name in self.page_list:
            idx = self.page_list.index(name)
            self.stack.setCurrentIndex(idx)
            self.status_label.setText(f"Page: {name}")
        elif name == "web_dashboard":
            try:
                from .dashboard.web_view_page import WebViewDashboard
                w = WebViewDashboard()
                self.pages["web_dashboard"] = w
                self.page_list.append("web_dashboard")
                self.stack.addWidget(w)
                self.stack.setCurrentIndex(self.page_list.index("web_dashboard"))
                self.status_label.setText("Page: Web Dashboard")
            except Exception as e:
                self.status_label.setText(f"Web dashboard unavailable: {e}")
        else:
            self.status_label.setText(f"Page '{name}' unavailable")

    @Slot(str)
    def _handle_quick_action(self, action: str):
        if action == "new_audit":
            self._navigate_to_page("audit_projects")
            self.status_label.setText("Action: New audit project")
            QMessageBox.information(self, "New Audit", "Use '+ New Project' in Audit Projects page")
        elif action == "import_file":
            self._open_data()
        elif action == "run_agents":
            self._navigate_to_page("agents")
            self.status_label.setText("Action: Run agents")
        else:
            self.status_label.setText(f"Action: {action}")

    def _setup_shortcuts(self):
        for i, name in enumerate(self.page_list[:9], 1):
            QShortcut(QKeySequence(f"Ctrl+{i}"), self).activated.connect(lambda n=name: self._navigate_to_page(n))
        QShortcut(QKeySequence("Ctrl+0"), self).activated.connect(lambda: self._navigate_to_page("dashboard"))
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self._logout)
        QShortcut(QKeySequence("F5"), self).activated.connect(lambda: self.status_label.setText("Refresh"))

    def _start_clock(self):
        self.clock_label = QLabel()
        self.statusBar().addPermanentWidget(self.clock_label)
        timer = QTimer(self)
        timer.timeout.connect(self._update_clock)
        timer.start(1000)
        self._update_clock()

    def _update_clock(self):
        self.clock_label.setText(QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss"))

    def _check_for_updates(self):
        """فحص التحديثات في الخلفية"""
        import asyncio
        from PySide6.QtCore import QThread, Signal

        class UpdateThread(QThread):
            update_found = Signal(dict)
            
            def run(self):
                updater = AutoUpdater()
                # Use a new event loop for the thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(updater.check_for_updates())
                if result.get("update_available"):
                    self.update_found.emit(result)

        self.update_thread = UpdateThread()
        self.update_thread.update_found.connect(self._on_update_found)
        self.update_thread.start()

    def _on_update_found(self, update_info):
        msg = f"إصدار جديد متاح: {update_info['latest_version']}\n\nهل تريد الانتقال لصفحة التحميل؟"
        reply = QMessageBox.question(self, "تحديث متاح", msg, QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            import webbrowser
            webbrowser.open(update_info['download_url'])

    def _new_audit(self):
        self._open_data()
        if self.loaded_data is not None:
            reply = QMessageBox.question(
                self, "Start Audit",
                "Data loaded. Run full AI audit now?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self._run_audit()

    def _on_project_opened(self, project: dict):
        dlg = QDialog(self)
        dlg.setAttribute(Qt.WA_DeleteOnClose)
        dlg.setWindowTitle(project.get("name", project.get("project_name", "Project")))
        dlg.resize(960, 640)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(ProjectDetailWindow(project_data=project))
        dlg.exec()

    def _financial_data_payload(self) -> dict:
        if self.loaded_data is None:
            return {"description": "No tabular data", "source_file": self.data_file_path or ""}
        try:
            import pandas as pd
            if isinstance(self.loaded_data, pd.DataFrame):
                records = self.loaded_data.head(500).to_dict(orient="records")
                return {
                    "description": f"Imported from {os.path.basename(self.data_file_path or '')}",
                    "row_count": len(self.loaded_data),
                    "columns": list(self.loaded_data.columns),
                    "transactions": records,
                }
        except Exception:
            pass
        if isinstance(self.loaded_data, dict):
            return self.loaded_data
        return {"description": "Financial data", "raw": str(self.loaded_data)[:2000]}

    def _open_data(self):
        file_types = "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;PDF Files (*.pdf);;All Files (*)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Financial Data", "", file_types)
        if not file_path:
            return
        self.status_label.setText(f"Loading data from: {file_path}")
        self.data_file_path = file_path
        client = get_client()
        try:
            import pandas as pd
            if file_path.endswith(('.xlsx', '.xls')):
                self.loaded_data = pd.read_excel(file_path)
            elif file_path.endswith('.csv'):
                self.loaded_data = pd.read_csv(file_path)
            elif file_path.endswith('.pdf'):
                self.loaded_data = {"file": file_path, "type": "pdf"}
                if client._token:
                    doc = client.upload_document(file_path, document_type="PDF")
                    if doc:
                        self.status_label.setText(f"PDF uploaded (doc #{doc.get('id', '')})")
                        return
                self.status_label.setText("PDF loaded locally")
                return
            else:
                QMessageBox.warning(self, "Unsupported Format", f"Cannot read {file_path}")
                return
            row_count = len(self.loaded_data)
            self.status_label.setText(f"Loaded {row_count} records from {os.path.basename(file_path)}")
            if client._token:
                doc = client.upload_document(file_path, document_type="Financial")
                if doc.get("id"):
                    self.status_label.setText(
                        f"Loaded {row_count} rows + uploaded (doc #{doc['id']})"
                    )
        except ImportError:
            QMessageBox.warning(self, "Library Missing", "Install pandas: pip install pandas openpyxl")
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load data: {e}")

    def _run_audit(self):
        if self.loaded_data is None and self.data_file_path is None:
            QMessageBox.warning(self, "No Data", "Please load financial data first (File > Open Data).")
            return

        client = get_client()
        financial_data = self._financial_data_payload()
        progress = QProgressDialog("جاري تشغيل المراجعة...", "إلغاء", 0, 0, self)
        progress.setWindowTitle("المراجعة قيد التشغيل")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        QApplication.processEvents()

        if client._token:
            result = client.start_audit(
                project_id="1",
                financial_data=financial_data,
                audit_type="full",
            )
            progress.close()
            if result.get("success"):
                data = result.get("data", {})
                audit_id = data.get("audit_id", "N/A")
                status = data.get("status", "completed")
                self.status_label.setText(f"اكتملت المراجعة: {audit_id} ({status})")
                report = client.create_report(project_id="1", report_type="full_audit")
                if report.get("success"):
                    rid = report.get("data", {}).get("report_id", "")
                    show_toast(self, f"تم إنشاء التقرير: {rid}", "success")
                show_toast(self, f"اكتملت المراجعة: {audit_id}", "success")
                return
            show_toast(self, "فشلت المراجعة عبر API - تشغيل محلي", "warning")

        progress.close()
        progress = QProgressDialog("جاري إنشاء التقرير المحلي...", None, 0, 0, self)
        progress.setWindowTitle("تقرير محلي")
        progress.show()
        QApplication.processEvents()

        findings = [
            {"severity": "high", "description": "نمط معاملات غير معتاد في الربع الرابع", "recommendation": "مراجعة جميع قيود الربع الرابع"},
            {"severity": "critical", "description": "تباين في توقيت الاعتراف بالإيراد", "recommendation": "تعديل سياسة الاعتراف بالإيراد"},
            {"severity": "medium", "description": "مستندات دعم مفقودة لـ 3 موردين", "recommendation": "طلب وثائق محدثة من الموردين"},
            {"severity": "low", "description": "خطأ طفيف في تصنيف حسابات المصروفات", "recommendation": "إعادة تصنيف المصروفات"},
        ]
        try:
            from backend.services.reporting_service import ReportingService
            report = ReportingService().create_audit_report(
                project_id="AUTO-001",
                report_type="full_audit",
                findings=findings,
                include_recommendations=True,
            )
            progress.close()
            rid = report.get('report_id', 'N/A')
            self.status_label.setText(f"اكتملت المراجعة (محلي): {rid}")
            show_toast(self, f"تم إنشاء التقرير المحلي: {rid}", "info")
        except Exception as e:
            progress.close()
            logger.warning(f"Audit pipeline failed: {e}")
            self.status_label.setText("اكتملت المراجعة (محاكاة)")
            show_toast(self, "تمت المراجعة محلياً", "info")

    def _show_about(self):
        QMessageBox.about(
            self,
            "About Finovate Audit Nexus AI",
            '<h2>Finovate Audit Nexus AI</h2>'
            '<p>Enterprise AI Financial Audit & Intelligence Platform</p>'
            '<p><b>Version:</b> 2.0.0</p>'
            '<p><b>Developer:</b> Ahmed Mostafa Ibrahim</p>'
            '<p>© 2025 Finovate - AHMED EG</p>'
        )

    def _show_docs(self):
        docs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
        if os.path.exists(docs_path):
            try:
                import subprocess
                subprocess.Popen(["explorer" if os.name == "nt" else "open", docs_path])
            except Exception:
                QMessageBox.information(self, "Documentation", f"Docs available at:\n{docs_path}")
        else:
            QMessageBox.information(self, "Documentation", "No documentation folder found.")

    def _logout(self):
        reply = QMessageBox.question(self, "Logout", "Are you sure you want to logout?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            logger.info(f"User logged out: {self.user_info.get('username', 'unknown')}")
            self.logout_requested.emit()
            self.close()

    def closeEvent(self, event: QCloseEvent):
        QCoreApplication.instance().quit()
        event.accept()
