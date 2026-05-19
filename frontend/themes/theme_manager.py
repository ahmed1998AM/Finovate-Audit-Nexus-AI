"""
Finovate Audit Nexus AI - Theme Manager
Enterprise AI Financial Audit & Intelligence Platform
"""

from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ApplicationTheme:
    """Represents an application theme"""
    name: str
    colors: Dict[str, str]
    fonts: Dict[str, str]
    styles: Dict[str, str]

class ThemeManager:
    """Manages application themes and styling"""
    
    THEMES = {
        "Dark Professional": {
            "colors": {
                "primary": "#2E86AB",
                "secondary": "#1E5F7A",
                "accent": "#00ADB5",
                "background": "#1A1A2E",
                "surface": "#16213E",
                "text_primary": "#FFFFFF",
                "text_secondary": "#B0B0B0",
                "success": "#28A745",
                "warning": "#FFC107",
                "danger": "#DC3545",
                "info": "#17A2B8"
            },
            "fonts": {
                "default": "Segoe UI, 10pt",
                "heading": "Segoe UI, 14pt, bold",
                "title": "Segoe UI, 18pt, bold",
                "code": "Consolas, 9pt"
            },
            "styles": {
                "window": """
                    QMainWindow {
                        background-color: #1A1A2E;
                    }
                """,
                "button": """
                    QPushButton {
                        background-color: #2E86AB;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #1E5F7A;
                    }
                    QPushButton:pressed {
                        background-color: #00ADB5;
                    }
                """,
                "input": """
                    QLineEdit, QTextEdit, QPlainTextEdit {
                        background-color: #16213E;
                        color: #FFFFFF;
                        border: 1px solid #2E86AB;
                        border-radius: 4px;
                        padding: 5px;
                    }
                    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
                        border: 2px solid #00ADB5;
                    }
                """
            }
        },
        "Light Enterprise": {
            "colors": {
                "primary": "#2E86AB",
                "secondary": "#5FA8D3",
                "accent": "#00ADB5",
                "background": "#FFFFFF",
                "surface": "#F8F9FA",
                "text_primary": "#212529",
                "text_secondary": "#6C757D",
                "success": "#28A745",
                "warning": "#FFC107",
                "danger": "#DC3545",
                "info": "#17A2B8"
            },
            "fonts": {
                "default": "Segoe UI, 10pt",
                "heading": "Segoe UI, 14pt, bold",
                "title": "Segoe UI, 18pt, bold",
                "code": "Consolas, 9pt"
            },
            "styles": {
                "window": """
                    QMainWindow {
                        background-color: #FFFFFF;
                    }
                """,
                "button": """
                    QPushButton {
                        background-color: #2E86AB;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #1E5F7A;
                    }
                    QPushButton:pressed {
                        background-color: #00ADB5;
                    }
                """,
                "input": """
                    QLineEdit, QTextEdit, QPlainTextEdit {
                        background-color: #FFFFFF;
                        color: #212529;
                        border: 1px solid #CED4DA;
                        border-radius: 4px;
                        padding: 5px;
                    }
                    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
                        border: 2px solid #2E86AB;
                    }
                """
            }
        },
        "Neon Finance": {
            "colors": {
                "primary": "#00F5FF",
                "secondary": "#7B2CBF",
                "accent": "#FF006E",
                "background": "#0D0D0D",
                "surface": "#1A1A1A",
                "text_primary": "#FFFFFF",
                "text_secondary": "#CCCCCC",
                "success": "#00FF88",
                "warning": "#FFDD00",
                "danger": "#FF006E",
                "info": "#00F5FF"
            },
            "fonts": {
                "default": "Segoe UI, 10pt",
                "heading": "Segoe UI, 14pt, bold",
                "title": "Segoe UI, 18pt, bold",
                "code": "Consolas, 9pt"
            },
            "styles": {
                "window": """
                    QMainWindow {
                        background-color: #0D0D0D;
                    }
                """,
                "button": """
                    QPushButton {
                        background-color: #7B2CBF;
                        color: white;
                        border: 2px solid #00F5FF;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #9D4EDD;
                        border-color: #FF006E;
                    }
                """
            }
        },
        "Glassmorphism": {
            "colors": {
                "primary": "#4CC9F0",
                "secondary": "#4361EE",
                "accent": "#F72585",
                "background": "#F8F9FA",
                "surface": "rgba(255, 255, 255, 0.7)",
                "text_primary": "#2B2D42",
                "text_secondary": "#8D99AE",
                "success": "#06D6A0",
                "warning": "#FFD166",
                "danger": "#EF476F",
                "info": "#4CC9F0"
            },
            "fonts": {
                "default": "Segoe UI, 10pt",
                "heading": "Segoe UI, 14pt, bold",
                "title": "Segoe UI, 18pt, bold",
                "code": "Consolas, 9pt"
            },
            "styles": {
                "window": """
                    QMainWindow {
                        background-color: #F8F9FA;
                    }
                """,
                "button": """
                    QPushButton {
                        background-color: rgba(67, 97, 238, 0.8);
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 8px;
                        font-weight: bold;
                        backdrop-filter: blur(10px);
                    }
                    QPushButton:hover {
                        background-color: rgba(76, 201, 240, 0.9);
                    }
                """
            }
        }
    }
    
    def __init__(self):
        self.current_theme_name = "Dark Professional"
        self.current_theme = self.THEMES[self.current_theme_name]
    
    def get_available_themes(self) -> List[str]:
        """Get list of available themes"""
        return list(self.THEMES.keys())
    
    def set_theme(self, theme_name: str) -> bool:
        """Set the current theme"""
        if theme_name in self.THEMES:
            self.current_theme_name = theme_name
            self.current_theme = self.THEMES[theme_name]
            return True
        return False
    
    def get_color(self, color_name: str) -> str:
        """Get a color from the current theme"""
        return self.current_theme["colors"].get(color_name, "#000000")
    
    def get_font(self, font_name: str) -> str:
        """Get a font from the current theme"""
        return self.current_theme["fonts"].get(font_name, "Segoe UI, 10pt")
    
    def get_style(self, style_name: str) -> str:
        """Get a style from the current theme"""
        return self.current_theme["styles"].get(style_name, "")
    
    def apply_theme(self, widget) -> None:
        """Apply the current theme to a widget"""
        widget.setStyleSheet(self.get_style("window"))
    
    def get_all_colors(self) -> Dict[str, str]:
        """Get all colors from current theme"""
        return self.current_theme["colors"].copy()
    
    def get_all_fonts(self) -> Dict[str, str]:
        """Get all fonts from current theme"""
        return self.current_theme["fonts"].copy()
