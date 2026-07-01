from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QMessageBox, QLineEdit, QComboBox, QFormLayout,
    QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from loguru import logger
from frontend.api_client import get_client
from frontend.styles.design_system import Color
import threading


SYSTEM_TYPE_MAP = {
    "SAP": "sap",
    "Oracle": "oracle",
    "Dynamics": "dynamics",
    "NetSuite": "netsuite",
    "QuickBooks": "quickbooks",
    "Xero": "xero",
    "Odoo": "odoo",
    "Zoho": "zoho",
    "SQL Server": "sql",
    "MySQL": "sql",
    "PostgreSQL": "sql",
    "API Custom": "api",
}


class ConnectorDialog(QDialog):
    def __init__(self, parent=None, connector_data=None):
        super().__init__(parent)
        self.connector_data = connector_data
        self.setWindowTitle("Connector Settings" if not connector_data else f"Edit {connector_data.get('name', '')}")
        self.setMinimumSize(450, 300)
        self.setStyleSheet(f"QDialog {{ background-color: {Color.BG_DARK}; color: {Color.TEXT_PRIMARY}; }}")
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Connector name")
        self.name_input.setStyleSheet(f"background: {Color.BG_DARK}; color: {Color.TEXT_PRIMARY}; border: 1px solid {Color.BORDER}; border-radius: 6px; padding: 8px 12px;")
        layout.addRow("Name:", self.name_input)

        self.system_combo = QComboBox()
        self.system_combo.addItems(list(SYSTEM_TYPE_MAP.keys()))
        self.system_combo.setStyleSheet(f"background: {Color.BG_DARK}; color: {Color.TEXT_PRIMARY}; border: 1px solid {Color.BORDER}; border-radius: 6px; padding: 8px 12px;")
        layout.addRow("System:", self.system_combo)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://server:port")
        self.url_input.setStyleSheet(f"background: {Color.BG_DARK}; color: {Color.TEXT_PRIMARY}; border: 1px solid {Color.BORDER}; border-radius: 6px; padding: 8px 12px;")
        layout.addRow("Server URL:", self.url_input)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        ok_btn = QPushButton("Save")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        layout.addRow(btn_layout)

        if self.connector_data:
            self.name_input.setText(self.connector_data.get("name", ""))
            idx = self.system_combo.findText(self.connector_data.get("system", ""))
            if idx >= 0:
                self.system_combo.setCurrentIndex(idx)
            self.url_input.setText(self.connector_data.get("url", ""))

    def get_data(self):
        system = self.system_combo.currentText()
        return {
            "name": self.name_input.text(),
            "system": system,
            "connector_type": SYSTEM_TYPE_MAP.get(system, "api"),
            "url": self.url_input.text(),
            "status": "disconnected",
            "last_sync": "",
            "records": "0",
            "version": "1.0",
        }


class ConnectorPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ConnectorPage")
        self.connectors = []
        self._setup_ui()
        self._load_connectors()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Connector Manager")
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {Color.TEXT_PRIMARY};")
        header.addWidget(title)
        header.addStretch()

        add_btn = QPushButton("+ Add Connector")
        add_btn.clicked.connect(self._add_connector)
        header.addWidget(add_btn)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._load_connectors)
        header.addWidget(refresh_btn)

        test_btn = QPushButton("Test All")
        test_btn.clicked.connect(self._test_all)
        header.addWidget(test_btn)
        main_layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Name", "System", "Status", "Last Sync", "Records", "Version", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{ background-color: {Color.BG_CARD}; color: {Color.TEXT_PRIMARY};
                border: 1px solid {Color.BORDER}; border-radius: 8px; }}
            QHeaderView::section {{ background-color: {Color.BG_LIGHT}; color: {Color.TEXT_SECONDARY}; padding: 10px; }}
        """)
        main_layout.addWidget(self.table)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"color: {Color.TEXT_SECONDARY}; font-size: 12px;")
        main_layout.addWidget(self.status_label)

    def _api_to_row(self, c: dict) -> dict:
        status = c.get("status", "inactive")
        mapped = "connected" if status in ("active", "connected") else "disconnected"
        last_sync = c.get("last_sync")
        return {
            "id": c.get("connector_id", ""),
            "name": c.get("connector_name", ""),
            "system": (c.get("connector_type", "") or "").upper(),
            "status": mapped,
            "last_sync": str(last_sync) if last_sync else "",
            "records": "—",
            "version": c.get("connector_type", "1.0"),
            "raw": c,
        }

    def _load_connectors(self):
        client = get_client()
        self.connectors = []
        if client._token:
            api_list = client.list_connectors()
            self.connectors = [self._api_to_row(c) for c in api_list]
            self.status_label.setText(f"API: {len(self.connectors)} connectors")
        else:
            self.status_label.setText("Log in via API to manage connectors")
        self._refresh_table()

    def _refresh_table(self):
        self.table.setRowCount(0)
        status_map = {"connected": "Connected", "disconnected": "Disconnected", "error": "Error"}
        color_map = {"connected": Color.SUCCESS, "disconnected": Color.ERROR, "error": Color.WARNING}
        for row, c in enumerate(self.connectors):
            self.table.insertRow(row)
            self.table.setRowHeight(row, 44)
            self.table.setItem(row, 0, QTableWidgetItem(c["name"]))
            self.table.setItem(row, 1, QTableWidgetItem(c["system"]))
            status_text = status_map.get(c["status"], c["status"])
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QColor(color_map.get(c["status"], Color.TEXT_SECONDARY)))
            self.table.setItem(row, 2, status_item)
            self.table.setItem(row, 3, QTableWidgetItem(c.get("last_sync", "")))
            self.table.setItem(row, 4, QTableWidgetItem(c.get("records", "0")))
            self.table.setItem(row, 5, QTableWidgetItem(c.get("version", "1.0")))

            action_w = QWidget()
            al = QHBoxLayout(action_w)
            al.setContentsMargins(4, 4, 4, 4)
            for txt, cb in [
                ("Test", lambda x=c: self._test_one(x)),
                ("Delete", lambda x=c: self._delete(x)),
            ]:
                b = QPushButton(txt)
                b.setFixedSize(64, 28)
                b.clicked.connect(cb)
                al.addWidget(b)
            self.table.setCellWidget(row, 6, action_w)

    def _add_connector(self):
        if not get_client()._token:
            QMessageBox.warning(self, "API Login", "Please log in via API first.")
            return
        dialog = ConnectorDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return
        data = dialog.get_data()
        if not data["name"]:
            return
        result = get_client().register_connector({
            "connector_name": data["name"],
            "connector_type": data["connector_type"],
            "company_id": 1,
            "config": {"url": data["url"]},
        })
        if result.get("success"):
            QMessageBox.information(self, "Success", "Connector registered via API")
            self._load_connectors()
        else:
            QMessageBox.warning(self, "Error", "Failed to register connector")

    def _test_one(self, connector):
        cid = connector.get("id")
        if not cid:
            QMessageBox.information(self, "Test", f"{connector['name']}: no API id")
            return
        self.status_label.setText(f"Testing {connector['name']}...")
        result = get_client().test_connector(cid)
        ok = result.get("success") and result.get("data", {}).get("status") == "connected"
        QMessageBox.information(
            self, "Test Result",
            f"{connector['name']}: {'Connected' if ok else 'Failed'}",
        )
        self._load_connectors()

    def _delete(self, connector):
        cid = connector.get("id")
        if not cid:
            return
        if QMessageBox.question(self, "Confirm", f"Delete {connector['name']}?") != QMessageBox.Yes:
            return
        get_client().delete_connector(cid)
        self._load_connectors()

    def _test_all(self):
        client = get_client()
        self.status_label.setText("Testing connections...")
        lines = [f"API: {client.health().get('status', 'unknown')}"]
        for c in self.connectors:
            if c.get("id"):
                r = client.test_connector(c["id"])
                st = r.get("data", {}).get("status", "failed")
                lines.append(f"  {c['name']}: {st}")
        QMessageBox.information(self, "Test Results", "\n".join(lines))
        self.status_label.setText("Ready")
        self._load_connectors()
