"""
Finovate Audit Nexus AI - Notifications API Endpoints
نقاط نهاية API للإشعارات
"""
from datetime import datetime
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.notification_service import NotificationService

router = APIRouter()
_service = NotificationService()


class NotificationRequest(BaseModel):
    channel: str
    title: str
    message: str
    recipients: List[str]
    alert_type: str = "info"


@router.post("/send")
async def send_notification(req: NotificationRequest):
    results = []
    for recipient in req.recipients:
        if req.channel == "email":
            ok, _ = _service.send_email(
                to=recipient, subject=req.title, body=req.message,
                alert_type=req.alert_type
            )
            results.append({"recipient": recipient, "success": ok})
        elif req.channel == "slack":
            ok, _ = _service.send_slack(webhook_url=recipient, message=req.message, title=req.title)
            results.append({"recipient": recipient, "success": ok})
        elif req.channel == "teams":
            ok, _ = _service.send_teams(webhook_url=recipient, message=req.message, title=req.title)
            results.append({"recipient": recipient, "success": ok})
        elif req.channel == "inapp":
            _service.send_inapp(user_id=recipient, title=req.title, message=req.message,
                                alert_type=req.alert_type)
            results.append({"recipient": recipient, "success": True})
        else:
            results.append({"recipient": recipient, "success": False, "error": f"Unknown channel: {req.channel}"})
    return {"success": True, "results": results, "timestamp": datetime.now().isoformat()}


@router.post("/fraud-alert")
async def send_fraud_alert(project_id: str, risk_level: str, description: str, recipients: List[str]):
    title = f"🚨 Fraud Alert: {project_id}"
    message = f"Risk Level: {risk_level}\nDescription: {description}"
    return await send_notification(NotificationRequest(
        channel="email", title=title, message=message, recipients=recipients, alert_type="critical"
    ))


@router.post("/audit-reminder")
async def send_audit_reminder(project_id: str, days_overdue: int, recipients: List[str]):
    title = f"⏰ Audit Reminder: {project_id}"
    message = f"Project {project_id} is {days_overdue} days overdue. Immediate action required."
    return await send_notification(NotificationRequest(
        channel="email", title=title, message=message, recipients=recipients, alert_type="warning"
    ))


@router.get("/history")
async def get_notification_history():
    return {"success": True, "data": _service.get_notification_history()}


@router.get("/channels")
async def get_available_channels():
    return {"success": True, "data": _service.get_channel_status()}
