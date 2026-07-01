"""
Tests for ConnectorService - اختبارات خدمة إدارة الموصلات والأنظمة المحاسبية
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from backend.services.connector_service import ConnectorService


@pytest.fixture
def connector_service():
    """إنشاء خدمة موصلات جديدة لكل اختبار"""
    return ConnectorService()


@pytest.fixture
def sample_connector_params():
    """معلمات موصل نموذجية للتسجيل"""
    return {
        'connector_name': 'Test SAP',
        'connector_type': 'sap',
        'config': {'host': 'localhost', 'system_number': '00'},
        'company_id': 1
    }


@pytest.fixture
def registered_sap(connector_service, sample_connector_params):
    """تسجيل موصل SAP للاختبارات التي تحتاج موصل مسجل"""
    return connector_service.register_connector(**sample_connector_params)


class TestGetAvailableTypes:
    """اختبارات قائمة أنواع الموصلات المتاحة"""

    def test_get_available_types_returns_list(self, connector_service):
        """إرجاع قائمة بأنواع الموصلات المتاحة"""
        types = connector_service.get_available_types()
        assert isinstance(types, list)
        assert len(types) > 0

    def test_get_available_types_contains_sap(self, connector_service):
        """التحقق من وجود نوع SAP في القائمة"""
        types = connector_service.get_available_types()
        sap_types = [t for t in types if t['type'] == 'sap']
        assert len(sap_types) == 1
        assert 'SAPErpConnector' in sap_types[0]['name']


class TestRegisterConnector:
    """اختبارات تسجيل الموصلات"""

    def test_register_connector_success(self, connector_service, sample_connector_params):
        """تسجيل موصل بنجاح"""
        connector = connector_service.register_connector(**sample_connector_params)

        assert connector['connector_name'] == 'Test SAP'
        assert connector['connector_type'] == 'sap'
        assert connector['company_id'] == 1
        assert connector['status'] == 'inactive'
        assert connector['last_sync'] is None

    def test_register_connector_generates_id(self, connector_service, sample_connector_params):
        """التحقق من توليد معرف الموصل"""
        connector = connector_service.register_connector(**sample_connector_params)
        assert connector['connector_id'] == 'CONN-1-TEST-SAP'

    def test_register_connector_unsupported_type(self, connector_service, sample_connector_params):
        """تسجيل موصل بنوع غير مدعوم"""
        params = {**sample_connector_params, 'connector_type': 'nonexistent'}
        with pytest.raises(ValueError, match='Unsupported connector type'):
            connector_service.register_connector(**params)

    def test_register_connector_multiple_same_company(self, connector_service, sample_connector_params):
        """تسجيل موصلات متعددة لنفس الشركة"""
        c1 = connector_service.register_connector(**sample_connector_params)
        c2 = connector_service.register_connector(**{**sample_connector_params, 'connector_name': 'Test Oracle', 'connector_type': 'oracle'})

        assert c1['connector_id'] != c2['connector_id']
        assert len(connector_service.registered_connectors) == 2

    def test_register_connector_duplicate_name_different_id(self, connector_service, sample_connector_params):
        """تسجيل موصلين بنفس الاسم لشركتين مختلفتين"""
        c1 = connector_service.register_connector(**sample_connector_params)
        c2 = connector_service.register_connector(**{**sample_connector_params, 'company_id': 2})

        assert c1['connector_id'] != c2['connector_id']


class TestConnectDisconnect:
    """اختبارات الاتصال وقطع الاتصال"""

    def test_connect_success(self, connector_service, registered_sap, mock_connector_instance):
        """الاتصال بموصل بنجاح"""
        with patch('backend.services.connector_service._instantiate_connector', return_value=mock_connector_instance):
            result = connector_service.connect(registered_sap['connector_id'])

        assert result is True
        assert registered_sap['connector_id'] in connector_service.active_connections
        assert connector_service.registered_connectors[registered_sap['connector_id']]['status'] == 'active'

    def test_connect_non_existent_connector(self, connector_service):
        """الاتصال بموصل غير موجود"""
        result = connector_service.connect('NONEXISTENT')
        assert result is False

    def test_connect_failed_connection(self, connector_service, registered_sap, mock_connector_instance):
        """فشل الاتصال بسبب خطأ في الموصل"""
        mock_connector_instance.connect.return_value = False
        with patch('backend.services.connector_service._instantiate_connector', return_value=mock_connector_instance):
            result = connector_service.connect(registered_sap['connector_id'])

        assert result is False

    def test_connect_fails_when_no_connector_instance(self, connector_service, registered_sap):
        """فشل الاتصال عند عدم وجود موصل"""
        with patch('backend.services.connector_service._instantiate_connector', return_value=None):
            result = connector_service.connect(registered_sap['connector_id'])

        assert result is False
        assert registered_sap['connector_id'] not in connector_service.active_connections

    def test_disconnect_success(self, connector_service, registered_sap, mock_connector_instance):
        """قطع الاتصال بنجاح"""
        with patch('backend.services.connector_service._instantiate_connector', return_value=mock_connector_instance):
            connector_service.connect(registered_sap['connector_id'])

        result = connector_service.disconnect(registered_sap['connector_id'])

        assert result is True
        assert registered_sap['connector_id'] not in connector_service.active_connections
        assert connector_service.registered_connectors[registered_sap['connector_id']]['status'] == 'inactive'

    def test_disconnect_not_connected(self, connector_service, registered_sap):
        """قطع الاتصال بموصل غير متصل"""
        result = connector_service.disconnect(registered_sap['connector_id'])
        assert result is False

    def test_disconnect_calls_instance_disconnect(self, connector_service, registered_sap, mock_connector_instance):
        """التحقق من استدعاء disconnect على instance الموصل"""
        with patch('backend.services.connector_service._instantiate_connector', return_value=mock_connector_instance):
            connector_service.connect(registered_sap['connector_id'])

        connector_service.disconnect(registered_sap['connector_id'])
        mock_connector_instance.disconnect.assert_called_once()


class TestTestConnection:
    """اختبارات اختبار الاتصال"""

    def test_test_connection_connected(self, connector_service, registered_sap, mock_connector_instance):
        """اختبار اتصال لموصل متصل"""
        with patch('backend.services.connector_service._instantiate_connector', return_value=mock_connector_instance):
            connector_service.connect(registered_sap['connector_id'])
            result = connector_service.test_connection(registered_sap['connector_id'])

        assert result['success'] is True

    def test_test_connection_not_connected_registered(self, connector_service, registered_sap, mock_connector_instance):
        """اختبار اتصال لموصل مسجل لكن غير متصل (يتم إنشاء instance مؤقت)"""
        with patch('backend.services.connector_service._instantiate_connector', return_value=mock_connector_instance):
            result = connector_service.test_connection(registered_sap['connector_id'])

        assert result['success'] is True

    def test_test_connection_not_found(self, connector_service):
        """اختبار اتصال لموصل غير موجود"""
        result = connector_service.test_connection('NONEXISTENT')
        assert result['success'] is False
        assert 'Connector not found' in result['error']

    def test_test_connection_cannot_instantiate(self, connector_service, registered_sap):
        """اختبار اتصال عندما يتعذر إنشاء instance"""
        with patch('backend.services.connector_service._instantiate_connector', return_value=None):
            result = connector_service.test_connection(registered_sap['connector_id'])

        assert result['success'] is False
        assert 'Cannot instantiate connector' in result['error']


class TestGetHealthStatus:
    """اختبارات الحالة الصحية"""

    def test_health_status_healthy(self, connector_service, registered_sap, mock_connector_instance):
        """الحالة الصحية لموصل متصل"""
        with patch('backend.services.connector_service._instantiate_connector', return_value=mock_connector_instance):
            connector_service.connect(registered_sap['connector_id'])
            status = connector_service.get_health_status(registered_sap['connector_id'])

        assert status['status'] == 'healthy'

    def test_health_status_unhealthy_not_connected(self, connector_service, registered_sap):
        """الحالة الصحية لموصل غير متصل"""
        status = connector_service.get_health_status(registered_sap['connector_id'])
        assert status['status'] == 'unhealthy'
        assert 'Not connected' in status['error']


class TestSyncData:
    """اختبارات مزامنة البيانات"""

    def test_sync_data_success(self, connector_service, registered_sap, mock_connector_instance):
        """مزامنة البيانات بنجاح"""
        with patch('backend.services.connector_service._instantiate_connector', return_value=mock_connector_instance):
            connector_service.connect(registered_sap['connector_id'])
            result = connector_service.sync_data(
                registered_sap['connector_id'],
                ['journal_entries', 'trial_balance'],
                datetime(2024, 1, 1),
                datetime(2024, 12, 31)
            )

        assert result['success'] is True
        assert result['connector_id'] == registered_sap['connector_id']
        assert 'journal_entries' in result['records_synced']
        assert 'trial_balance' in result['records_synced']

    def test_sync_data_not_connected(self, connector_service, registered_sap):
        """مزامنة البيانات لموصل غير متصل"""
        result = connector_service.sync_data(registered_sap['connector_id'], ['journal_entries'])

        assert result['success'] is False
        assert 'Not connected' in result['error']

    def test_sync_data_empty_types(self, connector_service, registered_sap, mock_connector_instance):
        """مزامنة بدون أنواع بيانات"""
        with patch('backend.services.connector_service._instantiate_connector', return_value=mock_connector_instance):
            connector_service.connect(registered_sap['connector_id'])
            result = connector_service.sync_data(registered_sap['connector_id'], [])

        assert result['success'] is True
        assert result['records_synced'] == {}

    def test_sync_data_updates_last_sync(self, connector_service, registered_sap, mock_connector_instance):
        """التحقق من تحديث last_sync بعد المزامنة"""
        with patch('backend.services.connector_service._instantiate_connector', return_value=mock_connector_instance):
            connector_service.connect(registered_sap['connector_id'])
            connector_service.sync_data(registered_sap['connector_id'], ['accounts'])

        assert connector_service.registered_connectors[registered_sap['connector_id']]['last_sync'] is not None

    def test_sync_data_without_instance(self, connector_service, registered_sap, mock_connector_instance):
        """مزامنة بدون instance موصل (محاكاة)"""
        with patch('backend.services.connector_service._instantiate_connector', return_value=mock_connector_instance):
            connector_service.connect(registered_sap['connector_id'])
        connector_service.connector_instances.pop(registered_sap['connector_id'], None)

        result = connector_service.sync_data(registered_sap['connector_id'], ['journal_entries'])

        assert result['success'] is True
        assert result['records_synced']['journal_entries'] == 0


class TestMapChartOfAccounts:
    """اختبارات ربط دليل الحسابات"""

    def test_map_chart_of_accounts_success(self, connector_service, registered_sap):
        """ربط دليل الحسابات بنجاح"""
        source_accounts = [
            {'code': '1000', 'name': 'Cash'},
            {'code': '2000', 'name': 'AP'}
        ]
        result = connector_service.map_chart_of_accounts(registered_sap['connector_id'], source_accounts)

        assert result['success'] is True
        assert len(result['mapped_accounts']) == 2
        assert result['mapped_accounts'][0]['target_account'] == 'ACC-1000'
        assert result['mapping_confidence'] > 0

    def test_map_chart_of_accounts_stores_mapping(self, connector_service, registered_sap):
        """التحقق من تخزين نتيجة الربط"""
        result = connector_service.map_chart_of_accounts(
            registered_sap['connector_id'],
            [{'code': '1000', 'name': 'Cash'}]
        )
        assert connector_service.account_mappings[registered_sap['connector_id']] == result

    def test_map_chart_of_accounts_all_unmapped(self, connector_service, registered_sap):
        """جميع الحسابات غير مرتبطة (confidence منخفض)"""
        with patch('backend.services.connector_service.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2024, 1, 1)
            result = connector_service.map_chart_of_accounts(
                registered_sap['connector_id'],
                [{'code': 'UNKNOWN'}]
            )

        assert result['success'] is True
        assert len(result['mapped_accounts']) == 1
        assert result['mapping_confidence'] == 0.85


class TestGetConnectionStatus:
    """اختبارات حالة الاتصال"""

    def test_get_connection_status_exists(self, connector_service, registered_sap):
        """حالة اتصال لموصل موجود"""
        status = connector_service.get_connection_status(registered_sap['connector_id'])
        assert status['exists'] is True
        assert status['is_connected'] is False

    def test_get_connection_status_not_found(self, connector_service):
        """حالة اتصال لموصل غير موجود"""
        status = connector_service.get_connection_status('NONEXISTENT')
        assert status['exists'] is False

    def test_get_connection_status_with_connection_info(self, connector_service, registered_sap, mock_connector_instance):
        """حالة اتصال مع معلومات الاتصال"""
        with patch('backend.services.connector_service._instantiate_connector', return_value=mock_connector_instance):
            connector_service.connect(registered_sap['connector_id'])
            status = connector_service.get_connection_status(registered_sap['connector_id'])

        assert status['is_connected'] is True
        assert 'connection_info' in status
        assert status['connection_info']['status'] == 'connected'


class TestListConnectors:
    """اختبارات قائمة الموصلات"""

    def test_list_connectors_empty(self, connector_service):
        """قائمة فارغة عند عدم وجود موصلات"""
        assert connector_service.list_connectors() == []

    def test_list_connectors_all(self, connector_service, sample_connector_params):
        """قائمة بجميع الموصلات"""
        connector_service.register_connector(**sample_connector_params)
        connector_service.register_connector(**{**sample_connector_params, 'connector_name': 'Oracle', 'connector_type': 'oracle', 'company_id': 2})

        connectors = connector_service.list_connectors()
        assert len(connectors) == 2

    def test_list_connectors_filter_by_company(self, connector_service, sample_connector_params):
        """تصفية الموصلات حسب الشركة"""
        connector_service.register_connector(**sample_connector_params)
        connector_service.register_connector(**{**sample_connector_params, 'connector_name': 'Oracle', 'connector_type': 'oracle', 'company_id': 2})

        connectors = connector_service.list_connectors(company_id=1)
        assert len(connectors) == 1


class TestRemoveConnector:
    """اختبارات إزالة الموصلات"""

    def test_remove_connector_success(self, connector_service, registered_sap):
        """إزالة موصل بنجاح"""
        result = connector_service.remove_connector(registered_sap['connector_id'])
        assert result is True
        assert registered_sap['connector_id'] not in connector_service.registered_connectors

    def test_remove_connector_not_found(self, connector_service):
        """إزالة موصل غير موجود"""
        result = connector_service.remove_connector('NONEXISTENT')
        assert result is False

    def test_remove_connector_disconnects_if_connected(self, connector_service, registered_sap, mock_connector_instance):
        """إزالة موصل متصل يؤدي إلى قطع الاتصال أولاً"""
        with patch('backend.services.connector_service._instantiate_connector', return_value=mock_connector_instance):
            connector_service.connect(registered_sap['connector_id'])

        result = connector_service.remove_connector(registered_sap['connector_id'])

        assert result is True
        assert registered_sap['connector_id'] not in connector_service.registered_connectors
        assert registered_sap['connector_id'] not in connector_service.active_connections

    def test_remove_connector_clears_mappings(self, connector_service, registered_sap):
        """إزالة الموصل يمسح خرائط الحسابات المرتبطة"""
        connector_service.map_chart_of_accounts(registered_sap['connector_id'], [{'code': '1000', 'name': 'Cash'}])
        connector_service.remove_connector(registered_sap['connector_id'])

        assert registered_sap['connector_id'] not in connector_service.account_mappings
