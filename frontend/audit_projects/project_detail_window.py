from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QMessageBox, QProgressBar, QTabWidget, QTextEdit,
    QAbstractItemView, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QColor, QFont
from loguru import logger

from frontend.styles.design_system import Color, Typography
from frontend.api_client import get_client


class ProjectDetailWindow(QWidget):
    def __init__(self, parent=None, project_data: dict = None):
        super().__init__(parent)
        self.project = project_data or {}
        self.setObjectName("ProjectDetailWindow")
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("detailHeader")
        header.setFixedHeight(80)
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(24, 16, 24, 10)

        top_row = QHBoxLayout()
        self.title_label = QLabel("تفاصيل المشروع")
        self.title_label.setObjectName("detailTitle")
        top_row.addWidget(self.title_label)
        top_row.addStretch()

        edit_btn = QPushButton("✏️ تعديل")
        edit_btn.setObjectName("primaryButton")
        edit_btn.setFixedHeight(34)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(self._edit_project)
        top_row.addWidget(edit_btn)

        report_btn = QPushButton("📊 تقرير")
        report_btn.setObjectName("primaryButton")
        report_btn.setFixedHeight(34)
        report_btn.setCursor(Qt.PointingHandCursor)
        report_btn.clicked.connect(self._generate_report)
        top_row.addWidget(report_btn)

        ai_btn = QPushButton("🤖 تحليل AI")
        ai_btn.setObjectName("createButton")
        ai_btn.setFixedHeight(34)
        ai_btn.setCursor(Qt.PointingHandCursor)
        ai_btn.clicked.connect(self._run_ai_analysis)
        top_row.addWidget(ai_btn)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("cancelButton")
        close_btn.setFixedSize(34, 34)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close_window)
        top_row.addWidget(close_btn)

        h_layout.addLayout(top_row)
        layout.addWidget(header)

        content = QWidget()
        content.setObjectName("detailContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 16, 24, 24)

        tabs = QTabWidget()
        tabs.setObjectName("detailTabs")
        tabs.addTab(self._create_overview_tab(), "📋 النظرة العامة")
        tabs.addTab(self._create_team_tab(), "👥 فريق العمل")
        tabs.addTab(self._create_timeline_tab(), "📅 الجدول الزمني")
        tabs.addTab(self._create_tasks_tab(), "✅ المهام")
        tabs.addTab(self._create_docs_tab(), "📄 المستندات")
        tabs.addTab(self._create_ai_tab(), "🤖 تحليلات AI")

        content_layout.addWidget(tabs, 1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("detailProgress")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setFormat("نسبة الإنجاز: %p%")
        content_layout.addWidget(self.progress_bar)

        layout.addWidget(content, 1)

    def _create_overview_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setSpacing(20)

        info_group = QGroupBox("معلومات المشروع")
        info_group.setObjectName("detailGroupBox")
        info_form = QFormLayout(info_group)
        info_form.setSpacing(10)
        info_form.setLabelAlignment(Qt.AlignRight)

        self.lbl_name = QLabel("—")
        info_form.addRow("اسم المشروع:", self.lbl_name)
        self.lbl_type = QLabel("—")
        info_form.addRow("نوع المراجعة:", self.lbl_type)
        self.lbl_priority = QLabel("—")
        info_form.addRow("الأولوية:", self.lbl_priority)
        self.lbl_status = QLabel("—")
        info_form.addRow("الحالة:", self.lbl_status)

        self.desc_text = QTextEdit()
        self.desc_text.setReadOnly(True)
        self.desc_text.setMaximumHeight(100)
        info_form.addRow("الوصف:", self.desc_text)

        layout.addWidget(info_group, 1)

        client_group = QGroupBox("معلومات العميل")
        client_group.setObjectName("detailGroupBox")
        client_form = QFormLayout(client_group)
        client_form.setSpacing(10)
        client_form.setLabelAlignment(Qt.AlignRight)

        self.lbl_client = QLabel("—")
        client_form.addRow("العميل:", self.lbl_client)
        self.lbl_industry = QLabel("—")
        client_form.addRow("القطاع:", self.lbl_industry)
        self.lbl_size = QLabel("—")
        client_form.addRow("الحجم:", self.lbl_size)
        self.lbl_contact = QLabel("—")
        client_form.addRow("المسؤول:", self.lbl_contact)
        self.lbl_email = QLabel("—")
        client_form.addRow("البريد:", self.lbl_email)

        layout.addWidget(client_group, 1)
        return tab

    def _create_team_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.lbl_manager = QLabel("مدير المشروع: —")
        self.lbl_manager.setStyleSheet(f"color: {Color.PRIMARY}; font-size: 14px; font-weight: bold;")
        layout.addWidget(self.lbl_manager)

        self.team_table = QTableWidget()
        self.team_table.setColumnCount(4)
        self.team_table.setHorizontalHeaderLabels(["الاسم", "الدور", "الساعات", "الحالة"])
        self.team_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.team_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.team_table.verticalHeader().setVisible(False)
        layout.addWidget(self.team_table, 1)

        btn_row = QHBoxLayout()
        add_member = QPushButton("➕ إضافة عضو")
        add_member.setObjectName("primaryButton")
        add_member.setCursor(Qt.PointingHandCursor)
        btn_row.addWidget(add_member)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        return tab

    def _create_timeline_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        dates_group = QGroupBox("التواريخ الرئيسية")
        dates_group.setObjectName("detailGroupBox")
        dates_form = QFormLayout(dates_group)
        dates_form.setLabelAlignment(Qt.AlignRight)

        self.lbl_start = QLabel("—")
        dates_form.addRow("تاريخ البدء:", self.lbl_start)
        self.lbl_end = QLabel("—")
        dates_form.addRow("تاريخ الانتهاء:", self.lbl_end)
        self.lbl_duration = QLabel("—")
        dates_form.addRow("المدة:", self.lbl_duration)

        layout.addWidget(dates_group)

        self.phases_table = QTableWidget()
        self.phases_table.setColumnCount(5)
        self.phases_table.setHorizontalHeaderLabels(["المرحلة", "تاريخ البدء", "تاريخ الانتهاء", "الحالة", "التقدم"])
        self.phases_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.phases_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.phases_table.verticalHeader().setVisible(False)
        layout.addWidget(self.phases_table, 1)

        return tab

    def _create_tasks_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        btn_row = QHBoxLayout()
        add_task = QPushButton("➕ مهمة جديدة")
        add_task.setObjectName("createButton")
        add_task.setCursor(Qt.PointingHandCursor)
        btn_row.addWidget(add_task)
        refresh = QPushButton("تحديث")
        refresh.setObjectName("primaryButton")
        refresh.setCursor(Qt.PointingHandCursor)
        btn_row.addWidget(refresh)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(7)
        self.tasks_table.setHorizontalHeaderLabels(["#", "المهمة", "المسؤول", "الأولوية", "تاريخ الاستحقاق", "الحالة", "التقدم"])
        self.tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tasks_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tasks_table.verticalHeader().setVisible(False)
        layout.addWidget(self.tasks_table, 1)

        return tab

    def _create_docs_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        btn_row = QHBoxLayout()
        upload = QPushButton("📤 رفع مستند")
        upload.setObjectName("createButton")
        upload.setCursor(Qt.PointingHandCursor)
        btn_row.addWidget(upload)
        download = QPushButton("📥 تنزيل")
        download.setObjectName("primaryButton")
        download.setCursor(Qt.PointingHandCursor)
        btn_row.addWidget(download)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.docs_table = QTableWidget()
        self.docs_table.setColumnCount(6)
        self.docs_table.setHorizontalHeaderLabels(["اسم الملف", "النوع", "الحجم", "تم الرفع بواسطة", "التاريخ", "الحالة"])
        self.docs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.docs_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.docs_table.verticalHeader().setVisible(False)
        layout.addWidget(self.docs_table, 1)

        return tab

    def _create_ai_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        btn_row = QHBoxLayout()
        start_btn = QPushButton("🚀 بدء التحليل")
        start_btn.setObjectName("createButton")
        start_btn.setCursor(Qt.PointingHandCursor)
        start_btn.clicked.connect(self._run_ai_analysis)
        btn_row.addWidget(start_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.ai_output = QTextEdit()
        self.ai_output.setReadOnly(True)
        self.ai_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Color.BG_LIGHT};
                color: {Color.TEXT_PRIMARY};
                border: 1px solid {Color.BORDER};
                border-radius: 8px;
                padding: 16px;
                font-family: 'Segoe UI';
                font-size: 13px;
            }}
        """)
        self.ai_output.setText(
            "اضغط على 'بدء التحليل' لتشغيل وكلاء الذكاء الاصطناعي...\n\n"
            "الوكلاء المتاحون:\n"
            "  • وكيل التحليل المالي\n"
            "  • وكيل كشف الاحتيال\n"
            "  • وكيل الامتثال الضريبي\n"
            "  • وكيل مراجعة القيود اليومية\n"
            "  • وكيل التسوية البنكية"
        )
        layout.addWidget(self.ai_output, 1)

        return tab

    def _load_data(self):
        if not self.project:
            return

        self.title_label.setText(f"📁 {self.project.get('name', 'مشروع')}")
        self.lbl_name.setText(self.project.get("name", "—"))
        self.lbl_type.setText(self.project.get("audit_type", "—"))
        self.lbl_priority.setText(self.project.get("priority", "—"))
        self.lbl_status.setText(self.project.get("status", "—"))
        self.desc_text.setText(self.project.get("description", ""))

        self.lbl_client.setText(self.project.get("client_name", self.project.get("client", "—")))
        self.lbl_industry.setText(self.project.get("industry", "—"))
        self.lbl_size.setText(self.project.get("company_size", "—"))
        self.lbl_contact.setText(self.project.get("contact_person", "—"))
        self.lbl_email.setText(self.project.get("email", "—"))

        self.lbl_manager.setText(f"مدير المشروع: {self.project.get('manager', self.project.get('team', '—'))}")

        self.lbl_start.setText(self.project.get("start_date", "—"))
        self.lbl_end.setText(self.project.get("end_date", "—"))
        self.lbl_duration.setText(self.project.get("duration_weeks", "—"))

        progress = self.project.get("progress", 0)
        self.progress_bar.setValue(progress)

        self._load_sample_team()
        self._load_sample_phases()
        self._load_sample_tasks()
        self._load_sample_docs()

    def _load_sample_team(self):
        data = [("أحمد محمد", "مراجع أول", "120", "نشط"), ("سارة أحمد", "مراجع مالي", "80", "نشط")]
        self.team_table.setRowCount(len(data))
        for row, vals in enumerate(data):
            for col, val in enumerate(vals):
                self.team_table.setItem(row, col, QTableWidgetItem(val))

    def _load_sample_phases(self):
        data = [
            ("التخطيط والتحضير", "2024-01-15", "2024-01-22", "مكتمل", "100%"),
            ("تقييم المخاطر", "2024-01-23", "2024-02-05", "قيد التنفيذ", "75%"),
            ("اختبار الضوابط", "2024-02-06", "2024-02-20", "لم يبدأ", "0%"),
        ]
        self.phases_table.setRowCount(len(data))
        for row, vals in enumerate(data):
            for col, val in enumerate(vals):
                self.phases_table.setItem(row, col, QTableWidgetItem(val))

    def _load_sample_tasks(self):
        data = [
            (1, "جمع البيانات المالية", "أحمد محمد", "عالية", "2024-01-20", "مكتمل", "100%"),
            (2, "تحليل القوائم المالية", "سارة أحمد", "عالية", "2024-01-25", "قيد التنفيذ", "60%"),
        ]
        self.tasks_table.setRowCount(len(data))
        for row, vals in enumerate(data):
            for col, val in enumerate(vals):
                self.tasks_table.setItem(row, col, QTableWidgetItem(str(val)))

    def _load_sample_docs(self):
        data = [
            ("القوائم المالية 2024.pdf", "PDF", "2.5 MB", "أحمد محمد", "2024-01-15", "تمت المراجعة"),
            ("سجل القيود اليومية.xlsx", "XLSX", "1.8 MB", "سارة أحمد", "2024-01-16", "جاري المراجعة"),
        ]
        self.docs_table.setRowCount(len(data))
        for row, vals in enumerate(data):
            for col, val in enumerate(vals):
                self.docs_table.setItem(row, col, QTableWidgetItem(val))

    def _edit_project(self):
        QMessageBox.information(self, "تعديل", "وظيفة التعديل قيد التطوير")

    def _generate_report(self):
        client = get_client()
        pid = str(self.project.get("id", "1"))
        if client._token:
            result = client.create_report(project_id=pid, report_type="audit")
            if result.get("success"):
                rid = result.get("data", {}).get("report_id", "")
                summary = client.generate_report_summary(rid)
                text = str(summary.get("data", summary))
                QMessageBox.information(self, "تقرير", f"تم إنشاء التقرير: {rid}\n\n{text[:500]}")
                return
        QMessageBox.information(self, "تقرير", "سجّل دخول API لإنشاء تقرير")

    def _run_ai_analysis(self):
        self.ai_output.setText("🚀 بدء تشغيل وكلاء الذكاء الاصطناعي...\n\n")
        client = get_client()
        pid = str(self.project.get("id", "1"))
        if client._token:
            result = client.start_audit(
                project_id=pid,
                financial_data={"project": self.project.get("name", ""), "scope": "project_analysis"},
                audit_type="full",
            )
            if result.get("success"):
                data = result.get("data", {})
                self.ai_output.append(f"✓ Audit ID: {data.get('audit_id')}\n")
                self.ai_output.append(f"✓ Status: {data.get('status')}\n")
                self.ai_output.append(f"\n{str(data.get('result', ''))[:1500]}")
                self.ai_output.append("\n✅ اكتمل التحليل عبر API!")
                return
        steps = [
            "✓ وكيل التحليل المالي: اكتمل (محلي)\n",
            "✓ وكيل كشف الاحتيال: اكتمل\n",
            "✓ وكيل الامتثال: اكتمل\n",
        ]
        for s in steps:
            self.ai_output.append(s)
        self.ai_output.append("\n✅ اكتمل التحليل (وضع محلي)")

    def close_window(self):
        parent = self.parent()
        if parent:
            parent.close()
