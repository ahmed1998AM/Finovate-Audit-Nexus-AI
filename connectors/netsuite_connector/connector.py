"""
Finovate Audit Nexus AI - Oracle NetSuite Connector
الاتصال المباشر مع أنظمة Oracle NetSuite ERP
"""
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from connectors.base_connector import BaseERPConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NetSuiteConnectionConfig:
    """إعدادات الاتصال بـ NetSuite"""
    account_id: str
    consumer_key: str
    consumer_secret: str
    token_id: str
    token_secret: str
    environment: str = "production"  # production or sandbox

class NetSuiteErpConnector(BaseERPConnector):
    """
    موصل Oracle NetSuite للقراءة فقط
    يدعم SuiteTalk REST Web Services

    ملاحظة: يتطلب requests و OAuth 1.0a للاتصال الفعلي
    """

    def __init__(self, config: NetSuiteConnectionConfig):
        super().__init__()
        self.config = config
        self.access_token = None
        self.base_url = (
            "https://rest.netsuite.com" if config.environment == "production"
            else "https://rest.sandbox.netsuite.com"
        )

    def connect(self) -> bool:
        """
        إنشاء اتصال بـ NetSuite باستخدام OAuth 1.0a
        """
        try:
            logger.info(f"Connecting to NetSuite Account {self.config.account_id}")
            from requests_oauthlib import OAuth1Session

            self.oauth = OAuth1Session(
                client_key=self.config.consumer_key,
                client_secret=self.config.consumer_secret,
                resource_owner_key=self.config.token_id,
                resource_owner_secret=self.config.token_secret,
                signature_method='HMAC-SHA256',
                realm=self.config.account_id
            )
            self._connected = True
            self.last_sync = datetime.now()
            return True
        except Exception as e:
            logger.error(f"NetSuite connection failed: {str(e)}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """قطع الاتصال"""
        self.access_token = None
        self._connected = False
        logger.info("Disconnected from NetSuite")

    def test_connection(self) -> Dict[str, Any]:
        """اختبار الاتصال"""
        result = {
            "status": "connected" if self._connected else "disconnected",
            "account": self.config.account_id,
            "environment": self.config.environment,
            "timestamp": datetime.now().isoformat(),
            "read_only": True
        }

        if self._connected:
            result["system_info"] = {
                "platform": "Oracle NetSuite",
                "version": "2024.1"
            }

        return result

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """تنفيذ طلب API عبر OAuth 1.0a"""
        if not self._connected:
            logger.warning("Not connected to NetSuite")
            return {}

        url = f"{self.base_url}/services/rest/record/v1/{endpoint}"

        try:
            logger.info(f"Requesting {method} {url}")
            response = self.oauth.request(method, url, headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, params=params, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            return {}

    def get_journal_entries(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        subsidiary: Optional[str] = None
    ) -> List[Dict]:
        """
        جلب قيود اليومية من NetSuite

        Args:
            date_from: تاريخ البدء
            date_to: تاريخ الانتهاء
            subsidiary: الفرعية

        Returns:
            List[Dict]: قائمة القيود
        """
        endpoint = "journalEntry"
        params = {
            'limit': 1000
        }

        filters = []
        if date_from:
            filters.append(f"createdFrom='{date_from}'")
        if date_to:
            filters.append(f"createdTo='{date_to}'")
        if subsidiary:
            filters.append(f"subsidiary={subsidiary}")

        if filters:
            params['where'] = ' AND '.join(filters)

        results = self._request('GET', endpoint, params)

        # توحيد التنسيق
        entries = results.get('items', []) if isinstance(results, dict) else []
        standardized = []

        for entry in entries:
            standardized.append({
                'id': entry.get('id'),
                'date': entry.get('trandate'),
                'reference': entry.get('tranid'),
                'description': entry.get('memo'),
                'amount': entry.get('amount', 0),
                'lines': entry.get('lineList', {}).get('line', [])
            })

        return standardized

    def get_trial_balance(
        self,
        date: Optional[str] = None,
        subsidiary: Optional[str] = None
    ) -> List[Dict]:
        """
        جلب ميزان المراجعة

        Returns:
            List[Dict]: ميزان المراجعة
        """
        # NetSuite لا يوفر ميزان مراجعة مباشر عبر REST API
        # يجب استخدام Saved Search أو SuiteQL

        endpoint = "savedSearch"
        params = {'id': 'customsearch_trial_balance'}

        results = self._request('GET', endpoint, params)

        balances = results.get('items', []) if isinstance(results, dict) else []
        standardized = []

        for bal in balances:
            standardized.append({
                'account_code': bal.get('account', {}).get('id'),
                'account_name': bal.get('account', {}).get('name'),
                'debit': float(bal.get('debit') or 0),
                'credit': float(bal.get('credit') or 0),
                'balance': float(bal.get('balance') or 0)
            })

        return standardized

    def get_accounts(self, subsidiary: Optional[str] = None) -> List[Dict]:
        """جلب دليل الحسابات"""
        endpoint = "account"
        params = {'limit': 1000}

        if subsidiary:
            params['where'] = f'subsidiary={subsidiary}'

        results = self._request('GET', endpoint, params)

        accounts = results.get('items', []) if isinstance(results, dict) else []
        standardized = []

        for acc in accounts:
            standardized.append({
                'code': acc.get('acctNumber'),
                'name': acc.get('name'),
                'type': acc.get('acctType', {}).get('name'),
                'balance': acc.get('balance', 0)
            })

        return standardized

    def get_invoices(
        self,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict]:
        """جلب الفواتير"""
        endpoint = "invoice"
        params = {'limit': 1000}

        filters = []
        if status:
            filters.append(f"status={status}")
        if date_from:
            filters.append(f"trandate>='{date_from}'")
        if date_to:
            filters.append(f"trandate<='{date_to}'")

        if filters:
            params['where'] = ' AND '.join(filters)

        results = self._request('GET', endpoint, params)

        invoices = results.get('items', []) if isinstance(results, dict) else []
        standardized = []

        for inv in invoices:
            standardized.append({
                'id': inv.get('id'),
                'number': inv.get('tranid'),
                'date': inv.get('trandate'),
                'due_date': inv.get('duedate'),
                'customer_id': inv.get('entity', {}).get('id'),
                'customer_name': inv.get('entity', {}).get('name'),
                'amount': inv.get('amount', 0),
                'balance': inv.get('balance', 0),
                'status': inv.get('status', {}).get('name')
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
            'erp_type': 'Oracle NetSuite',
            'account': self.config.account_id,
            'environment': self.config.environment,
            'connected': self._connected,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None
        }

    def sync_all(self) -> Dict[str, int]:
        """مزامنة جميع البيانات"""
        results = {
            'journal_entries': 0,
            'trial_balance': 0,
            'accounts': 0,
            'invoices': 0
        }

        if self._connected:
            entries = self.get_journal_entries()
            results['journal_entries'] = len(entries)

            tb = self.get_trial_balance()
            results['trial_balance'] = len(tb)

            accounts = self.get_accounts()
            results['accounts'] = len(accounts)

            invoices = self.get_invoices()
            results['invoices'] = len(invoices)

            self.last_sync = datetime.now()

        return results

def create_netsuite_connector(config: Dict[str, Any]) -> NetSuiteErpConnector:
    """إنشاء موصل NetSuite"""
    netsuite_config = NetSuiteConnectionConfig(
        account_id=config.get("account_id", ""),
        consumer_key=config.get("consumer_key", ""),
        consumer_secret=config.get("consumer_secret", ""),
        token_id=config.get("token_id", ""),
        token_secret=config.get("token_secret", ""),
        environment=config.get("environment", "production")
    )
    return NetSuiteErpConnector(netsuite_config)
