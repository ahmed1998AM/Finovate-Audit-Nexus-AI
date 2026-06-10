"""
Web View Dashboard Page - Integration of Web UI into Desktop App
دمج واجهة الويب داخل تطبيق سطح المكتب
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt
import os

class WebViewDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header for the web view
        header = QWidget()
        header.setFixedHeight(50)
        header.setStyleSheet("background-color: #2c3e50; color: white;")
        header_layout = QVBoxLayout(header)
        title = QLabel("لوحة التحكم الذكية (واجهة الويب)")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(title)
        
        layout.addWidget(header)
        
        # Web View
        try:
            self.web_view = QWebEngineView()
            # Path to our previously created dashboard HTML
            dashboard_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web_dashboard", "audit_dashboard.html"))
            self.web_view.setUrl(QUrl.fromLocalFile(dashboard_path))
            layout.addWidget(self.web_view)
        except Exception as e:
            error_label = QLabel(f"❌ خطأ في تحميل واجهة الويب: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(error_label)
            
        # Refresh button
        refresh_btn = QPushButton("🔄 تحديث البيانات")
        refresh_btn.setFixedHeight(40)
        refresh_btn.setStyleSheet("background-color: #3498db; color: white; border: none; font-weight: bold;")
        refresh_btn.clicked.connect(self.refresh_page)
        layout.addWidget(refresh_btn)

    def refresh_page(self):
        if hasattr(self, 'web_view'):
            self.web_view.reload()
