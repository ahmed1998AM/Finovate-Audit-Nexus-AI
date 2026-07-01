from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTextEdit, QCheckBox, QRadioButton,
    QFrame, QMessageBox, QScrollArea, QButtonGroup, QStackedWidget
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont
from loguru import logger
from datetime import datetime

from frontend.styles.design_system import DesignSystem, Color, Typography


class CreateProjectWizard(QWidget):
    wizard_completed = Signal(dict)

    STEPS = [
        "المعلومات الأساسية",
        "تفاصيل العميل",
        "فريق العمل",
        "الإعدادات الزمنية",
        "مراجعة وتأكيد"
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_step = 0
        self.project_data = {}
        self.setObjectName("CreateProjectWizard")
        self.setWindowTitle("معالج إنشاء مشروع مراجعة")
        self.setMinimumSize(750, 600)
        self._setup_ui()
        self._show_step(0)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("dialogHeader")
        header.setFixedHeight(90)
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(30, 16, 30, 10)

        title = QLabel("معالج إنشاء مشروع مراجعة جديد")
        title.setObjectName("dialogTitle")
        h_layout.addWidget(title)

        self.step_indicator = QLabel("")
        self.step_indicator.setStyleSheet(f"color: {Color.TEXT_SECONDARY}; font-size: 12px;")
        h_layout.addWidget(self.step_indicator)

        layout.addWidget(header)

        step_bar = QFrame()
        step_bar.setObjectName("stepBar")
        step_bar.setFixedHeight(50)
        s_layout = QHBoxLayout(step_bar)
        s_layout.setContentsMargins(30, 8, 30, 8)

        self.step_labels = []
        for i, name in enumerate(self.STEPS):
            lbl = QLabel(f"{i+1}. {name}")
            lbl.setObjectName(f"stepLabel_{i}")
            lbl.setStyleSheet(f"""
                QLabel {{
                    color: {Color.TEXT_MUTED};
                    font-size: 12px;
                    padding: 4px 12px;
                    border-radius: 12px;
                }}
            """)
            self.step_labels.append(lbl)
            s_layout.addWidget(lbl)
            if i < len(self.STEPS) - 1:
                sep = QLabel("▸")
                sep.setStyleSheet(f"color: {Color.TEXT_MUTED};")
                s_layout.addWidget(sep)

        s_layout.addStretch()
        layout.addWidget(step_bar)

        self.stack = QStackedWidget()
        self.stack.setObjectName("wizardStack")
        layout.addWidget(self.stack, 1)

        button_frame = QFrame()
        button_frame.setObjectName("dialogButtonFrame")
        button_frame.setFixedHeight(60)
        b_layout = QHBoxLayout(button_frame)
        b_layout.setContentsMargins(30, 10, 30, 14)

        self.back_btn = QPushButton("السابق")
        self.back_btn.setObjectName("cancelButton")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setEnabled(False)
        self.back_btn.clicked.connect(self._prev_step)
        b_layout.addWidget(self.back_btn)

        b_layout.addStretch()

        self.next_btn = QPushButton("التالي")
        self.next_btn.setObjectName("createButton")
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.clicked.connect(self._next_step)
        b_layout.addWidget(self.next_btn)

        layout.addWidget(button_frame)

    def _build_step(self, index):
        widget = QWidget()
        widget.setObjectName("wizardStep")
        w_layout = QVBoxLayout(widget)
        w_layout.setContentsMargins(40, 24, 40, 24)

        if index == 0:
            w_layout.addWidget(QLabel("اسم المشروع *:"))
            self.wiz_name = QLineEdit()
            self.wiz_name.setPlaceholderText("أدخل اسم المشروع")
            w_layout.addWidget(self.wiz_name)

            w_layout.addWidget(QLabel("الوصف:"))
            self.wiz_desc = QTextEdit()
            self.wiz_desc.setPlaceholderText("وصف المشروع...")
            self.wiz_desc.setMaximumHeight(80)
            w_layout.addWidget(self.wiz_desc)

            w_layout.addWidget(QLabel("نوع المراجعة *:"))
            self.wiz_type = QComboBox()
            self.wiz_type.addItems([
                "مراجعة القوائم المالية", "مراجعة ضريبية", "مراجعة داخلية",
                "فحص امتثال", "مراجعة تشغيلية", "مراجعة خاصة"
            ])
            w_layout.addWidget(self.wiz_type)

            w_layout.addWidget(QLabel("الأولوية:"))
            self.wiz_priority = QComboBox()
            self.wiz_priority.addItems(["منخفضة", "متوسطة", "عالية", "عاجلة"])
            w_layout.addWidget(self.wiz_priority)

        elif index == 1:
            w_layout.addWidget(QLabel("اسم العميل *:"))
            self.wiz_client = QLineEdit()
            self.wiz_client.setPlaceholderText("أدخل اسم العميل")
            w_layout.addWidget(self.wiz_client)

            w_layout.addWidget(QLabel("القطاع الصناعي:"))
            self.wiz_industry = QComboBox()
            self.wiz_industry.addItems([
                "تقنية", "صناعة", "خدمات مالية", "رعاية صحية",
                "تجارة", "بناء وتشيد", "طاقة", "أخرى"
            ])
            w_layout.addWidget(self.wiz_industry)

            w_layout.addWidget(QLabel("حجم الشركة:"))
            self.wiz_size = QComboBox()
            self.wiz_size.addItems(["صغيرة", "متوسطة", "كبيرة", "متعددة الجنسيات"])
            w_layout.addWidget(self.wiz_size)

            w_layout.addWidget(QLabel("الشخص المسؤول:"))
            self.wiz_contact = QLineEdit()
            self.wiz_contact.setPlaceholderText("اسم الشخص المسؤول")
            w_layout.addWidget(self.wiz_contact)

            w_layout.addWidget(QLabel("البريد الإلكتروني:"))
            self.wiz_email = QLineEdit()
            self.wiz_email.setPlaceholderText("email@example.com")
            w_layout.addWidget(self.wiz_email)

        elif index == 2:
            w_layout.addWidget(QLabel("مدير المشروع *:"))
            self.wiz_manager = QLineEdit()
            self.wiz_manager.setPlaceholderText("اسم مدير المشروع")
            w_layout.addWidget(self.wiz_manager)

            w_layout.addWidget(QLabel("أعضاء الفريق (افصل بينهم بفاصلة):"))
            self.wiz_members = QLineEdit()
            self.wiz_members.setPlaceholderText("مثال: أحمد، سارة، محمد")
            w_layout.addWidget(self.wiz_members)

            w_layout.addWidget(QLabel("خبراء متخصصون:"))
            self.wiz_experts = QLineEdit()
            self.wiz_experts.setPlaceholderText("اختياري")
            w_layout.addWidget(self.wiz_experts)

        elif index == 3:
            w_layout.addWidget(QLabel("تاريخ البدء المتوقع *:"))
            self.wiz_start = QLineEdit()
            self.wiz_start.setPlaceholderText("YYYY-MM-DD")
            w_layout.addWidget(self.wiz_start)

            w_layout.addWidget(QLabel("تاريخ الانتهاء المتوقع *:"))
            self.wiz_end = QLineEdit()
            self.wiz_end.setPlaceholderText("YYYY-MM-DD")
            w_layout.addWidget(self.wiz_end)

            w_layout.addWidget(QLabel("المدة (بالأسابيع):"))
            self.wiz_duration = QLineEdit()
            self.wiz_duration.setPlaceholderText("مثال: 8")
            w_layout.addWidget(self.wiz_duration)

            w_layout.addWidget(QLabel("مراحل المشروع:"))
            self.wiz_phases = {}
            for phase in ["التخطيط والتحضير", "تقييم المخاطر", "اختبار الضوابط",
                           "الإجراءات التفصيلية", "إعداد التقرير", "مراجعة نهائية"]:
                cb = QCheckBox(phase)
                cb.setChecked(True)
                self.wiz_phases[phase] = cb
                w_layout.addWidget(cb)

        elif index == 4:
            self.wiz_summary = QTextEdit()
            self.wiz_summary.setReadOnly(True)
            w_layout.addWidget(QLabel("يرجى مراجعة البيانات أدناه:"))
            w_layout.addWidget(self.wiz_summary, 1)

        w_layout.addStretch()
        return widget

    def _show_step(self, index):
        self.stack.clear()
        widget = self._build_step(index)
        self.stack.addWidget(widget)
        self.current_step = index

        for i, lbl in enumerate(self.step_labels):
            if i < index:
                lbl.setStyleSheet(f"QLabel {{ color: {Color.SUCCESS}; font-size: 12px; padding: 4px 12px; border-radius: 12px; }}")
            elif i == index:
                lbl.setStyleSheet(f"QLabel {{ color: {Color.PRIMARY}; font-size: 12px; font-weight: bold; padding: 4px 12px; border-radius: 12px; background-color: {Color.PRIMARY}20; }}")
            else:
                lbl.setStyleSheet(f"QLabel {{ color: {Color.TEXT_MUTED}; font-size: 12px; padding: 4px 12px; border-radius: 12px; }}")

        self.step_indicator.setText(f"الخطوة {index + 1} من {len(self.STEPS)}")
        self.back_btn.setEnabled(index > 0)
        is_last = index == len(self.STEPS) - 1
        self.next_btn.setText("إنشاء المشروع" if is_last else "التالي")

        if is_last:
            self._collect_data()
            self._update_summary()

    def _collect_data(self):
        try:
            self.project_data = {
                "name": self.wiz_name.text().strip(),
                "description": self.wiz_desc.toPlainText().strip(),
                "audit_type": self.wiz_type.currentText(),
                "priority": self.wiz_priority.currentText(),
                "client_name": self.wiz_client.text().strip(),
                "industry": self.wiz_industry.currentText(),
                "company_size": self.wiz_size.currentText(),
                "contact_person": self.wiz_contact.text().strip(),
                "email": self.wiz_email.text().strip(),
                "manager": self.wiz_manager.text().strip(),
                "members": self.wiz_members.text().strip(),
                "experts": self.wiz_experts.text().strip(),
                "start_date": self.wiz_start.text().strip(),
                "end_date": self.wiz_end.text().strip(),
                "duration_weeks": self.wiz_duration.text().strip(),
                "status": "جديد",
                "progress": 0,
            }
        except AttributeError:
            pass

    def _update_summary(self):
        d = self.project_data
        summary = "=== ملخص مشروع المراجعة ===\n\n"
        summary += "📋 المعلومات الأساسية:\n"
        summary += f"  • اسم المشروع: {d.get('name', '—')}\n"
        summary += f"  • نوع المراجعة: {d.get('audit_type', '—')}\n"
        summary += f"  • الأولوية: {d.get('priority', '—')}\n\n"
        summary += "🏢 العميل:\n"
        summary += f"  • الاسم: {d.get('client_name', '—')}\n"
        summary += f"  • القطاع: {d.get('industry', '—')}\n"
        summary += f"  • المسؤول: {d.get('contact_person', '—')}\n\n"
        summary += "👥 الفريق:\n"
        summary += f"  • المدير: {d.get('manager', '—')}\n"
        summary += f"  • الأعضاء: {d.get('members', '—')}\n\n"
        summary += "📅 الجدول الزمني:\n"
        summary += f"  • من: {d.get('start_date', '—')}\n"
        summary += f"  • إلى: {d.get('end_date', '—')}\n"

        if hasattr(self, 'wiz_summary'):
            self.wiz_summary.setText(summary)

    def _validate_step(self, index):
        try:
            if index == 0:
                if not self.wiz_name.text().strip():
                    QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم المشروع")
                    return False
            elif index == 1:
                if not self.wiz_client.text().strip():
                    QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم العميل")
                    return False
            elif index == 2:
                if not self.wiz_manager.text().strip():
                    QMessageBox.warning(self, "خطأ", "يرجى إدخال مدير المشروع")
                    return False
            elif index == 3:
                if not self.wiz_start.text().strip() or not self.wiz_end.text().strip():
                    QMessageBox.warning(self, "خطأ", "يرجى إدخال تاريخ البدء والانتهاء")
                    return False
        except AttributeError:
            return False
        return True

    def _next_step(self):
        if not self._validate_step(self.current_step):
            return

        if self.current_step < len(self.STEPS) - 1:
            self._show_step(self.current_step + 1)
        else:
            self._collect_data()
            d = self.project_data
            required = ["name", "client_name", "manager", "start_date", "end_date"]
            missing = [f for f in required if not d.get(f)]
            if missing:
                QMessageBox.warning(self, "خطأ", "يرجى تعبئة جميع الحقول الإلزامية")
                return
            d["team"] = f"{d.get('manager', '')}, {d.get('members', '')}"
            d["id"] = None
            d["created_at"] = datetime.now().isoformat()
            self.wizard_completed.emit(d)
            QMessageBox.information(self, "نجاح", f"تم إنشاء مشروع '{d['name']}' بنجاح!")

    def _prev_step(self):
        if self.current_step > 0:
            self._show_step(self.current_step - 1)
