"""
Web View Dashboard Page - Integration of Web UI into Desktop App
دمج واجهة الويب داخل تطبيق سطح المكتب
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt
import os

from frontend.styles.design_system import Color


class WebViewDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QWidget()
        header.setFixedHeight(50)
        header.setStyleSheet(f"background-color: {Color.BG_MEDIUM}; color: {Color.TEXT_WHITE};")
        header_layout = QVBoxLayout(header)
        title = QLabel("لوحة التحكم الذكية (واجهة الويب)")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Color.TEXT_WHITE};")
        header_layout.addWidget(title)

        layout.addWidget(header)

        try:
            self.web_view = QWebEngineView()
            dashboard_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web_dashboard", "audit_dashboard.html"))
            self.web_view.setUrl(QUrl.fromLocalFile(dashboard_path))
            layout.addWidget(self.web_view)
        except Exception as e:
            error_label = QLabel(f"Error loading web view: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(error_label)

        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.setFixedHeight(40)
        refresh_btn.setObjectName("primaryButton")
        refresh_btn.clicked.connect(self.refresh_page)
        layout.addWidget(refresh_btn)

    def refresh_page(self):
        if hasattr(self, 'web_view'):
            self.web_view.reload()
