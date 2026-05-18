"""
Finovate Audit Nexus AI - Main Dashboard Window
Professional desktop interface for the AI Financial Audit Platform.
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                                QTabWidget, QLabel, QFrame, QScrollArea, QGridLayout,
                                QPushButton, QMenuBar, QMenu, QAction, QStatusBar,
                                QMessageBox, QFileDialog, QApplication)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon

from .components.theme_manager import ThemeManager
from .components.audit_card import AuditCard
from .components.risk_gauge import RiskGauge
from .components.financial_chart import FinancialChart
from .components.agent_status_widget import AgentsDashboard


class MainWindow(QMainWindow):
    """Main application window for Finovate Audit Nexus AI."""
    
    def __init__(self):
        super().__init__()
        
        self.theme_manager = ThemeManager("Dark Professional")
        self.setWindowTitle("Finovate Audit Nexus AI - Enterprise Financial Audit Platform")
        self.setMinimumSize(1400, 900)
        
        # Apply theme
        self.theme_manager.apply_theme(QApplication.instance())
        
        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        
        # Auto-refresh timer for live data
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_dashboard)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def setup_ui(self):
        """Setup the main UI components."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Tab widget for different views
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: transparent;
            }
            QTabBar::tab {
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
                background-color: #16213e;
                color: white;
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #0f3460;
            }
            QTabBar::tab:hover {
                background-color: #1a1a2e;
            }
        """)
        
        # Add tabs
        self.tabs.addTab(self.create_dashboard_tab(), "📊 Dashboard")
        self.tabs.addTab(self.create_agents_tab(), "🤖 AI Agents")
        self.tabs.addTab(self.create_reports_tab(), "📑 Reports")
        self.tabs.addTab(self.create_analytics_tab(), "📈 Analytics")
        self.tabs.addTab(self.create_settings_tab(), "⚙️ Settings")
        
        main_layout.addWidget(self.tabs)
    
    def create_header(self) -> QFrame:
        """Create the application header."""
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme_manager.get_color('surface')};
                border-bottom: 2px solid {self.theme_manager.get_color('primary')};
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 10, 30, 10)
        
        # Logo and title
        logo_label = QLabel("🔍")
        logo_label.setStyleSheet("font-size: 40px;")
        layout.addWidget(logo_label)
        
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setSpacing(2)
        
        title = QLabel("Finovate Audit Nexus AI")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #00ffff;")
        title_layout.addWidget(title)
        
        subtitle = QLabel("Enterprise AI Financial Audit & Intelligence Platform")
        subtitle.setStyleSheet("font-size: 14px; color: #a0a0a0;")
        title_layout.addWidget(subtitle)
        
        layout.addWidget(title_container)
        
        layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Quick action buttons
        new_audit_btn = QPushButton("➕ New Audit")
        new_audit_btn.setFixedSize(140, 40)
        layout.addWidget(new_audit_btn)
        
        export_btn = QPushButton("📤 Export")
        export_btn.setFixedSize(120, 40)
        layout.addWidget(export_btn)
        
        return header
    
    def create_dashboard_tab(self) -> QWidget:
        """Create the main dashboard tab."""
        dashboard = QWidget()
        layout = QVBoxLayout(dashboard)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # KPI Cards Row
        kpi_container = QWidget()
        kpi_layout = QGridLayout(kpi_container)
        kpi_layout.setSpacing(15)
        
        # Create KPI cards
        self.total_transactions_card = AuditCard(
            title="Total Transactions",
            subtitle="This Period",
            value="0",
            status="normal",
            theme_manager=self.theme_manager
        )
        
        self.risk_score_card = AuditCard(
            title="Overall Risk Score",
            subtitle="AI Assessment",
            value="0/100",
            status="success",
            theme_manager=self.theme_manager
        )
        
        self.fraud_alerts_card = AuditCard(
            title="Fraud Alerts",
            subtitle="Detected Issues",
            value="0",
            status="success",
            theme_manager=self.theme_manager
        )
        
        self.compliance_card = AuditCard(
            title="Compliance Score",
            subtitle="Regulatory Adherence",
            value="0%",
            status="normal",
            theme_manager=self.theme_manager
        )
        
        kpi_layout.addWidget(self.total_transactions_card, 0, 0)
        kpi_layout.addWidget(self.risk_score_card, 0, 1)
        kpi_layout.addWidget(self.fraud_alerts_card, 0, 2)
        kpi_layout.addWidget(self.compliance_card, 0, 3)
        
        layout.addWidget(kpi_container)
        
        # Risk Gauge and Summary
        summary_container = QWidget()
        summary_layout = QHBoxLayout(summary_container)
        summary_layout.setSpacing(20)
        
        # Risk gauge
        gauge_frame = QFrame()
        gauge_frame.setFrameShape(QFrame.StyledPanel)
        gauge_layout = QVBoxLayout(gauge_frame)
        
        self.risk_gauge = RiskGauge(
            value=0,
            min_value=0,
            max_value=100,
            label="Risk Level",
            theme_manager=self.theme_manager
        )
        self.risk_gauge.setMinimumSize(250, 250)
        gauge_layout.addWidget(self.risk_gauge, alignment=Qt.AlignCenter)
        
        summary_layout.addWidget(gauge_frame)
        
        # Summary text
        summary_text = QFrame()
        summary_text.setFrameShape(QFrame.StyledPanel)
        text_layout = QVBoxLayout(summary_text)
        
        summary_title = QLabel("Executive Summary")
        summary_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        text_layout.addWidget(summary_title)
        
        self.summary_content = QLabel("""
            <p>Welcome to Finovate Audit Nexus AI.</p>
            <p>To begin an audit:</p>
            <ul>
                <li>Upload financial data (Excel, CSV, PDF)</li>
                <li>Connect to your ERP system</li>
                <li>Select audit modules to run</li>
                <li>Review AI-generated insights</li>
            </ul>
            <p><b>Status:</b> Ready to audit</p>
        """)
        self.summary_content.setWordWrap(True)
        self.summary_content.setStyleSheet("font-size: 14px; line-height: 1.6;")
        text_layout.addWidget(self.summary_content)
        
        text_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        summary_layout.addWidget(summary_text, stretch=1)
        
        layout.addWidget(summary_container)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(dashboard)
        
        return dashboard
    
    def create_agents_tab(self) -> QWidget:
        """Create the AI agents management tab."""
        agents_widget = QWidget()
        layout = QVBoxLayout(agents_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.agents_dashboard = AgentsDashboard(self.theme_manager)
        layout.addWidget(self.agents_dashboard)
        
        # Initialize with some agents
        agent_names = [
            "Chief Audit Agent",
            "Journal Entry Agent",
            "General Ledger Agent",
            "Trial Balance Agent",
            "Financial Statements Agent",
            "Tax Compliance Agent",
            "Fraud Detection Agent",
            "Bank & Treasury Agent"
        ]
        
        for name in agent_names:
            self.agents_dashboard.add_agent(name)
        
        return agents_widget
    
    def create_reports_tab(self) -> QWidget:
        """Create the reports tab."""
        reports_widget = QWidget()
        layout = QVBoxLayout(reports_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        placeholder = QLabel("📑 Reports will appear here after running audits.\n\nSupported formats: PDF, Excel, Word, HTML")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("font-size: 18px; color: gray;")
        layout.addWidget(placeholder)
        
        return reports_widget
    
    def create_analytics_tab(self) -> QWidget:
        """Create the analytics tab."""
        analytics_widget = QWidget()
        layout = QVBoxLayout(analytics_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        placeholder = QLabel("📈 Financial analytics charts will be displayed here.\n\nConnect data to see trends, ratios, and predictions.")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("font-size: 18px; color: gray;")
        layout.addWidget(placeholder)
        
        return analytics_widget
    
    def create_settings_tab(self) -> QWidget:
        """Create the settings tab."""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Theme selection
        theme_label = QLabel("Select Theme:")
        theme_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(theme_label)
        
        theme_buttons = QWidget()
        theme_layout = QHBoxLayout(theme_buttons)
        theme_layout.setSpacing(10)
        
        themes = ["Dark Professional", "Light Enterprise", "Neon Finance", "Glassmorphism"]
        for theme in themes:
            btn = QPushButton(theme)
            btn.clicked.connect(lambda checked, t=theme: self.change_theme(t))
            theme_layout.addWidget(btn)
        
        layout.addWidget(theme_buttons)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Developer info
        dev_info = QLabel("""
            <h3>About Finovate Audit Nexus AI</h3>
            <p><b>Version:</b> 1.0.0</p>
            <p><b>Developer:</b> Ahmed Mostafa Ibrahim</p>
            <p><b>Email:</b> gogom8870@gmail.com</p>
            <p><b>Phone:</b> 01225155329</p>
            <p><b>Copyright:</b> © 2025 Finovate – AHMED EG</p>
        """)
        dev_info.setWordWrap(True)
        layout.addWidget(dev_info)
        
        return settings_widget
    
    def setup_menu(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Audit", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_audit)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open Data", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_data)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        run_audit_action = QAction("Run Full Audit", self)
        run_audit_action.setShortcut("F5")
        run_audit_action.triggered.connect(self.run_audit)
        tools_menu.addAction(run_audit_action)
        
        tools_menu.addSeparator()
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(lambda: self.tabs.setCurrentIndex(4))
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        docs_action = QAction("Documentation", self)
        docs_action.triggered.connect(self.show_docs)
        help_menu.addAction(docs_action)
    
    def setup_statusbar(self):
        """Setup the status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready | AI Engine: Online | Database: Connected")
    
    def change_theme(self, theme_name: str):
        """Change the application theme."""
        try:
            self.theme_manager.set_theme(theme_name)
            self.theme_manager.apply_theme(QApplication.instance())
            self.statusbar.showMessage(f"Theme changed to: {theme_name}")
        except Exception as e:
            QMessageBox.warning(self, "Theme Error", f"Could not change theme: {str(e)}")
    
    def new_audit(self):
        """Start a new audit."""
        QMessageBox.information(self, "New Audit", "New Audit wizard will open here.\n(Feature under development)")
    
    def open_data(self):
        """Open financial data files."""
        file_types = "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;PDF Files (*.pdf);;All Files (*)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Financial Data", "", file_types)
        
        if file_path:
            self.statusbar.showMessage(f"Loading data from: {file_path}")
            # TODO: Implement data loading logic
    
    def run_audit(self):
        """Run full audit process."""
        QMessageBox.information(self, "Running Audit", "Full audit process initiated.\nThis may take several minutes.\n(Feature under development)")
    
    def refresh_dashboard(self):
        """Refresh dashboard data."""
        # TODO: Implement real-time data refresh
        pass
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Finovate Audit Nexus AI",
            """<h2>Finovate Audit Nexus AI</h2>
            <p>Enterprise AI Financial Audit & Intelligence Platform</p>
            <p><b>Version:</b> 1.0.0</p>
            <p><b>Developer:</b> Ahmed Mostafa Ibrahim</p>
            <p><b>Email:</b> gogom8870@gmail.com</p>
            <p><b>Copyright:</b> © 2025 Finovate – AHMED EG</p>
            <p>Next-Generation AI Financial Audit Intelligence</p>"""
        )
    
    def show_docs(self):
        """Show documentation."""
        QMessageBox.information(
            self,
            "Documentation",
            "Documentation viewer will open here.\n(Feature under development)"
        )
