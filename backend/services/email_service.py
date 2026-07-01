"""
Finovate Audit Nexus AI - Email Service
SMTP email delivery with Jinja2 HTML templates
"""

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "templates" / "email"


class EmailService:
    def __init__(self):
        self._smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self._smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self._smtp_user = os.getenv("SMTP_USER", "")
        self._smtp_pass = os.getenv("SMTP_PASS", "")
        self._from_addr = os.getenv("SMTP_FROM", "noreply@finovate.ai")
        self._from_name = os.getenv("SMTP_FROM_NAME", "Finovate Audit Nexus")
        self._use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self._enabled = bool(self._smtp_user and self._smtp_pass)
        self._template_env = self._init_templates()

    def _init_templates(self) -> Environment:
        template_dir = TEMPLATE_DIR
        if not template_dir.exists():
            template_dir.mkdir(parents=True, exist_ok=True)
            self._create_default_templates(template_dir)
        return Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"])
        )

    def _create_default_templates(self, template_dir: Path):
        templates = {
            "base.html": """<!DOCTYPE html>
<html dir="{{ direction }}">
<head><meta charset="utf-8"><style>
body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #f4f4f4; }
.container { max-width: 600px; margin: 20px auto; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.header { background: linear-gradient(135deg, #1a237e, #283593); color: #fff; padding: 30px; text-align: center; }
.header h1 { margin: 0; font-size: 24px; }
.body { padding: 30px; color: #333; line-height: 1.6; }
.footer { background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; }
.badge { display: inline-block; padding: 6px 16px; border-radius: 20px; font-size: 14px; font-weight: bold; }
.badge-success { background: #e8f5e9; color: #2e7d32; }
.badge-warning { background: #fff3e0; color: #e65100; }
.badge-danger { background: #ffebee; color: #c62828; }
.btn { display: inline-block; padding: 12px 30px; background: #1a237e; color: #fff !important; text-decoration: none; border-radius: 6px; margin: 10px 0; }
</style></head><body>
<div class="container">
<div class="header"><h1>{{ title }}</h1></div>
<div class="body">{% block content %}{% endblock %}</div>
<div class="footer"><p>{{ footer_text }}</p></div>
</div></body></html>""",
            "welcome.html": """{% extends "base.html" %}{% block content %}
<p>{{ greeting }}</p>
<p>{{ intro_text }}</p>
<div style="text-align:center;margin:20px 0;">
<a href="{{ dashboard_url }}" class="btn">{{ btn_text }}</a>
</div>
<p>{{ help_text }}</p>
{% endblock %}""",
            "audit_complete.html": """{% extends "base.html" %}{% block content %}
<p>{{ greeting }}</p>
<p>{{ complete_text }}</p>
<div style="margin:20px 0;">
<p><strong>{{ project_label }}:</strong> {{ project_name }}</p>
<p><strong>{{ status_label }}:</strong> <span class="badge badge-{{ status_class }}">{{ status }}</span></p>
<p><strong>{{ findings_label }}:</strong> {{ findings_count }}</p>
<p><strong>{{ duration_label }}:</strong> {{ duration }}</p>
</div>
<div style="text-align:center;margin:20px 0;">
<a href="{{ report_url }}" class="btn">{{ btn_text }}</a>
</div>
{% endblock %}""",
            "fraud_alert.html": """{% extends "base.html" %}{% block content %}
<div style="text-align:center;margin:20px 0;">
<span class="badge badge-danger">{{ severity_label }}: {{ severity }}</span>
</div>
<p>{{ alert_text }}</p>
<div style="margin:20px 0;background:#ffebee;padding:20px;border-radius:8px;border-left:4px solid #c62828;">
<p><strong>{{ description_label }}:</strong> {{ description }}</p>
{% if evidence %}<p><strong>{{ evidence_label }}:</strong></p><ul>{% for item in evidence %}<li>{{ item }}</li>{% endfor %}</ul>{% endif %}
</div>
<div style="text-align:center;margin:20px 0;">
<a href="{{ dashboard_url }}" class="btn">{{ btn_text }}</a>
</div>
{% endblock %}""",
            "reminder.html": """{% extends "base.html" %}{% block content %}
<p>{{ greeting }}</p>
<p>{{ reminder_text }}</p>
<div style="margin:20px 0;background:#fff3e0;padding:20px;border-radius:8px;border-left:4px solid #e65100;">
<p><strong>{{ task_label }}:</strong> {{ task_name }}</p>
<p><strong>{{ due_label }}:</strong> {{ due_date }}</p>
<p><strong>{{ project_label }}:</strong> {{ project_name }}</p>
</div>
<div style="text-align:center;margin:20px 0;">
<a href="{{ dashboard_url }}" class="btn">{{ btn_text }}</a>
</div>
{% endblock %}""",
            "password_reset.html": """{% extends "base.html" %}{% block content %}
<p>{{ greeting }}</p>
<p>{{ reset_text }}</p>
<div style="text-align:center;margin:20px 0;">
<a href="{{ reset_url }}" class="btn">{{ btn_text }}</a>
</div>
<p>{{ expiry_text }}: {{ expiry_minutes }} {{ minutes_label }}</p>
<p>{{ ignore_text }}</p>
{% endblock %}""",
        }
        for name, content in templates.items():
            (template_dir / name).write_text(content, encoding="utf-8")
        logger.info(f"Created {len(templates)} email templates")

    def _render(self, template_name: str, **kwargs) -> str:
        template = self._template_env.get_template(template_name)
        defaults = {
            "direction": "ltr",
            "title": "Finovate Audit Nexus",
            "footer_text": "© Finovate Audit Nexus AI — Enterprise Financial Audit Platform",
            "dashboard_url": os.getenv("APP_URL", "http://localhost:8000"),
        }
        defaults.update(kwargs)
        ar_keywords = {
            "greeting": "مرحباً",
            "intro_text": "شكراً لانضمامك إلى منصة Finovate للتدقيق المالي الذكي.",
            "btn_text": "الذهاب إلى لوحة التحكم",
            "help_text": "إذا كان لديك أي استفسار، لا تتردد في التواصل معنا.",
            "complete_text": "تم الانتهاء من عملية التدقيق بنجاح.",
            "project_label": "المشروع",
            "status_label": "الحالة",
            "findings_label": "الملاحظات",
            "duration_label": "المدة",
            "severity_label": "مستوى الخطورة",
            "description_label": "الوصف",
            "evidence_label": "الأدلة",
            "alert_text": "تم اكتشاف نشاط يحتاج إلى مراجعة فورية.",
            "reminder_text": "هذا تذكير بمهمة تدقيق قادمة.",
            "task_label": "المهمة",
            "due_label": "تاريخ الاستحقاق",
            "reset_text": "لقد تلقينا طلباً لإعادة تعيين كلمة المرور.",
            "expiry_text": "ينتهي صلاحية الرابط بعد",
            "minutes_label": "دقيقة",
            "ignore_text": "إذا لم تطلب إعادة التعيين، يرجى تجاهل هذا البريد.",
            "report_url": os.getenv("APP_URL", "http://localhost:8000") + "/reports",
        }
        for k, v in ar_keywords.items():
            if k not in kwargs:
                defaults.setdefault(k, v)
        return template.render(**defaults)

    def send(self, to: str, subject: str, template_name: str = "base.html", **template_kwargs) -> tuple:
        if not self._enabled:
            logger.warning(f"Email not sent (SMTP not configured): {subject} -> {to}")
            return False, "SMTP not configured"
        try:
            html = self._render(template_name, **template_kwargs)
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self._from_name} <{self._from_addr}>"
            msg["To"] = to
            msg.attach(MIMEText(html, "html"))
            with smtplib.SMTP(self._smtp_host, self._smtp_port, timeout=10) as server:
                if self._use_tls:
                    server.starttls()
                if self._smtp_user:
                    server.login(self._smtp_user, self._smtp_pass)
                server.send_message(msg)
            logger.info(f"Email sent: {subject} -> {to}")
            return True, "Sent"
        except Exception as e:
            logger.error(f"Email failed: {subject} -> {to}: {e}")
            return False, str(e)

    def send_welcome(self, to: str, name: str, lang: str = "ar"):
        return self.send(to, "مرحباً بك في Finovate" if lang == "ar" else "Welcome to Finovate",
                        "welcome.html", greeting=f"مرحباً {name}" if lang == "ar" else f"Welcome {name}",
                        direction="rtl" if lang == "ar" else "ltr")

    def send_audit_complete(self, to: str, project_name: str, status: str, findings_count: int, duration: str, lang: str = "ar"):
        return self.send(to, f"اكتمل التدقيق: {project_name}" if lang == "ar" else f"Audit Complete: {project_name}",
                        "audit_complete.html", project_name=project_name, status=status,
                        findings_count=findings_count, duration=duration,
                        status_class="success" if status == "passed" else "warning",
                        direction="rtl" if lang == "ar" else "ltr")

    def send_fraud_alert(self, to: str, severity: str, description: str, evidence: Optional[list] = None, lang: str = "ar"):
        return self.send(to, f"تنبيه احتيال: {severity}" if lang == "ar" else f"Fraud Alert: {severity}",
                        "fraud_alert.html", severity=severity, description=description,
                        evidence=evidence or [], direction="rtl" if lang == "ar" else "ltr")

    def send_reminder(self, to: str, task_name: str, due_date: str, project_name: str, lang: str = "ar"):
        return self.send(to, f"تذكير: {task_name}" if lang == "ar" else f"Reminder: {task_name}",
                        "reminder.html", task_name=task_name, due_date=due_date,
                        project_name=project_name, direction="rtl" if lang == "ar" else "ltr")

    def send_password_reset(self, to: str, reset_url: str, expiry_minutes: int = 30, lang: str = "ar"):
        return self.send(to, "إعادة تعيين كلمة المرور" if lang == "ar" else "Password Reset",
                        "password_reset.html", reset_url=reset_url, expiry_minutes=expiry_minutes,
                        direction="rtl" if lang == "ar" else "ltr")

    def is_configured(self) -> bool:
        return self._enabled


_email_service_instance: Optional[EmailService] = None


def get_email_service() -> EmailService:
    global _email_service_instance
    if _email_service_instance is None:
        _email_service_instance = EmailService()
    return _email_service_instance
