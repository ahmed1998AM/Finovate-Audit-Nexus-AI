"""
Finovate Audit Nexus AI - Zoho Books Connector
موصل نظام Zoho Books السحابي
"""
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json


class ZohoBooksConnector:
    """
    موصل احترافي لنظام Zoho Books
    يستخدم Zoho Books API الرسمي
    """

    def __init__(self, config: Dict[str, Any]):
        """
        تهيئة موصل Zoho Books
        
        Args:
            config: إعدادات الاتصال
                - client_id: معرف العميل
                - client_secret: السر
                - refresh_token: رمز التحديث
                - organization_id: معرف المنظمة
                - region: المنطقة (com, in, eu, au, cn)
        """
        self.client_id = config.get('client_id', '')
        self.client_secret = config.get('client_secret', '')
        self.refresh_token = config.get('refresh_token', '')
        self.organization_id = config.get('organization_id', '')
        self.region = config.get('region', 'com')
        
        self.access_token = None
        self.token_expiry = None
        self.connected = False
        self.last_sync = None
        
        self.base_url = f"https://www.zohoapis.{self.region}/books/v3"
    
    def _get_access_token(self) -> str:
        """
        الحصول على رمز الوصول
        
        Returns:
            str: رمز الوصول
        """
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token
        
        try:
            url = "https://accounts.zoho.com/oauth/v2/token"
            
            data = {
                'grant_type': 'refresh_token',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token
            }
            
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            self.access_token = result['access_token']
            expires_in = result.get('expires_in', 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            self.connected = True
            
            return self.access_token
            
        except Exception as e:
            print(f"خطأ في الحصول على رمز الوصول: {str(e)}")
            self.connected = False
            raise
    
    def _get_headers(self) -> Dict:
        """الحصول على رؤساء الطلب"""
        token = self._get_access_token()
        
        return {
            'Authorization': f'Zoho-oauthtoken {token}',
            'Content-Type': 'application/json'
        }
    
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
        
        if params is None:
            params = {}
        
        params['organization_id'] = self.organization_id
        
        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                params=params,
                json=data,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            print(f"خطأ HTTP: {str(e)}")
            if e.response.status_code == 401:
                # رمز الوصول منتهي، محاولة التجديد
                self.access_token = None
                return self._request(method, endpoint, params, data)
            raise
        except Exception as e:
            print(f"خطأ في الطلب: {str(e)}")
            raise
    
    # ==================== جلب القيود المحاسبية ====================
    
    def get_journal_entries(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page: int = 1,
        per_page: int = 200
    ) -> List[Dict]:
        """
        جلب قيود اليومية
        
        Args:
            date_from: تاريخ البدء YYYY-MM-DD
            date_to: تاريخ الانتهاء YYYY-MM-DD
            page: رقم الصفحة
            per_page: عدد العناصر
            
        Returns:
            List[Dict]: قائمة القيود
        """
        params = {
            'page': page,
            'per_page': per_page
        }
        
        if date_from:
            params['date_from'] = date_from
        if date_to:
            params['date_to'] = date_to
        
        try:
            result = self._request('GET', 'journalentries', params)
            
            entries = []
            for entry in result.get('journalentries', []):
                entries.append({
                    'id': entry.get('journalentry_id'),
                    'number': entry.get('journalentry_number'),
                    'date': entry.get('date'),
                    'reference': entry.get('reference_number'),
                    'description': entry.get('narration'),
                    'status': entry.get('status'),
                    'total_amount': entry.get('total'),
                    'lines': []
                })
                
                # جلب الأسطر
                for line in entry.get('journalentrylines', []):
                    entries[-1]['lines'].append({
                        'account_id': line.get('account_id'),
                        'account_name': line.get('account_name'),
                        'description': line.get('description'),
                        'debit': line.get('debit', 0),
                        'credit': line.get('credit', 0)
                    })
            
            return entries
            
        except Exception as e:
            print(f"خطأ في جلب القيود: {str(e)}")
            return []
    
    # ==================== جلب ميزان المراجعة ====================
    
    def get_trial_balance(
        self,
        as_of_date: Optional[str] = None
    ) -> List[Dict]:
        """
        جلب ميزان المراجعة
        
        Args:
            as_of_date: التاريخ YYYY-MM-DD
            
        Returns:
            List[Dict]: ميزان المراجعة
        """
        params = {}
        if as_of_date:
            params['as_of_date'] = as_of_date
        
        try:
            result = self._request('GET', 'reports/trialbalance', params)
            
            trial_balance = []
            for section in result.get('trialbalance', []):
                for account in section.get('trialbalance', []):
                    trial_balance.append({
                        'account_id': account.get('account_id'),
                        'account_code': account.get('account_code'),
                        'account_name': account.get('account_name'),
                        'debit': account.get('debit', 0),
                        'credit': account.get('credit', 0),
                        'balance': account.get('balance', 0)
                    })
            
            return trial_balance
            
        except Exception as e:
            print(f"خطأ في جلب ميزان المراجعة: {str(e)}")
            return []
    
    # ==================== جلب القوائم المالية ====================
    
    def get_financial_statements(
        self,
        date_from: str,
        date_to: str
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
        
        try:
            # قائمة الدخل
            pl_params = {'from_date': date_from, 'to_date': date_to}
            pl_result = self._request('GET', 'reports/profitandloss', pl_params)
            result['income_statement'] = pl_result.get('profitandloss', [])
            
            # الميزانية العمومية
            bs_params = {'as_of_date': date_to}
            bs_result = self._request('GET', 'reports/balancesheet', bs_params)
            result['balance_sheet'] = bs_result.get('balancesheet', [])
            
            # التدفقات النقدية
            cf_params = {'from_date': date_from, 'to_date': date_to}
            cf_result = self._request('GET', 'reports/cashflow', cf_params)
            result['cash_flow'] = cf_result.get('cashflow', [])
            
            return result
            
        except Exception as e:
            print(f"خطأ في جلب القوائم المالية: {str(e)}")
            return result
    
    # ==================== جلب الفواتير ====================
    
    def get_invoices(
        self,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page: int = 1,
        per_page: int = 200
    ) -> List[Dict]:
        """
        جلب الفواتير
        
        Args:
            status: الحالة (draft, sent, viewed, accepted, paid, overdue)
            date_from: تاريخ البدء
            date_to: تاريخ الانتهاء
            
        Returns:
            List[Dict]: قائمة الفواتير
        """
        params = {
            'page': page,
            'per_page': per_page
        }
        
        if status:
            params['status'] = status
        if date_from:
            params['date_from'] = date_from
        if date_to:
            params['date_to'] = date_to
        
        try:
            result = self._request('GET', 'invoices', params)
            
            invoices = []
            for inv in result.get('invoices', []):
                invoices.append({
                    'id': inv.get('invoice_id'),
                    'number': inv.get('invoice_number'),
                    'date': inv.get('date'),
                    'due_date': inv.get('due_date'),
                    'customer_id': inv.get('customer_id'),
                    'customer_name': inv.get('customer_name'),
                    'amount': inv.get('total'),
                    'balance': inv.get('balance'),
                    'status': inv.get('status'),
                    'currency': inv.get('currency_code', 'USD')
                })
            
            return invoices
            
        except Exception as e:
            print(f"خطأ في جلب الفواتير: {str(e)}")
            return []
    
    # ==================== جلب العملاء ====================
    
    def get_customers(
        self,
        status: str = 'active',
        page: int = 1,
        per_page: int = 200
    ) -> List[Dict]:
        """
        جلب العملاء
        
        Returns:
            List[Dict]: قائمة العملاء
        """
        params = {
            'page': page,
            'per_page': per_page
        }
        
        if status:
            params['status'] = status
        
        try:
            result = self._request('GET', 'customers', params)
            
            customers = []
            for cust in result.get('contacts', []):
                customers.append({
                    'id': cust.get('contact_id'),
                    'name': cust.get('company_name') or cust.get('contact_name'),
                    'email': cust.get('email'),
                    'phone': cust.get('mobile'),
                    'billing_address': cust.get('billing_address'),
                    'shipping_address': cust.get('shipping_address'),
                    'tax_number': cust.get('tax_number'),
                    'outstanding_receivable': cust.get('outstanding_receivable_amount'),
                    'status': cust.get('status')
                })
            
            return customers
            
        except Exception as e:
            print(f"خطأ في جلب العملاء: {str(e)}")
            return []
    
    # ==================== جلب البائعين ====================
    
    def get_vendors(
        self,
        status: str = 'active',
        page: int = 1,
        per_page: int = 200
    ) -> List[Dict]:
        """
        جلب البائعين
        
        Returns:
            List[Dict]: قائمة البائعين
        """
        params = {
            'page': page,
            'per_page': per_page
        }
        
        if status:
            params['status'] = status
        
        try:
            result = self._request('GET', 'vendors', params)
            
            vendors = []
            for vend in result.get('contacts', []):
                vendors.append({
                    'id': vend.get('contact_id'),
                    'name': vend.get('company_name') or vend.get('contact_name'),
                    'email': vend.get('email'),
                    'phone': vend.get('mobile'),
                    'billing_address': vend.get('billing_address'),
                    'tax_number': vend.get('tax_number'),
                    'outstanding_payable': vend.get('outstanding_payable_amount'),
                    'status': vend.get('status')
                })
            
            return vendors
            
        except Exception as e:
            print(f"خطأ في جلب البائعين: {str(e)}")
            return []
    
    # ==================== جلب المخزون ====================
    
    def get_inventory(
        self,
        page: int = 1,
        per_page: int = 200
    ) -> List[Dict]:
        """
        جلب المخزون
        
        Returns:
            List[Dict]: قائمة المنتجات
        """
        params = {
            'page': page,
            'per_page': per_page
        }
        
        try:
            result = self._request('GET', 'items', params)
            
            items = []
            for item in result.get('items', []):
                items.append({
                    'id': item.get('item_id'),
                    'name': item.get('name'),
                    'sku': item.get('sku'),
                    'rate': item.get('rate'),
                    'purchase_rate': item.get('purchase_rate'),
                    'quantity_available': item.get('quantity_available'),
                    'quantity_on_hand': item.get('quantity_on_hand'),
                    'reorder_level': item.get('reorder_level'),
                    'account_name': item.get('sales_account_name'),
                    'tax_name': item.get('tax_name')
                })
            
            return items
            
        except Exception as e:
            print(f"خطأ في جلب المخزون: {str(e)}")
            return []
    
    # ==================== جلب الحسابات ====================
    
    def get_accounts(
        self,
        account_type: Optional[str] = None
    ) -> List[Dict]:
        """
        جلب دليل الحسابات
        
        Args:
            account_type: نوع الحساب
            
        Returns:
            List[Dict]: قائمة الحسابات
        """
        params = {}
        if account_type:
            params['type'] = account_type
        
        try:
            result = self._request('GET', 'chartofaccounts', params)
            
            accounts = []
            for acc in result.get('chartofaccounts', []):
                accounts.append({
                    'id': acc.get('account_id'),
                    'code': acc.get('account_code'),
                    'name': acc.get('account_name'),
                    'type': acc.get('account_type'),
                    'description': acc.get('account_description'),
                    'balance': acc.get('balance')
                })
            
            return accounts
            
        except Exception as e:
            print(f"خطأ في جلب الحسابات: {str(e)}")
            return []
    
    # ==================== معلومات المنظمة ====================
    
    def get_organization_info(self) -> Dict:
        """
        جلب معلومات المنظمة
        
        Returns:
            Dict: معلومات المنظمة
        """
        try:
            result = self._request('GET', 'organizations')
            
            orgs = result.get('organizations', [])
            if orgs:
                org = orgs[0]
                return {
                    'erp_type': 'Zoho Books',
                    'organization_id': org.get('organization_id'),
                    'organization_name': org.get('organization_name'),
                    'company_name': org.get('company_name'),
                    'currency': org.get('currency_code'),
                    'timezone': org.get('timezone'),
                    'locale': org.get('locale'),
                    'connected': self.connected,
                    'last_sync': self.last_sync.isoformat() if self.last_sync else None
                }
            
            return {'error': 'لم يتم العثور على منظمة'}
            
        except Exception as e:
            print(f"خطأ في جلب معلومات المنظمة: {str(e)}")
            return {'error': str(e), 'connected': False}
    
    # ==================== المزامنة ====================
    
    def sync_all(self) -> Dict[str, int]:
        """
        مزامنة جميع البيانات
        
        Returns:
            Dict: عدد العناصر المزامنة
        """
        synced = {}
        
        try:
            # جلب الفواتير
            invoices = self.get_invoices(per_page=1)
            synced['invoices_count'] = len(invoices) if invoices else 0
            
            # جلب القيود
            entries = self.get_journal_entries(per_page=1)
            synced['journal_entries_count'] = len(entries) if entries else 0
            
            # جلب العملاء
            customers = self.get_customers(per_page=1)
            synced['customers_count'] = len(customers) if customers else 0
            
            # جلب البائعين
            vendors = self.get_vendors(per_page=1)
            synced['vendors_count'] = len(vendors) if vendors else 0
            
            # جلب المخزون
            items = self.get_inventory(per_page=1)
            synced['inventory_count'] = len(items) if items else 0
            
            self.last_sync = datetime.now()
            
        except Exception as e:
            print(f"خطأ في المزامنة: {str(e)}")
        
        return synced
    
    # ==================== اختبار الاتصال ====================
    
    def test_connection(self) -> Dict:
        """
        اختبار الاتصال
        
        Returns:
            Dict: نتيجة الاختبار
        """
        result = {
            'success': False,
            'message': '',
            'details': {}
        }
        
        try:
            info = self.get_organization_info()
            
            if 'error' not in info:
                result['success'] = True
                result['message'] = 'اتصال ناجح'
                result['details'] = info
            else:
                result['message'] = info.get('error', 'خطأ غير معروف')
            
            return result
            
        except Exception as e:
            result['message'] = str(e)
            return result


# دالة مساعدة لإنشاء الموصل
def create_zoho_connector(config: Dict[str, Any]) -> ZohoBooksConnector:
    """
    إنشاء موصل Zoho Books
    
    Args:
        config: إعدادات الاتصال
        
    Returns:
        ZohoBooksConnector: موصل جاهز
    """
    connector = ZohoBooksConnector(config)
    connector._get_access_token()  # اختبار الاتصال الأولي
    return connector
