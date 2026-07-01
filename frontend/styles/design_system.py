"""
Finovate Audit Nexus AI - Design System
Centralized styles, colors, and typography tokens
"""

from PySide6.QtGui import QColor, QFont


class Color:
    # Primary palette
    PRIMARY = "#00d4aa"
    PRIMARY_HOVER = "#00b894"
    PRIMARY_DARK = "#009975"

    # Background
    BG_DARK = "#0f1923"
    BG_MEDIUM = "#1a2a3a"
    BG_LIGHT = "#243447"
    BG_CARD = "#1e2d3d"

    # Text
    TEXT_PRIMARY = "#e0e0e0"
    TEXT_SECONDARY = "#8899aa"
    TEXT_MUTED = "#556677"
    TEXT_WHITE = "#ffffff"

    # Status
    SUCCESS = "#00d4aa"
    WARNING = "#f0a500"
    ERROR = "#ff4757"
    INFO = "#2e86ab"

    # Borders
    BORDER = "#2a3a4a"
    BORDER_LIGHT = "#3a4a5a"

    # Special
    ACCENT = "#00d4aa"
    GRADIENT_START = "#0f1923"
    GRADIENT_END = "#1a2a3a"


class Typography:
    FAMILY = "Segoe UI"
    SIZES = {
        "h1": 28,
        "h2": 22,
        "h3": 18,
        "h4": 15,
        "body": 13,
        "small": 11,
        "caption": 9,
    }

    @staticmethod
    def font(size_key: str = "body", bold: bool = False) -> QFont:
        font = QFont(Typography.FAMILY, Typography.SIZES.get(size_key, 13))
        font.setBold(bold)
        return font


class DesignSystem:
    """Central design system providing consistent styles across the application"""

    @staticmethod
    def get_dialog_style() -> str:
        return f"""
        QDialog {{
            background-color: {Color.BG_DARK};
        }}
        #dialogHeader {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {Color.GRADIENT_START}, stop:1 {Color.GRADIENT_END});
            border-bottom: 1px solid {Color.BORDER};
        }}
        #dialogTitle {{
            color: {Color.TEXT_WHITE};
            font-size: {Typography.SIZES["h3"]}px;
            font-weight: bold;
            font-family: {Typography.FAMILY};
        }}
        #dialogSubtitle {{
            color: {Color.TEXT_SECONDARY};
            font-size: {Typography.SIZES["body"]}px;
            font-family: {Typography.FAMILY};
        }}
        #dialogContent {{
            background-color: {Color.BG_DARK};
        }}
        #dialogButtonFrame {{
            background-color: {Color.BG_MEDIUM};
            border-top: 1px solid {Color.BORDER};
        }}
        QLabel {{
            color: {Color.TEXT_PRIMARY};
            font-size: {Typography.SIZES["body"]}px;
            font-family: {Typography.FAMILY};
        }}
        QLineEdit, QTextEdit {{
            background-color: {Color.BG_LIGHT};
            color: {Color.TEXT_WHITE};
            border: 1px solid {Color.BORDER};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: {Typography.SIZES["body"]}px;
            font-family: {Typography.FAMILY};
            selection-background-color: {Color.PRIMARY};
            selection-color: {Color.BG_DARK};
        }}
        QLineEdit:focus, QTextEdit:focus {{
            border: 1px solid {Color.PRIMARY};
            background-color: {Color.BG_CARD};
        }}
        QLineEdit:hover, QTextEdit:hover {{
            border: 1px solid {Color.BORDER_LIGHT};
        }}
        QComboBox {{
            background-color: {Color.BG_LIGHT};
            color: {Color.TEXT_WHITE};
            border: 1px solid {Color.BORDER};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: {Typography.SIZES["body"]}px;
            font-family: {Typography.FAMILY};
            min-width: 120px;
        }}
        QComboBox:hover {{
            border: 1px solid {Color.BORDER_LIGHT};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border: none;
        }}
        QComboBox QAbstractItemView {{
            background-color: {Color.BG_MEDIUM};
            color: {Color.TEXT_PRIMARY};
            border: 1px solid {Color.BORDER};
            selection-background-color: {Color.PRIMARY};
            selection-color: {Color.BG_DARK};
            border-radius: 4px;
            padding: 4px;
            outline: none;
        }}
        QComboBox:focus {{
            border: 1px solid {Color.PRIMARY};
        }}
        QPushButton {{
            border: none;
            border-radius: 6px;
            padding: 10px 24px;
            font-size: {Typography.SIZES["body"]}px;
            font-family: {Typography.FAMILY};
            font-weight: bold;
        }}
        #createButton {{
            background-color: {Color.PRIMARY};
            color: {Color.BG_DARK};
        }}
        #createButton:hover {{
            background-color: {Color.PRIMARY_HOVER};
        }}
        #createButton:pressed {{
            background-color: {Color.PRIMARY_DARK};
        }}
        #cancelButton {{
            background-color: transparent;
            color: {Color.TEXT_SECONDARY};
            border: 1px solid {Color.BORDER};
        }}
        #cancelButton:hover {{
            background-color: {Color.BG_LIGHT};
            color: {Color.TEXT_PRIMARY};
        }}
        #resetButton {{
            background-color: transparent;
            color: {Color.TEXT_MUTED};
        }}
        #resetButton:hover {{
            color: {Color.WARNING};
        }}
        QGroupBox {{
            border: 1px solid {Color.BORDER};
            border-radius: 8px;
            margin-top: 16px;
            padding: 20px 16px 12px 16px;
            font-size: {Typography.SIZES["h4"]}px;
            font-weight: bold;
            color: {Color.PRIMARY};
            font-family: {Typography.FAMILY};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 4px 12px;
            background-color: {Color.BG_DARK};
            border: 1px solid {Color.BORDER};
            border-radius: 4px;
            color: {Color.PRIMARY};
        }}
        QCheckBox {{
            color: {Color.TEXT_PRIMARY};
            font-size: {Typography.SIZES["body"]}px;
            font-family: {Typography.FAMILY};
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 3px;
            border: 1px solid {Color.BORDER};
            background-color: {Color.BG_LIGHT};
        }}
        QCheckBox::indicator:checked {{
            background-color: {Color.PRIMARY};
            border: 1px solid {Color.PRIMARY};
        }}
        QCheckBox::indicator:hover {{
            border: 1px solid {Color.PRIMARY};
        }}
        QSpinBox {{
            background-color: {Color.BG_LIGHT};
            color: {Color.TEXT_WHITE};
            border: 1px solid {Color.BORDER};
            border-radius: 6px;
            padding: 6px 10px;
            font-size: {Typography.SIZES["body"]}px;
            font-family: {Typography.FAMILY};
        }}
        QSpinBox:focus {{
            border: 1px solid {Color.PRIMARY};
        }}
        QSpinBox::up-button, QSpinBox::down-button {{
            border: none;
            background: transparent;
            width: 20px;
        }}
        QDateEdit {{
            background-color: {Color.BG_LIGHT};
            color: {Color.TEXT_WHITE};
            border: 1px solid {Color.BORDER};
            border-radius: 6px;
            padding: 6px 10px;
            font-size: {Typography.SIZES["body"]}px;
            font-family: {Typography.FAMILY};
        }}
        QDateEdit:focus {{
            border: 1px solid {Color.PRIMARY};
        }}
        QDateEdit::drop-down {{
            border: none;
            width: 24px;
        }}
        QTabWidget::pane {{
            border: 1px solid {Color.BORDER};
            border-radius: 8px;
            background-color: {Color.BG_MEDIUM};
            padding: 4px;
        }}
        QTabBar::tab {{
            background-color: {Color.BG_DARK};
            color: {Color.TEXT_SECONDARY};
            border: none;
            border-bottom: 2px solid transparent;
            padding: 10px 20px;
            margin-right: 4px;
            font-size: {Typography.SIZES["body"]}px;
            font-family: {Typography.FAMILY};
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }}
        QTabBar::tab:selected {{
            background-color: {Color.BG_MEDIUM};
            color: {Color.PRIMARY};
            border-bottom: 2px solid {Color.PRIMARY};
        }}
        QTabBar::tab:hover:!selected {{
            background-color: {Color.BG_LIGHT};
            color: {Color.TEXT_PRIMARY};
        }}
        QProgressBar {{
            background-color: {Color.BG_LIGHT};
            border-radius: 2px;
            border: none;
        }}
        QProgressBar::chunk {{
            background-color: {Color.PRIMARY};
            border-radius: 2px;
        }}
        QScrollBar:vertical {{
            background-color: {Color.BG_DARK};
            width: 8px;
            border: none;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {Color.BORDER};
            border-radius: 4px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {Color.BORDER_LIGHT};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        """
