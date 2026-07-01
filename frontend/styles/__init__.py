"""
Finovate Audit Nexus AI - Styles Package
Design tokens, shared stylesheets for PySide6 desktop components.
"""
from .design_system import Color, Typography, DesignSystem


def table_style() -> str:
    """Stylesheet for QTableWidget used across the desktop UI."""
    return f"""
        QTableWidget {{
            background-color: {Color.BG_CARD};
            border: 1px solid {Color.BORDER};
            border-radius: 8px;
            gridline-color: {Color.BORDER};
            color: {Color.TEXT_PRIMARY};
            font-size: 13px;
        }}
        QTableWidget::item {{
            padding: 8px 12px;
            border-bottom: 1px solid {Color.BORDER};
        }}
        QTableWidget::item:selected {{
            background-color: {Color.PRIMARY_DARK};
            color: {Color.TEXT_WHITE};
        }}
        QHeaderView::section {{
            background-color: {Color.BG_MEDIUM};
            color: {Color.TEXT_SECONDARY};
            padding: 10px 12px;
            border: none;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
        }}
    """


metric_label_style = f"""
    QLabel {{
        background-color: {Color.BG_CARD};
        border: 1px solid {Color.BORDER};
        border-radius: 8px;
        padding: 16px;
        font-size: 14px;
        color: {Color.TEXT_PRIMARY};
    }}
"""
