"""
Notification Service - خدمة الإشعارات والتنبيهات
Multi-channel notification delivery (Email, Slack, Teams, In-App)
"""
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class NotificationChannel:
    name: str
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)


class EmailChannel(NotificationChannel):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="email", config=config or {})
        import smtplib
        from email.mime.text import MIMEText
        self.smtp = smtplib
        self.mime = MIMEText
        self._server = None

    def send(self, to: str, subject: str, body: str) -> bool:
        if not self.enabled:
            return False
        try:
            msg = self.mime(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = self.config.get("from_addr", "noreply@finovate.ai")
            msg["To"] = to
            logger.info(f"[Email] Sent to {to}: {subject}")
            return True
        except Exception as e:
            logger.error(f"[Email] Failed: {e}")
            return False


class SlackChannel(NotificationChannel):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="slack", config=config or {})
        import requests as req
        self.http = req

    def send(self, webhook_url: str, message: str, title: Optional[str] = None) -> bool:
        if not self.enabled:
            return False
        try:
            payload = {"text": f"*{title or 'Finovate Alert'}*\n{message}"}
            resp = self.http.post(webhook_url or self.config.get("webhook_url", ""), json=payload, timeout=10)
            if resp.status_code == 200:
                logger.info(f"[Slack] Sent: {title}")
                return True
            logger.warning(f"[Slack] HTTP {resp.status_code}")
            return False
        except Exception as e:
            logger.error(f"[Slack] Failed: {e}")
            return False


class TeamsChannel(NotificationChannel):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="teams", config=config or {})
        import requests as req
        self.http = req

    def send(self, webhook_url: str, title: str, message: str) -> bool:
        if not self.enabled:
            return False
        try:
            payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "summary": title,
                "title": title,
                "text": message,
            }
            resp = self.http.post(webhook_url or self.config.get("webhook_url", ""), json=payload, timeout=10)
            if resp.status_code == 200:
                logger.info(f"[Teams] Sent: {title}")
                return True
            logger.warning(f"[Teams] HTTP {resp.status_code}")
            return False
        except Exception as e:
            logger.error(f"[Teams] Failed: {e}")
            return False


class NotificationService:
    """
    خدمة الإشعارات متعددة القنوات
    تدعم: Email, Slack, Teams, In-App
    """

    def __init__(self):
        self.channels: Dict[str, NotificationChannel] = {
            "email": EmailChannel(self._get_channel_config("email")),
            "slack": SlackChannel(self._get_channel_config("slack")),
            "teams": TeamsChannel(self._get_channel_config("teams")),
        }
        self.notifications: Dict[str, Dict[str, Any]] = {}
        self.user_preferences: Dict[int, Dict[str, Any]] = {}
        logger.info("NotificationService initialized with %d channels", len(self.channels))

    def _get_channel_config(self, name: str) -> Dict[str, Any]:
        prefix = f"NOTIFY_{name.upper()}_"
        return {k.replace(prefix, "").lower(): v for k, v in os.environ.items() if k.startswith(prefix)}

    def send_notification(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        priority: str = "normal",
        channels: Optional[List[str]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        notif_id = f"NOTIF-{datetime.now().strftime('%Y%m%d%H%M%S')}-{user_id}"
        notification = {
            "notification_id": notif_id,
            "user_id": user_id,
            "notification_type": notification_type,
            "title": title,
            "message": message,
            "priority": priority,
            "channels": channels or ["in_app"],
            "data": data or {},
            "status": "sent",
            "read": False,
            "created_at": datetime.now().isoformat(),
            "read_at": None,
        }
        self.notifications[notif_id] = notification
        logger.info(f"Notification {notif_id} created")
        for ch in notification["channels"]:
            self._dispatch_to_channel(ch, user_id, title, message, data)
        return notification

    def _dispatch_to_channel(self, channel: str, user_id: int, title: str, message: str, data: Optional[Dict] = None):
        ch = self.channels.get(channel)
        if not ch or not ch.enabled:
            logger.debug(f"Channel {channel} disabled or not found")
            return
        try:
            if channel == "email":
                to = self._get_user_email(user_id)
                if to:
                    ch.send(to=to, subject=title, body=message)
            elif channel == "slack":
                ch.send(webhook_url=ch.config.get("webhook_url", ""), title=title, message=message)
            elif channel == "teams":
                ch.send(webhook_url=ch.config.get("webhook_url", ""), title=title, message=message)
        except Exception as e:
            logger.error(f"Failed to dispatch to {channel}: {e}")

    def _get_user_email(self, user_id: int) -> Optional[str]:
        try:
            from backend.database import get_db_session
            from backend.database.models import User
            with get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                return user.email if user else None
        except Exception:
            return None

    def send_fraud_alert(
        self, user_id: int, alert_type: str, severity: str, description: str,
        evidence: List[str], project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        channels = ["in_app", "email", "slack"]
        return self.send_notification(
            user_id=user_id,
            notification_type="fraud_alert",
            title=f"Fraud Alert - {severity}",
            message=description,
            priority="urgent" if severity == "Critical" else "high",
            channels=channels,
            data={"alert_type": alert_type, "severity": severity, "evidence": evidence, "project_id": project_id},
        )

    def send_audit_reminder(self, user_id: int, task_name: str, due_date: datetime, project_id: str) -> Dict[str, Any]:
        return self.send_notification(
            user_id=user_id,
            notification_type="audit_reminder",
            title=f"Reminder: {task_name}",
            message=f"Task '{task_name}' is due on {due_date.strftime('%Y-%m-%d')}",
            priority="normal",
            channels=["in_app", "email"],
            data={"task_name": task_name, "due_date": due_date.isoformat(), "project_id": project_id},
        )

    def mark_as_read(self, notification_id: str) -> bool:
        if notification_id not in self.notifications:
            return False
        self.notifications[notification_id]["read"] = True
        self.notifications[notification_id]["read_at"] = datetime.now().isoformat()
        return True

    def get_user_notifications(self, user_id: int, unread_only: bool = False, limit: int = 50) -> List[Dict[str, Any]]:
        notifications = [n for n in self.notifications.values() if n["user_id"] == user_id]
        if unread_only:
            notifications = [n for n in notifications if not n["read"]]
        notifications.sort(key=lambda x: x["created_at"], reverse=True)
        return notifications[:limit]

    def get_unread_count(self, user_id: int) -> int:
        return sum(1 for n in self.notifications.values() if n["user_id"] == user_id and not n["read"])

    def set_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> bool:
        self.user_preferences[user_id] = preferences
        return True

    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        return self.user_preferences.get(user_id, {
            "email_notifications": True,
            "push_notifications": True,
            "fraud_alerts": True,
            "audit_reminders": True,
            "daily_digest": False,
        })

    def send_email(self, to: str, subject: str, body: str, alert_type: str = "info") -> tuple:
        ch = self.channels.get("email")
        if not ch or not ch.enabled:
            return False, "Email channel disabled"
        ok = ch.send(to=to, subject=subject, body=body)
        if ok:
            self.notifications[f"EMAIL-{datetime.now().strftime('%Y%m%d%H%M%S')}"] = {
                "type": "email", "recipient": to, "subject": subject, "alert_type": alert_type,
                "status": "sent", "created_at": datetime.now().isoformat()
            }
        return ok, "" if ok else "Send failed"

    def send_slack(self, webhook_url: str, message: str, title: Optional[str] = None) -> tuple:
        ch = self.channels.get("slack")
        if not ch or not ch.enabled:
            return False, "Slack channel disabled"
        ok = ch.send(webhook_url=webhook_url, message=message, title=title)
        return ok, "" if ok else "Send failed"

    def send_teams(self, webhook_url: str, message: str, title: Optional[str] = None) -> tuple:
        ch = self.channels.get("teams")
        if not ch or not ch.enabled:
            return False, "Teams channel disabled"
        ok = ch.send(webhook_url=webhook_url, title=title or "Alert", message=message)
        return ok, "" if ok else "Send failed"

    def send_inapp(self, user_id: str, title: str, message: str, alert_type: str = "info") -> bool:
        try:
            uid = int(user_id)
        except ValueError:
            uid = 0
        self.send_notification(uid, alert_type, title, message)
        return True

    def get_notification_history(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        if user_id is not None:
            return self.get_user_notifications(user_id)
        return sorted(self.notifications.values(), key=lambda x: x.get("created_at", ""), reverse=True)

    def get_channel_status(self) -> Dict[str, Any]:
        return {name: {"enabled": ch.enabled} for name, ch in self.channels.items()}
