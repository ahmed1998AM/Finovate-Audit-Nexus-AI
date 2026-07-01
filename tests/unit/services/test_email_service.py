"""
اختبارات خدمة البريد الإلكتروني
"""
import os
from email.header import decode_header
from unittest.mock import MagicMock, patch

import pytest

from backend.services.email_service import EmailService


def _decode_subject(msg):
    parts = decode_header(msg["Subject"])
    return "".join(
        p.decode(charset or "utf-8") if isinstance(p, bytes) else p
        for p, charset in parts
    )


def _get_html_body(msg):
    payload = msg.get_payload()
    if isinstance(payload, list):
        return payload[0].get_payload(decode=True).decode("utf-8")
    return payload.get_payload(decode=True).decode("utf-8")


class TestEmailService:
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        tmpl_dir = tmp_path / "email_templates"
        with patch("backend.services.email_service.TEMPLATE_DIR", tmpl_dir):
            with patch.dict(os.environ, {
                "SMTP_HOST": "smtp.test.com",
                "SMTP_PORT": "587",
                "SMTP_USER": "user@test.com",
                "SMTP_PASS": "secret",
                "SMTP_FROM": "noreply@test.com",
                "SMTP_FROM_NAME": "Tester",
                "SMTP_USE_TLS": "true",
                "APP_URL": "http://app.test.com",
            }):
                self.service = EmailService()
                yield

    @patch("smtplib.SMTP")
    def test_send_plain(self, mock_smtp_class):
        """اختبار إرسال بريد إلكتروني عادي"""
        mock_server = mock_smtp_class.return_value.__enter__.return_value
        ok, msg = self.service.send("a@b.com", "Hello", "base.html")
        assert ok is True
        assert msg == "Sent"
        mock_smtp_class.assert_called_once_with("smtp.test.com", 587, timeout=10)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user@test.com", "secret")
        mock_server.send_message.assert_called_once()

    @patch("smtplib.SMTP")
    def test_send_welcome_ar(self, mock_smtp_class):
        """اختبار إرسال بريد الترحيب باللغة العربية"""
        mock_server = mock_smtp_class.return_value.__enter__.return_value
        ok, msg = self.service.send_welcome("a@b.com", "أحمد", lang="ar")
        assert ok is True
        assert msg == "Sent"
        sent_msg = mock_server.send_message.call_args[0][0]
        html = _get_html_body(sent_msg)
        assert "أحمد" in html
        assert "مرحباً" in html

    @patch("smtplib.SMTP")
    def test_send_welcome_en(self, mock_smtp_class):
        """اختبار إرسال بريد الترحيب باللغة الإنجليزية"""
        mock_server = mock_smtp_class.return_value.__enter__.return_value
        ok, msg = self.service.send_welcome("a@b.com", "Ahmed", lang="en")
        assert ok is True
        assert msg == "Sent"
        sent_msg = mock_server.send_message.call_args[0][0]
        assert _decode_subject(sent_msg) == "Welcome to Finovate"
        html = _get_html_body(sent_msg)
        assert "Welcome Ahmed" in html

    @patch("smtplib.SMTP")
    def test_send_audit_complete(self, mock_smtp_class):
        """اختبار إرسال إشعار اكتمال التدقيق"""
        mock_server = mock_smtp_class.return_value.__enter__.return_value
        ok, msg = self.service.send_audit_complete(
            "a@b.com", "ProjectX", "passed", 5, "2h 30m"
        )
        assert ok is True
        sent_msg = mock_server.send_message.call_args[0][0]
        html = _get_html_body(sent_msg)
        assert "ProjectX" in html
        assert "passed" in html

    @patch("smtplib.SMTP")
    def test_send_fraud_alert(self, mock_smtp_class):
        """اختبار إرسال تنبيه احتيال"""
        mock_server = mock_smtp_class.return_value.__enter__.return_value
        ok, msg = self.service.send_fraud_alert(
            "a@b.com", "high", "مشتبه به", evidence=["item1", "item2"]
        )
        assert ok is True
        sent_msg = mock_server.send_message.call_args[0][0]
        html = _get_html_body(sent_msg)
        assert "item1" in html
        assert "item2" in html
        assert "مشتبه به" in html

    @patch("smtplib.SMTP")
    def test_send_reminder(self, mock_smtp_class):
        """اختبار إرسال تذكير"""
        mock_server = mock_smtp_class.return_value.__enter__.return_value
        ok, msg = self.service.send_reminder(
            "a@b.com", "مراجعة", "2026-07-01", "ProjectX"
        )
        assert ok is True
        sent_msg = mock_server.send_message.call_args[0][0]
        html = _get_html_body(sent_msg)
        assert "مراجعة" in html
        assert "2026-07-01" in html

    @patch("smtplib.SMTP")
    def test_send_password_reset(self, mock_smtp_class):
        """اختبار إرسال رابط إعادة تعيين كلمة المرور"""
        mock_server = mock_smtp_class.return_value.__enter__.return_value
        ok, msg = self.service.send_password_reset(
            "a@b.com", "http://reset.test/token", expiry_minutes=30
        )
        assert ok is True
        sent_msg = mock_server.send_message.call_args[0][0]
        html = _get_html_body(sent_msg)
        assert "http://reset.test/token" in html

    @patch("smtplib.SMTP")
    def test_send_smtp_connection_failure(self, mock_smtp_class):
        """اختبار فشل الاتصال بخادم SMTP"""
        mock_smtp_class.side_effect = Exception("Connection refused")
        ok, msg = self.service.send("a@b.com", "Test", "base.html")
        assert ok is False
        assert "Connection refused" in msg

    def test_is_configured_true(self):
        """اختبار أن الخدمة مهيأة بشكل صحيح"""
        assert self.service.is_configured() is True

    def test_is_configured_false(self):
        """اختبار أن الخدمة غير مهيأة عند عدم وجود بيانات الاعتماد"""
        with patch.dict(os.environ, {"SMTP_USER": "", "SMTP_PASS": ""}):
            svc = EmailService()
            assert svc.is_configured() is False

    def test_send_not_configured(self):
        """اختبار عدم إرسال البريد عندما تكون الخدمة غير مهيأة"""
        with patch.dict(os.environ, {"SMTP_USER": "", "SMTP_PASS": ""}):
            svc = EmailService()
            ok, msg = svc.send("a@b.com", "Test", "base.html")
            assert ok is False
            assert "SMTP not configured" in msg

    @patch("smtplib.SMTP")
    def test_send_missing_template(self, mock_smtp_class):
        """اختبار إرسال مع قالب غير موجود"""
        ok, msg = self.service.send("a@b.com", "Test", "nonexistent.html")
        assert ok is False
        assert "nonexistent" in msg

    @patch("smtplib.SMTP")
    def test_send_bilingual_welcome(self, mock_smtp_class):
        """اختبار اختلاف الكلمات المفتاحية بين العربية والإنجليزية"""
        mock_server = mock_smtp_class.return_value.__enter__.return_value
        self.service.send_welcome("a@b.com", "User", lang="ar")
        ar_html = _get_html_body(mock_server.send_message.call_args[0][0])
        mock_server.reset_mock()
        self.service.send_welcome("a@b.com", "User", lang="en")
        en_html = _get_html_body(mock_server.send_message.call_args[0][0])
        assert "مرحباً" in ar_html
        assert "Welcome" in en_html

    @patch("smtplib.SMTP")
    def test_send_without_tls(self, mock_smtp_class, tmp_path):
        """اختبار إرسال بدون تشفير TLS"""
        tmpl_dir = tmp_path / "no_tls_templates"
        with patch.dict(os.environ, {"SMTP_USE_TLS": "false"}):
            with patch("backend.services.email_service.TEMPLATE_DIR", tmpl_dir):
                svc = EmailService()
            mock_server = mock_smtp_class.return_value.__enter__.return_value
            ok, msg = svc.send("a@b.com", "Test", "base.html")
            assert ok is True
            mock_server.starttls.assert_not_called()

    @patch("smtplib.SMTP")
    def test_send_pas_reset_english(self, mock_smtp_class):
        """اختبار إعادة تعيين كلمة المرور بالإنجليزية"""
        mock_server = mock_smtp_class.return_value.__enter__.return_value
        ok, msg = self.service.send_password_reset(
            "a@b.com", "http://reset.test/token", lang="en"
        )
        assert ok is True
        sent_msg = mock_server.send_message.call_args[0][0]
        assert _decode_subject(sent_msg) == "Password Reset"

    def test_get_email_service_singleton(self):
        """اختبار دالة get_email_service"""
        from backend.services.email_service import get_email_service
        instance1 = get_email_service()
        instance2 = get_email_service()
        assert instance1 is instance2
