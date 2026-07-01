"""
Finovate Audit Nexus AI - Workday Connector
الاتصال المباشر مع أنظمة Workday Financial Management
"""
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from connectors.base_connector import BaseERPConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WorkdayConnectionConfig:
    """إعدادات الاتصال بـ Workday"""
    tenant: str
    username: str
    password: str
    api_version: str = "v45.0"
    environment: str = "production"  # production or sandbox

class WorkdayErpConnector(BaseERPConnector):
    """
    موصل Workday Financial Management للقراءة فقط
    يدعم Workday Studio و REST APIs

    ملاحظة: يتطلب requests و Basic Auth للاتصال الفعلي
    """

    def __init__(self, config: WorkdayConnectionConfig):
        super().__init__()
        self.config = config
        self.access_token = None
        self.base_url = (
            f"https://wd2-impl-services1.workday.com/ccx/service/{config.tenant}"
            if config.environment == "sandbox"
            else f"https://wd3-impl-services1.workday.com/ccx/service/{config.tenant}"
        )

    def connect(self) -> bool:
        """
        إنشاء اتصال بـ Workday باستخدام Basic Auth
        """
        try:
            logger.info(f"Connecting to Workday Tenant {self.config.tenant}")
            import requests
            from requests.auth import HTTPBasicAuth
            response = requests.get(
                f"{self.base_url}/Financial_Management/{self.config.api_version}",
                auth=HTTPBasicAuth(
                    f"{self.config.username}@{self.config.tenant}",
                    self.config.password
                )
            )
            response.raise_for_status()
            self._connected = True
            self.last_sync = datetime.now()
            return True
        except Exception as e:
            logger.error(f"Workday connection failed: {str(e)}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """قطع الاتصال"""
        self.access_token = None
        self._connected = False
        logger.info("Disconnected from Workday")

    def test_connection(self) -> Dict[str, Any]:
        """اختبار الاتصال"""
        result = {
            "status": "connected" if self._connected else "disconnected",
            "tenant": self.config.tenant,
            "api_version": self.config.api_version,
            "timestamp": datetime.now().isoformat(),
            "read_only": True
        }

        if self._connected:
            result["system_info"] = {
                "platform": "Workday Financial Management",
                "environment": self.config.environment
            }

        return result

    def _get_headers(self) -> Dict:
        """الحصول على رؤساء الطلب"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        return headers

    def _get_auth(self):
        """الحصول على بيانات المصادقة"""
        from requests.auth import HTTPBasicAuth
        return HTTPBasicAuth(
            f"{self.config.username}@{self.config.tenant}",
            self.config.password
        )

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """تنفيذ طلب API"""
        if not self._connected:
            logger.warning("Not connected to Workday")
            return {}

        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()

        try:
            logger.info(f"Requesting {method} {url}")
            import requests
            response = requests.request(
                method, url, headers=headers, params=params, json=data,
                auth=self._get_auth()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            return {}

    def get_journal_entries(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        company: Optional[str] = None
    ) -> List[Dict]:
        """
        جلب قيود اليومية من Workday

        Args:
            date_from: تاريخ البدء
            date_to: تاريخ الانتهاء
            company: الشركة

        Returns:
            List[Dict]: قائمة القيود
        """
        endpoint = f"Financial_Management/{self.config.api_version}/journal-entries"
        params = {}

        if date_from:
            params['entryDateFrom'] = date_from
        if date_to:
            params['entryDateTo'] = date_to
        if company:
            params['companyReferenceID'] = company

        results = self._request('GET', endpoint, params)

        # توحيد التنسيق
        entries = results.get('Journal_Entries', []) if isinstance(results, dict) else []
        standardized = []

        for entry in entries:
            standardized.append({
                'id': entry.get('Journal_Entry_ID', {}).get('ID'),
                'date': entry.get('Accounting_Date'),
                'reference': entry.get('Journal_Entry_Number'),
                'description': entry.get('Journal_Entry_Description'),
                'amount': entry.get('Total_Amount', 0),
                'lines': entry.get('Journal_Entry_Line', [])
            })

        return standardized

    def get_trial_balance(
        self,
        date: Optional[str] = None,
        company: Optional[str] = None
    ) -> List[Dict]:
        """
        جلب ميزان المراجعة

        Returns:
            List[Dict]: ميزان المراجعة
        """
        endpoint = f"Financial_Management/{self.config.api_version}/trial-balance"
        params = {}

        if date:
            params['asOfDate'] = date
        if company:
            params['companyReferenceID'] = company

        results = self._request('GET', endpoint, params)

        balances = results.get('Trial_Balance_Entries', []) if isinstance(results, dict) else []
        standardized = []

        for bal in balances:
            standardized.append({
                'account_code': bal.get('Account', {}).get('Account_ID'),
                'account_name': bal.get('Account', {}).get('Account_Name'),
                'debit': float(bal.get('Debit_Amount') or 0),
                'credit': float(bal.get('Credit_Amount') or 0),
                'balance': float(bal.get('Balance') or 0)
            })

        return standardized

    def get_accounts(self, company: Optional[str] = None) -> List[Dict]:
        """جلب دليل الحسابات"""
        endpoint = f"Financial_Management/{self.config.api_version}/chart-of-accounts"
        params = {}

        if company:
            params['companyReferenceID'] = company

        results = self._request('GET', endpoint, params)

        accounts = results.get('Accounts', []) if isinstance(results, dict) else []
        standardized = []

        for acc in accounts:
            standardized.append({
                'code': acc.get('Account_ID'),
                'name': acc.get('Account_Name'),
                'type': acc.get('Account_Type', {}).get('Name'),
                'balance': acc.get('Current_Balance', 0)
            })

        return standardized

    def get_financial_statements(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Dict:
        """جلب القوائم المالية"""
        return {
            'income_statement': [],
            'balance_sheet': [],
            'cash_flow': []
        }

    def get_system_info(self) -> Dict[str, Any]:
        """جلب معلومات النظام"""
        return {
            'erp_type': 'Workday Financial Management',
            'tenant': self.config.tenant,
            'api_version': self.config.api_version,
            'connected': self._connected,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None
        }

    def sync_all(self) -> Dict[str, int]:
        """مزامنة جميع البيانات"""
        results = {
            'journal_entries': 0,
            'trial_balance': 0,
            'accounts': 0
        }

        if self._connected:
            entries = self.get_journal_entries()
            results['journal_entries'] = len(entries)

            tb = self.get_trial_balance()
            results['trial_balance'] = len(tb)

            accounts = self.get_accounts()
            results['accounts'] = len(accounts)

            self.last_sync = datetime.now()

        return results

def create_workday_connector(config: Dict[str, Any]) -> WorkdayErpConnector:
    """إنشاء موصل Workday"""
    workday_config = WorkdayConnectionConfig(
        tenant=config.get("tenant", ""),
        username=config.get("username", ""),
        password=config.get("password", ""),
        api_version=config.get("api_version", "v45.0"),
        environment=config.get("environment", "production")
    )
    return WorkdayErpConnector(workday_config)
