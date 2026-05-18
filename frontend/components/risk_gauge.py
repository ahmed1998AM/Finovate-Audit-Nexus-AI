"""
Finovate Audit Nexus AI - Risk Gauge Component
Circular gauge widget for displaying risk scores, financial health, and compliance metrics.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QConicalGradient, QPen, QFont, QRadialGradient
from PySide6.QtCore import Qt, QRectF
from .theme_manager import ThemeManager


class RiskGauge(QWidget):
    """Circular gauge component for displaying risk scores and metrics."""
    
    def __init__(self, value: float = 0.0, min_value: float = 0.0, max_value: float = 100.0,
                 label: str = "Risk Score", theme_manager: ThemeManager = None):
        super().__init__()
        
        self.theme_manager = theme_manager or ThemeManager()
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.label = label
        
        self.setMinimumSize(200, 200)
        self.setMaximumSize(300, 300)
    
    def set_value(self, value: float):
        """Update the gauge value."""
        self.value = max(self.min_value, min(self.max_value, value))
        self.update()
    
    def set_label(self, label: str):
        """Update the gauge label."""
        self.label = label
        self.update()
    
    def get_color_for_value(self) -> QColor:
        """Get color based on value percentage."""
        percentage = (self.value - self.min_value) / (self.max_value - self.min_value)
        
        if percentage < 0.33:
            return QColor(self.theme_manager.get_color("success"))  # Low risk
        elif percentage < 0.66:
            return QColor(self.theme_manager.get_color("warning"))  # Medium risk
        else:
            return QColor(self.theme_manager.get_color("error"))  # High risk
    
    def paintEvent(self, event):
        """Paint the circular gauge."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get dimensions
        width = self.width()
        height = self.height()
        size = min(width, height)
        center_x = width / 2
        center_y = height / 2
        radius = (size / 2) - 20
        
        # Draw background circle
        bg_pen = QPen(QColor(self.theme_manager.get_color("surface")), 15)
        painter.setPen(bg_pen)
        painter.drawEllipse(QPointF(center_x, center_y), radius, radius)
        
        # Calculate angle for value
        percentage = (self.value - self.min_value) / (self.max_value - self.min_value)
        span_angle = int(percentage * 360 * 16)  # 16 units per degree
        
        # Draw value arc with gradient
        gradient = QRadialGradient(center_x, center_y, radius)
        color = self.get_color_for_value()
        gradient.setColorAt(0, color)
        gradient.setColorAt(1, color.lighter(120))
        
        value_pen = QPen(gradient, 15)
        value_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(value_pen)
        
        # Draw arc from top (-90 degrees)
        start_angle = -90 * 16
        painter.drawArc(
            QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2),
            start_angle,
            span_angle
        )
        
        # Draw center text
        painter.setPen(QColor(self.theme_manager.get_color("text")))
        
        # Value in center (large font)
        value_font = QFont("Segoe UI", 32, QFont.Bold)
        painter.setFont(value_font)
        value_text = f"{self.value:.1f}"
        painter.drawText(
            QRectF(center_x - 50, center_y - 20, 100, 40),
            Qt.AlignCenter,
            value_text
        )
        
        # Label below value
        label_font = QFont("Segoe UI", 12)
        painter.setFont(label_font)
        painter.setPen(QColor(self.theme_manager.get_color("text_secondary")))
        painter.drawText(
            QRectF(center_x - 50, center_y + 20, 100, 20),
            Qt.AlignCenter,
            self.label
        )
        
        # Min/Max labels
        min_max_font = QFont("Segoe UI", 10)
        painter.setFont(min_max_font)
        
        # Min value (left)
        painter.drawText(
            QRectF(center_x - radius - 20, center_y, 60, 20),
            Qt.AlignRight,
            f"{self.min_value:.0f}"
        )
        
        # Max value (right)
        painter.drawText(
            QRectF(center_x + radius - 20, center_y, 60, 20),
            Qt.AlignLeft,
            f"{self.max_value:.0f}"
        )
        
        # Risk level indicator
        risk_level = self.get_risk_level()
        level_font = QFont("Segoe UI", 11, QFont.Bold)
        painter.setFont(level_font)
        painter.setPen(self.get_color_for_value())
        painter.drawText(
            QRectF(center_x - 60, center_y + 45, 120, 20),
            Qt.AlignCenter,
            risk_level
        )
    
    def get_risk_level(self) -> str:
        """Get risk level text based on value."""
        percentage = (self.value - self.min_value) / (self.max_value - self.min_value)
        
        if percentage < 0.33:
            return "LOW RISK"
        elif percentage < 0.66:
            return "MEDIUM RISK"
        else:
            return "HIGH RISK"
