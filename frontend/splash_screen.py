"""
Finovate Audit Nexus AI - Animated Splash Screen
Enterprise AI Financial Audit & Intelligence Platform
"""

from PySide6.QtWidgets import QSplashScreen, QVBoxLayout, QLabel, QProgressBar, QFrame
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Signal
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient, QBrush, QPen

from loguru import logger
from frontend.styles.design_system import Color


class AnimatedSplashScreen(QSplashScreen):
    """Professional animated splash screen with progress feedback"""

    splash_closed = Signal()

    def __init__(self):
        pixmap = QPixmap(600, 400)
        pixmap.fill(Qt.transparent)
        super().__init__(pixmap)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._progress = 0
        self._setup_ui()
        self._animate_in()

    def _setup_ui(self):
        # Build the splash content on the pixmap
        pixmap = QPixmap(600, 400)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        gradient = QLinearGradient(0, 0, 600, 400)
        gradient.setColorAt(0.0, QColor(Color.BG_DARK))
        gradient.setColorAt(1.0, QColor(Color.BG_MEDIUM))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 600, 400, 20, 20)

        border_pen = QPen(QColor(Color.PRIMARY), 2)
        painter.setPen(border_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(1, 1, 598, 398, 20, 20)

        painter.setPen(QColor(Color.PRIMARY))
        accent_font = QFont("Segoe UI", 9)
        accent_font.setBold(True)
        painter.setFont(accent_font)
        painter.drawText(30, 50, "▲ FINOVATE")

        painter.setPen(QColor(Color.TEXT_PRIMARY))
        title_font = QFont("Segoe UI", 28)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.drawText(30, 120, "Audit Nexus AI")

        painter.setPen(QColor(Color.TEXT_SECONDARY))
        sub_font = QFont("Segoe UI", 13)
        painter.setFont(sub_font)
        painter.drawText(30, 155, "Enterprise AI Financial Audit & Intelligence Platform")

        painter.setPen(QColor(Color.TEXT_MUTED))
        small_font = QFont("Segoe UI", 9)
        painter.setFont(small_font)
        painter.drawText(30, 360, "v2.0.0  |  Finovate Technologies  © 2026")

        self._version_label_pos = (30, 360)
        self._accent_pos = (30, 50)
        self._title_pos = (30, 120)
        self._subtitle_pos = (30, 155)

        painter.end()
        self.setPixmap(pixmap)

        overlay = QFrame(self)
        overlay.setGeometry(30, 250, 540, 60)
        overlay.setStyleSheet("background: transparent;")

        self._layout = QVBoxLayout(overlay)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(6)

        self._status_label = QLabel("جارٍ التحميل...")
        self._status_label.setStyleSheet(f"color: {Color.TEXT_SECONDARY}; font-size: 11px;")
        self._layout.addWidget(self._status_label)

        self._progress_bar = QProgressBar()
        self._progress_bar.setFixedHeight(4)
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {Color.BG_MEDIUM};
                border-radius: 2px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {Color.PRIMARY};
                border-radius: 2px;
            }}
        """)
        self._layout.addWidget(self._progress_bar)

    def _animate_in(self):
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(400)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()

    def update_progress(self, value: int, status: str = ""):
        self._progress = value
        self._progress_bar.setValue(value)
        if status:
            self._status_label.setText(status)

    def advance_progress(self, step: int = 5, status: str = ""):
        self._progress = min(100, self._progress + step)
        self._progress_bar.setValue(self._progress)
        if status:
            self._status_label.setText(status)

    def finish_with_main(self, main_window):
        self._animate_out()
        QTimer.singleShot(300, lambda: self._finish(main_window))

    def _animate_out(self):
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(300)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.finished.connect(self.close)
        anim.start()

    def _finish(self, main_window):
        self.close()
        main_window.show()
        self.splash_closed.emit()
