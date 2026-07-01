from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QMessageBox, QLineEdit, QComboBox, QMenu, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QFont, QAction, QCursor
from loguru import logger

from frontend.styles.design_system import DesignSystem, Color, Typography


class ProjectListWindow(QWidget):
    project_selected = Signal(dict)
    create_requested = Signal()

    # Status keys are Arabic user-facing strings matching the filter dropdown & data
    STATUS_COLORS = {
        "جديد": QColor(Color.INFO),           # New
        "قيد التنفيذ": QColor(Color.WARNING),  # In Progress
        "مكتمل": QColor(Color.SUCCESS),        # Completed
        "متوقف": QColor(Color.TEXT_SECONDARY), # On Hold
    }
    PRIORITY_COLORS = {
        "عالية": QColor(Color.ERROR),     # High
        "متوسطة": QColor(Color.WARNING),  # Medium
        "منخفضة": QColor(Color.SUCCESS),  # Low
        "عاجلة": QColor(Color.ERROR),     # Urgent
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.projects = []
        self.setObjectName("ProjectListWindow")
        self._setup_ui()
        self._load_projects()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("listHeader")
        header.setFixedHeight(80)
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(24, 16, 24, 10)

        top_row = QHBoxLayout()
        title = QLabel("📁 مشاريع المراجعة")
        title.setObjectName("listTitle")
        top_row.addWidget(title)
        top_row.addStretch()

        self.add_btn = QPushButton("+ مشروع جديد")
        self.add_btn.setObjectName("createButton")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setFixedHeight(36)
        self.add_btn.clicked.connect(self.create_requested.emit)
        top_row.addWidget(self.add_btn)

        self.refresh_btn = QPushButton("تحديث")
        self.refresh_btn.setObjectName("primaryButton")
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.setFixedHeight(36)
        self.refresh_btn.clicked.connect(self._load_projects)
        top_row.addWidget(self.refresh_btn)

        h_layout.addLayout(top_row)
        layout.addWidget(header)

        filter_bar = QFrame()
        filter_bar.setObjectName("filterBar")
        filter_bar.setFixedHeight(56)
        f_layout = QHBoxLayout(filter_bar)
        f_layout.setContentsMargins(24, 8, 24, 8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 بحث في المشاريع...")
        self.search_input.textChanged.connect(self._filter_projects)
        self.search_input.setFixedWidth(260)
        self.search_input.setObjectName("searchInput")
        f_layout.addWidget(self.search_input)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["الكل", "جديد", "قيد التنفيذ", "مكتمل", "متوقف"])
        self.status_filter.currentTextChanged.connect(self._filter_projects)
        self.status_filter.setFixedWidth(130)
        f_layout.addWidget(self.status_filter)

        f_layout.addStretch()

        self.count_label = QLabel("عدد المشاريع:")
        self.count_label.setStyleSheet(f"color: {Color.TEXT_SECONDARY}; font-size: 13px;")
        f_layout.addWidget(self.count_label)

        self.status_label = QLabel("0")
        self.status_label.setStyleSheet(f"color: {Color.TEXT_WHITE}; font-size: 13px; font-weight: 600;")
        f_layout.addWidget(self.status_label)

        layout.addWidget(filter_bar)

        table_container = QFrame()
        table_container.setObjectName("tableContainer")
        t_layout = QVBoxLayout(table_container)
        t_layout.setContentsMargins(24, 8, 24, 24)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "#", "اسم المشروع", "العميل", "الحالة",
            "تاريخ البدء", "تاريخ الانتهاء", "التقدم", "الفريق", "الأولوية"
        ])
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(QHeaderView.Stretch)
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

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
            QScrollBar:vertical {{
                background-color: {Color.BG_DARK};
                width: 8px;
                border: none;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {Color.BORDER};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {Color.BORDER_LIGHT};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)

        self.table.doubleClicked.connect(self._open_selected)
        t_layout.addWidget(self.table)
        layout.addWidget(table_container, 1)

    def _load_projects(self):
        self.projects = [
            {"id": 1, "name": "مراجعة القوائم المالية 2024", "client": "شركة التقنية المتقدمة", "status": "قيد التنفيذ", "start_date": "2024-01-15", "end_date": "2024-03-15", "progress": 65, "team": "أحمد، سارة", "priority": "عالية"},
            {"id": 2, "name": "مراجعة ضريبية ربع سنوية", "client": "مجموعة الأفق", "status": "جديد", "start_date": "2024-02-01", "end_date": "2024-02-28", "progress": 10, "team": "فاطمة", "priority": "متوسطة"},
            {"id": 3, "name": "فحص الامتثال الداخلي", "client": "البنك الأهلي", "status": "مكتمل", "start_date": "2023-11-01", "end_date": "2023-12-31", "progress": 100, "team": "أحمد، فاطمة", "priority": "عالية"},
            {"id": 4, "name": "مراجعة المشتريات", "client": "شركة البناء الحديثة", "status": "قيد التنفيذ", "start_date": "2024-01-20", "end_date": "2024-04-20", "progress": 45, "team": "خالد", "priority": "منخفضة"},
        ]
        self._refresh_table()

    def _refresh_table(self, filtered=None):
        self.table.setRowCount(0)
        items = filtered if filtered is not None else self.projects

        for row, p in enumerate(items):
            self.table.insertRow(row)
            self.table.setRowHeight(row, 48)
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
        if status != "الكل":
            filtered = [p for p in filtered if p.get("status") == status]
        self._refresh_table(filtered)

    def _open_selected(self):
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 0)
        if not item:
            return
        pid = int(item.text())
        project = next((p for p in self.projects if p.get("id") == pid), None)
        if project:
            self.project_selected.emit(project)

    def _show_context_menu(self, pos):
        row = self.table.rowAt(pos.y())
        if row < 0:
            return
        self.table.selectRow(row)
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {Color.BG_MEDIUM};
                border: 1px solid {Color.BORDER};
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 8px 24px;
                color: {Color.TEXT_PRIMARY};
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {Color.PRIMARY}30;
                color: {Color.TEXT_WHITE};
            }}
        """)
        menu.addAction("📂 فتح المشروع", self._open_selected)
        menu.addAction("✏️ تعديل")
        menu.addSeparator()
        menu.addAction("📤 تصدير")
        menu.addAction("🗑️ حذف")
        menu.exec(QCursor.pos())
