from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont
from loguru import logger

from ..api_client import get_client, reset_client
from ..services.auth_service import AuthService
from ..users.manager import RBACManager, create_rbac_manager
from frontend.styles.design_system import DesignSystem, Color, Typography


class LoginDialog(QDialog):
    login_successful = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Finovate Audit Nexus AI - Login")
        self.setFixedSize(420, 520)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setStyleSheet(DesignSystem.get_dialog_style())
        self._api = get_client()
        self._auth = AuthService(self._api)
        self._rbac: RBACManager = create_rbac_manager()
        self.user_info: dict = {}
        self._setup_ui()
        self._animate_in()

    def _animate_in(self):
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(350)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(16)
        layout.addStretch(1)

        title_frame = QFrame()
        title_frame.setObjectName("loginTitleFrame")
        title_frame.setStyleSheet(f"""
            QFrame#loginTitleFrame {{
                background-color: {Color.BG_MEDIUM};
                border-radius: 12px;
                padding: 20px;
                border: 1px solid {Color.BORDER};
            }}
        """)
        title_layout = QVBoxLayout(title_frame)
        title_layout.setAlignment(Qt.AlignCenter)
        title_layout.setSpacing(4)

        title = QLabel("Finovate Audit")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(Typography.font("h2", bold=True))
        title.setStyleSheet(f"color: {Color.TEXT_WHITE}; background: transparent;")
        title_layout.addWidget(title)

        subtitle = QLabel("Nexus AI")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(Typography.font("h3", bold=True))
        subtitle.setStyleSheet(f"color: {Color.PRIMARY}; background: transparent;")
        title_layout.addWidget(subtitle)

        tagline = QLabel("Enterprise Financial Audit Platform")
        tagline.setAlignment(Qt.AlignCenter)
        tagline.setStyleSheet(f"color: {Color.TEXT_SECONDARY}; font-size: 11px; background: transparent;")
        title_layout.addWidget(tagline)

        layout.addWidget(title_frame)
        layout.addSpacing(16)

        self.error_label = QLabel()
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        username_label = QLabel("Username")
        username_label.setStyleSheet(f"font-size: 12px; color: {Color.TEXT_SECONDARY};")
        layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username...")
        self.username_input.returnPressed.connect(self._on_login)
        layout.addWidget(self.username_input)

        password_label = QLabel("Password")
        password_label.setStyleSheet(f"font-size: 12px; color: {Color.TEXT_SECONDARY};")
        layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password...")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self._on_login)
        layout.addWidget(self.password_input)

        layout.addSpacing(8)

        self.login_btn = QPushButton("Sign In")
        self.login_btn.setObjectName("createButton")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setMinimumHeight(44)
        self.login_btn.clicked.connect(self._on_login)
        layout.addWidget(self.login_btn)

        layout.addStretch(2)

        footer = QLabel("© 2025 Finovate - AHMED EG  |  v2.0.0")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"color: {Color.TEXT_MUTED}; font-size: 10px;")
        layout.addWidget(footer)

    def _on_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self._show_error("Please enter username and password")
            return

        self.login_btn.setEnabled(False)
        self.login_btn.setText("Signing in...")
        self.error_label.setVisible(False)

        try:
            result = self._try_api_login(username, password)
            if result:
                self.user_info = result
                self.login_successful.emit(result)
                self.accept()
                return
        except Exception as e:
            logger.warning(f"API login failed, trying local: {e}")

        try:
            result = self._try_local_login(username, password)
            if result:
                self.user_info = result
                self.login_successful.emit(result)
                self.accept()
                return
        except Exception as e:
            logger.warning(f"Local login failed: {e}")

        self._show_error("Invalid credentials")
        self.login_btn.setEnabled(True)
        self.login_btn.setText("Sign In")

    def _try_api_login(self, username: str, password: str) -> dict:
        return self._auth.login_api(username, password)

    def _try_local_login(self, username: str, password: str) -> dict:
        session_token = self._rbac.authenticate(username, password)
        if session_token:
            user = self._rbac.validate_session(session_token)
            if user:
                return self._auth.apply_local_login({
                    "username": user.username,
                    "role": user.role.value,
                    "token": session_token,
                    "must_change_password": False,
                    "full_name": user.full_name,
                })
        return None

    def _show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.setStyleSheet(
            f"color: {Color.ERROR}; background-color: {Color.BG_DARK}; padding: 10px; "
            f"border-radius: 6px; font-size: 12px; border: 1px solid {Color.ERROR}30;"
        )
        self.error_label.setVisible(True)
