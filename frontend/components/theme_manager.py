"""
Finovate Audit Nexus AI - Theme Manager
Professional themes: Dark Professional, Light Enterprise, Neon Finance, Glassmorphism
"""

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication
from typing import Dict, Any

from frontend.styles.design_system import Color


class ThemeManager:
    """Manages application themes for the financial audit interface."""

    THEMES = {
        "Dark Professional": {
            "background": Color.BG_MAIN,
            "surface": Color.BG_SIDEBAR,
            "primary": Color.PRIMARY,
            "secondary": Color.PRIMARY_HOVER,
            "text": Color.TEXT_PRIMARY,
            "text_secondary": Color.TEXT_SECONDARY,
            "success": Color.SUCCESS,
            "warning": Color.WARNING,
            "error": Color.ERROR,
            "info": Color.INFO,
        },
        "Light Enterprise": {
            "background": "#ffffff",
            "surface": "#f6f8fa",
            "primary": "#0969da",
            "secondary": "#0550ae",
            "text": "#1f2328",
            "text_secondary": "#656d76",
            "success": "#1a7f37",
            "warning": "#9a6700",
            "error": "#cf222e",
            "info": "#0969da",
        },
        "Neon Finance": {
            "background": "#0a0a12",
            "surface": "#12121e",
            "primary": "#00ffc8",
            "secondary": "#ff00e4",
            "text": "#ffffff",
            "text_secondary": "#b0b0c0",
            "success": "#00ff88",
            "warning": "#ffe600",
            "error": "#ff0055",
            "info": "#00ccff",
        },
        "Glassmorphism": {
            "background": "#1a103c",
            "surface": "rgba(255, 255, 255, 0.06)",
            "primary": "#a78bfa",
            "secondary": "#f472b6",
            "text": "#ffffff",
            "text_secondary": "#c4b5fd",
            "success": "#34d399",
            "warning": "#fbbf24",
            "error": "#fb7185",
            "info": "#60a5fa",
        },
    }

    def __init__(self, theme_name: str = "Dark Professional"):
        self.current_theme = theme_name
        self.colors = self.THEMES.get(theme_name, self.THEMES["Dark Professional"])

    def apply_theme(self, app: QApplication):
        palette = QPalette()
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
        app.setStyleSheet(self.get_stylesheet())

    def get_stylesheet(self) -> str:
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
        return self.colors.get(color_name, "#000000")

    def list_themes(self) -> list:
        return list(self.THEMES.keys())

    def set_theme(self, theme_name: str):
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            self.colors = self.THEMES[theme_name]
        else:
            raise ValueError(f"Theme '{theme_name}' not found")
