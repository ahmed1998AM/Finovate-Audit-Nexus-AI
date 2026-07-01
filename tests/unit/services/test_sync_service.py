"""
Tests for SyncService - اختبارات خدمة مزامنة البيانات في الخلفية
"""

import time
from unittest.mock import MagicMock, patch

import pytest


class TestSyncService:
    """اختبارات SyncService"""

    @pytest.fixture
    def mock_audit_service(self):
        """محاكاة خدمة المراجعة"""
        return MagicMock()

    @pytest.fixture
    def mock_thread(self):
        """محاكاة threading.Thread"""
        thread = MagicMock()
        thread.daemon = True
        return thread

    @pytest.fixture
    def sync_service(self, mock_audit_service, mock_thread):
        """إنشاء خدمة مزامنة بمكونات وهمية"""
        with patch('backend.services.sync_service.get_audit_service', return_value=mock_audit_service), \
                patch('threading.Thread', return_value=mock_thread):
            from backend.services.sync_service import SyncService
            service = SyncService()
            service.sync_thread = None
            yield service

    def test_initial_state(self, sync_service):
        """الحالة الأولية للخدمة - غير عاملة"""
        assert sync_service.is_running is False
        assert sync_service.sync_thread is None

    def test_start_background_sync_creates_thread(self, sync_service, mock_thread):
        """بدء المزامنة ينشئ thread جديد"""
        with patch('threading.Thread', return_value=mock_thread) as mock_thread_cls:
            sync_service.start_background_sync(interval=60, callback=None)

        mock_thread_cls.assert_called_once_with(
            target=sync_service._sync_loop,
            args=(60, None),
            daemon=True
        )
        mock_thread.start.assert_called_once()

    def test_start_background_sync_sets_running_flag(self, sync_service, mock_thread):
        """بدء المزامنة يضبط is_running على True"""
        with patch('threading.Thread', return_value=mock_thread):
            sync_service.start_background_sync(interval=60)

        assert sync_service.is_running is True

    def test_start_background_sync_with_callback(self, sync_service, mock_thread):
        """بدء المزامنة مع دالة استدعاء"""
        callback = MagicMock()

        with patch('threading.Thread', return_value=mock_thread):
            sync_service.start_background_sync(interval=30, callback=callback)

        assert sync_service.sync_thread is not None

    def test_start_background_sync_does_not_restart(self, sync_service, mock_thread):
        """عدم إعادة تشغيل المزامنة إذا كانت قيد التشغيل"""
        sync_service.is_running = True

        with patch('threading.Thread') as mock_thread_cls:
            sync_service.start_background_sync(interval=60)

        mock_thread_cls.assert_not_called()

    def test_stop_sync_sets_running_false(self, sync_service, mock_thread):
        """إيقاف المزامنة يضبط is_running على False"""
        with patch('threading.Thread', return_value=mock_thread):
            sync_service.start_background_sync(interval=60)

        sync_service.stop_sync()

        assert sync_service.is_running is False

    def test_stop_sync_joins_thread(self, sync_service, mock_thread):
        """إيقاف المزامنة يستدعي join على thread"""
        with patch('threading.Thread', return_value=mock_thread):
            sync_service.start_background_sync(interval=60)

        sync_service.stop_sync()

        mock_thread.join.assert_called_once_with(timeout=2)

    def test_stop_sync_without_start(self, sync_service):
        """إيقاف المزامنة دون بدء لا يسبب خطأ"""
        sync_service.stop_sync()
        assert sync_service.is_running is False

    def test_stop_sync_no_thread(self, sync_service):
        """إيقاف المزامنة عندما يكون thread None"""
        sync_service.is_running = True
        sync_service.sync_thread = None
        sync_service.stop_sync()
        assert sync_service.is_running is False

    def test_sync_loop_calls_callback_on_success(self, sync_service, mock_thread):
        """حلقة المزامنة تستدعي callback عند النجاح"""
        callback = MagicMock()
        sync_service.is_running = True

        def _stop_loop(*args):
            sync_service.is_running = False

        with patch.object(time, 'sleep', side_effect=_stop_loop):
            sync_service._sync_loop(interval=1, callback=callback)

        callback.assert_called_once()
        call_args = callback.call_args[0][0]
        assert call_args['status'] == 'success'
        assert 'timestamp' in call_args

    def test_sync_loop_calls_callback_on_error(self, sync_service, mock_thread):
        """حلقة المزامنة تستدعي callback عند الخطأ"""
        sync_service.is_running = True
        call_attempts = []

        def _fail_once(data):
            call_attempts.append(data)
            if len(call_attempts) == 1:
                raise Exception('Sync failed')

        def _stop_loop(*args):
            sync_service.is_running = False

        with patch.object(time, 'sleep', side_effect=_stop_loop):
            sync_service._sync_loop(interval=1, callback=_fail_once)

        assert len(call_attempts) == 2
        assert call_attempts[0]['status'] == 'success'
        assert call_attempts[1]['status'] == 'error'
        assert call_attempts[1]['message'] == 'Sync failed'

    def test_sync_loop_without_callback(self, sync_service, mock_thread):
        """حلقة المزامنة تعمل بدون callback"""
        sync_service.is_running = True

        def _stop_loop(*args):
            sync_service.is_running = False

        with patch.object(time, 'sleep', side_effect=_stop_loop):
            sync_service._sync_loop(interval=1, callback=None)

    def test_sync_loop_sleeps_for_interval(self, sync_service, mock_thread):
        """التحقق من أن الحلقة تنتظر للفاصل الزمني المحدد"""
        callback = MagicMock()
        sync_service.is_running = True

        def _stop_loop(*args):
            sync_service.is_running = False

        with patch.object(time, 'sleep', side_effect=_stop_loop) as mock_sleep:
            sync_service._sync_loop(interval=42, callback=callback)

        mock_sleep.assert_called_once_with(42)

    def test_sync_loop_loops_while_running(self, sync_service, mock_thread):
        """التحقق من أن الحلقة تستمر في التكرار أثناء التشغيل"""
        callback = MagicMock()
        sync_service.is_running = True
        loop_count = 0

        def _run_two_loops(*args):
            nonlocal loop_count
            loop_count += 1
            if loop_count >= 2:
                sync_service.is_running = False

        with patch.object(time, 'sleep', side_effect=_run_two_loops):
            sync_service._sync_loop(interval=1, callback=callback)

        assert callback.call_count == 2
