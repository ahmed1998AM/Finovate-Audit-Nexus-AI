"""
Finovate Audit Nexus AI - Webhook System
Send and receive webhooks for external integrations
"""

import hashlib
import hmac
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests as http_requests

from backend.core.events import Event, get_event_bus

logger = logging.getLogger(__name__)


@dataclass
class WebhookSubscription:
    subscription_id: str
    url: str
    events: List[str]
    secret: str = ""
    enabled: bool = True
    retry_count: int = 3
    timeout: int = 30
    headers: Dict[str, str] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class WebhookManager:
    def __init__(self):
        self._subscriptions: Dict[str, WebhookSubscription] = {}
        self._delivery_log: List[Dict[str, Any]] = []
        self._max_log: int = 1000
        self._init_bridge()

    def _init_bridge(self):
        bus = get_event_bus()
        bus.on("*", self._handle_event)

    async def _handle_event(self, event: Event):
        if event.event_type.startswith("webhook:"):
            return
        for sub in list(self._subscriptions.values()):
            if not sub.enabled:
                continue
            if event.event_type in sub.events or "*" in sub.events:
                self._deliver(sub, event)

    def _deliver(self, sub: WebhookSubscription, event: Event):
        payload = {
            "event": event.event_type,
            "data": event.data,
            "source": event.source,
            "timestamp": event.timestamp.isoformat(),
            "event_id": event.event_id,
            "delivered_at": datetime.now().isoformat(),
        }
        body = json.dumps(payload)
        signature = ""
        if sub.secret:
            signature = hmac.new(sub.secret.encode(), body.encode(), hashlib.sha256).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Event": event.event_type,
            "X-Webhook-Signature": signature,
            "X-Webhook-Timestamp": str(int(time.time())),
            **sub.headers,
        }

        last_error = None
        for attempt in range(sub.retry_count):
            try:
                resp = http_requests.post(sub.url, data=body, headers=headers, timeout=sub.timeout)
                if resp.status_code < 300:
                    self._log_delivery(sub.subscription_id, event.event_type, True)
                    return
                last_error = f"HTTP {resp.status_code}"
            except Exception as e:
                last_error = str(e)
            if attempt < sub.retry_count - 1:
                time.sleep(2 ** attempt)

        logger.error(f"Webhook delivery failed to {sub.url}: {last_error}")
        self._log_delivery(sub.subscription_id, event.event_type, False, last_error)

    def _log_delivery(self, sub_id: str, event_type: str, success: bool, error: str = ""):
        self._delivery_log.append({
            "subscription_id": sub_id,
            "event_type": event_type,
            "success": success,
            "error": error,
            "timestamp": datetime.now().isoformat(),
        })
        if len(self._delivery_log) > self._max_log:
            self._delivery_log = self._delivery_log[-self._max_log:]

    def register(self, url: str, events: List[str], secret: str = "", retry_count: int = 3, timeout: int = 30) -> WebhookSubscription:
        sub = WebhookSubscription(
            subscription_id=f"wh_{uuid.uuid4().hex[:12]}",
            url=url, events=events, secret=secret,
            retry_count=retry_count, timeout=timeout,
        )
        self._subscriptions[sub.subscription_id] = sub
        logger.info(f"Webhook registered: {sub.subscription_id} -> {url} ({events})")
        return sub

    def unregister(self, subscription_id: str) -> bool:
        if subscription_id in self._subscriptions:
            del self._subscriptions[subscription_id]
            logger.info(f"Webhook unregistered: {subscription_id}")
            return True
        return False

    def get_subscription(self, subscription_id: str) -> Optional[WebhookSubscription]:
        return self._subscriptions.get(subscription_id)

    def list_subscriptions(self) -> List[Dict[str, Any]]:
        return [
            {
                "subscription_id": s.subscription_id,
                "url": s.url,
                "events": s.events,
                "enabled": s.enabled,
                "created_at": s.created_at,
            }
            for s in self._subscriptions.values()
        ]

    def get_delivery_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._delivery_log[-limit:]


_webhook_instance: Optional[WebhookManager] = None


def get_webhook_manager() -> WebhookManager:
    global _webhook_instance
    if _webhook_instance is None:
        _webhook_instance = WebhookManager()
    return _webhook_instance
