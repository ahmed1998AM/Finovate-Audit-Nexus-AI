from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QGridLayout, QPushButton,
    QComboBox, QLineEdit, QFormLayout, QMessageBox
)
from PySide6.QtCore import Qt
from loguru import logger
from frontend.api_client import get_client
from frontend.styles.design_system import Color


class AIProviderManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AIProviderManager")
        self._cards = []
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        header = QHBoxLayout()
        title_label = QLabel("AI Provider Manager")
        title_label.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {Color.TEXT_PRIMARY};")
        header.addWidget(title_label)
        header.addStretch()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._reload_providers)
        header.addWidget(refresh_btn)
        main_layout.addLayout(header)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {Color.TEXT_SECONDARY}; font-size: 12px;")
        main_layout.addWidget(self.status_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(16)
        scroll.setWidget(self.content_widget)
        main_layout.addWidget(scroll)

        self._reload_providers()

    def _clear_cards(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._cards.clear()

    def _reload_providers(self):
        self._clear_cards()
        client = get_client()
        if not client._token:
            self.status_label.setText("Log in via API to view providers")
            return

        data = client.ai_providers()
        providers_raw = data.get("providers", [])
        ai_status = client.ai_status()
        self.status_label.setText(
            f"Engine: {ai_status.get('status', 'unknown')} | "
            f"Active: {data.get('active_provider', '—')}"
        )

        if not providers_raw:
            lbl = QLabel("No providers configured — set API keys in .env")
            lbl.setStyleSheet(f"color: {Color.TEXT_SECONDARY};")
            self.content_layout.addWidget(lbl)
            return

        for p in providers_raw:
            name = p.get("name", p.get("provider", "Unknown"))
            connected = p.get("available", p.get("status") == "connected")
            status = "Connected" if connected else "Not configured"
            color = Color.SUCCESS if connected else Color.ERROR
            desc = p.get("description", p.get("default_model", ""))
            card = self._create_provider_card(name, status, desc, color)
            self.content_layout.addWidget(card)

        self.content_layout.addStretch()

    def _create_provider_card(self, name, status, description, status_color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {Color.BG_CARD};
                border: 1px solid {Color.BORDER};
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        layout = QVBoxLayout(card)

        header_layout = QHBoxLayout()
        name_label = QLabel(name)
        name_label.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {Color.TEXT_PRIMARY};")
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        status_label = QLabel(status)
        status_label.setStyleSheet(f"color: {status_color}; font-weight: 600; font-size: 12px;")
        header_layout.addWidget(status_label)
        layout.addLayout(header_layout)

        desc_label = QLabel(description or "—")
        desc_label.setStyleSheet(f"color: {Color.TEXT_SECONDARY}; font-size: 13px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        btn_layout = QHBoxLayout()
        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(lambda: self._on_test_provider(name))
        btn_layout.addWidget(test_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        return card

    def _on_test_provider(self, provider_key: str):
        client = get_client()
        if not client._token:
            QMessageBox.warning(self, "API", "Log in via API first.")
            return
        self.status_label.setText(f"Testing {provider_key}...")
        result = client.test_ai_provider(provider_key.lower().replace(" ", "_"))
        if not result:
            result = client.test_ai_provider(provider_key)
        ok = result.get("success", False)
        msg = result.get("data", result.get("message", "No response"))
        QMessageBox.information(
            self, "Test Result",
            f"{provider_key}: {'OK' if ok else 'Failed'}\n{msg}",
        )
        self._reload_providers()
