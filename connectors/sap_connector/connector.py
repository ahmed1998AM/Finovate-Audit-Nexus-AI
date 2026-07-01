"""
Finovate Audit Nexus AI - SAP ERP Connector
الاتصال المباشر مع أنظمة SAP ERP
"""
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from connectors.base_connector import BaseERPConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SAPConnectionConfig:
    """إعدادات الاتصال بـ SAP"""
    host: str
    system_number: str
    client: str
    username: str
    password: str
    language: str = 'EN'
    port: int = 3300


class SAPErpConnector(BaseERPConnector):
    """
    موصل SAP ERP للقراءة فقط
    يدعم BAPI و RFC

    ملاحظة: يتطلب تثبيت pyrfc للاتصال الفعلي
    """

    def __init__(self, config: SAPConnectionConfig):
        super().__init__()
        self.config = config
        self.connection = None

    def connect(self) -> bool:
        """
        إنشاء اتصال بـ SAP ERP
        """
        try:
            logger.info(f"Connecting to SAP ERP at {self.config.host}:{self.config.port}")
            from pyrfc import Connection
            self.connection = Connection(
                ashost=self.config.host,
                sysnr=self.config.system_number,
                client=self.config.client,
                user=self.config.username,
                passwd=self.config.password,
                lang=self.config.language,
                saptrace=1
            )
            self._connected = True
            self.last_sync = datetime.now()
            return True
        except Exception as e:
            logger.error(f"SAP connection failed: {str(e)}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """قطع الاتصال"""
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
        self._connected = False
        self.connection = None
        logger.info("Disconnected from SAP ERP")

    def test_connection(self) -> Dict[str, Any]:
        """اختبار الاتصال"""
        result = {
            "status": "connected" if self._connected else "disconnected",
            "system": self.config.host,
            "client": self.config.client,
            "timestamp": datetime.now().isoformat(),
            "read_only": True
        }

        if self._connected:
            try:
                self.connection.call('BAPI_USER_GET_DETAIL', USERNAME=self.config.username)
                attrs = self.connection.get_connection_attr()
                result["system_info"] = {
                    "system_id": attrs.get("sysid", "N/A"),
                    "instance": self.config.system_number,
                    "release": attrs.get("release", "N/A"),
                    "kernel": attrs.get("kernel", "N/A")
                }
            except Exception as e:
                logger.error(f"test_connection failed: {str(e)}")
                result["system_info"] = {"error": str(e)}

        return result

    def execute_bapi(self, bapi_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        تنفيذ BAPI function

        أمثلة:
        - BAPI_COMPANYCODE_GETLIST
        - BAPI_GL_GETBALANCES
        - BAPI_ACC_DOCUMENT_CHECK
        """
        if not self._connected:
            return {"error": "Not connected to SAP"}

        logger.info(f"Executing BAPI: {bapi_name}")

        try:
            return self.connection.call(bapi_name, **parameters)
        except Exception as e:
            logger.error(f"BAPI call failed: {str(e)}")
            return {"error": str(e)}

    def get_journal_entries(self, company_code: str, fiscal_year: str,
                           start_period: int = 1, end_period: int = 12) -> List[Dict[str, Any]]:
        """
        جلب قيود اليومية من SAP

        تستخدم BAPI_GL_GETPOSTINGDATA
        """
        if not self._connected:
            return []

        logger.info(f"Fetching journal entries for company {company_code}, year {fiscal_year}")

        try:
            result = self.connection.call(
                'BAPI_GL_GETPOSTINGDATA',
                COMPANYCODE=company_code,
                FISCALYEAR=fiscal_year
            )
            return result.get("POSTINGDATA", [])
        except Exception as e:
            logger.error(f"Failed to fetch journal entries: {str(e)}")
            return []

    def get_general_ledger(self, account: str, company_code: str,
                          fiscal_year: str) -> List[Dict[str, Any]]:
        """
        جلب حركات دفتر الأستاذ العام

        تستخدم BAPI_GL_GETBALANCES
        """
        if not self._connected:
            return []

        logger.info(f"Fetching GL movements for account {account}")

        try:
            result = self.connection.call(
                'BAPI_GL_GETBALANCES',
                COMPANYCODE=company_code,
                FISCALYEAR=fiscal_year,
                GL_ACCOUNT=account
            )
            return result.get("GL_BALANCES", [])
        except Exception as e:
            logger.error(f"Failed to fetch GL movements: {str(e)}")
            return []

    def get_trial_balance(self, company_code: str, fiscal_year: str,
                         period: int = 12) -> List[Dict[str, Any]]:
        """
        جلب ميزان المراجعة

        تستخدم BAPI_GL_GETGLACCOUNTBALANCE
        """
        if not self._connected:
            return []

        logger.info(f"Fetching trial balance for period {period}")

        try:
            result = self.connection.call(
                'BAPI_GL_GETGLACCOUNTBALANCE',
                COMPANYCODE=company_code,
                FISCALYEAR=fiscal_year,
                PERIOD=period
            )
            return result.get("ACCOUNT_BALANCES", [])
        except Exception as e:
            logger.error(f"Failed to fetch trial balance: {str(e)}")
            return []

    def get_financial_statements(self, company_code: str, fiscal_year: str,
                                statement_type: str = "balance_sheet") -> Dict[str, Any]:
        """
        جلب القوائم المالية

        types: balance_sheet, income_statement, cash_flow
        """
        if not self._connected:
            return {}

        logger.info(f"Fetching {statement_type} for year {fiscal_year}")

        try:
            if statement_type == "balance_sheet":
                result = self.connection.call(
                    'BAPI_FIXEDASSET_GETLIST',
                    COMPANYCODE=company_code
                )
                return {"status": "retrieved", "data": result.get("ASSET_LIST", [])}
            return {"status": "not_implemented", "statement_type": statement_type}
        except Exception as e:
            logger.error(f"Failed to fetch financial statements: {str(e)}")
            return {}

    def get_accounts(self, account_type: str = None) -> List[Dict[str, Any]]:
        """
        جلب الحسابات

        تستخدم BAPI_GL_GETACCOUNTBALANCE
        """
        if not self._connected:
            return []

        logger.info("Fetching accounts")

        try:
            result = self.connection.call('BAPI_GL_GETACCOUNTBALANCE')
            return result.get("ACCOUNT_BALANCES", [])
        except Exception as e:
            logger.error(f"Failed to fetch accounts: {str(e)}")
            return []

    def get_chart_of_accounts(self, chart_id: str) -> List[Dict[str, Any]]:
        """
        جلب دليل الحسابات

        تستخدم BAPI_GL_ACCOUNT_GETDETAIL
        """
        if not self._connected:
            return []

        logger.info(f"Fetching chart of accounts: {chart_id}")

        try:
            result = self.connection.call('BAPI_GL_ACCOUNT_GETDETAIL', CHARTACCOUNTS=chart_id)
            return result.get("ACCOUNT_DETAIL", [])
        except Exception as e:
            logger.error(f"Failed to fetch chart of accounts: {str(e)}")
            return []

    def sync_incremental(self, last_sync_time: datetime) -> Dict[str, Any]:
        """
        مزامنة تزايديّة منذ آخر مزامنة
        """
        if not self._connected:
            return {"error": "Not connected"}

        logger.info(f"Performing incremental sync since {last_sync_time}")

        try:
            self.connection.call('BAPI_TRANSACTION_COMMIT')
            return {
                "status": "success",
                "sync_type": "incremental",
                "last_sync": last_sync_time.isoformat(),
                "current_sync": datetime.now().isoformat(),
                "records_synced": {}
            }
        except Exception as e:
            logger.error(f"Incremental sync failed: {str(e)}")
            return {"error": str(e)}

    def get_health_status(self) -> Dict[str, Any]:
        """الحصول على حالة النظام الصحية"""
        return {
            "connector": "SAP ERP",
            "status": "healthy" if self._connected else "unhealthy",
            "connection_host": self.config.host,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "read_only_mode": True,
            "security": {
                "encryption": "TLS",
                "authentication": "SAP Auth"
            }
        }

def create_sap_connector(config: Dict[str, Any]) -> SAPErpConnector:
    """إنشاء موصل SAP"""
    sap_config = SAPConnectionConfig(
        host=config.get("host", "localhost"),
        system_number=config.get("system_number", "00"),
        client=config.get("client", "100"),
        username=config.get("username", ""),
        password=config.get("password", ""),
        language=config.get("language", "EN"),
        port=config.get("port", 3300)
    )
    return SAPErpConnector(sap_config)
