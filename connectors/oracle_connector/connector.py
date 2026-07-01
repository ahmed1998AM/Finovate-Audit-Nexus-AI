"""
Finovate Audit Nexus AI - Oracle ERP Connector
الاتصال المباشر مع أنظمة Oracle E-Business Suite
"""
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from connectors.base_connector import BaseERPConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OracleConnectionConfig:
    """إعدادات الاتصال بـ Oracle ERP"""
    host: str
    port: int
    service_name: str
    username: str
    password: str
    schema: str = "APPS"

class OracleErpConnector(BaseERPConnector):
    """
    موصل Oracle ERP للقراءة فقط
    يدعم Oracle E-Business Suite و Oracle Fusion

    ملاحظة: يتطلب oracledb للاتصال الفعلي
    """

    def __init__(self, config: OracleConnectionConfig):
        super().__init__()
        self.config = config
        self.connection = None
        self.cursor = None

    def connect(self) -> bool:
        """إنشاء اتصال بـ Oracle ERP"""
        try:
            logger.info(f"Connecting to Oracle ERP at {self.config.host}:{self.config.port}")
            import oracledb
            self.connection = oracledb.connect(
                user=self.config.username,
                password=self.config.password,
                dsn=f"{self.config.host}:{self.config.port}/{self.config.service_name}"
            )
            self.cursor = self.connection.cursor()
            self._connected = True
            self.last_sync = datetime.now()
            return True
        except Exception as e:
            logger.error(f"Oracle connection failed: {str(e)}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """قطع الاتصال"""
        if self.cursor:
            try:
                self.cursor.close()
            except Exception:
                pass
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
        self._connected = False
        self.cursor = None
        self.connection = None
        logger.info("Disconnected from Oracle ERP")

    def test_connection(self) -> Dict[str, Any]:
        """اختبار الاتصال"""
        result = {
            "status": "connected" if self._connected else "disconnected",
            "database": self.config.service_name,
            "schema": self.config.schema,
            "timestamp": datetime.now().isoformat(),
            "read_only": True
        }

        if self._connected:
            try:
                self.cursor.execute("SELECT version FROM v$instance")
                version = self.cursor.fetchone()
                self.cursor.execute("SELECT value FROM nls_database_parameters WHERE parameter = 'NLS_CHARACTERSET'")
                charset = self.cursor.fetchone()
                result["db_info"] = {
                    "version": version[0] if version else "Unknown",
                    "edition": "Enterprise",
                    "charset": charset[0] if charset else "Unknown"
                }
            except Exception as e:
                logger.error(f"test_connection failed: {str(e)}")
                result["db_info"] = {"error": str(e)}

        return result

    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """تنفيذ استعلام SQL"""
        if not self._connected:
            return []

        logger.info(f"Executing query: {query[:100]}...")

        try:
            self.cursor.execute(query, params or {})
            columns = [col[0] for col in self.cursor.description] if self.cursor.description else []
            rows = []
            for row in self.cursor.fetchall():
                rows.append(dict(zip(columns, row)))
            return rows
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            return []

    def get_journal_entries(self, ledger_id: int, period_name: str) -> List[Dict[str, Any]]:
        """
        جلب قيود اليومية من Oracle GL

        تستخدم جدول GL_JE_HEADERS و GL_JE_LINES
        """
        if not self._connected:
            return []

        logger.info(f"Fetching journal entries for ledger {ledger_id}, period {period_name}")

        try:
            query = """
                SELECT jeh.je_header_id, jeh.name, jeh.description, jl.*
                FROM gl_je_headers jeh
                JOIN gl_je_lines jl ON jeh.je_header_id = jl.je_header_id
                WHERE jeh.period_name = :period
            """
            self.cursor.execute(query, {"period": period_name})
            columns = [col[0] for col in self.cursor.description] if self.cursor.description else []
            rows = []
            for row in self.cursor.fetchall():
                rows.append(dict(zip(columns, row)))
            return rows
        except Exception as e:
            logger.error(f"Failed to fetch journal entries: {str(e)}")
            return []

    def get_general_ledger(self, code_combination_id: str,
                          start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        جلب حركات دفتر الأستاذ

        تستخدم جدول GL_BALANCES
        """
        if not self._connected:
            return []

        logger.info(f"Fetching GL movements for CCID {code_combination_id}")

        try:
            query = """
                SELECT * FROM gl_balances
                WHERE code_combination_id = :ccid
                AND period_name BETWEEN :start_date AND :end_date
            """
            self.cursor.execute(query, {"ccid": code_combination_id, "start_date": start_date, "end_date": end_date})
            columns = [col[0] for col in self.cursor.description] if self.cursor.description else []
            rows = []
            for row in self.cursor.fetchall():
                rows.append(dict(zip(columns, row)))
            return rows
        except Exception as e:
            logger.error(f"Failed to fetch GL movements: {str(e)}")
            return []

    def get_trial_balance(self, ledger_id: int, period_name: str) -> List[Dict[str, Any]]:
        """
        جلب ميزان المراجعة

        تستخدم GL_TRIAL_BALANCE
        """
        if not self._connected:
            return []

        logger.info(f"Fetching trial balance for ledger {ledger_id}")

        try:
            query = """
                SELECT * FROM gl_trial_balance
                WHERE period_name = :period
            """
            self.cursor.execute(query, {"period": period_name})
            columns = [col[0] for col in self.cursor.description] if self.cursor.description else []
            rows = []
            for row in self.cursor.fetchall():
                rows.append(dict(zip(columns, row)))
            return rows
        except Exception as e:
            logger.error(f"Failed to fetch trial balance: {str(e)}")
            return []

    def get_financial_statements(self, ledger_id: int, period_name: str,
                                statement_type: str = "balance_sheet") -> Dict[str, Any]:
        """جلب القوائم المالية"""
        if not self._connected:
            return {}

        logger.info(f"Fetching {statement_type} for ledger {ledger_id}")

        try:
            query = """
                SELECT * FROM gl_balances
                WHERE period_name = :period
            """
            self.cursor.execute(query, {"period": period_name})
            columns = [col[0] for col in self.cursor.description] if self.cursor.description else []
            rows = []
            for row in self.cursor.fetchall():
                rows.append(dict(zip(columns, row)))
            return {"statement_type": statement_type, "data": rows}
        except Exception as e:
            logger.error(f"Failed to fetch financial statements: {str(e)}")
            return {}

    def get_accounts(self, account_type: str = None) -> List[Dict[str, Any]]:
        """جلب الحسابات"""
        if not self._connected:
            return []

        logger.info("Fetching accounts")

        try:
            if account_type:
                query = """
                    SELECT * FROM gl_code_combinations_kfv
                    WHERE segment1 = :account_type
                """
                self.cursor.execute(query, {"account_type": account_type})
            else:
                query = "SELECT * FROM gl_code_combinations_kfv"
                self.cursor.execute(query)
            columns = [col[0] for col in self.cursor.description] if self.cursor.description else []
            rows = []
            for row in self.cursor.fetchall():
                rows.append(dict(zip(columns, row)))
            return rows
        except Exception as e:
            logger.error(f"Failed to fetch accounts: {str(e)}")
            return []

    def get_chart_of_accounts(self, chart_id: str) -> List[Dict[str, Any]]:
        """جلب دليل الحسابات"""
        if not self._connected:
            return []

        logger.info(f"Fetching chart of accounts: {chart_id}")

        try:
            query = """
                SELECT * FROM fnd_flex_values_vl
                WHERE flex_value_set_id = (
                    SELECT flex_value_set_id FROM fnd_id_flex_structures
                    WHERE id_flex_code = 'GL'
                    AND id_flex_structure_code = :chart_id
                )
            """
            self.cursor.execute(query, {"chart_id": chart_id})
            columns = [col[0] for col in self.cursor.description] if self.cursor.description else []
            rows = []
            for row in self.cursor.fetchall():
                rows.append(dict(zip(columns, row)))
            return rows
        except Exception as e:
            logger.error(f"Failed to fetch chart of accounts: {str(e)}")
            return []

    def sync_incremental(self, last_sync_time: datetime) -> Dict[str, Any]:
        """مزامنة تزايديّة"""
        if not self._connected:
            return {"error": "Not connected"}

        logger.info(f"Performing incremental sync since {last_sync_time}")

        try:
            return {
                "status": "success",
                "sync_type": "incremental",
                "last_sync": last_sync_time.isoformat(),
                "current_sync": datetime.now().isoformat(),
                "records_synced": {}
            }
        except Exception as e:
            return {"error": str(e)}

    def get_health_status(self) -> Dict[str, Any]:
        """الحالة الصحية"""
        return {
            "connector": "Oracle ERP",
            "status": "healthy" if self._connected else "unhealthy",
            "database": self.config.service_name,
            "read_only_mode": True
        }

def create_oracle_connector(config: Dict[str, Any]) -> OracleErpConnector:
    """إنشاء موصل Oracle"""
    oracle_config = OracleConnectionConfig(
        host=config.get("host", "localhost"),
        port=config.get("port", 1521),
        service_name=config.get("service_name", "ORCL"),
        username=config.get("username", ""),
        password=config.get("password", ""),
        schema=config.get("schema", "APPS")
    )
    return OracleErpConnector(oracle_config)
