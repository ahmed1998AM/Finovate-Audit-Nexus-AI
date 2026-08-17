from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFrame,
    QLabel, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from frontend.styles.design_system import Color


class Sidebar(QFrame):
    page_requested = Signal(str)

    NAV_ITEMS = [
        ("dashboard", "لوحة القيادة"),
        ("executive", "القيادة التنفيذية"),
        ("analytics", "التحليلات"),
        ("agents", "وكلاء AI"),
        ("reports", "التقارير"),
        ("ai_management", "إدارة AI"),
        ("connectors", "الموصلات"),
        ("audit_projects", "مشاريع التدقيق"),
        ("fraud_detection", "كشف الاحتيال"),
        ("compliance", "الامتثال"),
        ("settings", "الإعدادات"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(250)
        self.current_page = None
        self.nav_buttons = {}
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"""
            #sidebar {{
                background-color: {Color.BG_SIDEBAR};
                border-right: 1px solid {Color.BORDER};
            }}
            #sidebar QPushButton#navButton {{
                background-color: transparent;
                color: {Color.TEXT_SECONDARY};
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                text-align: left;
                font-size: 14px;
                font-weight: 500;
                margin: 2px 8px;
            }}
            #sidebar QPushButton#navButton:hover {{
                background-color: {Color.BG_HOVER};
                color: {Color.TEXT_PRIMARY};
            }}
            #sidebar QScrollArea#navScrollArea {{
                border: none;
                background-color: transparent;
            }}
            #logoLabel {{
                color: {Color.PRIMARY_LIGHT};
                font-size: 18px;
                font-weight: 800;
                padding: 20px 10px 5px 10px;
                letter-spacing: 1px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 16, 8, 12)
        layout.setSpacing(6)

        logo_label = QLabel("Finovate Audit\nNexus AI")
        logo_label.setObjectName("logoLabel")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet(f"""
            color: {Color.TEXT_WHITE};
            font-size: 16px;
            font-weight: bold;
            padding: 12px 8px;
        """)
        layout.addWidget(logo_label)

        subtitle = QLabel("Enterprise Audit Platform")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"color: {Color.TEXT_MUTED}; font-size: 10px; padding: 0 0 8px 0;")
        layout.addWidget(subtitle)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background-color: {Color.BORDER}; max-height: 1px; margin: 4px 10px;")
        layout.addWidget(line)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setObjectName("navScrollArea")

        nav_widget = QWidget()
        nav_widget.setStyleSheet("background: transparent;")
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 4, 0, 0)
        nav_layout.setSpacing(2)

        for page_id, title in self.NAV_ITEMS:
            btn = QPushButton(title)
            btn.setObjectName("navButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setMinimumHeight(38)
            btn.clicked.connect(lambda pid=page_id: self._on_nav_clicked(pid))
            nav_layout.addWidget(btn)
            self.nav_buttons[page_id] = btn

        nav_layout.addStretch()
        scroll.setWidget(nav_widget)
        layout.addWidget(scroll, stretch=1)

        bottom_line = QFrame()
        bottom_line.setFrameShape(QFrame.HLine)
        bottom_line.setStyleSheet(f"background-color: {Color.BORDER}; max-height: 1px; margin: 4px 10px;")
        layout.addWidget(bottom_line)

        version_label = QLabel("v2.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet(f"color: {Color.TEXT_MUTED}; font-size: 11px; padding: 8px;")
        layout.addWidget(version_label)

    def _on_nav_clicked(self, page_id):
        self.set_active(page_id)
        self.page_requested.emit(page_id)

    def set_active(self, page_id):
        for pid, btn in self.nav_buttons.items():
            if pid == page_id:
                btn.setStyleSheet(f"""
                    QPushButton#navButton {{
                        background-color: {Color.PRIMARY};
                        color: {Color.TEXT_WHITE};
                        border-radius: 8px;
                        padding: 12px 16px;
                        text-align: left;
                        font-size: 14px;
                        font-weight: 600;
                        margin: 2px 8px;
                    }}
                """)
            else:
                btn.setStyleSheet("")
