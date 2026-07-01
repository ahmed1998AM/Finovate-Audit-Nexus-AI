from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QConicalGradient, QPen, QFont, QRadialGradient
from PySide6.QtCore import Qt, QRectF, QPointF
from .theme_manager import ThemeManager

from frontend.styles.design_system import Color


class RiskGauge(QWidget):
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
        self.value = max(self.min_value, min(self.max_value, value))
        self.update()

    def set_label(self, label: str):
        self.label = label
        self.update()

    def get_color_for_value(self) -> QColor:
        percentage = (self.value - self.min_value) / (self.max_value - self.min_value)
        if percentage < 0.33:
            return QColor(Color.SUCCESS)
        elif percentage < 0.66:
            return QColor(Color.WARNING)
        else:
            return QColor(Color.ERROR)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        size = min(width, height)
        center_x = width / 2
        center_y = height / 2
        radius = (size / 2) - 20

        painter.setPen(QPen(QColor(Color.BG_LIGHT), 14))
        painter.drawEllipse(QPointF(center_x, center_y), radius, radius)

        percentage = (self.value - self.min_value) / (self.max_value - self.min_value)
        span_angle = int(percentage * 360 * 16)

        color = self.get_color_for_value()
        gradient = QRadialGradient(center_x, center_y, radius)
        gradient.setColorAt(0, color)
        gradient.setColorAt(1, color.lighter(130))

        value_pen = QPen(gradient, 14)
        value_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(value_pen)

        start_angle = -90 * 16
        painter.drawArc(
            QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2),
            start_angle,
            span_angle
        )

        painter.setPen(QColor(Color.TEXT_WHITE))
        value_font = QFont("Segoe UI", 32, QFont.Bold)
        painter.setFont(value_font)
        value_text = f"{self.value:.1f}"
        painter.drawText(
            QRectF(center_x - 50, center_y - 20, 100, 40),
            Qt.AlignCenter,
            value_text
        )

        label_font = QFont("Segoe UI", 12)
        painter.setFont(label_font)
        painter.setPen(QColor(Color.TEXT_SECONDARY))
        painter.drawText(
            QRectF(center_x - 50, center_y + 20, 100, 20),
            Qt.AlignCenter,
            self.label
        )

        min_max_font = QFont("Segoe UI", 10)
        painter.setFont(min_max_font)
        painter.setPen(QColor(Color.TEXT_MUTED))
        painter.drawText(
            QRectF(center_x - radius - 20, center_y, 60, 20),
            Qt.AlignRight,
            f"{self.min_value:.0f}"
        )
        painter.drawText(
            QRectF(center_x + radius - 20, center_y, 60, 20),
            Qt.AlignLeft,
            f"{self.max_value:.0f}"
        )

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
        percentage = (self.value - self.min_value) / (self.max_value - self.min_value)
        if percentage < 0.33:
            return "LOW RISK"
        elif percentage < 0.66:
            return "MEDIUM RISK"
        else:
            return "HIGH RISK"
