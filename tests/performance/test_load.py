"""
Finovate Audit Nexus AI - Load & Stress Tests
اختبارات الأداء والتحمل
"""

import pytest
import sys
import time
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestCachePerformance:
    def test_cache_set_get(self):
        from backend.core.cache import CacheManager
        cache = CacheManager()
        cache.set("test_key", {"data": "value"}, ttl=60)
        result = cache.get("test_key")
        assert result == {"data": "value"}
        cache.delete("test_key")
        assert cache.get("test_key") is None

    def test_cache_expiry(self):
        import time as ttime
        from backend.core.cache import CacheManager
        cache = CacheManager()
        cache.set("expire_test", "data", ttl=1)
        assert cache.get("expire_test") == "data"
        ttime.sleep(1.1)
        assert cache.get("expire_test") is None

    def test_cache_stats(self):
        from backend.core.cache import CacheManager
        cache = CacheManager()
        stats = cache.get_stats()
        assert "items" in stats or "backend" in stats


class TestTaskQueuePerformance:
    def test_submit_and_complete(self):
        from backend.core.tasks import get_task_queue
        queue = get_task_queue()

        def dummy():
            return 42

        task_id = queue.submit("dummy", dummy)
        import time
        time.sleep(0.1)
        task = queue.get_task(task_id)
        assert task is not None
        assert task.status.value == "success"
        assert queue.get_result(task_id) == 42

    def test_task_failure(self):
        from backend.core.tasks import get_task_queue

        def fail():
            raise ValueError("Intentional failure")

        task_id = get_task_queue().submit("fail", fail)
        import time
        time.sleep(0.1)
        task = get_task_queue().get_task(task_id)
        assert task.status.value == "failed"
        assert "Intentional failure" in task.error

    def test_multiple_tasks(self):
        from backend.core.tasks import get_task_queue
        queue = get_task_queue()
        ids = []

        def make_fn(v):
            return lambda: v * 2

        for i in range(10):
            ids.append(queue.submit(f"task_{i}", make_fn(i)))

        import time
        time.sleep(0.3)
        for i, tid in enumerate(ids):
            task = queue.get_task(tid)
            assert task is not None
            if task.status.value == "success":
                assert queue.get_result(tid) == i * 2

    def test_list_tasks(self):
        from backend.core.tasks import get_task_queue
        tasks = get_task_queue().list_tasks()
        assert isinstance(tasks, list)

    def test_async_task_decorator(self):
        from backend.core.tasks import async_task

        @async_task(name="test_decorator")
        def sample_task(x: int, y: int) -> int:
            return x + y

        task_id = sample_task(3, 4)
        assert isinstance(task_id, str)
        assert task_id.startswith("task_")


class TestEventBusPerformance:
    def test_event_emit_receive(self):
        from backend.core.events import EventBus
        bus = EventBus()
        received = []

        async def handler(event):
            received.append(event.data)

        bus.on("test.event", handler)

        import asyncio
        asyncio.run(bus.emit("test.event", {"msg": "hello"}))
        assert len(received) == 1
        assert received[0]["msg"] == "hello"

    def test_event_once(self):
        from backend.core.events import EventBus
        bus = EventBus()
        count = 0

        async def handler(event):
            nonlocal count
            count += 1

        bus.once("once.event", handler)
        import asyncio
        asyncio.run(bus.emit("once.event", {}))
        asyncio.run(bus.emit("once.event", {}))
        assert count == 1

    def test_multiple_handlers(self):
        from backend.core.events import EventBus
        bus = EventBus()
        results = []

        async def h1(e):
            results.append("h1")

        async def h2(e):
            results.append("h2")

        bus.on("multi", h1)
        bus.on("multi", h2)
        import asyncio
        asyncio.run(bus.emit("multi", {}))
        assert len(results) == 2

    def test_handler_exception_does_not_break_bus(self):
        from backend.core.events import EventBus
        bus = EventBus()
        results = []

        def failing(e):
            raise RuntimeError("fail")

        def good(e):
            results.append("ok")

        bus.on("error.event", failing)
        bus.on("error.event", good)
        import asyncio
        asyncio.run(bus.emit("error.event", {}))
        assert len(results) == 1


class TestEventBusHistory:
    def test_history_limit(self):
        from backend.core.events import EventBus
        bus = EventBus()
        import asyncio
        for i in range(1050):
            asyncio.run(bus.emit("bulk", {"i": i}))
        hist = bus.history()
        assert len(hist) <= 1000

    def test_history_filter(self):
        from backend.core.events import EventBus
        bus = EventBus()
        import asyncio
        asyncio.run(bus.emit("type_a", {"a": 1}))
        asyncio.run(bus.emit("type_b", {"b": 2}))
        hist_a = bus.history(event_type="type_a")
        assert len(hist_a) == 1
        assert hist_a[0].data["a"] == 1


class TestWebSocketManager:
    def test_manager_initialization(self):
        from backend.api.websocket import WebSocketManager
        mgr = WebSocketManager()
        assert mgr.connected_count == 0
        assert mgr.room_count == 0

    def test_room_operations(self):
        from backend.api.websocket import WebSocketManager
        import asyncio

        async def test():
            mgr = WebSocketManager()
            assert mgr.room_count == 0
        asyncio.run(test())


class TestTLSConfig:
    def test_tls_config_defaults(self):
        from backend.core.tls import TLSConfig
        cfg = TLSConfig()
        assert cfg.enabled is False
        assert cfg.get_uvicorn_kwargs() == {}
        assert cfg.get_ssl_context() is None

    def test_tls_invalid_paths(self):
        import os
        old_cert = os.environ.get('TLS_CERT_PATH')
        old_key = os.environ.get('TLS_KEY_PATH')
        os.environ['TLS_ENABLED'] = 'true'
        os.environ['TLS_CERT_PATH'] = '/nonexistent/cert.pem'
        os.environ['TLS_KEY_PATH'] = '/nonexistent/key.pem'
        from backend.core.tls import TLSConfig
        cfg = TLSConfig()
        assert cfg.enabled is False
        if old_cert:
            os.environ['TLS_CERT_PATH'] = old_cert
        else:
            del os.environ['TLS_CERT_PATH']
        if old_key:
            os.environ['TLS_KEY_PATH'] = old_key
        else:
            del os.environ['TLS_KEY_PATH']
        os.environ['TLS_ENABLED'] = 'false'


class TestI18n:
    def test_arabic_translation(self):
        from backend.core.i18n import I18n
        i18n = I18n(default_lang='ar')
        assert i18n.t('dashboard.title') == 'لوحة التحكم'
        assert i18n.t('app.name') != ''
        assert i18n.direction('ar') == 'rtl'

    def test_english_translation(self):
        from backend.core.i18n import I18n
        i18n = I18n(default_lang='en')
        assert i18n.t('dashboard.title') == 'Dashboard'
        assert i18n.direction('en') == 'ltr'

    def test_missing_key_falls_back(self):
        from backend.core.i18n import I18n
        i18n = I18n()
        result = i18n.t('nonexistent_key')
        assert result == 'nonexistent_key'

    def test_available_languages(self):
        from backend.core.i18n import I18n
        i18n = I18n()
        langs = i18n.available_languages()
        assert len(langs) == 2
        codes = [l['code'] for l in langs]
        assert 'ar' in codes
        assert 'en' in codes


class TestWebhookManager:
    def test_register_and_unregister(self):
        from backend.api.endpoints.webhooks import WebhookManager
        mgr = WebhookManager()
        sub = mgr.register("https://test.com/hook", ["test.event"], "secret123")
        assert sub.subscription_id.startswith("wh_")
        assert sub.url == "https://test.com/hook"
        assert len(mgr.list_subscriptions()) == 1
        mgr.unregister(sub.subscription_id)
        assert len(mgr.list_subscriptions()) == 0

    def test_delivery_log(self):
        from backend.api.endpoints.webhooks import WebhookManager
        mgr = WebhookManager()
        log = mgr.get_delivery_log()
        assert isinstance(log, list)


class TestEmailService:
    def test_service_initialization(self):
        from backend.services.email_service import EmailService
        svc = EmailService()
        assert svc.is_configured() is False

    def test_render_template(self):
        from backend.services.email_service import EmailService
        svc = EmailService()
        html = svc._render("base.html", title="Test", direction="ltr")
        assert "Test" in html
        assert "Finovate" in html


class TestRBAC:
    def test_admin_has_all_permissions(self):
        from backend.security.rbac import Role, Permission, has_permission
        for perm in Permission:
            assert has_permission(Role.ADMIN, perm), f"Admin missing {perm}"

    def test_viewer_has_limited_permissions(self):
        from backend.security.rbac import Role, Permission, has_permission
        assert has_permission(Role.VIEWER, Permission.AUDIT_READ)
        assert has_permission(Role.VIEWER, Permission.REPORT_READ)
        assert not has_permission(Role.VIEWER, Permission.ADMIN_ACCESS)
        assert not has_permission(Role.VIEWER, Permission.USER_CREATE)

    def test_auditor_can_approve(self):
        from backend.security.rbac import Role, Permission, has_permission
        assert has_permission(Role.AUDITOR, Permission.AUDIT_APPROVE)
        assert not has_permission(Role.AUDITOR, Permission.ADMIN_ACCESS)

    def test_role_permissions_consistency(self):
        from backend.security.rbac import Role, Permission, get_role_permissions
        for role in Role:
            perms = get_role_permissions(role)
            assert isinstance(perms, set)
            for p in perms:
                assert isinstance(p, Permission)
