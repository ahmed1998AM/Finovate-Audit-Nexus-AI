"""
Finovate Audit Nexus AI - Audit Card Component
Professional card widget for displaying audit findings, metrics, and summaries.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt
from .theme_manager import ThemeManager


class AuditCard(QFrame):
    """Professional card component for displaying audit information."""
    
    def __init__(self, title: str = "", subtitle: str = "", value: str = "", 
                 status: str = "normal", theme_manager: ThemeManager = None):
        super().__init__()
        
        self.theme_manager = theme_manager or ThemeManager()
        self.status = status
        
        self.setup_ui(title, subtitle, value, status)
        self.apply_style()
    
    def setup_ui(self, title: str, subtitle: str, value: str, status: str):
        """Setup the card UI components."""
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setObjectName("card")
        self.setMinimumSize(250, 150)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        if title:
            self.title_label = QLabel(title)
            self.title_label.setObjectName("title")
            self.title_label.setWordWrap(True)
            layout.addWidget(self.title_label)
        
        # Subtitle
        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setObjectName("subtitle")
            self.subtitle_label.setWordWrap(True)
            layout.addWidget(self.subtitle_label)
        
        # Spacer
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Value/Status row
        if value or status != "normal":
            value_layout = QHBoxLayout()
            
            if value:
                self.value_label = QLabel(value)
                self.value_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {self.get_status_color()};")
                value_layout.addWidget(self.value_label)
            
            value_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
            
            # Status indicator
            self.status_indicator = QLabel("●")
            self.status_indicator.setStyleSheet(f"font-size: 24px; color: {self.get_status_color()};")
            value_layout.addWidget(self.status_indicator)
            
            layout.addLayout(value_layout)
    
    def get_status_color(self) -> str:
        """Get color based on status."""
        colors = {
            "success": self.theme_manager.get_color("success"),
            "warning": self.theme_manager.get_color("warning"),
            "error": self.theme_manager.get_color("error"),
            "info": self.theme_manager.get_color("info"),
            "normal": self.theme_manager.get_color("primary")
        }
        return colors.get(self.status, colors["normal"])
    
    def apply_style(self):
        """Apply card styling."""
        self.setStyleSheet(f"""
            QFrame#card {{
                background-color: {self.theme_manager.get_color('surface')};
                border-radius: 15px;
                padding: 20px;
                border: 1px solid {self.theme_manager.get_color('primary')};
            }}
            
            QFrame#card:hover {{
                border: 2px solid {self.theme_manager.get_color('secondary')};
            }}
        """)
    
    def set_status(self, status: str):
        """Update the card status."""
        self.status = status
        if hasattr(self, 'status_indicator'):
            self.status_indicator.setStyleSheet(f"font-size: 24px; color: {self.get_status_color()};")
        if hasattr(self, 'value_label'):
            self.value_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {self.get_status_color()};")
    
    def set_value(self, value: str):
        """Update the card value."""
        if hasattr(self, 'value_label'):
            self.value_label.setText(value)
            self.value_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {self.get_status_color()};")
