"""
Finovate Audit Nexus AI - Infor CloudSuite Connector
الاتصال المباشر مع أنظمة Infor CloudSuite (LN, M3, SyteLine)
"""
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from connectors.base_connector import BaseERPConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class InforConnectionConfig:
    """إعدادات الاتصال بـ Infor CloudSuite"""
    tenant_id: str
    client_id: str
    client_secret: str
    api_endpoint: str
    company: str = ""
    environment: str = "production"

class InforErpConnector(BaseERPConnector):
    """
    موصل Infor CloudSuite للقراءة فقط
    يدعم LN و M3 و SyteLine عبر ION API

    ملاحظة: يتطلب requests للاتصال الفعلي
    """

    def __init__(self, config: InforConnectionConfig):
        super().__init__()
        self.config = config
        self.access_token = None
        self.base_url = config.api_endpoint.rstrip('/')

    def connect(self) -> bool:
        """
        إنشاء اتصال بـ Infor CloudSuite
        """
        try:
            logger.info(f"Connecting to Infor CloudSuite at {self.config.api_endpoint}")
            import requests
            token_response = requests.post(
                f"https://login.infor.com/oauth2/{self.config.tenant_id}/token",
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.config.client_id,
                    'client_secret': self.config.client_secret
                }
            )
            self.access_token = token_response.json()['access_token']
            self._connected = True
            self.last_sync = datetime.now()
            return True
        except Exception as e:
            logger.error(f"Infor connection failed: {str(e)}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """قطع الاتصال"""
        self.access_token = None
        self._connected = False
        logger.info("Disconnected from Infor CloudSuite")

    def test_connection(self) -> Dict[str, Any]:
        """اختبار الاتصال"""
        result = {
            "status": "connected" if self._connected else "disconnected",
            "tenant": self.config.tenant_id,
            "endpoint": self.config.api_endpoint,
            "timestamp": datetime.now().isoformat(),
            "read_only": True
        }

        if self._connected:
            result["system_info"] = {
                "platform": "Infor OS",
                "environment": self.config.environment
            }

        return result

    def _get_headers(self) -> Dict:
        """الحصول على رؤساء الطلب"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        return headers

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """تنفيذ طلب API"""
        if not self._connected:
            logger.warning("Not connected to Infor CloudSuite")
            return {}

        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()

        try:
            logger.info(f"Requesting {method} {url}")
            import requests
            response = requests.request(method, url, headers=headers, params=params, json=data)
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
        جلب قيود اليومية من Infor

        Args:
            date_from: تاريخ البدء
            date_to: تاريخ الانتهاء
            company: الشركة

        Returns:
            List[Dict]: قائمة القيود
        """
        endpoint = "api/gld/journalentries"
        params = {}

        if date_from:
            params['transactionDateFrom'] = date_from
        if date_to:
            params['transactionDateTo'] = date_to
        if company or self.config.company:
            params['company'] = company or self.config.company

        results = self._request('GET', endpoint, params)

        # توحيد التنسيق
        entries = results.get('items', []) if isinstance(results, dict) else []
        standardized = []

        for entry in entries:
            standardized.append({
                'id': entry.get('journalEntryId'),
                'date': entry.get('transactionDate'),
                'reference': entry.get('reference'),
                'description': entry.get('description'),
                'amount': entry.get('amount', 0),
                'lines': entry.get('lines', [])
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
        endpoint = "api/gld/trialbalance"
        params = {}

        if date:
            params['asOfDate'] = date
        if company or self.config.company:
            params['company'] = company or self.config.company

        results = self._request('GET', endpoint, params)

        balances = results.get('items', []) if isinstance(results, dict) else []
        standardized = []

        for bal in balances:
            standardized.append({
                'account_code': bal.get('accountCode'),
                'account_name': bal.get('accountName'),
                'debit': float(bal.get('debitAmount') or 0),
                'credit': float(bal.get('creditAmount') or 0),
                'balance': float(bal.get('balance') or 0)
            })

        return standardized

    def get_accounts(self, company: Optional[str] = None) -> List[Dict]:
        """جلب دليل الحسابات"""
        endpoint = "api/gld/accounts"
        params = {}

        if company or self.config.company:
            params['company'] = company or self.config.company

        results = self._request('GET', endpoint, params)

        accounts = results.get('items', []) if isinstance(results, dict) else []
        standardized = []

        for acc in accounts:
            standardized.append({
                'code': acc.get('accountCode'),
                'name': acc.get('accountName'),
                'type': acc.get('accountType'),
                'balance': acc.get('balance', 0)
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
            'erp_type': 'Infor CloudSuite',
            'tenant': self.config.tenant_id,
            'endpoint': self.config.api_endpoint,
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

def create_infor_connector(config: Dict[str, Any]) -> InforErpConnector:
    """إنشاء موصل Infor"""
    infor_config = InforConnectionConfig(
        tenant_id=config.get("tenant_id", ""),
        client_id=config.get("client_id", ""),
        client_secret=config.get("client_secret", ""),
        api_endpoint=config.get("api_endpoint", ""),
        company=config.get("company", ""),
        environment=config.get("environment", "production")
    )
    return InforErpConnector(infor_config)
