"""
Finovate Audit Nexus AI - Theme Manager
Professional themes: Dark Professional, Light Enterprise, Neon Finance, Glassmorphism
"""

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication
from typing import Dict, Any


class ThemeManager:
    """Manages application themes for the financial audit interface."""
    
    THEMES = {
        "Dark Professional": {
            "background": "#1a1a2e",
            "surface": "#16213e",
            "primary": "#0f3460",
            "secondary": "#e94560",
            "text": "#ffffff",
            "text_secondary": "#a0a0a0",
            "success": "#00c853",
            "warning": "#ffd600",
            "error": "#ff3d00",
            "info": "#2979ff"
        },
        "Light Enterprise": {
            "background": "#f5f5f5",
            "surface": "#ffffff",
            "primary": "#1976d2",
            "secondary": "#424242",
            "text": "#212121",
            "text_secondary": "#757575",
            "success": "#388e3c",
            "warning": "#fbc02d",
            "error": "#d32f2f",
            "info": "#1976d2"
        },
        "Neon Finance": {
            "background": "#0a0a0f",
            "surface": "#12121a",
            "primary": "#00ffff",
            "secondary": "#ff00ff",
            "text": "#ffffff",
            "text_secondary": "#b0b0b0",
            "success": "#00ff88",
            "warning": "#ffff00",
            "error": "#ff0055",
            "info": "#00ccff"
        },
        "Glassmorphism": {
            "background": "#2d1b69",
            "surface": "rgba(255, 255, 255, 0.1)",
            "primary": "#6a5acd",
            "secondary": "#ff69b4",
            "text": "#ffffff",
            "text_secondary": "#e0e0e0",
            "success": "#32cd32",
            "warning": "#ffa500",
            "error": "#ff4500",
            "info": "#1e90ff"
        }
    }
    
    def __init__(self, theme_name: str = "Dark Professional"):
        self.current_theme = theme_name
        self.colors = self.THEMES.get(theme_name, self.THEMES["Dark Professional"])
    
    def apply_theme(self, app: QApplication):
        """Apply the current theme to the Qt application."""
        palette = QPalette()
        
        # Set colors based on theme
        bg_color = QColor(self.colors["background"])
        surface_color = QColor(self.colors["surface"])
        text_color = QColor(self.colors["text"])
        primary_color = QColor(self.colors["primary"])
        
        palette.setColor(QPalette.Window, bg_color)
        palette.setColor(QPalette.WindowText, text_color)
        palette.setColor(QPalette.Base, surface_color)
        palette.setColor(QPalette.AlternateBase, bg_color)
        palette.setColor(QPalette.Text, text_color)
        palette.setColor(QPalette.Button, surface_color)
        palette.setColor(QPalette.ButtonText, text_color)
        palette.setColor(QPalette.Highlight, primary_color)
        palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
        
        app.setPalette(palette)
        
        # Apply stylesheet
        app.setStyleSheet(self.get_stylesheet())
    
    def get_stylesheet(self) -> str:
        """Get the complete stylesheet for the current theme."""
        return f"""
            QMainWindow, QDialog {{
                background-color: {self.colors["background"]};
                color: {self.colors["text"]};
            }}
            
            QWidget {{
                background-color: {self.colors["background"]};
                color: {self.colors["text"]};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            
            QFrame#card {{
                background-color: {self.colors["surface"]};
                border-radius: 10px;
                padding: 15px;
            }}
            
            QPushButton {{
                background-color: {self.colors["primary"]};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {self.colors["secondary"]};
            }}
            
            QPushButton:pressed {{
                background-color: {self.colors["primary"]};
            }}
            
            QTableWidget {{
                background-color: {self.colors["surface"]};
                color: {self.colors["text"]};
                gridline-color: {self.colors["primary"]};
            }}
            
            QTableWidget::item:selected {{
                background-color: {self.colors["primary"]};
            }}
            
            QHeaderView::section {{
                background-color: {self.colors["primary"]};
                color: white;
                padding: 10px;
                border: none;
            }}
            
            QProgressBar {{
                border: none;
                border-radius: 5px;
                background-color: {self.colors["surface"]};
                height: 10px;
            }}
            
            QProgressBar::chunk {{
                background-color: {self.colors["success"]};
                border-radius: 5px;
            }}
            
            QLabel#title {{
                font-size: 24px;
                font-weight: bold;
                color: {self.colors["primary"]};
            }}
            
            QLabel#subtitle {{
                font-size: 14px;
                color: {self.colors["text_secondary"]};
            }}
            
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
        """
    
    def get_color(self, color_name: str) -> str:
        """Get a specific color from the current theme."""
        return self.colors.get(color_name, "#000000")
    
    def list_themes(self) -> list:
        """Return list of available themes."""
        return list(self.THEMES.keys())
    
    def set_theme(self, theme_name: str):
        """Change the current theme."""
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            self.colors = self.THEMES[theme_name]
        else:
            raise ValueError(f"Theme '{theme_name}' not found")
