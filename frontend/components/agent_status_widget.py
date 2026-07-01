from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QFrame, QProgressBar, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt
from typing import Dict

from frontend.styles.design_system import Color


class AgentStatusWidget(QFrame):
    STATUS_COLORS = {
        "idle": Color.TEXT_SECONDARY,
        "running": Color.INFO,
        "completed": Color.SUCCESS,
        "error": Color.ERROR,
        "warning": Color.WARNING,
    }

    def __init__(self, agent_name: str, agent_id: str = ""):
        super().__init__()
        self.agent_name = agent_name
        self.agent_id = agent_id
        self.status = "idle"
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setObjectName("agentCard")
        self.setMinimumHeight(100)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)

        header = QHBoxLayout()
        self.name_label = QLabel(self.agent_name)
        self.name_label.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {Color.TEXT_PRIMARY};")
        header.addWidget(self.name_label)
        header.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet(f"font-size: 18px; color: {self._get_status_color()};")
        header.addWidget(self.status_dot)

        self.status_label = QLabel("IDLE")
        self.status_label.setStyleSheet(f"font-size: 11px; color: {Color.TEXT_SECONDARY}; font-weight: 500;")
        header.addWidget(self.status_label)

        layout.addLayout(header)

        if self.agent_id:
            id_label = QLabel(f"ID: {self.agent_id}")
            id_label.setStyleSheet(f"font-size: 11px; color: {Color.TEXT_MUTED};")
            layout.addWidget(id_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setMinimumHeight(6)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none; border-radius: 3px;
                background-color: {Color.BG_LIGHT}; height: 6px;
                text-align: center; font-size: 10px;
            }}
            QProgressBar::chunk {{
                background-color: {self._get_status_color()}; border-radius: 3px;
            }}
        """)
        layout.addWidget(self.progress_bar)

        stats = QHBoxLayout()
        self.tasks_label = QLabel("Tasks: 0")
        self.tasks_label.setStyleSheet(f"font-size: 11px; color: {Color.TEXT_SECONDARY};")
        stats.addWidget(self.tasks_label)
        stats.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.last_run_label = QLabel("Last run: Never")
        self.last_run_label.setStyleSheet(f"font-size: 11px; color: {Color.TEXT_MUTED};")
        stats.addWidget(self.last_run_label)
        layout.addLayout(stats)

    def _get_status_color(self) -> str:
        return self.STATUS_COLORS.get(self.status, self.STATUS_COLORS["idle"])

    def _apply_style(self):
        self.setStyleSheet(f"""
            QFrame#agentCard {{
                background-color: {Color.BG_CARD};
                border-radius: 10px;
                padding: 10px;
                border: 1px solid {Color.BORDER};
            }}
            QFrame#agentCard:hover {{
                border: 1px solid {Color.PRIMARY};
            }}
        """)

    def set_status(self, status: str, progress: int = 0):
        self.status = status
        color = self._get_status_color()
        self.status_dot.setStyleSheet(f"font-size: 18px; color: {color};")
        self.status_label.setText(status.upper())
        self.status_label.setStyleSheet(f"font-size: 11px; color: {color}; font-weight: 500;")
        self.progress_bar.setValue(progress)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none; border-radius: 3px;
                background-color: {Color.BG_LIGHT}; height: 6px;
                text-align: center; font-size: 10px;
            }}
            QProgressBar::chunk {{
                background-color: {color}; border-radius: 3px;
            }}
        """)

    def set_tasks_count(self, count: int):
        self.tasks_label.setText(f"Tasks: {count}")

    def set_last_run(self, timestamp: str):
        self.last_run_label.setText(f"Last run: {timestamp}")


class AgentsDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.agent_widgets: Dict[str, AgentStatusWidget] = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("AI Agents Status")
        title_label.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {Color.TEXT_PRIMARY};")
        layout.addWidget(title_label)

        self.agents_container = QWidget()
        self.agents_layout = QVBoxLayout(self.agents_container)
        self.agents_layout.setSpacing(8)
        self.agents_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.agents_container)

        summary_frame = QFrame()
        summary_frame.setObjectName("summaryBar")
        summary_frame.setStyleSheet(f"""
            QFrame#summaryBar {{
                background-color: {Color.BG_MEDIUM};
                border: 1px solid {Color.BORDER};
                border-radius: 8px;
                padding: 12px 16px;
            }}
        """)
        summary_layout = QHBoxLayout(summary_frame)
        summary_layout.setSpacing(24)

        self.total_agents_label = QLabel("Total: 0")
        self.total_agents_label.setStyleSheet(f"font-size: 12px; color: {Color.TEXT_SECONDARY};")
        summary_layout.addWidget(self.total_agents_label)

        self.running_label = QLabel("Running: 0")
        self.running_label.setStyleSheet(f"font-size: 12px; color: {Color.INFO};")
        summary_layout.addWidget(self.running_label)

        self.completed_label = QLabel("Completed: 0")
        self.completed_label.setStyleSheet(f"font-size: 12px; color: {Color.SUCCESS};")
        summary_layout.addWidget(self.completed_label)

        self.error_label = QLabel("Errors: 0")
        self.error_label.setStyleSheet(f"font-size: 12px; color: {Color.ERROR};")
        summary_layout.addWidget(self.error_label)

        summary_layout.addStretch()
        layout.addWidget(summary_frame)

    def add_agent(self, agent_name: str, agent_id: str = "") -> AgentStatusWidget:
        agent_widget = AgentStatusWidget(agent_name, agent_id)
        self.agent_widgets[agent_name] = agent_widget
        self.agents_layout.addWidget(agent_widget)
        self._update_summary()
        return agent_widget

    def update_agent_status(self, agent_name: str, status: str, progress: int = 0):
        if agent_name in self.agent_widgets:
            self.agent_widgets[agent_name].set_status(status, progress)
            self._update_summary()

    def _update_summary(self):
        total = len(self.agent_widgets)
        running = sum(1 for w in self.agent_widgets.values() if w.status == "running")
        completed = sum(1 for w in self.agent_widgets.values() if w.status == "completed")
        errors = sum(1 for w in self.agent_widgets.values() if w.status == "error")
        self.total_agents_label.setText(f"Total: {total}")
        self.running_label.setText(f"Running: {running}")
        self.completed_label.setText(f"Completed: {completed}")
        self.error_label.setText(f"Errors: {errors}")
