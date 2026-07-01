from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel,
    QFrame, QSpacerItem, QSizePolicy, QLineEdit, QComboBox
)
from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QFont

from frontend.styles.design_system import Color


class TopToolbar(QWidget):
    quick_action_requested = Signal(str)
    search_requested = Signal(str)
    filter_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("topToolbar")
        self.setFixedHeight(60)
        self.setStyleSheet(f"""
            #topToolbar {{
                background-color: {Color.BG_MEDIUM};
                border-bottom: 1px solid {Color.BORDER};
            }}
        """)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 8, 16, 8)
        main_layout.setSpacing(10)

        self.btn_new_audit = QPushButton("+ New Audit")
        self.btn_new_audit.setObjectName("createButton")
        self.btn_new_audit.setFixedHeight(34)
        self.btn_new_audit.setCursor(Qt.PointingHandCursor)
        self.btn_new_audit.clicked.connect(lambda: self.quick_action_requested.emit("new_audit"))
        main_layout.addWidget(self.btn_new_audit)

        self.btn_import = QPushButton("Import")
        self.btn_import.setObjectName("primaryButton")
        self.btn_import.setFixedHeight(34)
        self.btn_import.setCursor(Qt.PointingHandCursor)
        self.btn_import.clicked.connect(lambda: self.quick_action_requested.emit("import_file"))
        main_layout.addWidget(self.btn_import)

        self.btn_run_agents = QPushButton("Run Agents")
        self.btn_run_agents.setObjectName("primaryButton")
        self.btn_run_agents.setFixedHeight(34)
        self.btn_run_agents.setCursor(Qt.PointingHandCursor)
        self.btn_run_agents.clicked.connect(lambda: self.quick_action_requested.emit("run_agents"))
        main_layout.addWidget(self.btn_run_agents)

        main_layout.addSpacerItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setMinimumWidth(240)
        self.search_input.setFixedHeight(34)
        self.search_input.returnPressed.connect(self._on_search)
        main_layout.addWidget(self.search_input)

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("All", "all")
        self.filter_combo.addItem("Active Audits", "active_audits")
        self.filter_combo.addItem("High Risk", "high_risks")
        self.filter_combo.addItem("Active Agents", "active_agents")
        self.filter_combo.addItem("Recent Reports", "recent_reports")
        self.filter_combo.setMinimumWidth(140)
        self.filter_combo.setFixedHeight(34)
        self.filter_combo.currentIndexChanged.connect(self._on_filter_changed)
        main_layout.addWidget(self.filter_combo)

        self.notif_btn = QPushButton("🔔")
        self.notif_btn.setFixedSize(36, 34)
        self.notif_btn.setCursor(Qt.PointingHandCursor)
        self.notif_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Color.BG_LIGHT};
                border: 1px solid {Color.BORDER};
                border-radius: 6px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {Color.BORDER};
            }}
        """)
        self.notif_btn.clicked.connect(self._show_notifications)
        main_layout.addWidget(self.notif_btn)

    @Slot()
    def _on_search(self):
        query = self.search_input.text().strip()
        if query:
            self.search_requested.emit(query)

    @Slot(int)
    def _on_filter_changed(self, index):
        filter_value = self.filter_combo.itemData(index)
        if filter_value:
            self.filter_changed.emit(filter_value)

    @Slot()
    def _show_notifications(self):
        pass

    def set_search_text(self, text):
        self.search_input.setText(text)

    def clear_search(self):
        self.search_input.clear()

    def set_filter(self, filter_type):
        for i in range(self.filter_combo.count()):
            if self.filter_combo.itemData(i) == filter_type:
                self.filter_combo.setCurrentIndex(i)
                break
