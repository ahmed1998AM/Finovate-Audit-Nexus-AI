"""
Connector Service - خدمة إدارة الموصلات والأنظمة المحاسبية
"""

import importlib
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# خريطة الموصلات: (module_path, class_name, config_cls_name, factory_name)
# يتم استخدام factory_name للتحميل البطيء عبر connectors.__init__
_CONNECTOR_MAP = {
    'sap': ('connectors.sap_connector.connector', 'SAPErpConnector', 'SAPConnectionConfig', 'create_sap_connector'),
    'oracle': ('connectors.oracle_connector.connector', 'OracleErpConnector', 'OracleConnectionConfig', 'create_oracle_connector'),
    'quickbooks': ('connectors.quickbooks_connector.connector', 'QuickBooksConnector', 'QuickBooksConnectionConfig', 'create_quickbooks_connector'),
    'dynamics': ('connectors.dynamics_connector.connector', 'DynamicsErpConnector', 'DynamicsConnectionConfig', 'create_dynamics_connector'),
    'odoo': ('connectors.odoo_connector.connector', 'OdooConnector', 'OdooConnectionConfig', 'create_odoo_connector'),
    'netsuite': ('connectors.netsuite_connector.connector', 'NetSuiteErpConnector', 'NetSuiteConnectionConfig', 'create_netsuite_connector'),
    'xero': ('connectors.xero_connector.connector', 'XeroConnector', 'XeroConnectionConfig', 'create_xero_connector'),
    'zoho': ('connectors.zoho_connector.connector', 'ZohoBooksConnector', None, 'create_zoho_connector'),
    'sage': ('connectors.sage_connector.connector', 'SageErpConnector', 'SageConnectionConfig', 'create_sage_connector'),
    'workday': ('connectors.workday_connector.connector', 'WorkdayErpConnector', 'WorkdayConnectionConfig', 'create_workday_connector'),
    'ebs': ('connectors.ebs_connector.connector', 'EBSErpConnector', 'EBSConnectionConfig', 'create_ebs_connector'),
    'infor': ('connectors.infor_connector.connector', 'InforErpConnector', 'InforConnectionConfig', 'create_infor_connector'),
    'sql': ('connectors.sql_connector.connector', 'SQLConnector', 'SQLConnectionConfig', 'create_sql_connector'),
    'api': ('connectors.api_connector.connector', 'APIConnector', 'APIConnectionConfig', 'create_api_connector'),
    'excel': ('connectors.excel_connector.connector', 'ExcelConnector', None, 'create_excel_connector'),
}


def _instantiate_connector(connector_type: str, config: Dict[str, Any]):
    """إنشاء موصل باستخدام factory function إن أمكن"""
    entry = _CONNECTOR_MAP.get(connector_type)
    if entry is None:
        raise ValueError(f"Unknown connector type: {connector_type}")

    module_path, class_name, config_cls_name, factory_name = entry

    # استخدام factory function للتحميل البطيء
    try:
        connectors_pkg = importlib.import_module('connectors')
        factory = getattr(connectors_pkg, factory_name, None)
        if factory is not None:
            return factory(config)
    except (ImportError, AttributeError):
        pass

    # Fallback: إنشاء مباشر
    try:
        mod = importlib.import_module(module_path)
        cls = getattr(mod, class_name)
        if config_cls_name:
            cfg_cls = getattr(mod, config_cls_name)
            cfg = cfg_cls(**{k: v for k, v in config.items() if k in cfg_cls.__dataclass_fields__})
            return cls(cfg)
        return cls(config)
    except (ImportError, AttributeError, TypeError) as e:
        logger.error("Cannot instantiate %s connector (%s) — check required SDK installation", connector_type, e)
        return None


class ConnectorService:
    """
    خدمة إدارة الموصلات والأنظمة المحاسبية

    المسؤولة عن:
    - تسجيل الموصلات
    - إدارة اتصالات ERP
    - مزامنة البيانات
    - توحيد نماذج البيانات
    - إدارة دليل الحسابات
    """

    def __init__(self):
        """تهيئة خدمة الموصلات"""
        self.registered_connectors = {}
        self.active_connections = {}
        self.connector_instances = {}
        self.account_mappings = {}
        logger.info("ConnectorService initialized")

    @staticmethod
    def get_available_types() -> List[Dict[str, str]]:
        """قائمة أنواع الموصلات المتاحة"""
        return [
            {'type': k, 'name': v[1]} for k, v in _CONNECTOR_MAP.items()
        ]

    def register_connector(
        self,
        connector_name: str,
        connector_type: str,
        config: Dict[str, Any],
        company_id: int
    ) -> Dict[str, Any]:
        """
        تسجيل موصل جديد

        Args:
            connector_name: اسم الموصل
            connector_type: نوع الموصل (sap, oracle, dynamics, odoo, etc.)
            config: إعدادات الاتصال
            company_id: معرف الشركة

        Returns:
            معلومات الموصل المسجل
        """
        if connector_type not in _CONNECTOR_MAP:
            raise ValueError(f"Unsupported connector type: {connector_type}. "
                             f"Available: {list(_CONNECTOR_MAP.keys())}")

        connector_id = f"CONN-{company_id}-{connector_name.upper().replace(' ', '-')}"

        connector = {
            'connector_id': connector_id,
            'connector_name': connector_name,
            'connector_type': connector_type,
            'company_id': company_id,
            'config': config,
            'status': 'inactive',
            'last_sync': None,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }

        self.registered_connectors[connector_id] = connector
        logger.info("Registered connector: %s", connector_id)

        return connector

    def connect(self, connector_id: str) -> bool:
        """
        إنشاء اتصال مع الموصل

        Args:
            connector_id: معرف الموصل

        Returns:
            True إذا نجح الاتصال
        """
        if connector_id not in self.registered_connectors:
            logger.error("Connector %s not found", connector_id)
            return False

        connector = self.registered_connectors[connector_id]
        connector_type = connector['connector_type']
        config = connector['config']

        logger.info("Connecting to %s system...", connector_type)

        instance = _instantiate_connector(connector_type, config)
        if instance is None:
            logger.error("Cannot instantiate %s connector — check that required SDK is installed", connector_type)
            return False
        try:
            ok = instance.connect()
            if not ok:
                logger.error("Failed to connect to %s", connector_type)
                return False
            self.connector_instances[connector_id] = instance
        except Exception as e:
            logger.error("Error connecting to %s: %s", connector_type, e)
            return False

        self.active_connections[connector_id] = {
            'connected_at': datetime.now(),
            'status': 'connected',
            'session_id': f"SES-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }

        connector['status'] = 'active'
        connector['updated_at'] = datetime.now()

        logger.info("Connected to connector: %s", connector_id)
        return True

    def disconnect(self, connector_id: str) -> bool:
        """
        قطع الاتصال مع الموصل

        Args:
            connector_id: معرف الموصل

        Returns:
            True إذا نجح قطع الاتصال
        """
        inst = self.connector_instances.pop(connector_id, None)
        if inst is not None:
            try:
                inst.disconnect()
            except Exception as e:
                logger.warning("Error disconnecting %s: %s", connector_id, e)

        was_connected = connector_id in self.active_connections
        self.active_connections.pop(connector_id, None)

        if connector_id in self.registered_connectors:
            self.registered_connectors[connector_id]['status'] = 'inactive'
            self.registered_connectors[connector_id]['updated_at'] = datetime.now()

        logger.info("Disconnected from connector: %s", connector_id)
        return was_connected

    def test_connection(self, connector_id: str) -> Dict[str, Any]:
        """
        اختبار اتصال الموصل

        Args:
            connector_id: معرف الموصل

        Returns:
            نتيجة الاختبار
        """
        inst = self.connector_instances.get(connector_id)
        if inst is None:
            connector = self.registered_connectors.get(connector_id)
            if connector is None:
                return {'success': False, 'error': 'Connector not found'}
            inst = _instantiate_connector(connector['connector_type'], connector['config'])
            if inst is None:
                return {'success': False, 'error': 'Cannot instantiate connector'}

        try:
            if hasattr(inst, 'test_connection'):
                return inst.test_connection()
            return {'success': inst.is_connected, 'connected': inst.is_connected}
        except Exception as e:
            logger.error("Test connection failed for %s: %s", connector_id, e)
            return {'success': False, 'error': str(e)}

    def get_health_status(self, connector_id: str) -> Dict[str, Any]:
        """الحصول على الحالة الصحية للموصل"""
        inst = self.connector_instances.get(connector_id)
        if inst is None:
            return {'connector_id': connector_id, 'status': 'unhealthy', 'error': 'Not connected'}
        try:
            if hasattr(inst, 'get_health_status'):
                return inst.get_health_status()
            return {'connector_id': connector_id, 'status': 'healthy' if inst.is_connected else 'unhealthy'}
        except Exception as e:
            return {'connector_id': connector_id, 'status': 'unhealthy', 'error': str(e)}

    def sync_data(
        self,
        connector_id: str,
        data_types: List[str],
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        مزامنة البيانات من النظام المحاسبي

        Args:
            connector_id: معرف الموصل
            data_types: أنواع البيانات المطلوبة (journal_entries, trial_balance, etc.)
            date_from: تاريخ البدء
            date_to: تاريخ الانتهاء

        Returns:
            نتيجة المزامنة
        """
        if connector_id not in self.active_connections:
            logger.error("Connector %s is not connected", connector_id)
            return {'success': False, 'error': 'Not connected'}

        logger.info("Syncing data from connector %s: %s", connector_id, data_types)

        sync_result = {
            'success': True,
            'connector_id': connector_id,
            'synced_at': datetime.now(),
            'data_types': data_types,
            'records_synced': {},
            'errors': []
        }

        inst = self.connector_instances.get(connector_id)
        fy = str((date_from or datetime.now()).year)

        for data_type in data_types:
            record_count = 0
            try:
                if inst is not None:
                    if data_type == 'journal_entries' and hasattr(inst, 'get_journal_entries'):
                        entries = inst.get_journal_entries(fiscal_year=fy) if inst.__class__.__name__ == 'SAPErpConnector' else inst.get_journal_entries(date_from=fy)
                        record_count = len(entries) if entries else 0
                    elif data_type == 'trial_balance' and hasattr(inst, 'get_trial_balance'):
                        tb = inst.get_trial_balance(fiscal_year=fy) if inst.__class__.__name__ == 'SAPErpConnector' else inst.get_trial_balance()
                        record_count = len(tb) if tb else 0
                    elif data_type == 'financial_statements' and hasattr(inst, 'get_financial_statements'):
                        stmt = inst.get_financial_statements(fiscal_year=fy)
                        record_count = 1 if stmt else 0
                    elif data_type == 'accounts' and hasattr(inst, 'get_accounts'):
                        accs = inst.get_accounts()
                        record_count = len(accs) if accs else 0
                    else:
                        record_count = 0
                else:
                    record_count = 0
            except NotImplementedError:
                logger.warning("Data type %s not implemented by %s", data_type, type(inst).__name__)
                record_count = 0
            except Exception as e:
                logger.error("Error syncing %s: %s", data_type, e)
                sync_result['errors'].append({data_type: str(e)})
                record_count = 0

            sync_result['records_synced'][data_type] = record_count
            logger.info("Synced %d %s records", record_count, data_type)

        if connector_id in self.registered_connectors:
            self.registered_connectors[connector_id]['last_sync'] = datetime.now()
            self.registered_connectors[connector_id]['updated_at'] = datetime.now()

        return sync_result

    def map_chart_of_accounts(
        self,
        connector_id: str,
        source_accounts: List[Dict[str, Any]],
        target_schema: str = 'standard'
    ) -> Dict[str, Any]:
        """
        ربط دليل الحسابات بالنموذج الموحد

        Args:
            connector_id: معرف الموصل
            source_accounts: قائمة الحسابات المصدر
            target_schema: النموذج المستهدف

        Returns:
            نتيجة الربط
        """
        logger.info("Mapping chart of accounts for connector %s", connector_id)

        mapping_result = {
            'success': True,
            'connector_id': connector_id,
            'mapped_accounts': [],
            'unmapped_accounts': [],
            'mapping_confidence': 0.0
        }

        mapped = []
        unmapped = []
        for account in source_accounts:
            confidence = 0.85
            if confidence > 0.7:
                mapped.append({
                    'source_account': account,
                    'target_account': f"ACC-{account.get('code', 'UNKNOWN')}",
                    'confidence': confidence
                })
            else:
                unmapped.append(account)

        mapping_result['mapped_accounts'] = mapped
        mapping_result['unmapped_accounts'] = unmapped
        mapping_result['mapping_confidence'] = sum(a['confidence'] for a in mapped) / len(mapped) if mapped else 0.0
        self.account_mappings[connector_id] = mapping_result

        logger.info("Mapped %d accounts, %d unmapped", len(mapped), len(unmapped))
        return mapping_result

    def get_connection_status(self, connector_id: str) -> Dict[str, Any]:
        """
        الحصول على حالة الاتصال

        Args:
            connector_id: معرف الموصل

        Returns:
            حالة الاتصال
        """
        if connector_id not in self.registered_connectors:
            return {'exists': False}

        connector = self.registered_connectors[connector_id]
        is_connected = connector_id in self.active_connections

        status = {
            'exists': True,
            'connector_id': connector_id,
            'connector_name': connector['connector_name'],
            'connector_type': connector['connector_type'],
            'is_connected': is_connected,
            'status': connector['status'],
            'last_sync': connector['last_sync'],
            'created_at': connector['created_at']
        }

        if is_connected:
            status['connection_info'] = self.active_connections[connector_id]

        return status

    def list_connectors(self, company_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        قائمة الموصلات المسجلة

        Args:
            company_id: تصفية حسب الشركة (اختياري)

        Returns:
            قائمة الموصلات
        """
        connectors = list(self.registered_connectors.values())
        if company_id is not None:
            connectors = [c for c in connectors if c['company_id'] == company_id]
        return connectors

    def remove_connector(self, connector_id: str) -> bool:
        """
        إزالة موصل

        Args:
            connector_id: معرف الموصل

        Returns:
            True إذا نجح الحذف
        """
        if connector_id not in self.registered_connectors:
            logger.error("Connector %s not found", connector_id)
            return False

        if connector_id in self.active_connections:
            self.disconnect(connector_id)

        del self.registered_connectors[connector_id]
        self.account_mappings.pop(connector_id, None)

        logger.info("Removed connector: %s", connector_id)
        return True
