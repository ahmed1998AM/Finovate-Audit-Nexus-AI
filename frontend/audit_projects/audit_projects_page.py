from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QMessageBox, QLineEdit, QComboBox, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from loguru import logger
from frontend.api_client import get_client
from frontend.styles.design_system import Color


class AuditProjectsPage(QWidget):
    project_opened = Signal(dict)

    STATUS_COLORS = {
        "New": QColor(Color.INFO),
        "In Progress": QColor(Color.WARNING),
        "Completed": QColor(Color.SUCCESS),
        "On Hold": QColor(Color.TEXT_SECONDARY),
    }
    PRIORITY_COLORS = {
        "High": QColor(Color.ERROR),
        "Medium": QColor(Color.WARNING),
        "Low": QColor(Color.SUCCESS),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AuditProjectsPage")
        self.projects = []
        self._setup_ui()
        self._load_projects()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("listHeader")
        header.setFixedHeight(70)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 16, 24, 16)

        title = QLabel("مشاريع التدقيق")
        title.setObjectName("listTitle")
        h_layout.addWidget(title)
        h_layout.addStretch()

        self.add_btn = QPushButton("+ مشروع جديد")
        self.add_btn.setObjectName("createButton")
        self.add_btn.setFixedHeight(36)
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.clicked.connect(self._create_project)
        h_layout.addWidget(self.add_btn)

        self.refresh_btn = QPushButton("تحديث")
        self.refresh_btn.setObjectName("primaryButton")
        self.refresh_btn.setFixedHeight(36)
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.clicked.connect(self._load_projects)
        h_layout.addWidget(self.refresh_btn)

        main_layout.addWidget(header)

        filter_bar = QFrame()
        filter_bar.setObjectName("filterBar")
        filter_bar.setFixedHeight(56)
        f_layout = QHBoxLayout(filter_bar)
        f_layout.setContentsMargins(24, 8, 24, 8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 بحث في المشاريع...")
        self.search_input.textChanged.connect(self._filter_projects)
        self.search_input.setFixedWidth(260)
        self.search_input.setPlaceholderText("بحث في المشاريع...")
        f_layout.addWidget(self.search_input)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "New", "In Progress", "Completed", "On Hold"])
        self.status_filter.currentTextChanged.connect(self._filter_projects)
        self.status_filter.setFixedWidth(140)
        f_layout.addWidget(self.status_filter)

        f_layout.addStretch()

        count_label = QLabel("عدد المشاريع:")
        count_label.setStyleSheet(f"color: {Color.TEXT_SECONDARY}; font-size: 13px;")
        f_layout.addWidget(count_label)

        self.status_label = QLabel("0")
        self.status_label.setStyleSheet(f"color: {Color.TEXT_WHITE}; font-size: 13px; font-weight: 600;")
        f_layout.addWidget(self.status_label)

        main_layout.addWidget(filter_bar)

        table_container = QFrame()
        table_container.setObjectName("tableContainer")
        t_layout = QVBoxLayout(table_container)
        t_layout.setContentsMargins(24, 8, 24, 24)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "#", "Project Name", "Client", "Status", "Start Date",
            "End Date", "Progress", "Team", "Priority"
        ])
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(QHeaderView.Stretch)
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.doubleClicked.connect(self._open_project)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {Color.BG_MEDIUM};
                alternate-background-color: {Color.BG_CARD};
                border: 1px solid {Color.BORDER};
                border-radius: 8px;
                gridline-color: transparent;
                outline: none;
            }}
            QTableWidget::item {{
                padding: 8px 12px;
                border-bottom: 1px solid {Color.BORDER};
                color: {Color.TEXT_PRIMARY};
            }}
            QTableWidget::item:selected {{
                background-color: {Color.PRIMARY}30;
                color: {Color.TEXT_WHITE};
            }}
            QHeaderView::section {{
                background-color: {Color.BG_LIGHT};
                color: {Color.TEXT_SECONDARY};
                padding: 10px 12px;
                border: none;
                border-bottom: 1px solid {Color.BORDER};
                font-weight: 600;
                font-size: 12px;
            }}
        """)
        t_layout.addWidget(self.table)
        main_layout.addWidget(table_container, 1)

    def _map_api_project(self, p: dict) -> dict:
        status = p.get("status", "Planning")
        status_display = {
            "Planning": "New",
            "Running": "In Progress",
            "Completed": "Completed",
            "Failed": "On Hold",
        }.get(status, status)
        sd = p.get("start_date")
        ed = p.get("end_date")
        return {
            "id": p.get("id"),
            "name": p.get("project_name", ""),
            "client": f"Company #{p.get('company_id', 1)}",
            "status": status_display,
            "start_date": sd[:10] if isinstance(sd, str) else (sd.strftime("%Y-%m-%d") if sd else ""),
            "end_date": ed[:10] if isinstance(ed, str) else (ed.strftime("%Y-%m-%d") if ed else ""),
            "progress": 100 if status == "Completed" else (50 if status == "Running" else 10),
            "team": "—",
            "priority": p.get("risk_level", "Medium"),
            "audit_type": p.get("audit_type", ""),
            "raw": p,
        }

    def _load_projects(self):
        client = get_client()
        self.projects = []
        if client._token:
            try:
                data = client.get_audit_projects()
                self.projects = [self._map_api_project(p) for p in (data if isinstance(data, list) else [])]
            except Exception as e:
                logger.warning(f"Failed to load projects from API: {e}")
        if not self.projects:
            self.status_label.setText("0 (offline — log in via API)")
        self._refresh_table()

    def _refresh_table(self, filtered=None):
        self.table.setRowCount(0)
        items = filtered if filtered is not None else self.projects

        for row, p in enumerate(items):
            self.table.insertRow(row)
            self.table.setRowHeight(row, 44)
            self.table.setItem(row, 0, QTableWidgetItem(str(p.get("id", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(p.get("name", "")))
            self.table.setItem(row, 2, QTableWidgetItem(p.get("client", "")))

            status_item = QTableWidgetItem(p.get("status", ""))
            status_item.setForeground(self.STATUS_COLORS.get(p.get("status", ""), QColor(Color.TEXT_SECONDARY)))
            self.table.setItem(row, 3, status_item)

            self.table.setItem(row, 4, QTableWidgetItem(str(p.get("start_date", ""))))
            self.table.setItem(row, 5, QTableWidgetItem(str(p.get("end_date", ""))))
            self.table.setItem(row, 6, QTableWidgetItem(f"{p.get('progress', 0)}%"))
            self.table.setItem(row, 7, QTableWidgetItem(p.get("team", "")))

            priority_item = QTableWidgetItem(p.get("priority", ""))
            priority_item.setForeground(self.PRIORITY_COLORS.get(p.get("priority", ""), QColor(Color.TEXT_SECONDARY)))
            self.table.setItem(row, 8, priority_item)

        self.status_label.setText(str(len(items)))

    def _filter_projects(self):
        search = self.search_input.text().lower()
        status = self.status_filter.currentText()
        filtered = self.projects
        if search:
            filtered = [p for p in filtered if search in p.get("name", "").lower() or search in p.get("client", "").lower()]
        if status != "All":
            filtered = [p for p in filtered if p.get("status") == status]
        self._refresh_table(filtered)

    def _create_project(self):
        from .create_project_dialog import CreateProjectDialog
        dialog = CreateProjectDialog(self)
        dialog.project_created.connect(self._on_project_created)
        dialog.exec()

    def _on_project_created(self, data):
        client = get_client()
        if client._token:
            from datetime import datetime
            payload = {
                "company_id": 1,
                "project_name": data.get("name", ""),
                "audit_type": data.get("audit_type", "مراجعة مالية"),
                "scope": data.get("description", ""),
                "objectives": data.get("manager", ""),
            }
            sd = data.get("start_date")
            ed = data.get("end_date")
            if sd:
                payload["start_date"] = sd
            if ed:
                payload["end_date"] = ed
            result = client.create_audit_project(payload)
            if result and result.get("id"):
                self._load_projects()
                QMessageBox.information(self, "نجاح", "تم إنشاء المشروع عبر API")
                return
        data["id"] = len(self.projects) + 1
        self.projects.append(data)
        self._refresh_table()
        QMessageBox.information(self, "نجاح", "تم إنشاء المشروع محلياً (سجّل دخول API للحفظ)")

    def _open_project(self):
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 0)
        if not item:
            return
        pid = int(item.text())
        project = next((p for p in self.projects if p.get("id") == pid), None)
        if project:
            self.project_opened.emit(project)
