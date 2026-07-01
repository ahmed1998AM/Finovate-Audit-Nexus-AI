from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve
from PySide6.QtGui import QFont

from frontend.styles.design_system import Color


class ToastNotification(QFrame):
    COLORS = {
        "info": {"border": Color.BORDER, "accent": Color.INFO},
        "success": {"border": Color.SUCCESS, "accent": Color.SUCCESS},
        "warning": {"border": Color.WARNING, "accent": Color.WARNING},
        "error": {"border": Color.ERROR, "accent": Color.ERROR},
    }

    def __init__(self, parent, message, type="info", duration=3000):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

        c = self.COLORS.get(type, self.COLORS["info"])

        self.setStyleSheet(f"""
            ToastNotification {{
                background-color: {Color.BG_MEDIUM};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 0px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        icon = QLabel("●")
        icon.setStyleSheet(f"color: {c['accent']}; font-size: 14px; background: transparent;")
        layout.addWidget(icon)

        msg = QLabel(message)
        msg.setStyleSheet(f"color: {Color.TEXT_PRIMARY}; font-size: 13px; background: transparent;")
        msg.setWordWrap(True)
        layout.addWidget(msg, stretch=1)

        self.adjustSize()
        self._duration = duration

    def show_with_animation(self):
        parent = self.parent()
        if parent:
            pr = parent.geometry()
            x = pr.right() - self.width() - 20
            y = pr.bottom() - self.height() - 60

        self.setGeometry(x, y + 20, self.width(), self.height())
        self.show()

        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(x, y + 20, self.width(), self.height()))
        self.anim.setEndValue(QRect(x, y, self.width(), self.height()))
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

        QTimer.singleShot(self._duration, self.fade_out)

    def fade_out(self):
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(300)
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.setEasingCurve(QEasingCurve.InCubic)
        self.fade_anim.finished.connect(self.close)
        self.fade_anim.start()


def show_toast(parent, message, type="info", duration=3000):
    toast = ToastNotification(parent, message, type, duration)
    toast.show_with_animation()
    return toast
