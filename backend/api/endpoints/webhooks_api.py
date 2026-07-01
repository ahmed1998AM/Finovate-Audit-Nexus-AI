"""
Finovate Audit Nexus AI - Webhook API Endpoints
نقاط نهاية API لإدارة Webhook
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.api.endpoints.webhooks import get_webhook_manager

router = APIRouter()


class WebhookRegisterRequest(BaseModel):
    url: str
    events: List[str]
    secret: str = ""
    retry_count: int = 3
    timeout: int = 30


class WebhookUpdateRequest(BaseModel):
    url: Optional[str] = None
    events: Optional[List[str]] = None
    secret: Optional[str] = None
    enabled: Optional[bool] = None
    retry_count: Optional[int] = None
    timeout: Optional[int] = None


@router.post("/register")
async def register_webhook(req: WebhookRegisterRequest):
    manager = get_webhook_manager()
    sub = manager.register(req.url, req.events, req.secret, req.retry_count, req.timeout)
    return {"success": True, "data": {
        "subscription_id": sub.subscription_id,
        "url": sub.url,
        "events": sub.events,
        "enabled": sub.enabled,
    }}


@router.delete("/{subscription_id}")
async def unregister_webhook(subscription_id: str):
    manager = get_webhook_manager()
    if manager.unregister(subscription_id):
        return {"success": True, "message": "Webhook unregistered"}
    raise HTTPException(status_code=404, detail="Webhook not found")


@router.get("")
async def list_webhooks():
    manager = get_webhook_manager()
    return {"success": True, "data": manager.list_subscriptions()}


@router.get("/delivery-log")
async def delivery_log(limit: int = 100):
    manager = get_webhook_manager()
    return {"success": True, "data": manager.get_delivery_log(limit)}
