"""
Finovate Audit Nexus AI - Agents Manager Component
مكون إدارة الوكلاء الذكية

Provides interface for managing and configuring AI agents.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QPushButton, QScrollArea,
    QComboBox, QCheckBox, QLineEdit, QTextEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class AgentsManager(QWidget):
    """
    Agents Manager Component
    Provides interface to manage all 22 AI agents
    """
    
    agent_status_changed = Signal(str, bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إدارة الوكلاء الذكية")
        self.agents = {}
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """Initialize the UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Search and Filter
        search_section = self.create_search_section()
        main_layout.addWidget(search_section)
        
        # Agents Grid
        agents_scroll = QScrollArea()
        agents_scroll.setWidgetResizable(True)
        agents_widget = self.create_agents_grid()
        agents_scroll.setWidget(agents_widget)
        main_layout.addWidget(agents_scroll)
        
    def create_header(self) -> QWidget:
        """Create header section"""
        header = QWidget()
        layout = QHBoxLayout(header)
        
        title = QLabel("🤖 إدارة الوكلاء الذكية")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        
        stats_label = QLabel("الوكلاء النشطين: 22/22")
        stats_label.setFont(QFont("Arial", 12))
        stats_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(stats_label)
        
        return header
    
    def create_search_section(self) -> QWidget:
        """Create search and filter section"""
        search_widget = QWidget()
        layout = QHBoxLayout(search_widget)
        layout.setContentsMargins(0, 10, 0, 10)
        
        search_label = QLabel("🔍 بحث:")
        search_input = QLineEdit()
        search_input.setPlaceholderText("ابحث عن وكيل...")
        search_input.setMinimumWidth(300)
        
        filter_label = QLabel("تصفية حسب:")
        filter_combo = QComboBox()
        filter_combo.addItems(["الكل", "نشط", "غير نشط", "حسب النوع"])
        
        layout.addWidget(search_label)
        layout.addWidget(search_input)
        layout.addWidget(filter_label)
        layout.addWidget(filter_combo)
        layout.addStretch()
        
        return search_widget
    
    def create_agents_grid(self) -> QWidget:
        """Create grid of agent cards"""
        grid_widget = QWidget()
        layout = QGridLayout(grid_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 10, 0, 10)
        
        # List of all 22 agents
        agents_list = [
            ("📊 FinancialAgent", "وكيل التحليل المالي", "active"),
            ("⚖️ ComplianceAgent", "وكيل الامتثال", "active"),
            ("🔍 AuditAgent", "وكيل التدقيق", "active"),
            ("📄 DocumentAgent", "وكيل المستندات", "active"),
            ("🔐 SecurityAgent", "وكيل الأمان", "active"),
            ("🤖 MLAgent", "وكيل التعلم الآلي", "active"),
            ("📈 RiskAgent", "وكيل المخاطر", "active"),
            ("💰 TaxAgent", "وكيل الضرائب", "active"),
            ("🌐 ERPConnector", "متصل ERP", "active"),
            ("📝 ReportAgent", "وكيل التقارير", "active"),
            ("🔎 FraudAgent", "وكيل كشف الاحتيال", "active"),
            ("📉 AnalyticsAgent", "وكيل التحليلات", "active"),
            ("🗂️ DataAgent", "وكيل البيانات", "active"),
            ("🔄 WorkflowAgent", "وكيل سير العمل", "active"),
            ("💬 ChatAgent", "وكيل الدردشة", "active"),
            ("📅 ScheduleAgent", "وكيل الجدولة", "active"),
            ("🔔 NotificationAgent", "وكيل الإشعارات", "active"),
            ("👥 UserAgent", "وكيل المستخدمين", "active"),
            ("⚙️ ConfigAgent", "وكيل الإعدادات", "active"),
            ("📊 DashboardAgent", "وكيل لوحة المعلومات", "active"),
            ("🧠 KnowledgeAgent", "وكيل المعرفة", "active"),
            ("🎯 StrategyAgent", "وكيل الاستراتيجية", "active"),
        ]
        
        row = 0
        col = 0
        max_cols = 2
        
        for agent_id, name, status in agents_list:
            card = self.create_agent_card(agent_id, name, status)
            layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        return grid_widget
    
    def create_agent_card(self, agent_id: str, name: str, status: str) -> QFrame:
        """Create individual agent card"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        
        is_active = status == "active"
        color = "#27ae60" if is_active else "#95a5a6"
        
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border-left: 4px solid {color};
                padding: 15px;
            }}
            QFrame:hover {{
                background-color: #f8f9fa;
                border-left: 4px solid #3498db;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        # Agent ID and Status
        id_label = QLabel(agent_id)
        id_label.setFont(QFont("Arial", 10, QFont.Bold))
        id_label.setStyleSheet("color: #7f8c8d;")
        
        # Agent Name
        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        name_label.setStyleSheet("color: #2c3e50;")
        
        # Status Indicator
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        
        status_dot = QLabel("●")
        status_dot.setStyleSheet(f"color: {color}; font-size: 14px;")
        
        status_text = QLabel("نشط" if is_active else "غير نشط")
        status_text.setFont(QFont("Arial", 9))
        status_text.setStyleSheet(f"color: {color};")
        
        status_layout.addWidget(status_dot)
        status_layout.addWidget(status_text)
        status_layout.addStretch()
        
        # Controls
        controls = QWidget()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        toggle_btn = QPushButton("تعطيل" if is_active else "تفعيل")
        toggle_btn.setCursor(Qt.PointingHandCursor)
        toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 10px;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        
        config_btn = QPushButton("⚙️ إعدادات")
        config_btn.setCursor(Qt.PointingHandCursor)
        config_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 10px;
            }
            QPushButton:hover {
                opacity: 0.8;
            }
        """)
        
        controls_layout.addWidget(toggle_btn)
        controls_layout.addWidget(config_btn)
        
        layout.addWidget(id_label)
        layout.addWidget(name_label)
        layout.addWidget(status_widget)
        layout.addWidget(controls)
        
        return card
    
    def setup_styles(self):
        """Apply styles"""
        self.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
        """)
    
    def toggle_agent(self, agent_id: str, active: bool):
        """Toggle agent status"""
        self.agent_status_changed.emit(agent_id, active)
        print(f"Agent {agent_id} toggled: {'active' if active else 'inactive'}")
