"""Executive dashboard — KPIs, risk, compliance, and board-level insights."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QTextBrowser, QMessageBox,
)
from PySide6.QtCore import Qt, QTimer

from frontend.api_client import get_client
from frontend.styles.design_system import Color


class KPICard(QFrame):
    def __init__(self, title: str, value: str = "---", subtitle: str = "", accent: str = None):
        super().__init__()
        accent = accent or Color.PRIMARY
        self.setStyleSheet(f"""
            QFrame {{
                background: {Color.BG_CARD}; border: 1px solid {Color.BORDER};
                border-radius: 10px; padding: 16px;
            }}
            QFrame:hover {{ border-color: {accent}; }}
        """)
        layout = QVBoxLayout(self)
        t = QLabel(title)
        t.setStyleSheet(f"color: {Color.TEXT_SECONDARY}; font-size: 11px; font-weight: 600;")
        layout.addWidget(t)
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"color: {accent}; font-size: 26px; font-weight: 700;")
        layout.addWidget(self.value_label)
        self.sub_label = QLabel(subtitle)
        self.sub_label.setStyleSheet(f"color: {Color.TEXT_MUTED}; font-size: 11px;")
        layout.addWidget(self.sub_label)

    def set_data(self, value: str, subtitle: str = ""):
        self.value_label.setText(value)
        if subtitle:
            self.sub_label.setText(subtitle)


class ExecutiveDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._kpis: dict = {}
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("القيادة التنفيذية")
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {Color.TEXT_PRIMARY};")
        header.addWidget(title)
        header.addStretch()
        self.conn_label = QLabel("")
        self.conn_label.setStyleSheet(f"color: {Color.TEXT_SECONDARY}; font-size: 12px;")
        header.addWidget(self.conn_label)
        refresh = QPushButton("تحديث")
        refresh.clicked.connect(self._load_data)
        header.addWidget(refresh)
        report_btn = QPushButton("تقرير تنفيذي")
        report_btn.clicked.connect(self._generate_executive_report)
        header.addWidget(report_btn)
        main.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setSpacing(16)

        grid = QGridLayout()
        grid.setSpacing(12)
        kpi_defs = [
            ("health", "الصحة المالية", "---", Color.SUCCESS),
            ("risk", "درجة المخاطر", "---", Color.ERROR),
            ("compliance", "الامتثال", "---", Color.INFO),
            ("findings", "الملاحظات", "---", Color.WARNING),
            ("projects", "المشاريع النشطة", "---", Color.PRIMARY),
            ("status", "حالة المراجعة", "---", Color.PRIMARY_HOVER),
        ]
        for i, (key, title, val, color) in enumerate(kpi_defs):
            card = KPICard(title, val, accent=color)
            self._kpis[key] = card
            grid.addWidget(card, i // 3, i % 3)
        cl.addLayout(grid)

        rec_title = QLabel("توصيات الإدارة العليا")
        rec_title.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {Color.TEXT_PRIMARY};")
        cl.addWidget(rec_title)

        self.recommendations = QTextBrowser()
        self.recommendations.setMaximumHeight(160)
        self.recommendations.setStyleSheet(f"""
            QTextBrowser {{
                background: {Color.BG_CARD}; color: {Color.TEXT_PRIMARY};
                border: 1px solid {Color.BORDER}; border-radius: 8px; padding: 10px;
            }}
        """)
        cl.addWidget(self.recommendations)

        sum_title = QLabel("الملخص التنفيذي")
        sum_title.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {Color.TEXT_PRIMARY};")
        cl.addWidget(sum_title)

        self.summary = QTextBrowser()
        self.summary.setMinimumHeight(200)
        self.summary.setStyleSheet(f"""
            QTextBrowser {{
                background: {Color.BG_CARD}; color: {Color.TEXT_PRIMARY};
                border: 1px solid {Color.BORDER}; border-radius: 8px; padding: 10px;
            }}
        """)
        cl.addWidget(self.summary)

        scroll.setWidget(content)
        main.addWidget(scroll)

        timer = QTimer(self)
        timer.timeout.connect(self._load_data)
        timer.start(45000)

    def _set_offline(self, msg: str):
        self.conn_label.setText(msg)
        self.conn_label.setStyleSheet(f"color: {Color.WARNING}; font-size: 12px;")
        for card in self._kpis.values():
            card.set_data("---", "غير متصل")
        self.recommendations.setPlainText("اتصل بالخادم وسجّل الدخول عبر API لعرض التوصيات.")
        self.summary.setPlainText("")

    def _load_data(self):
        client = get_client()
        if not client.check_available():
            self._set_offline("● غير متصل")
            return
        if not client._token:
            self._set_offline("● محلي — سجّل دخول API")
            return

        self.conn_label.setText("● متصل")
        self.conn_label.setStyleSheet(f"color: {Color.SUCCESS}; font-size: 12px;")

        dash = client.get_dashboard_v1()
        summary = client.get_summary_report()
        recs = client.get_dashboard_recommendations()

        risk = dash.get("riskScore", 0)
        compliance = dash.get("complianceScore", 0)
        findings = dash.get("findingsCount", 0)
        status = dash.get("auditStatus", "—")
        health = max(0, min(100, 100 - float(risk) * 0.5))

        self._kpis["health"].set_data(f"{health:.0f}%", "مؤشر الصحة المالية")
        self._kpis["risk"].set_data(f"{risk:.1f}", "من 100")
        self._kpis["compliance"].set_data(f"{compliance:.1f}%", "معدل الامتثال")
        self._kpis["findings"].set_data(str(findings), "إجمالي الملاحظات")
        self._kpis["status"].set_data(status, "المراجعة الحالية")

        exec_sum = summary.get("executive_summary", {}) if summary else {}
        projects = exec_sum.get("projects_completed", "—")
        self._kpis["projects"].set_data(str(projects), "مكتمل / إجمالي")

        rec_lines = []
        if isinstance(recs, dict):
            for section in ("immediate_actions", "short_term", "long_term"):
                items = recs.get(section, [])
                if items:
                    rec_lines.append(f"【{section}】")
                    rec_lines.extend(f"  • {x}" for x in items)
        self.recommendations.setPlainText("\n".join(rec_lines) or "لا توجد توصيات حالياً.")

        if summary:
            lines = [
                f"التقييم العام: {exec_sum.get('overall_assessment', '—')}",
                f"الملاحظات الحرجة: {exec_sum.get('critical_issues', 0)}",
                f"معدل الامتثال: {exec_sum.get('compliance_rate', '—')}",
                f"الخلاصة: {summary.get('audit_conclusion', '—')}",
            ]
            self.summary.setPlainText("\n".join(lines))
        else:
            self.summary.setPlainText("لا يتوفر ملخص تنفيذي بعد.")

    def _generate_executive_report(self):
        client = get_client()
        if not client._token:
            QMessageBox.warning(self, "تسجيل الدخول", "يجب تسجيل الدخول عبر API.")
            return
        result = client.create_report(project_id="1", report_type="executive")
        if result.get("success"):
            rid = result.get("data", {}).get("report_id", "")
            summary = client.generate_report_summary(rid)
            if summary.get("success"):
                data = summary.get("data", {})
                self.summary.setPlainText(str(data.get("executive_summary", data)))
            QMessageBox.information(self, "تم", f"تم إنشاء التقرير التنفيذي: {rid}")
        else:
            QMessageBox.warning(self, "خطأ", "تعذّر إنشاء التقرير التنفيذي.")
