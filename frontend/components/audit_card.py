from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt

from frontend.styles.design_system import Color


class AuditCard(QFrame):
    STATUS_COLORS = {
        "success": Color.SUCCESS,
        "warning": Color.WARNING,
        "error": Color.ERROR,
        "info": Color.INFO,
        "normal": Color.PRIMARY,
    }

    def __init__(self, title: str = "", subtitle: str = "", value: str = "",
                 status: str = "normal"):
        super().__init__()
        self.status = status
        self._setup_ui(title, subtitle, value)
        self._apply_style()

    def _setup_ui(self, title: str, subtitle: str, value: str):
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setObjectName("card")
        self.setMinimumSize(250, 150)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 20, 20, 20)

        if title:
            self.title_label = QLabel(title)
            self.title_label.setWordWrap(True)
            self.title_label.setStyleSheet(
                f"font-size: 11px; color: {Color.TEXT_SECONDARY}; font-weight: 500;"
            )
            layout.addWidget(self.title_label)

        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setWordWrap(True)
            self.subtitle_label.setStyleSheet(f"font-size: 12px; color: {Color.TEXT_MUTED};")
            layout.addWidget(self.subtitle_label)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        if value or self.status != "normal":
            value_layout = QHBoxLayout()
            if value:
                self.value_label = QLabel(value)
                self.value_label.setStyleSheet(
                    f"font-size: 32px; font-weight: 700; color: {self._get_status_color()};"
                )
                value_layout.addWidget(self.value_label)

            value_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

            self.status_indicator = QLabel("●")
            self.status_indicator.setStyleSheet(f"font-size: 18px; color: {self._get_status_color()};")
            value_layout.addWidget(self.status_indicator)

            layout.addLayout(value_layout)

    def _get_status_color(self) -> str:
        return self.STATUS_COLORS.get(self.status, self.STATUS_COLORS["normal"])

    def _apply_style(self):
        self.setStyleSheet(f"""
            QFrame#card {{
                background-color: {Color.BG_CARD};
                border-radius: 10px;
                padding: 20px;
                border: 1px solid {Color.BORDER};
            }}
            QFrame#card:hover {{
                border: 1px solid {Color.PRIMARY};
            }}
        """)

    def set_status(self, status: str):
        self.status = status
        color = self._get_status_color()
        if hasattr(self, 'status_indicator'):
            self.status_indicator.setStyleSheet(f"font-size: 18px; color: {color};")
        if hasattr(self, 'value_label'):
            self.value_label.setStyleSheet(f"font-size: 32px; font-weight: 700; color: {color};")

    def set_value(self, value: str):
        if hasattr(self, 'value_label'):
            self.value_label.setText(value)
            color = self._get_status_color()
            self.value_label.setStyleSheet(f"font-size: 32px; font-weight: 700; color: {color};")
