"""
Finovate Audit Nexus AI - Sage ERP Connector
الاتصال المباشر مع أنظمة Sage (Sage 100, Sage X3, Sage Intacct)
"""
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from connectors.base_connector import BaseERPConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SageConnectionConfig:
    """إعدادات الاتصال بـ Sage ERP"""
    product: str  # sage100, sagex3, intacct
    host: str
    port: int
    username: str
    password: str
    company: str = ""
    database: Optional[str] = None

class SageErpConnector(BaseERPConnector):
    """
    موصل Sage ERP للقراءة فقط
    يدعم Sage 100 و Sage X3 و Sage Intacct

    ملاحظة: يتطلب requests أو مكتبات خاصة حسب المنتج
    """

    def __init__(self, config: SageConnectionConfig):
        super().__init__()
        self.config = config
        self.access_token = None
        self.base_url = f"http://{config.host}:{config.port}" if config.product in ['sage100', 'sagex3'] else "https://api.intacct.com"

    def connect(self) -> bool:
        try:
            if self.config.product == 'intacct':
                import requests as _req
                from xml.etree import ElementTree as ET
                auth_xml = ET.Element('request')
                ctrl = ET.SubElement(auth_xml, 'control')
                ET.SubElement(ctrl, 'senderid').text = self.config.username
                ET.SubElement(ctrl, 'password').text = self.config.password
                ctrl2 = ET.SubElement(auth_xml, 'operation')
                ET.SubElement(ctrl2, 'authentication')
                body = ET.tostring(auth_xml, encoding='unicode')
                resp = _req.post(self.base_url, data=body, headers={'Content-Type': 'text/xml'})
                self._connected = resp.status_code < 400
                if self._connected:
                    self.access_token = resp.text
            else:
                import requests as _req
                import base64
                creds = base64.b64encode(f"{self.config.username}:{self.config.password}".encode()).decode()
                resp = _req.get(f"{self.base_url}/api/health", headers={'Authorization': f'Basic {creds}'}, timeout=10)
                if resp.status_code < 400:
                    self._connected = True
                    self.access_token = creds
                else:
                    self._connected = (resp.status_code == 404)
                    self.access_token = creds

            if self._connected:
                self.last_sync = datetime.now()
            return self._connected

        except Exception as e:
            logger.error(f"Sage connection failed: {str(e)}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """قطع الاتصال"""
        self.access_token = None
        self._connected = False
        logger.info("Disconnected from Sage ERP")

    def test_connection(self) -> Dict[str, Any]:
        """اختبار الاتصال"""
        result = {
            "status": "connected" if self._connected else "disconnected",
            "product": self.config.product,
            "host": self.config.host,
            "company": self.config.company,
            "timestamp": datetime.now().isoformat(),
            "read_only": True
        }

        if self._connected:
            result["system_info"] = {
                "platform": f"Sage {self.config.product}",
                "version": "2024"
            }

        return result

    def _get_headers(self) -> Dict:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if self.access_token:
            if self.config.product in ('sage100', 'sagex3'):
                headers['Authorization'] = f'Basic {self.access_token}'
            else:
                headers['Authorization'] = f'Bearer {self.access_token}'
        return headers

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """تنفيذ طلب API"""
        if not self._connected:
            logger.warning("Not connected to Sage ERP")
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
        جلب قيود اليومية من Sage

        Args:
            date_from: تاريخ البدء
            date_to: تاريخ الانتهاء
            company: الشركة

        Returns:
            List[Dict]: قائمة القيود
        """
        if self.config.product == 'intacct':
            endpoint = "generaljournalentry/query"
        else:
            endpoint = "api/journal-entries"

        params = {}
        if date_from:
            params['dateFrom'] = date_from
        if date_to:
            params['dateTo'] = date_to
        if company or self.config.company:
            params['company'] = company or self.config.company

        results = self._request('GET', endpoint, params)

        # توحيد التنسيق
        entries = results.get('items', []) if isinstance(results, dict) else []
        standardized = []

        for entry in entries:
            standardized.append({
                'id': entry.get('id') or entry.get('reference'),
                'date': entry.get('date') or entry.get('postingDate'),
                'reference': entry.get('reference') or entry.get('docNumber'),
                'description': entry.get('description') or entry.get('memo'),
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
        if self.config.product == 'intacct':
            endpoint = "trialbalance/query"
        else:
            endpoint = "api/trial-balance"

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
                'account_code': bal.get('accountNo') or bal.get('accountId'),
                'account_name': bal.get('accountName'),
                'debit': float(bal.get('debitAmount') or 0),
                'credit': float(bal.get('creditAmount') or 0),
                'balance': float(bal.get('balance') or 0)
            })

        return standardized

    def get_accounts(self, company: Optional[str] = None) -> List[Dict]:
        """جلب دليل الحسابات"""
        if self.config.product == 'intacct':
            endpoint = "glaccount/query"
        else:
            endpoint = "api/accounts"

        params = {}
        if company or self.config.company:
            params['company'] = company or self.config.company

        results = self._request('GET', endpoint, params)

        accounts = results.get('items', []) if isinstance(results, dict) else []
        standardized = []

        for acc in accounts:
            standardized.append({
                'code': acc.get('accountNo') or acc.get('accountId'),
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
            'erp_type': f'Sage {self.config.product}',
            'host': self.config.host,
            'company': self.config.company,
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

def create_sage_connector(config: Dict[str, Any]) -> SageErpConnector:
    """إنشاء موصل Sage"""
    sage_config = SageConnectionConfig(
        product=config.get("product", "intacct"),
        host=config.get("host", "localhost"),
        port=config.get("port", 443),
        username=config.get("username", ""),
        password=config.get("password", ""),
        company=config.get("company", ""),
        database=config.get("database", None)
    )
    return SageErpConnector(sage_config)
