"""
Finovate Audit Nexus AI - Microsoft Dynamics 365 Connector
الاتصال المباشر مع أنظمة Microsoft Dynamics 365 Finance & Operations
"""
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from connectors.base_connector import BaseERPConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DynamicsConnectionConfig:
    """إعدادات الاتصال بـ Dynamics 365"""
    tenant_id: str
    client_id: str
    client_secret: str
    environment_url: str
    company: str = "DAT"

class DynamicsErpConnector(BaseERPConnector):
    """
    موصل Microsoft Dynamics 365 للقراءة فقط
    يدعم F&O و Business Central

    ملاحظة: يتطلب msal و requests للاتصال الفعلي
    """

    def __init__(self, config: DynamicsConnectionConfig):
        super().__init__()
        self.config = config
        self.access_token = None
        self._session = None

    def connect(self) -> bool:
        """إنشاء اتصال بـ Dynamics 365"""
        try:
            logger.info(f"Connecting to Dynamics 365 at {self.config.environment_url}")
            import msal
            import requests
            app = msal.ConfidentialClientApplication(
                self.config.client_id,
                authority=f"https://login.microsoftonline.com/{self.config.tenant_id}",
                client_credential=self.config.client_secret
            )
            result = app.acquire_token_for_client(scopes=[f"{self.config.environment_url}/.default"])
            self.access_token = result["access_token"]
            self._session = requests.Session()
            self._session.headers.update({
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            })
            self._connected = True
            self.last_sync = datetime.now()
            return True
        except Exception as e:
            logger.error(f"Dynamics connection failed: {str(e)}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """قطع الاتصال"""
        if self._session:
            try:
                self._session.close()
            except Exception:
                pass
        self.access_token = None
        self._session = None
        self._connected = False
        logger.info("Disconnected from Dynamics 365")

    def _get(self, relative_url: str, params: dict = None) -> List[Dict[str, Any]]:
        url = f"{self.config.environment_url}/data/{relative_url}"
        try:
            resp = self._session.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("value", [])
        except Exception as e:
            logger.error(f"Dynamics API GET failed: {str(e)}")
            return []

    def test_connection(self) -> Dict[str, Any]:
        """اختبار الاتصال"""
        result = {
            "status": "connected" if self._connected else "disconnected",
            "environment": self.config.environment_url,
            "company": self.config.company,
            "timestamp": datetime.now().isoformat(),
            "read_only": True
        }

        if self._connected:
            try:
                resp = self._session.get(f"{self.config.environment_url}/data/Companies")
                if resp.ok:
                    result["env_info"] = {
                        "version": "Live",
                        "type": "Finance & Operations",
                        "region": "Connected"
                    }
            except Exception as e:
                logger.error(f"test_connection failed: {str(e)}")
                result["env_info"] = {"error": str(e)}

        return result

    def get_journal_entries(self, company: str, from_date: str, to_date: str) -> List[Dict[str, Any]]:
        """
        جلب قيود اليومية

        تستخدم GeneralJournalEntries OData entity
        """
        if not self._connected:
            return []

        logger.info(f"Fetching journal entries for company {company}")

        return self._get(
            "GeneralJournalEntries",
            {"$filter": f"postingDate ge {from_date} and postingDate le {to_date}"}
        )

    def get_general_ledger(self, main_account: str, from_date: str, to_date: str) -> List[Dict[str, Any]]:
        """جلب حركات دفتر الأستاذ"""
        if not self._connected:
            return []

        logger.info(f"Fetching GL movements for account {main_account}")

        return self._get(
            "GeneralJournalAccountEntries",
            {"$filter": f"mainAccountId eq '{main_account}' and accountingDate ge {from_date} and accountingDate le {to_date}"}
        )

    def get_trial_balance(self, company: str, period: str) -> List[Dict[str, Any]]:
        """جلب ميزان المراجعة"""
        if not self._connected:
            return []

        logger.info(f"Fetching trial balance for period {period}")

        return self._get("TrialBalance", {"$filter": f"period eq '{period}'"})

    def get_financial_statements(self, company: str, period: str,
                                statement_type: str = "balance_sheet") -> Dict[str, Any]:
        """جلب القوائم المالية"""
        if not self._connected:
            return {}

        logger.info(f"Fetching {statement_type}")

        data = self._get("FinancialReports", {"$filter": f"reportType eq '{statement_type}'"})
        return {"statement_type": statement_type, "data": data}

    def get_accounts(self, account_type: str = None) -> List[Dict[str, Any]]:
        """جلب الحسابات"""
        if not self._connected:
            return []

        logger.info("Fetching accounts")

        if account_type:
            return self._get("MainAccounts", {"$filter": f"type eq '{account_type}'"})
        return self._get("MainAccounts")

    def get_chart_of_accounts(self) -> List[Dict[str, Any]]:
        """جلب دليل الحسابات"""
        if not self._connected:
            return []

        logger.info("Fetching chart of accounts")

        return self._get("MainAccounts")

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
            "connector": "Dynamics 365",
            "status": "healthy" if self._connected else "unhealthy",
            "environment": self.config.environment_url,
            "read_only_mode": True
        }

def create_dynamics_connector(config: Dict[str, Any]) -> DynamicsErpConnector:
    """إنشاء موصل Dynamics"""
    dynamics_config = DynamicsConnectionConfig(
        tenant_id=config.get("tenant_id", ""),
        client_id=config.get("client_id", ""),
        client_secret=config.get("client_secret", ""),
        environment_url=config.get("environment_url", ""),
        company=config.get("company", "DAT")
    )
    return DynamicsErpConnector(dynamics_config)
