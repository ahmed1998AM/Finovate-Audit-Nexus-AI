"""
اختبارات خدمة الإشعارات متعددة القنوات
"""
import os
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from backend.services.notification_service import (
    EmailChannel,
    NotificationChannel,
    NotificationService,
    SlackChannel,
    TeamsChannel,
)


class TestNotificationService:
    @pytest.fixture(autouse=True)
    def setup(self):
        with patch.dict(os.environ, {
            "NOTIFY_EMAIL_FROM_ADDR": "noreply@finovate.ai",
            "NOTIFY_SLACK_WEBHOOK_URL": "https://hooks.slack.com/test",
            "NOTIFY_TEAMS_WEBHOOK_URL": "https://outlook.office.com/webhook/test",
        }):
            self.service = NotificationService()
            self.service.notifications.clear()
            self.service.user_preferences.clear()
        yield

    # ---------- Helper assertions ----------

    def _assert_notification_structure(self, notif, expected):
        for key in ("notification_id", "user_id", "notification_type", "title",
                     "message", "priority", "channels", "data", "status",
                     "read", "created_at", "read_at"):
            assert key in notif, f"Missing key: {key}"
        assert notif["user_id"] == expected["user_id"]
        assert notif["notification_type"] == expected.get("notification_type")
        assert notif["title"] == expected.get("title")
        assert notif["priority"] == expected.get("priority")
        assert notif["read"] is False

    # ---------- Initialization ----------

    def test_initialization_creates_channels(self):
        """اختبار تهيئة القنوات عند إنشاء الخدمة"""
        assert "email" in self.service.channels
        assert "slack" in self.service.channels
        assert "teams" in self.service.channels
        assert isinstance(self.service.channels["email"], EmailChannel)
        assert isinstance(self.service.channels["slack"], SlackChannel)
        assert isinstance(self.service.channels["teams"], TeamsChannel)

    def test_initialization_channel_config(self):
        """اختبار قراءة إعدادات القنوات من المتغيرات البيئية"""
        assert self.service.channels["email"].config.get("from_addr") == "noreply@finovate.ai"
        assert self.service.channels["slack"].config.get("webhook_url") == "https://hooks.slack.com/test"

    def test_notification_channel_base(self):
        """اختبار إنشاء قناة أساسية"""
        ch = NotificationChannel(name="test", enabled=False, config={"k": "v"})
        assert ch.name == "test"
        assert ch.enabled is False
        assert ch.config == {"k": "v"}

    # ---------- send_notification ----------

    def test_send_notification_inapp_only(self):
        """اختبار إرسال إشعار عبر القناة الداخلية فقط"""
        notif = self.service.send_notification(
            user_id=1, notification_type="info", title="Hello",
            message="Test message", channels=["in_app"],
        )
        self._assert_notification_structure(notif, {
            "user_id": 1, "notification_type": "info",
            "title": "Hello", "priority": "normal",
        })
        assert notif["channels"] == ["in_app"]
        nid = notif["notification_id"]
        assert nid in self.service.notifications

    @patch("requests.post")
    @patch("backend.database.get_db_session")
    def test_send_notification_multi_channel(self, mock_get_db, mock_post):
        """اختبار إرسال إشعار عبر قنوات متعددة"""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp
        mock_session = MagicMock()
        mock_user = MagicMock()
        mock_user.email = "user@test.com"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        mock_get_db.return_value.__enter__.return_value = mock_session
        mock_get_db.return_value.__exit__.return_value = None

        notif = self.service.send_notification(
            user_id=1, notification_type="alert", title="Multi",
            message="Multi channel", channels=["email", "slack", "teams"],
        )
        assert notif["channels"] == ["email", "slack", "teams"]
        assert mock_post.call_count == 2

    def test_send_notification_empty_message(self):
        """اختبار إرسال إشعار برسالة فارغة"""
        notif = self.service.send_notification(
            user_id=1, notification_type="info", title="Empty",
            message="", channels=["in_app"],
        )
        assert notif["message"] == ""
        assert notif["status"] == "sent"

    def test_send_notification_invalid_channel(self):
        """اختبار إرسال إشعار عبر قناة غير موجودة"""
        notif = self.service.send_notification(
            user_id=1, notification_type="info", title="Bad",
            message="Test", channels=["nonexistent_channel"],
        )
        assert notif["status"] == "sent"

    def test_send_notification_with_data(self):
        """اختبار إرسال إشعار مع بيانات إضافية"""
        notif = self.service.send_notification(
            user_id=1, notification_type="info", title="Data",
            message="With data", channels=["in_app"],
            data={"key": "value", "count": 42},
        )
        assert notif["data"] == {"key": "value", "count": 42}

    # ---------- send_fraud_alert ----------

    def test_send_fraud_alert_critical(self):
        """اختبار إرسال تنبيه احتيال بمستوى خطورة حرج"""
        notif = self.service.send_fraud_alert(
            user_id=1, alert_type="unusual_transaction", severity="Critical",
            description="Large transfer detected",
            evidence=["txn_001", "txn_002"],
            project_id="proj_1",
        )
        self._assert_notification_structure(notif, {
            "user_id": 1, "notification_type": "fraud_alert",
            "title": "Fraud Alert - Critical", "priority": "urgent",
        })
        assert notif["data"]["severity"] == "Critical"
        assert notif["data"]["evidence"] == ["txn_001", "txn_002"]

    def test_send_fraud_alert_high(self):
        """اختبار إرسال تنبيه احتيال بمستوى خطورة عال"""
        notif = self.service.send_fraud_alert(
            user_id=1, alert_type="suspicious_login", severity="High",
            description="Login from unknown IP",
            evidence=["ip_192.168.1.1"],
        )
        assert notif["priority"] == "high"
        assert notif["data"]["severity"] == "High"

    def test_send_fraud_alert_medium(self):
        """اختبار إرسال تنبيه احتيال بمستوى خطورة متوسط"""
        notif = self.service.send_fraud_alert(
            user_id=1, alert_type="pattern_match", severity="Medium",
            description="Suspicious pattern", evidence=[],
        )
        assert notif["priority"] == "high"
        assert notif["data"]["severity"] == "Medium"

    def test_send_fraud_alert_low(self):
        """اختبار إرسال تنبيه احتيال بمستوى خطورة منخفض"""
        notif = self.service.send_fraud_alert(
            user_id=1, alert_type="info_only", severity="Low",
            description="Minor anomaly", evidence=[],
        )
        assert notif["priority"] == "high"
        assert notif["data"]["severity"] == "Low"

    def test_send_fraud_alert_channels(self):
        """اختبار أن تنبيه الاحتيال يرسل عبر القنوات المحددة"""
        notif = self.service.send_fraud_alert(
            user_id=1, alert_type="test", severity="Low",
            description="Test", evidence=[],
        )
        assert notif["channels"] == ["in_app", "email", "slack"]

    # ---------- send_audit_reminder ----------

    def test_send_audit_reminder(self):
        """اختبار إرسال تذكير تدقيق"""
        due = datetime(2026, 7, 15)
        notif = self.service.send_audit_reminder(
            user_id=1, task_name="مراجعة مالية", due_date=due,
            project_id="proj_audit_1",
        )
        self._assert_notification_structure(notif, {
            "user_id": 1, "notification_type": "audit_reminder",
            "title": "Reminder: مراجعة مالية", "priority": "normal",
        })
        assert notif["data"]["task_name"] == "مراجعة مالية"
        assert notif["data"]["due_date"] == "2026-07-15T00:00:00"
        assert notif["data"]["project_id"] == "proj_audit_1"

    def test_send_audit_reminder_channels(self):
        """اختبار أن تذكير التدقيق يرسل عبر in_app والبريد"""
        due = datetime(2026, 7, 1)
        notif = self.service.send_audit_reminder(
            user_id=1, task_name="Audit", due_date=due, project_id="p1",
        )
        assert notif["channels"] == ["in_app", "email"]

    # ---------- mark_as_read ----------

    def test_mark_as_read(self):
        """اختبار وضع إشعار كمقروء"""
        notif = self.service.send_notification(
            user_id=1, notification_type="info", title="Read",
            message="Mark me", channels=["in_app"],
        )
        nid = notif["notification_id"]
        result = self.service.mark_as_read(nid)
        assert result is True
        assert self.service.notifications[nid]["read"] is True
        assert self.service.notifications[nid]["read_at"] is not None

    def test_mark_as_read_not_found(self):
        """اختبار وضع إشعار غير موجود كمقروء"""
        result = self.service.mark_as_read("NONEXISTENT")
        assert result is False

    # ---------- get_user_notifications ----------

    def test_get_user_notifications(self):
        """اختبار جلب إشعارات مستخدم معين"""
        self.service.send_notification(1, "info", "N1", "Msg1", channels=["in_app"])
        time.sleep(1.001)
        self.service.send_notification(1, "info", "N2", "Msg2", channels=["in_app"])
        self.service.send_notification(2, "info", "N3", "Msg3", channels=["in_app"])
        notifs = self.service.get_user_notifications(1)
        assert len(notifs) == 2
        assert all(n["user_id"] == 1 for n in notifs)

    def test_get_user_notifications_unread_only(self):
        """اختبار جلب الإشعارات غير المقروءة فقط"""
        n1 = self.service.send_notification(1, "info", "N1", "Msg1", channels=["in_app"])
        time.sleep(1.001)
        self.service.send_notification(1, "info", "N2", "Msg2", channels=["in_app"])
        self.service.mark_as_read(n1["notification_id"])
        unread = self.service.get_user_notifications(1, unread_only=True)
        assert len(unread) == 1
        assert unread[0]["title"] == "N2"

    def test_get_user_notifications_limit(self):
        """اختبار تحديد عدد الإشعارات المسترجعة"""
        for i in range(10):
            nid = f"notif_limit_{i}"
            self.service.notifications[nid] = {
                "notification_id": nid, "user_id": 1,
                "notification_type": "info", "title": f"N{i}",
                "message": f"Msg{i}", "priority": "normal",
                "channels": ["in_app"], "data": {},
                "status": "sent", "read": False,
                "created_at": f"2026-06-22T13:00:0{i}.000000",
                "read_at": None,
            }
        notifs = self.service.get_user_notifications(1, limit=3)
        assert len(notifs) == 3

    def test_get_user_notifications_order(self):
        """اختبار ترتيب الإشعارات من الأحدث إلى الأقدم"""
        self.service.send_notification(1, "info", "First", "Msg1", channels=["in_app"])
        time.sleep(1.001)
        self.service.send_notification(1, "info", "Second", "Msg2", channels=["in_app"])
        notifs = self.service.get_user_notifications(1)
        assert notifs[0]["title"] == "Second"

    # ---------- get_unread_count ----------

    def test_get_unread_count(self):
        """اختبار حساب عدد الإشعارات غير المقروءة"""
        n1 = self.service.send_notification(1, "info", "N1", "M1", channels=["in_app"])
        time.sleep(1.001)
        self.service.send_notification(1, "info", "N2", "M2", channels=["in_app"])
        self.service.send_notification(2, "info", "N3", "M3", channels=["in_app"])
        assert self.service.get_unread_count(1) == 2
        self.service.mark_as_read(n1["notification_id"])
        assert self.service.get_unread_count(1) == 1

    def test_get_unread_count_zero(self):
        """اختبار عدد غير مقروء صفر لمستخدم بدون إشعارات"""
        assert self.service.get_unread_count(999) == 0

    # ---------- user_preferences ----------

    def test_set_and_get_user_preferences(self):
        """اختبار تعيين وجلب تفضيلات المستخدم"""
        prefs = {
            "email_notifications": False,
            "push_notifications": True,
            "fraud_alerts": False,
            "audit_reminders": True,
            "daily_digest": True,
        }
        ok = self.service.set_user_preferences(1, prefs)
        assert ok is True
        assert self.service.get_user_preferences(1) == prefs

    def test_get_user_preferences_default(self):
        """اختبار جلب التفضيلات الافتراضية لمستخدم جديد"""
        prefs = self.service.get_user_preferences(999)
        assert prefs["email_notifications"] is True
        assert prefs["push_notifications"] is True
        assert prefs["fraud_alerts"] is True
        assert prefs["audit_reminders"] is True
        assert prefs["daily_digest"] is False

    def test_set_user_preferences_overwrite(self):
        """اختبار تحديث تفضيلات مستخدم موجود"""
        self.service.set_user_preferences(1, {"email_notifications": False})
        assert self.service.get_user_preferences(1)["email_notifications"] is False

    # ---------- send_email ----------

    def test_send_email(self):
        """اختبار إرسال بريد إلكتروني عبر خدمة الإشعارات"""
        ok, err = self.service.send_email(
            to="user@test.com", subject="Test Subject", body="Test body",
        )
        assert ok is True
        assert err == ""
        assert len(self.service.notifications) == 1
        nid = list(self.service.notifications.keys())[0]
        assert nid.startswith("EMAIL-")
        assert self.service.notifications[nid]["type"] == "email"

    def test_send_email_with_alert_type(self):
        """اختبار إرسال بريد إلكتروني مع نوع تنبيه"""
        ok, err = self.service.send_email(
            to="user@test.com", subject="Alert", body="Body", alert_type="warning",
        )
        assert ok is True
        nid = list(self.service.notifications.keys())[0]
        assert self.service.notifications[nid]["alert_type"] == "warning"

    # ---------- send_slack ----------

    @patch("requests.post")
    def test_send_slack(self, mock_post):
        """اختبار إرسال إشعار إلى Slack"""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp
        ok, err = self.service.send_slack(
            webhook_url="https://hooks.test.com",
            message="Hello Slack",
            title="Alert",
        )
        assert ok is True
        assert err == ""
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "Hello Slack" in str(kwargs.get("json", {}))

    @patch("requests.post")
    def test_send_slack_http_error(self, mock_post):
        """اختبار فشل إرسال Slack عند خطأ HTTP"""
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_post.return_value = mock_resp
        ok, err = self.service.send_slack("https://hooks.test.com", "Test", "Title")
        assert ok is False
        assert err == "Send failed"

    # ---------- send_teams ----------

    @patch("requests.post")
    def test_send_teams(self, mock_post):
        """اختبار إرسال إشعار إلى Microsoft Teams"""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp
        ok, err = self.service.send_teams(
            webhook_url="https://teams.test.com",
            message="Hello Teams",
            title="Alert",
        )
        assert ok is True
        assert err == ""
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        payload = kwargs.get("json", {})
        assert payload["@type"] == "MessageCard"

    @patch("requests.post")
    def test_send_teams_http_error(self, mock_post):
        """اختبار فشل إرسال Teams عند خطأ HTTP"""
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_post.return_value = mock_resp
        ok, err = self.service.send_teams("https://teams.test.com", "Msg", "Title")
        assert ok is False
        assert err == "Send failed"

    # ---------- send_inapp ----------

    def test_send_inapp(self):
        """اختبار إرسال إشعار داخلي داخل التطبيق"""
        result = self.service.send_inapp(
            user_id="1", title="InApp Title", message="InApp Message",
        )
        assert result is True
        notifs = self.service.get_user_notifications(1)
        assert len(notifs) == 1
        assert notifs[0]["title"] == "InApp Title"

    def test_send_inapp_invalid_user_id(self):
        """اختبار إرسال إشعار داخلي مع معرف مستخدم غير صالح"""
        result = self.service.send_inapp(
            user_id="invalid", title="Test", message="Test",
        )
        assert result is True

    def test_send_inapp_with_alert_type(self):
        """اختبار إرسال إشعار داخلي مع نوع تنبيه"""
        self.service.send_inapp("1", "Title", "Msg", alert_type="warning")
        notifs = self.service.get_user_notifications(1)
        assert notifs[0]["notification_type"] == "warning"

    # ---------- get_notification_history ----------

    def test_get_notification_history_all(self):
        """اختبار جلب سجل الإشعارات بالكامل"""
        n1 = self.service.send_notification(1, "info", "N1", "M1", channels=["in_app"])
        self.service.notifications[n1["notification_id"] + "_2"] = {
            "notification_id": n1["notification_id"] + "_2",
            "user_id": 2, "notification_type": "info", "title": "N2",
            "message": "M2", "priority": "normal", "channels": ["in_app"],
            "data": {}, "status": "sent", "read": False,
            "created_at": "2026-06-22T13:00:00.000000", "read_at": None,
        }
        history = self.service.get_notification_history()
        assert len(history) == 2

    def test_get_notification_history_by_user(self):
        """اختبار جلب سجل الإشعارات لمستخدم معين"""
        self.service.send_notification(1, "info", "N1", "M1", channels=["in_app"])
        self.service.send_notification(2, "info", "N2", "M2", channels=["in_app"])
        history = self.service.get_notification_history(user_id=1)
        assert len(history) == 1
        assert history[0]["user_id"] == 1

    # ---------- get_channel_status ----------

    def test_get_channel_status(self):
        """اختبار جلب حالة القنوات"""
        status = self.service.get_channel_status()
        assert "email" in status
        assert "slack" in status
        assert "teams" in status
        for ch_name, info in status.items():
            assert "enabled" in info
            assert info["enabled"] in (True, False)

    def test_get_channel_status_disabled(self):
        """اختبار حالة قناة معطلة"""
        self.service.channels["slack"].enabled = False
        status = self.service.get_channel_status()
        assert status["slack"]["enabled"] is False

    # ---------- EmailChannel direct ----------

    def test_email_channel_send(self):
        """اختبار إرسال عبر قناة البريد الإلكتروني مباشرة"""
        ch = EmailChannel(config={"from_addr": "test@finovate.ai"})
        result = ch.send(to="user@test.com", subject="Test", body="Hello")
        assert result is True

    def test_email_channel_disabled(self):
        """اختبار قناة البريد الإلكتروني المعطلة"""
        ch = EmailChannel()
        ch.enabled = False
        result = ch.send(to="user@test.com", subject="Test", body="Hello")
        assert result is False

    def test_email_channel_default_from(self):
        """اختبار المرسل الافتراضي لقناة البريد"""
        ch = EmailChannel()
        result = ch.send(to="user@test.com", subject="S", body="B")
        assert result is True

    # ---------- SlackChannel direct ----------

    @patch("requests.post")
    def test_slack_channel_send(self, mock_post):
        """اختبار إرسال عبر قناة Slack مباشرة"""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp
        ch = SlackChannel()
        result = ch.send(webhook_url="https://hooks.test.com", message="Hi", title="Alert")
        assert result is True

    @patch("requests.post")
    def test_slack_channel_failure(self, mock_post):
        """اختبار فشل إرسال عبر Slack"""
        mock_post.side_effect = Exception("Network error")
        ch = SlackChannel()
        result = ch.send(webhook_url="https://hooks.test.com", message="Hi")
        assert result is False

    def test_slack_channel_disabled(self):
        """اختبار قناة Slack المعطلة"""
        ch = SlackChannel()
        ch.enabled = False
        result = ch.send(webhook_url="https://hooks.test.com", message="Hi")
        assert result is False

    # ---------- TeamsChannel direct ----------

    @patch("requests.post")
    def test_teams_channel_send(self, mock_post):
        """اختبار إرسال عبر قناة Teams مباشرة"""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp
        ch = TeamsChannel()
        result = ch.send(webhook_url="https://teams.test.com", title="Alert", message="Hi")
        assert result is True

    @patch("requests.post")
    def test_teams_channel_failure(self, mock_post):
        """اختبار فشل إرسال عبر Teams"""
        mock_post.side_effect = Exception("Timeout")
        ch = TeamsChannel()
        result = ch.send(webhook_url="https://teams.test.com", title="T", message="M")
        assert result is False

    def test_teams_channel_disabled(self):
        """اختبار قناة Teams المعطلة"""
        ch = TeamsChannel()
        ch.enabled = False
        result = ch.send(webhook_url="https://teams.test.com", title="T", message="M")
        assert result is False

    # ---------- _get_user_email ----------

    @patch("backend.database.get_db_session")
    def test_get_user_email_found(self, mock_get_db):
        """اختبار جلب بريد مستخدم موجود"""
        mock_session = MagicMock()
        mock_user = MagicMock()
        mock_user.email = "found@test.com"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        mock_get_db.return_value.__enter__.return_value = mock_session
        mock_get_db.return_value.__exit__.return_value = None
        email = self.service._get_user_email(user_id=1)
        assert email == "found@test.com"

    @patch("backend.database.get_db_session")
    def test_get_user_email_not_found(self, mock_get_db):
        """اختبار جلب بريد مستخدم غير موجود"""
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db.return_value.__enter__.return_value = mock_session
        mock_get_db.return_value.__exit__.return_value = None
        email = self.service._get_user_email(user_id=999)
        assert email is None

    @patch("backend.database.get_db_session")
    def test_get_user_email_exception(self, mock_get_db):
        """اختبار جلب بريد مستخدم عند حدوث خطأ في قاعدة البيانات"""
        mock_get_db.return_value.__enter__.side_effect = Exception("DB error")
        email = self.service._get_user_email(user_id=1)
        assert email is None

    # ---------- send_email with disabled channel ----------

    def test_send_email_channel_disabled(self):
        """اختبار إرسال بريد عند تعطيل القناة"""
        self.service.channels["email"].enabled = False
        ok, err = self.service.send_email("a@b.com", "S", "B")
        assert ok is False
        assert err == "Email channel disabled"

    def test_send_slack_channel_disabled(self):
        """اختبار إرسال Slack عند تعطيل القناة"""
        self.service.channels["slack"].enabled = False
        ok, err = self.service.send_slack("https://hooks.test.com", "M")
        assert ok is False
        assert err == "Slack channel disabled"

    def test_send_teams_channel_disabled(self):
        """اختبار إرسال Teams عند تعطيل القناة"""
        self.service.channels["teams"].enabled = False
        ok, err = self.service.send_teams("https://teams.test.com", "M", "T")
        assert ok is False
        assert err == "Teams channel disabled"

    # ---------- send_notification with data with None channels ----------

    def test_send_notification_no_channels(self):
        """اختبار إرسال إشعار بدون تحديد قنوات"""
        notif = self.service.send_notification(
            user_id=1, notification_type="info", title="NoCh",
            message="Test",
        )
        assert notif["channels"] == ["in_app"]
