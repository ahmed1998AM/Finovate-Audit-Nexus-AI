"""Report viewer — list, create, preview, and export audit reports."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QTextBrowser,
    QMessageBox, QComboBox, QSplitter, QFrame,
)
from PySide6.QtCore import Qt, QTimer
from loguru import logger

from frontend.api_client import get_client
from frontend.styles.design_system import Color


class ReportViewerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._reports: list = []
        self._selected_id: str = ""
        self._setup_ui()
        self._load_reports()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("التقارير")
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {Color.TEXT_PRIMARY};")
        header.addWidget(title)
        header.addStretch()

        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {Color.TEXT_SECONDARY}; font-size: 12px;")
        header.addWidget(self.status_label)

        refresh_btn = QPushButton("تحديث")
        refresh_btn.clicked.connect(self._load_reports)
        header.addWidget(refresh_btn)

        create_btn = QPushButton("تقرير جديد")
        create_btn.clicked.connect(self._create_report)
        header.addWidget(create_btn)
        layout.addLayout(header)

        splitter = QSplitter(Qt.Horizontal)

        left = QFrame()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["المعرف", "المشروع", "النوع", "الحالة"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_row_selected)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background: {Color.BG_CARD}; color: {Color.TEXT_PRIMARY};
                border: 1px solid {Color.BORDER}; border-radius: 8px;
            }}
            QHeaderView::section {{
                background: {Color.BG_MEDIUM}; color: {Color.TEXT_PRIMARY}; padding: 8px;
            }}
        """)
        left_layout.addWidget(self.table)

        export_row = QHBoxLayout()
        self.format_combo = QComboBox()
        self.format_combo.addItems(["pdf", "html", "json", "xlsx"])
        export_row.addWidget(self.format_combo)
        export_btn = QPushButton("تصدير")
        export_btn.clicked.connect(self._export_report)
        export_row.addWidget(export_btn)
        summary_btn = QPushButton("ملخص تنفيذي")
        summary_btn.clicked.connect(self._show_summary)
        export_row.addWidget(summary_btn)
        left_layout.addLayout(export_row)
        splitter.addWidget(left)

        self.preview = QTextBrowser()
        self.preview.setStyleSheet(f"""
            QTextBrowser {{
                background: {Color.BG_CARD}; color: {Color.TEXT_PRIMARY};
                border: 1px solid {Color.BORDER}; border-radius: 8px; padding: 12px;
            }}
        """)
        self.preview.setPlaceholderText("اختر تقريراً لعرض الملخص التنفيذي...")
        splitter.addWidget(self.preview)
        splitter.setSizes([500, 400])
        layout.addWidget(splitter)

        timer = QTimer(self)
        timer.timeout.connect(self._load_reports)
        timer.start(60000)

    def _set_status(self, text: str, offline: bool = False):
        color = Color.WARNING if offline else Color.TEXT_SECONDARY
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color}; font-size: 12px;")

    def _load_reports(self):
        client = get_client()
        if not client.check_available():
            self._set_status("غير متصل بالخادم", offline=True)
            return
        if not client._token:
            self._set_status("سجّل الدخول عبر API لعرض التقارير", offline=True)
            return

        reports = client.list_reports()
        self._reports = reports
        self.table.setRowCount(0)
        for row, rpt in enumerate(reports):
            self.table.insertRow(row)
            rid = rpt.get("report_id", "")
            self.table.setItem(row, 0, QTableWidgetItem(rid))
            self.table.setItem(row, 1, QTableWidgetItem(str(rpt.get("project_id", ""))))
            self.table.setItem(row, 2, QTableWidgetItem(rpt.get("report_type", "")))
            self.table.setItem(row, 3, QTableWidgetItem(rpt.get("status", "draft")))
        self._set_status(f"{len(reports)} تقرير")

    def _on_row_selected(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        item = self.table.item(row, 0)
        if item:
            self._selected_id = item.text()

    def _create_report(self):
        client = get_client()
        if not client._token:
            QMessageBox.warning(self, "تسجيل الدخول", "يجب تسجيل الدخول عبر API أولاً.")
            return
        result = client.create_report(project_id="1", report_type="audit")
        if result.get("success"):
            data = result.get("data", {})
            QMessageBox.information(self, "تم", f"تم إنشاء التقرير: {data.get('report_id', '')}")
            self._load_reports()
        else:
            QMessageBox.warning(self, "خطأ", "تعذّر إنشاء التقرير.")

    def _show_summary(self):
        if not self._selected_id:
            QMessageBox.information(self, "اختيار", "اختر تقريراً من الجدول.")
            return
        client = get_client()
        result = client.generate_report_summary(self._selected_id)
        if not result.get("success"):
            QMessageBox.warning(self, "خطأ", "تعذّر توليد الملخص.")
            return
        summary = result.get("data", {}).get("executive_summary", result.get("data", {}))
        lines = ["<h2>الملخص التنفيذي</h2>"]
        if isinstance(summary, dict):
            for key, val in summary.items():
                lines.append(f"<p><b>{key}:</b> {val}</p>")
        else:
            lines.append(f"<p>{summary}</p>")
        self.preview.setHtml("\n".join(lines))

    def _export_report(self):
        if not self._selected_id:
            QMessageBox.information(self, "اختيار", "اختر تقريراً من الجدول.")
            return
        fmt = self.format_combo.currentText()
        client = get_client()
        result = client.export_report(self._selected_id, fmt)
        if result.get("success"):
            path = result.get("data", {}).get("file_path", result.get("data", {}).get("path", ""))
            QMessageBox.information(self, "تصدير", f"تم التصدير بنجاح.\n{path}")
        else:
            QMessageBox.warning(self, "خطأ", "تعذّر تصدير التقرير.")
