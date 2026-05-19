"""
Finovate Audit Nexus AI - QuickBooks Connector
موصل نظام QuickBooks Online السحابي
"""
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from authlib.integrations.requests_client import OAuth2Session


class QuickBooksConnector:
    """
    موصل احترافي لنظام QuickBooks Online
    يستخدم QuickBooks API الرسمي v3
    """

    def __init__(self, config: Dict[str, Any]):
        """
        تهيئة موصل QuickBooks
        
        Args:
            config: إعدادات الاتصال
                - client_id: معرف العميل
                - client_secret: السر
                - access_token: رمز الوصول
                - refresh_token: رمز التحديث
                - realm_id: معرف الشركة (Company ID)
                - environment: sandbox أو production
        """
        self.client_id = config.get('client_id', '')
        self.client_secret = config.get('client_secret', '')
        self.access_token = config.get('access_token', '')
        self.refresh_token = config.get('refresh_token', '')
        self.realm_id = config.get('realm_id', '')
        self.environment = config.get('environment', 'production')
        
        self.connected = False
        self.last_sync = None
        self.token_expiry = None
        
        # تحديد البيئة
        if self.environment == 'sandbox':
            self.base_url = 'https://sandbox-quickbooks.api.intuit.com/v3'
            self.oauth_url = 'https://oauth.platform.sandbox.intuit.com/oauth2/v1'
        else:
            self.base_url = 'https://quickbooks.api.intuit.com/v3'
            self.oauth_url = 'https://oauth.platform.intuit.com/oauth2/v1'
    
    def _get_headers(self) -> Dict:
        """الحصول على رؤساء الطلب"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _refresh_token(self):
        """تحديث رمز الوصول"""
        try:
            url = f"{self.oauth_url}/tokens/bearer"
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            self.access_token = result['access_token']
            self.refresh_token = result.get('refresh_token', self.refresh_token)
            expires_in = result.get('expires_in', 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            self.connected = True
            
            return True
            
        except Exception as e:
            print(f"خطأ في تحديث الرمز: {str(e)}")
            self.connected = False
            raise
    
    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """
        تنفيذ طلب API
        
        Args:
            method: نوع الطلب
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
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                # رمز الوصول منتهي، محاولة التجديد
                self._refresh_token()
                headers = self._get_headers()
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
            raise
        except Exception as e:
            print(f"خطأ في الطلب: {str(e)}")
            raise
    
    # ==================== جلب القيود المحاسبية ====================
    
    def get_journal_entries(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        max_results: int = 1000
    ) -> List[Dict]:
        """
        جلب قيود اليومية
        
        Args:
            date_from: تاريخ البدء YYYY-MM-DD
            date_to: تاريخ الانتهاء YYYY-MM-DD
            max_results: الحد الأقصى للنتائج
            
        Returns:
            List[Dict]: قائمة القيود
        """
        query = "SELECT * FROM JournalEntry"
        
        conditions = []
        if date_from:
            conditions.append(f"TxnDate >= '{date_from}'")
        if date_to:
            conditions.append(f"TxnDate <= '{date_to}'")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += f" MAXRESULTS {max_results}"
        
        try:
            result = self._request('POST', f'company/{self.realm_id}/query', {'query': query})
            
            entries = []
            for entry in result.get('QueryResponse', {}).get('JournalEntry', []):
                lines = []
                for line in entry.get('Line', []):
                    lines.append({
                        'id': line.get('Id'),
                        'description': line.get('Description'),
                        'amount': line.get('Amount', 0),
                        'detail_type': line.get('DetailType'),
                        'account_id': line.get('JournalEntryLineDetail', {}).get('AccountRef', {}).get('value'),
                        'account_name': line.get('JournalEntryLineDetail', {}).get('AccountRef', {}).get('name'),
                        'posting_type': line.get('JournalEntryLineDetail', {}).get('PostingType')
                    })
                
                entries.append({
                    'id': entry.get('Id'),
                    'doc_number': entry.get('DocNumber'),
                    'date': entry.get('TxnDate'),
                    'reference': entry.get('PrivateNote'),
                    'total_amount': entry.get('TotalAmt', 0),
                    'adjustment': entry.get('Adjustment', False),
                    'lines': lines
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
            params['asof'] = as_of_date
        
        try:
            result = self._request(
                'GET',
                f'company/{self.realm_id}/reports/TrialBalance',
                params
            )
            
            trial_balance = []
            rows = result.get('Report', {}).get('Rows', {}).get('Row', [])
            
            for row in rows:
                if row.get('type') == 'Data':
                    cells = row.get('ColData', [])
                    if len(cells) >= 4:
                        trial_balance.append({
                            'account_code': cells[0].get('value', ''),
                            'account_name': cells[1].get('value', ''),
                            'debit': float(cells[2].get('value', 0) or 0),
                            'credit': float(cells[3].get('value', 0) or 0)
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
            pl_params = {'start_date': date_from, 'end_date': date_to}
            pl_result = self._request(
                'GET',
                f'company/{self.realm_id}/reports/ProfitAndLoss',
                pl_params
            )
            result['income_statement'] = pl_result.get('Report', {})
            
            # الميزانية العمومية
            bs_params = {'asof': date_to}
            bs_result = self._request(
                'GET',
                f'company/{self.realm_id}/reports/BalanceSheet',
                bs_params
            )
            result['balance_sheet'] = bs_result.get('Report', {})
            
            # التدفقات النقدية
            cf_params = {'start_date': date_from, 'end_date': date_to}
            cf_result = self._request(
                'GET',
                f'company/{self.realm_id}/reports/CashFlow',
                cf_params
            )
            result['cash_flow'] = cf_result.get('Report', {})
            
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
        max_results: int = 500
    ) -> List[Dict]:
        """
        جلب الفواتير
        
        Args:
            status: الحالة (Payable, Paid)
            date_from: تاريخ البدء
            date_to: تاريخ الانتهاء
            
        Returns:
            List[Dict]: قائمة الفواتير
        """
        query = "SELECT * FROM Invoice"
        
        conditions = []
        if date_from:
            conditions.append(f"TxnDate >= '{date_from}'")
        if date_to:
            conditions.append(f"TxnDate <= '{date_to}'")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += f" MAXRESULTS {max_results}"
        
        try:
            result = self._request('POST', f'company/{self.realm_id}/query', {'query': query})
            
            invoices = []
            for inv in result.get('QueryResponse', {}).get('Invoice', []):
                invoices.append({
                    'id': inv.get('Id'),
                    'doc_number': inv.get('DocNumber'),
                    'date': inv.get('TxnDate'),
                    'due_date': inv.get('DueDate'),
                    'customer_id': inv.get('CustomerRef', {}).get('value'),
                    'customer_name': inv.get('CustomerRef', {}).get('name'),
                    'total_amount': inv.get('TotalAmt', 0),
                    'balance': inv.get('Balance', 0),
                    'status': 'Paid' if inv.get('Balance', 0) == 0 else 'Payable',
                    'email_status': inv.get('EmailStatus'),
                    'currency': inv.get('CurrencyRef', {}).get('name', 'USD')
                })
            
            return invoices
            
        except Exception as e:
            print(f"خطأ في جلب الفواتير: {str(e)}")
            return []
    
    # ==================== جلب العملاء ====================
    
    def get_customers(
        self,
        active_only: bool = True,
        max_results: int = 500
    ) -> List[Dict]:
        """
        جلب العملاء
        
        Returns:
            List[Dict]: قائمة العملاء
        """
        query = "SELECT * FROM Customer"
        
        if active_only:
            query += " WHERE Active = true"
        
        query += f" MAXRESULTS {max_results}"
        
        try:
            result = self._request('POST', f'company/{self.realm_id}/query', {'query': query})
            
            customers = []
            for cust in result.get('QueryResponse', {}).get('Customer', []):
                customers.append({
                    'id': cust.get('Id'),
                    'display_name': cust.get('DisplayName'),
                    'given_name': cust.get('GivenName'),
                    'family_name': cust.get('FamilyName'),
                    'company_name': cust.get('CompanyName'),
                    'email': cust.get('PrimaryEmailAddr', {}).get('Address'),
                    'phone': cust.get('PrimaryPhone', {}).get('FreeFormNumber'),
                    'balance': cust.get('Balance', 0),
                    'active': cust.get('Active', True),
                    'tax_identifier': cust.get('TaxIdentifier')
                })
            
            return customers
            
        except Exception as e:
            print(f"خطأ في جلب العملاء: {str(e)}")
            return []
    
    # ==================== جلب البائعين ====================
    
    def get_vendors(
        self,
        active_only: bool = True,
        max_results: int = 500
    ) -> List[Dict]:
        """
        جلب البائعين
        
        Returns:
            List[Dict]: قائمة البائعين
        """
        query = "SELECT * FROM Vendor"
        
        if active_only:
            query += " WHERE Active = true"
        
        query += f" MAXRESULTS {max_results}"
        
        try:
            result = self._request('POST', f'company/{self.realm_id}/query', {'query': query})
            
            vendors = []
            for vend in result.get('QueryResponse', {}).get('Vendor', []):
                vendors.append({
                    'id': vend.get('Id'),
                    'display_name': vend.get('DisplayName'),
                    'given_name': vend.get('GivenName'),
                    'family_name': vend.get('FamilyName'),
                    'company_name': vend.get('CompanyName'),
                    'email': vend.get('PrimaryEmailAddr', {}).get('Address'),
                    'phone': vend.get('PrimaryPhone', {}).get('FreeFormNumber'),
                    'balance': vend.get('Balance', 0),
                    'active': vend.get('Active', True),
                    'tax_identifier': vend.get('TaxIdentifier')
                })
            
            return vendors
            
        except Exception as e:
            print(f"خطأ في جلب البائعين: {str(e)}")
            return []
    
    # ==================== جلب المنتجات والمخزون ====================
    
    def get_items(
        self,
        max_results: int = 500
    ) -> List[Dict]:
        """
        جلب المنتجات والمخزون
        
        Returns:
            List[Dict]: قائمة المنتجات
        """
        query = "SELECT * FROM Item"
        query += f" MAXRESULTS {max_results}"
        
        try:
            result = self._request('POST', f'company/{self.realm_id}/query', {'query': query})
            
            items = []
            for item in result.get('QueryResponse', {}).get('Item', []):
                items.append({
                    'id': item.get('Id'),
                    'name': item.get('Name'),
                    'sku': item.get('Sku'),
                    'type': item.get('Type'),
                    'quantity_on_hand': item.get('QtyOnHand', 0),
                    'purchase_cost': item.get('PurchaseCost', 0),
                    'unit_price': item.get('UnitPrice', 0),
                    'income_account_ref': item.get('IncomeAccountRef', {}).get('name'),
                    'expense_account_ref': item.get('ExpenseAccountRef', {}).get('name'),
                    'asset_account_ref': item.get('AssetAccountRef', {}).get('name'),
                    'active': item.get('Active', True)
                })
            
            return items
            
        except Exception as e:
            print(f"خطأ في جلب المنتجات: {str(e)}")
            return []
    
    # ==================== جلب الحسابات ====================
    
    def get_accounts(
        self,
        max_results: int = 500
    ) -> List[Dict]:
        """
        جلب دليل الحسابات
        
        Returns:
            List[Dict]: قائمة الحسابات
        """
        query = "SELECT * FROM Account"
        query += f" MAXRESULTS {max_results}"
        
        try:
            result = self._request('POST', f'company/{self.realm_id}/query', {'query': query})
            
            accounts = []
            for acc in result.get('QueryResponse', {}).get('Account', []):
                accounts.append({
                    'id': acc.get('Id'),
                    'name': acc.get('Name'),
                    'account_type': acc.get('AccountType'),
                    'account_sub_type': acc.get('AccountSubType'),
                    'classification': acc.get('Classification'),
                    'current_balance': acc.get('CurrentBalance', 0),
                    'active': acc.get('Active', True),
                    'fully_qualified_name': acc.get('FullyQualifiedName')
                })
            
            return accounts
            
        except Exception as e:
            print(f"خطأ في جلب الحسابات: {str(e)}")
            return []
    
    # ==================== معلومات الشركة ====================
    
    def get_company_info(self) -> Dict:
        """
        جلب معلومات الشركة
        
        Returns:
            Dict: معلومات الشركة
        """
        try:
            result = self._request('GET', f'company/{self.realm_id}/companyinfo/{self.realm_id}')
            
            info = result.get('QueryResponse', {}).get('CompanyInfo', [{}])[0]
            
            return {
                'erp_type': 'QuickBooks Online',
                'company_id': self.realm_id,
                'company_name': info.get('CompanyName'),
                'legal_name': info.get('LegalName'),
                'address': info.get('CompanyAddr', {}),
                'email': info.get('CompanyEmail', {}).get('Address'),
                'phone': info.get('PrimaryPhone', {}).get('FreeFormNumber'),
                'country': info.get('Country'),
                'currency': info.get('Currency'),
                'fiscal_year_start': info.get('FiscalYearStartMonth'),
                'supported_languages': info.get('SupportedLanguages'),
                'connected': self.connected,
                'last_sync': self.last_sync.isoformat() if self.last_sync else None
            }
            
        except Exception as e:
            print(f"خطأ في جلب معلومات الشركة: {str(e)}")
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
            invoices = self.get_invoices(max_results=1)
            synced['invoices_count'] = len(invoices) if invoices else 0
            
            # جلب القيود
            entries = self.get_journal_entries(max_results=1)
            synced['journal_entries_count'] = len(entries) if entries else 0
            
            # جلب العملاء
            customers = self.get_customers(max_results=1)
            synced['customers_count'] = len(customers) if customers else 0
            
            # جلب البائعين
            vendors = self.get_vendors(max_results=1)
            synced['vendors_count'] = len(vendors) if vendors else 0
            
            # جلب المنتجات
            items = self.get_items(max_results=1)
            synced['items_count'] = len(items) if items else 0
            
            # جلب الحسابات
            accounts = self.get_accounts(max_results=1)
            synced['accounts_count'] = len(accounts) if accounts else 0
            
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
            info = self.get_company_info()
            
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

    def connect(self) -> bool:
        """إنشاء الاتصال"""
        self.connected = True
        return True
    
    def disconnect(self):
        """قطع الاتصال"""
        self.connected = False
    
    def is_connected(self) -> bool:
        """التحقق من حالة الاتصال"""
        return self.connected

def create_quickbooks_connector(config: Dict[str, Any]) -> QuickBooksConnector:
    """
    إنشاء موصل QuickBooks
    
    Args:
        config: إعدادات الاتصال
        
    Returns:
        QuickBooksConnector: موصل جاهز
    """
    connector = QuickBooksConnector(config)
    connector.get_company_info()  # اختبار الاتصال الأولي
    return connector



