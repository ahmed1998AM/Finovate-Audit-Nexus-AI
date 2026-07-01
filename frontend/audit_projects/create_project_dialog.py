from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QComboBox, QPushButton, QTextEdit, QDateEdit,
    QMessageBox, QFrame, QProgressBar, QWidget
)
from PySide6.QtCore import Qt, QDate, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont
from loguru import logger

from frontend.styles.design_system import DesignSystem, Color, Typography


class CreateProjectDialog(QDialog):
    project_created = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إنشاء مشروع مراجعة جديد")
        self.setMinimumSize(600, 550)
        self.setModal(True)
        self.setStyleSheet(DesignSystem.get_dialog_style())
        self._setup_ui()
        self._animate_in()

    def _animate_in(self):
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(300)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("dialogHeader")
        header.setFixedHeight(90)
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(25, 18, 25, 18)

        title = QLabel("إنشاء مشروع مراجعة جديد")
        title.setObjectName("dialogTitle")
        h_layout.addWidget(title)

        subtitle = QLabel("أدخل معلومات المشروع الأساسية")
        subtitle.setObjectName("dialogSubtitle")
        h_layout.addWidget(subtitle)

        main_layout.addWidget(header)

        content = QWidget()
        content.setObjectName("dialogContent")
        form = QFormLayout(content)
        form.setContentsMargins(25, 20, 25, 20)
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignRight)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("اسم المشروع")
        form.addRow("اسم المشروع:", self.name_input)

        self.client_input = QLineEdit()
        self.client_input.setPlaceholderText("اسم العميل")
        form.addRow("العميل:", self.client_input)

        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "مراجعة مالية", "مراجعة ضريبية", "مراجعة امتثال",
            "مراجعة تشغيلية", "مراجعة داخلية", "تدقيق احتيال"
        ])
        form.addRow("نوع المراجعة:", self.type_combo)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["عالية", "متوسطة", "منخفضة"])
        form.addRow("الأولوية:", self.priority_combo)

        self.manager_input = QLineEdit()
        self.manager_input.setPlaceholderText("اسم مدير المشروع")
        form.addRow("مدير المشروع:", self.manager_input)

        dates_widget = QWidget()
        dates_layout = QHBoxLayout(dates_widget)
        dates_layout.setContentsMargins(0, 0, 0, 0)
        self.start_date = QDateEdit(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        dates_layout.addWidget(QLabel("من:"))
        dates_layout.addWidget(self.start_date)
        dates_layout.addSpacing(15)
        self.end_date = QDateEdit(QDate.currentDate().addMonths(3))
        self.end_date.setCalendarPopup(True)
        dates_layout.addWidget(QLabel("إلى:"))
        dates_layout.addWidget(self.end_date)
        form.addRow("الفترة:", dates_widget)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("وصف المشروع...")
        self.desc_input.setMaximumHeight(100)
        form.addRow("الوصف:", self.desc_input)

        main_layout.addWidget(content, 1)

        progress_frame = QFrame()
        progress_frame.setObjectName("progressFrame")
        p_layout = QVBoxLayout(progress_frame)
        p_layout.setContentsMargins(25, 8, 25, 8)
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("formProgress")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        p_layout.addWidget(self.progress_bar)
        main_layout.addWidget(progress_frame)

        button_frame = QFrame()
        button_frame.setObjectName("dialogButtonFrame")
        btn_layout = QHBoxLayout(button_frame)
        btn_layout.setContentsMargins(25, 12, 25, 16)
        btn_layout.addStretch()

        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        create_btn = QPushButton("إنشاء المشروع")
        create_btn.setObjectName("createButton")
        create_btn.setCursor(Qt.PointingHandCursor)
        create_btn.setDefault(True)
        create_btn.clicked.connect(self._on_accept)
        btn_layout.addWidget(create_btn)

        main_layout.addWidget(button_frame)

        self.name_input.textChanged.connect(self._update_progress)
        self.client_input.textChanged.connect(self._update_progress)

    def _update_progress(self):
        filled = 0
        if self.name_input.text().strip():
            filled += 1
        if self.client_input.text().strip():
            filled += 1
        pct = int((filled / 2) * 100)
        self.progress_bar.setValue(pct)

    def _on_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال اسم المشروع")
            self.name_input.setFocus()
            return

        data = {
            "name": self.name_input.text().strip(),
            "client": self.client_input.text().strip() or "غير محدد",
            "audit_type": self.type_combo.currentText(),
            "priority": self.priority_combo.currentText(),
            "manager": self.manager_input.text().strip() or "غير محدد",
            "start_date": self.start_date.date().toString("yyyy-MM-dd"),
            "end_date": self.end_date.date().toString("yyyy-MM-dd"),
            "description": self.desc_input.toPlainText().strip(),
            "status": "جديد",
            "progress": 0,
            "team": self.manager_input.text().strip() or "غير محدد",
        }
        self.project_created.emit(data)
        self.accept()
