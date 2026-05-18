"""
Finovate Audit Nexus AI - Agent Status Widget Component
Widget for displaying real-time status of AI audit agents.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                QFrame, QProgressBar, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QTimer
from typing import Dict, List
from .theme_manager import ThemeManager


class AgentStatusWidget(QFrame):
    """Widget displaying the status of a single AI agent."""
    
    def __init__(self, agent_name: str, agent_id: str = "", theme_manager: ThemeManager = None):
        super().__init__()
        
        self.theme_manager = theme_manager or ThemeManager()
        self.agent_name = agent_name
        self.agent_id = agent_id
        self.status = "idle"  # idle, running, completed, error
        
        self.setup_ui()
        self.apply_style()
    
    def setup_ui(self):
        """Setup the widget UI."""
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setObjectName("agentCard")
        self.setMinimumHeight(100)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header row: Name + Status indicator
        header_layout = QHBoxLayout()
        
        self.name_label = QLabel(self.agent_name)
        self.name_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(self.name_label)
        
        header_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Status indicator
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet(f"font-size: 20px; color: {self.get_status_color()};")
        header_layout.addWidget(self.status_dot)
        
        self.status_label = QLabel("IDLE")
        self.status_label.setStyleSheet("font-size: 12px; color: gray;")
        header_layout.addWidget(self.status_label)
        
        layout.addLayout(header_layout)
        
        # Agent ID (if provided)
        if self.agent_id:
            id_label = QLabel(f"ID: {self.agent_id}")
            id_label.setStyleSheet("font-size: 11px; color: gray;")
            layout.addWidget(id_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setMinimumHeight(20)
        layout.addWidget(self.progress_bar)
        
        # Stats row
        stats_layout = QHBoxLayout()
        
        self.tasks_label = QLabel("Tasks: 0")
        self.tasks_label.setStyleSheet("font-size: 12px;")
        stats_layout.addWidget(self.tasks_label)
        
        stats_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        self.last_run_label = QLabel("Last run: Never")
        self.last_run_label.setStyleSheet("font-size: 11px; color: gray;")
        stats_layout.addWidget(self.last_run_label)
        
        layout.addLayout(stats_layout)
    
    def get_status_color(self) -> str:
        """Get color based on current status."""
        colors = {
            "idle": self.theme_manager.get_color("text_secondary"),
            "running": self.theme_manager.get_color("info"),
            "completed": self.theme_manager.get_color("success"),
            "error": self.theme_manager.get_color("error"),
            "warning": self.theme_manager.get_color("warning")
        }
        return colors.get(self.status, colors["idle"])
    
    def apply_style(self):
        """Apply widget styling."""
        self.setStyleSheet(f"""
            QFrame#agentCard {{
                background-color: {self.theme_manager.get_color('surface')};
                border-radius: 10px;
                padding: 10px;
                border: 1px solid {self.theme_manager.get_color('primary')};
            }}
            
            QFrame#agentCard:hover {{
                border: 2px solid {self.theme_manager.get_color('secondary')};
            }}
            
            QProgressBar {{
                border: none;
                border-radius: 5px;
                background-color: {self.theme_manager.get_color('background')};
                text-align: center;
            }}
            
            QProgressBar::chunk {{
                background-color: {self.get_status_color()};
                border-radius: 5px;
            }}
        """)
    
    def set_status(self, status: str, progress: int = 0):
        """Update agent status and progress."""
        self.status = status
        self.status_dot.setStyleSheet(f"font-size: 20px; color: {self.get_status_color()};")
        self.status_label.setText(status.upper())
        self.status_label.setStyleSheet(f"font-size: 12px; color: {self.get_status_color()};")
        self.progress_bar.setValue(progress)
        
        # Update progress bar color
        self.setStyleSheet(f"""
            QFrame#agentCard {{
                background-color: {self.theme_manager.get_color('surface')};
                border-radius: 10px;
                padding: 10px;
                border: 1px solid {self.theme_manager.get_color('primary')};
            }}
            
            QProgressBar {{
                border: none;
                border-radius: 5px;
                background-color: {self.theme_manager.get_color('background')};
                text-align: center;
            }}
            
            QProgressBar::chunk {{
                background-color: {self.get_status_color()};
                border-radius: 5px;
            }}
        """)
    
    def set_tasks_count(self, count: int):
        """Update tasks count."""
        self.tasks_label.setText(f"Tasks: {count}")
    
    def set_last_run(self, timestamp: str):
        """Update last run timestamp."""
        self.last_run_label.setText(f"Last run: {timestamp}")


class AgentsDashboard(QWidget):
    """Dashboard displaying all AI agents status."""
    
    def __init__(self, theme_manager: ThemeManager = None):
        super().__init__()
        
        self.theme_manager = theme_manager or ThemeManager()
        self.agent_widgets: Dict[str, AgentStatusWidget] = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("AI Agents Status")
        title_label.setObjectName("title")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        # Agents grid container
        self.agents_container = QWidget()
        self.agents_layout = QVBoxLayout(self.agents_container)
        self.agents_layout.setSpacing(10)
        self.agents_layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(self.agents_container)
        
        # Summary section
        summary_frame = QFrame()
        summary_frame.setFrameShape(QFrame.StyledPanel)
        summary_layout = QHBoxLayout(summary_frame)
        
        self.total_agents_label = QLabel("Total Agents: 0")
        summary_layout.addWidget(self.total_agents_label)
        
        summary_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        self.running_label = QLabel("Running: 0")
        summary_layout.addWidget(self.running_label)
        
        summary_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        self.completed_label = QLabel("Completed: 0")
        summary_layout.addWidget(self.completed_label)
        
        summary_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        self.error_label = QLabel("Errors: 0")
        summary_layout.addWidget(self.error_label)
        
        layout.addWidget(summary_frame)
    
    def add_agent(self, agent_name: str, agent_id: str = "") -> AgentStatusWidget:
        """Add an agent to the dashboard."""
        agent_widget = AgentStatusWidget(agent_name, agent_id, self.theme_manager)
        self.agent_widgets[agent_name] = agent_widget
        self.agents_layout.addWidget(agent_widget)
        
        self.update_summary()
        return agent_widget
    
    def update_agent_status(self, agent_name: str, status: str, progress: int = 0):
        """Update status of a specific agent."""
        if agent_name in self.agent_widgets:
            self.agent_widgets[agent_name].set_status(status, progress)
            self.update_summary()
    
    def update_summary(self):
        """Update the summary statistics."""
        total = len(self.agent_widgets)
        running = sum(1 for w in self.agent_widgets.values() if w.status == "running")
        completed = sum(1 for w in self.agent_widgets.values() if w.status == "completed")
        errors = sum(1 for w in self.agent_widgets.values() if w.status == "error")
        
        self.total_agents_label.setText(f"Total Agents: {total}")
        self.running_label.setText(f"Running: {running}")
        self.completed_label.setText(f"Completed: {completed}")
        self.error_label.setText(f"Errors: {errors}")
