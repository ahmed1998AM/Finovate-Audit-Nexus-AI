"""
Finovate Audit Nexus AI - Generic API Connector
موصل API عام للأنظمة المالية المخصصة
"""
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json


class APIConnector:
    """
    موصل API عام مرن للاتصال بالأنظمة المالية المخصصة
    يدعم REST APIs مع مصادقة متعددة الطرق
    """

    def __init__(self, config: Dict[str, Any]):
        """
        تهيئة موصل API
        
        Args:
            config: إعدادات الاتصال
                - base_url: الرابط الأساسي
                - auth_type: نوع المصادقة (none, api_key, bearer, basic, oauth2)
                - api_key: مفتاح API
                - access_token: رمز الوصول
                - username: اسم المستخدم
                - password: كلمة المرور
                - headers: رؤساء مخصصة
                - timeout: مهلة الطلب
        """
        self.base_url = config.get('base_url', '').rstrip('/')
        self.auth_type = config.get('auth_type', 'none')
        self.api_key = config.get('api_key', '')
        self.access_token = config.get('access_token', '')
        self.username = config.get('username', '')
        self.password = config.get('password', '')
        self.custom_headers = config.get('headers', {})
        self.timeout = config.get('timeout', 30)
        
        # OAuth2
        self.client_id = config.get('client_id', '')
        self.client_secret = config.get('client_secret', '')
        self.refresh_token = config.get('refresh_token', '')
        self.token_url = config.get('token_url', '')
        
        self.connected = False
        self.last_sync = None
        self.token_expiry = None
    
    def _get_headers(self) -> Dict:
        """الحصول على رؤساء الطلب"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # إضافة الرؤساء المخصصة
        headers.update(self.custom_headers)
        
        # إضافة المصادقة
        if self.auth_type == 'api_key':
            headers['X-API-Key'] = self.api_key
        elif self.auth_type == 'bearer':
            headers['Authorization'] = f'Bearer {self.access_token}'
        elif self.auth_type == 'basic':
            import base64
            credentials = base64.b64encode(f'{self.username}:{self.password}'.encode()).decode()
            headers['Authorization'] = f'Basic {credentials}'
        elif self.auth_type == 'oauth2':
            if not self.access_token or (self.token_expiry and datetime.now() >= self.token_expiry):
                self._refresh_oauth_token()
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        return headers
    
    def _refresh_oauth_token(self):
        """تحديث رمز OAuth2"""
        if not self.token_url:
            raise Exception("token_url غير محدد")
        
        try:
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            if self.refresh_token:
                data['grant_type'] = 'refresh_token'
                data['refresh_token'] = self.refresh_token
            
            response = requests.post(self.token_url, data=data, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            self.access_token = result['access_token']
            expires_in = result.get('expires_in', 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            self.connected = True
            
        except Exception as e:
            print(f"خطأ في تحديث رمز OAuth2: {str(e)}")
            self.connected = False
            raise
    
    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """
        تنفيذ طلب API
        
        Args:
            method: نوع الطلب (GET, POST, PUT, DELETE)
            endpoint: نقطة النهاية
            params: معاملات الاستعلام
            data: بيانات الجسم
            
        Returns:
            Dict: النتيجة
        """
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        
        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                params=params,
                json=data,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            # محاولة تحليل JSON
            try:
                return response.json()
            except:
                return {'data': response.text}
            
        except requests.exceptions.HTTPError as e:
            print(f"خطأ HTTP {e.response.status_code}: {e.response.text}")
            if e.response.status_code == 401 and self.auth_type == 'oauth2':
                # محاولة تحديث الرمز وإعادة الطلب
                self._refresh_oauth_token()
                return self._request(method, endpoint, params, data)
            raise
        except Exception as e:
            print(f"خطأ في الطلب: {str(e)}")
            raise
    
    # ==================== طرق عامة قابلة للتخصيص ====================
    
    def get_journal_entries(
        self,
        endpoint: str = 'journal-entries',
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        params: Optional[Dict] = None
    ) -> List[Dict]:
        """
        جلب قيود اليومية
        
        Args:
            endpoint: نقطة النهاية
            date_from: تاريخ البدء
            date_to: تاريخ الانتهاء
            params: معاملات إضافية
            
        Returns:
            List[Dict]: قائمة القيود
        """
        query_params = params or {}
        
        if date_from:
            query_params['date_from'] = date_from
        if date_to:
            query_params['date_to'] = date_to
        
        try:
            result = self._request('GET', endpoint, query_params)
            
            # محاولة استخراج البيانات من استجابات مختلفة
            entries = []
            if isinstance(result, dict):
                # البحث عن مفاتيح شائعة
                for key in ['entries', 'data', 'records', 'journal_entries', 'result']:
                    if key in result:
                        entries = result[key]
                        break
                if not entries and 'journal_entries' in result:
                    entries = result['journal_entries']
            elif isinstance(result, list):
                entries = result
            
            # توحيد التنسيق
            standardized = []
            for entry in entries:
                standardized.append({
                    'id': entry.get('id') or entry.get('Id') or entry.get('entry_id'),
                    'date': entry.get('date') or entry.get('Date') or entry.get('entry_date'),
                    'reference': entry.get('reference') or entry.get('Reference') or entry.get('ref_number'),
                    'description': entry.get('description') or entry.get('Description') or entry.get('narration'),
                    'amount': entry.get('amount') or entry.get('Amount') or entry.get('total', 0),
                    'lines': entry.get('lines') or entry.get('Lines') or entry.get('details', [])
                })
            
            return standardized
            
        except Exception as e:
            print(f"خطأ في جلب القيود: {str(e)}")
            return []
    
    def get_trial_balance(
        self,
        endpoint: str = 'trial-balance',
        date: Optional[str] = None,
        params: Optional[Dict] = None
    ) -> List[Dict]:
        """
        جلب ميزان المراجعة
        
        Returns:
            List[Dict]: ميزان المراجعة
        """
        query_params = params or {}
        if date:
            query_params['date'] = date
        
        try:
            result = self._request('GET', endpoint, query_params)
            
            balances = []
            if isinstance(result, dict):
                for key in ['balances', 'data', 'records', 'trial_balance', 'accounts']:
                    if key in result:
                        balances = result[key]
                        break
            elif isinstance(result, list):
                balances = result
            
            standardized = []
            for bal in balances:
                standardized.append({
                    'account_code': bal.get('account_code') or bal.get('code') or bal.get('accountCode'),
                    'account_name': bal.get('account_name') or bal.get('name') or bal.get('accountName'),
                    'debit': float(bal.get('debit') or bal.get('Debit') or 0),
                    'credit': float(bal.get('credit') or bal.get('Credit') or 0),
                    'balance': float(bal.get('balance') or bal.get('Balance') or 0)
                })
            
            return standardized
            
        except Exception as e:
            print(f"خطأ في جلب ميزان المراجعة: {str(e)}")
            return []
    
    def get_financial_statements(
        self,
        income_endpoint: str = 'income-statement',
        balance_endpoint: str = 'balance-sheet',
        cashflow_endpoint: str = 'cash-flow',
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Dict:
        """
        جلب القوائم المالية
        
        Returns:
            Dict: القوائم المالية
        """
        result = {
            'income_statement': [],
            'balance_sheet': [],
            'cash_flow': []
        }
        
        params = {}
        if date_from:
            params['from_date'] = date_from
        if date_to:
            params['to_date'] = date_to
        
        try:
            # قائمة الدخل
            pl_result = self._request('GET', income_endpoint, params)
            result['income_statement'] = pl_result.get('data') or pl_result.get('statement') or pl_result
            
            # الميزانية
            bs_result = self._request('GET', balance_endpoint, params)
            result['balance_sheet'] = bs_result.get('data') or bs_result.get('statement') or bs_result
            
            # التدفقات النقدية
            cf_result = self._request('GET', cashflow_endpoint, params)
            result['cash_flow'] = cf_result.get('data') or cf_result.get('statement') or cf_result
            
            return result
            
        except Exception as e:
            print(f"خطأ في جلب القوائم المالية: {str(e)}")
            return result
    
    def get_invoices(
        self,
        endpoint: str = 'invoices',
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        params: Optional[Dict] = None
    ) -> List[Dict]:
        """
        جلب الفواتير
        
        Returns:
            List[Dict]: قائمة الفواتير
        """
        query_params = params or {}
        
        if status:
            query_params['status'] = status
        if date_from:
            query_params['date_from'] = date_from
        if date_to:
            query_params['date_to'] = date_to
        
        try:
            result = self._request('GET', endpoint, query_params)
            
            invoices = []
            if isinstance(result, dict):
                for key in ['invoices', 'data', 'records', 'result']:
                    if key in result:
                        invoices = result[key]
                        break
            elif isinstance(result, list):
                invoices = result
            
            standardized = []
            for inv in invoices:
                standardized.append({
                    'id': inv.get('id') or inv.get('invoice_id'),
                    'number': inv.get('number') or inv.get('invoice_number'),
                    'date': inv.get('date') or inv.get('invoice_date'),
                    'due_date': inv.get('due_date'),
                    'customer_id': inv.get('customer_id') or inv.get('client_id'),
                    'customer_name': inv.get('customer_name') or inv.get('client_name'),
                    'amount': inv.get('amount') or inv.get('total') or inv.get('invoice_amount', 0),
                    'balance': inv.get('balance') or inv.get('amount_due', 0),
                    'status': inv.get('status') or inv.get('state')
                })
            
            return standardized
            
        except Exception as e:
            print(f"خطأ في جلب الفواتير: {str(e)}")
            return []
    
    def get_customers(
        self,
        endpoint: str = 'customers',
        params: Optional[Dict] = None
    ) -> List[Dict]:
        """جلب العملاء"""
        try:
            result = self._request('GET', endpoint, params)
            
            customers = []
            if isinstance(result, dict):
                for key in ['customers', 'data', 'records', 'clients']:
                    if key in result:
                        customers = result[key]
                        break
            elif isinstance(result, list):
                customers = result
            
            standardized = []
            for cust in customers:
                standardized.append({
                    'id': cust.get('id') or cust.get('customer_id'),
                    'name': cust.get('name') or cust.get('company_name'),
                    'email': cust.get('email'),
                    'phone': cust.get('phone'),
                    'balance': cust.get('balance') or cust.get('outstanding', 0)
                })
            
            return standardized
            
        except Exception as e:
            print(f"خطأ في جلب العملاء: {str(e)}")
            return []
    
    def get_accounts(
        self,
        endpoint: str = 'accounts',
        params: Optional[Dict] = None
    ) -> List[Dict]:
        """جلب دليل الحسابات"""
        try:
            result = self._request('GET', endpoint, params)
            
            accounts = []
            if isinstance(result, dict):
                for key in ['accounts', 'data', 'records', 'chart_of_accounts']:
                    if key in result:
                        accounts = result[key]
                        break
            elif isinstance(result, list):
                accounts = result
            
            standardized = []
            for acc in accounts:
                standardized.append({
                    'id': acc.get('id') or acc.get('account_id'),
                    'code': acc.get('code') or acc.get('account_code'),
                    'name': acc.get('name') or acc.get('account_name'),
                    'type': acc.get('type') or acc.get('account_type'),
                    'balance': acc.get('balance') or acc.get('current_balance', 0)
                })
            
            return standardized
            
        except Exception as e:
            print(f"خطأ في جلب الحسابات: {str(e)}")
            return []
    
    # ==================== معلومات النظام ====================
    
    def get_system_info(self, endpoint: str = 'system/info') -> Dict:
        """جلب معلومات النظام"""
        try:
            result = self._request('GET', endpoint)
            
            return {
                'erp_type': 'Custom API',
                'base_url': self.base_url,
                'auth_type': self.auth_type,
                'connected': self.connected,
                'last_sync': self.last_sync.isoformat() if self.last_sync else None,
                'system_info': result
            }
            
        except Exception as e:
            return {'error': str(e), 'connected': False}
    
    # ==================== المزامنة ====================
    
    def sync_all(self, endpoints: Optional[Dict[str, str]] = None) -> Dict[str, int]:
        """
        مزامنة جميع البيانات
        
        Args:
            endpoints: قاموس بنقاط النهاية المخصصة
            
        Returns:
            Dict: عدد العناصر المزامنة
        """
        if endpoints is None:
            endpoints = {
                'journal_entries': 'journal-entries',
                'trial_balance': 'trial-balance',
                'invoices': 'invoices',
                'customers': 'customers',
                'accounts': 'accounts'
            }
        
        synced = {}
        
        try:
            # جلب القيود
            entries = self.get_journal_entries(endpoint=endpoints.get('journal_entries', 'journal-entries'))
            synced['journal_entries_count'] = len(entries)
            
            # جلب الفواتير
            invoices = self.get_invoices(endpoint=endpoints.get('invoices', 'invoices'))
            synced['invoices_count'] = len(invoices)
            
            # جلب العملاء
            customers = self.get_customers(endpoint=endpoints.get('customers', 'customers'))
            synced['customers_count'] = len(customers)
            
            # جلب الحسابات
            accounts = self.get_accounts(endpoint=endpoints.get('accounts', 'accounts'))
            synced['accounts_count'] = len(accounts)
            
            self.last_sync = datetime.now()
            
        except Exception as e:
            print(f"خطأ في المزامنة: {str(e)}")
        
        return synced
    
    # ==================== اختبار الاتصال ====================
    
    def test_connection(self, test_endpoint: str = 'health') -> Dict:
        """
        اختبار الاتصال
        
        Args:
            test_endpoint: نقطة نهاية الاختبار
            
        Returns:
            Dict: نتيجة الاختبار
        """
        result = {
            'success': False,
            'message': '',
            'details': {}
        }
        
        try:
            # محاولة الاتصال بنقطة الاختبار
            try:
                info = self._request('GET', test_endpoint)
                result['success'] = True
                result['message'] = 'اتصال ناجح'
                result['details'] = info
            except:
                # إذا فشلت نقطة الاختبار، محاولة جلب البيانات الأساسية
                try:
                    self.get_accounts(params={'limit': 1})
                    result['success'] = True
                    result['message'] = 'اتصال ناجح (اختبار بديل)'
                    result['details'] = {'test_method': 'accounts_endpoint'}
                except Exception as e:
                    result['message'] = str(e)
            
            return result
            
        except Exception as e:
            result['message'] = str(e)
            return result


# دالة مساعدة لإنشاء الموصل
def create_api_connector(config: Dict[str, Any]) -> APIConnector:
    """
    إنشاء موصل API مخصص
    
    Args:
        config: إعدادات الاتصال
        
    Returns:
        APIConnector: موصل جاهز
    """
    connector = APIConnector(config)
    connector.test_connection()  # اختبار الاتصال الأولي
    return connector
