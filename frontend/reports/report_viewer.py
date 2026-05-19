"""
Finovate Audit Nexus AI - Report Viewer Widget
عارض التقارير الاحترافي
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QGridLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class ReportViewerWidget(QWidget):
    """واجهة عرض التقارير"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ReportViewerWidget")
        self._setup_ui()

    def _setup_ui(self):
        """إعداد الواجهة"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # العنوان الرئيسي
        title_label = QLabel("📑 عرض التقارير")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        main_layout.addWidget(title_label)

        # أزرار الإجراءات
        actions_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 تحديث")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        actions_layout.addWidget(refresh_btn)

        export_btn = QPushButton("📤 تصدير")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        actions_layout.addWidget(export_btn)

        actions_layout.addStretch()
        main_layout.addLayout(actions_layout)

        # جدول التقارير
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "اسم التقرير", "النوع", "التاريخ", "الحجم", "الإجراءات"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)

        # إضافة بيانات تجريبية
        sample_reports = [
            ("تقرير التدقيق الشامل Q1 2025", "PDF", "2025-01-15", "2.5 MB"),
            ("تحليل المخاطر المالية", "Excel", "2025-01-14", "1.8 MB"),
            ("تقرير الامتثال الضريبي", "PDF", "2025-01-13", "3.2 MB"),
            ("كشف الاحتيال - يناير", "HTML", "2025-01-12", "0.5 MB"),
            ("ميزان المراجعة التفصيلي", "Excel", "2025-01-11", "4.1 MB"),
        ]

        self.table.setRowCount(len(sample_reports))
        for row, (name, type_, date, size) in enumerate(sample_reports):
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(type_))
            self.table.setItem(row, 2, QTableWidgetItem(date))
            self.table.setItem(row, 3, QTableWidgetItem(size))

            # زر الإجراء
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 5, 5, 5)

            view_btn = QPushButton("👁️")
            view_btn.setFixedSize(40, 30)
            view_btn.setToolTip("عرض")
            action_layout.addWidget(view_btn)

            download_btn = QPushButton("📥")
            download_btn.setFixedSize(40, 30)
            download_btn.setToolTip("تنزيل")
            action_layout.addWidget(download_btn)

            action_layout.addStretch()
            self.table.setCellWidget(row, 4, action_widget)

        main_layout.addWidget(self.table)

    def load_reports(self):
        """تحميل قائمة التقارير"""
        # سيتم تنفيذه عبر خدمة التقارير
        pass


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    widget = ReportViewerWidget()
    widget.show()
    sys.exit(app.exec())
