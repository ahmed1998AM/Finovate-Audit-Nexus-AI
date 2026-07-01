"""
Finovate Audit Nexus AI - Xero Connector
موصل نظام Xero Accounting السحابي
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests

from connectors.base_connector import BaseERPConnector

logger = logging.getLogger(__name__)


@dataclass
class XeroConnectionConfig:
    """فئة إعدادات الاتصال بـ Xero"""
    client_id: str
    client_secret: str
    access_token: str = ''
    refresh_token: str = ''
    tenant_id: str = ''
    environment: str = 'production'

    def to_dict(self) -> Dict[str, Any]:
        """تحويل الإعدادات إلى قاموس"""
        return {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'tenant_id': self.tenant_id,
            'environment': self.environment
        }


class XeroConnector(BaseERPConnector):
    """
    موصل احترافي لنظام Xero Accounting
    يستخدم Xero API الرسمي v2
    """

    def __init__(self, config: Dict[str, Any]):
        """
        تهيئة موصل Xero

        Args:
            config: إعدادات الاتصال
                - client_id: معرف العميل
                - client_secret: السر
                - access_token: رمز الوصول
                - refresh_token: رمز التحديث
                - tenant_id: معرف المستأجر (Organization ID)
                - environment: sandbox أو production
        """
        super().__init__()
        self.client_id = config.get('client_id', '')
        self.client_secret = config.get('client_secret', '')
        self.access_token = config.get('access_token', '')
        self.refresh_token = config.get('refresh_token', '')
        self.tenant_id = config.get('tenant_id', '')
        self.environment = config.get('environment', 'production')

        self.token_expiry = None

        # تحديد البيئة
        if self.environment == 'sandbox':
            self.base_url = 'https://api-sandbox.xero.com/api.xro/2.0'
            self.auth_url = 'https://identity-sandbox.xero.com/connect/token'
        else:
            self.base_url = 'https://api.xero.com/api.xro/2.0'
            self.auth_url = 'https://identity.xero.com/connect/token'

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
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }

            response = requests.post(self.auth_url, data=data, timeout=30)
            response.raise_for_status()

            result = response.json()

            self.access_token = result['access_token']
            self.refresh_token = result.get('refresh_token', self.refresh_token)
            expires_in = result.get('expires_in', 1800)  # Xero tokens expire in 30 mins
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            self._connected = True

            return True

        except Exception as e:
            logger.error("خطأ في تحديث الرمز: %s", e)
            self._connected = False
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
            logger.error("خطأ في الطلب: %s", e)
            raise

    # ==================== جلب القيود المحاسبية ====================

    def get_journal_entries(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page: int = 1
    ) -> List[Dict]:
        """
        جلب قيود اليومية

        Args:
            date_from: تاريخ البدء YYYY-MM-DD
            date_to: تاريخ الانتهاء YYYY-MM-DD
            page: رقم الصفحة

        Returns:
            List[Dict]: قائمة القيود
        """
        params = {'page': page}

        if date_from or date_to:
            where_clauses = []
            if date_from:
                where_clauses.append(f'Date >= DateTime("{date_from}T00:00:00")')
            if date_to:
                where_clauses.append(f'Date <= DateTime("{date_to}T23:59:59")')

            params['where'] = ' && '.join(where_clauses)

        try:
            result = self._request('GET', 'Journals', params)

            entries = []
            for entry in result.get('Journals', []):
                lines = []
                for line in entry.get('JournalLines', []):
                    lines.append({
                        'account_id': line.get('Account', {}).get('AccountID'),
                        'account_code': line.get('Account', {}).get('Code'),
                        'account_name': line.get('Account', {}).get('Name'),
                        'description': line.get('Description'),
                        'debit': line.get('DebitAmount', 0),
                        'credit': line.get('CreditAmount', 0),
                        'line_amount': line.get('LineAmount', 0)
                    })

                entries.append({
                    'id': entry.get('JournalID'),
                    'journal_number': entry.get('JournalNumber'),
                    'date': entry.get('Date'),
                    'reference': entry.get('Reference'),
                    'source_type': entry.get('SourceType'),
                    'source_id': entry.get('SourceID'),
                    'lines': lines
                })

            return entries

        except Exception as e:
            logger.error("خطأ في جلب القيود: %s", e)
            return []

    # ==================== جلب ميزان المراجعة ====================

    def get_trial_balance(
        self,
        as_of_date: Optional[str] = None,
        standard_only: bool = True
    ) -> List[Dict]:
        """
        جلب ميزان المراجعة

        Args:
            as_of_date: التاريخ YYYY-MM-DD
            standard_only: حسابات قياسية فقط

        Returns:
            List[Dict]: ميزان المراجعة
        """
        params = {}
        if as_of_date:
            params['date'] = as_of_date
        if standard_only:
            params['standardOnly'] = 'true'

        try:
            result = self._request('GET', 'Reports/TrialBalance', params)

            trial_balance = []
            rows = result.get('Reports', [{}])[0].get('Rows', [])

            for row in rows:
                if row.get('RowType') == 'Section':
                    for section_row in row.get('Rows', []):
                        if section_row.get('RowType') == 'Row':
                            cells = section_row.get('Cells', [])
                            if len(cells) >= 4:
                                trial_balance.append({
                                    'account_name': cells[0].get('Value', ''),
                                    'ytd_debit': float(cells[1].get('Value', 0) or 0),
                                    'ytd_credit': float(cells[2].get('Value', 0) or 0),
                                    'month_debit': float(cells[3].get('Value', 0) or 0),
                                    'month_credit': float(cells[4].get('Value', 0) or 0) if len(cells) > 4 else 0
                                })

            return trial_balance

        except Exception as e:
            logger.error("خطأ في جلب ميزان المراجعة: %s", e)
            return []

    # ==================== جلب القوائم المالية ====================

    def get_financial_statements(
        self,
        date_from: str,
        date_to: str,
        standard_only: bool = True
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
            # قائمة الدخل (Profit & Loss)
            pl_params = {
                'fromDate': date_from,
                'toDate': date_to,
                'standardOnly': 'true' if standard_only else 'false'
            }
            pl_result = self._request('GET', 'Reports/ProfitAndLoss', pl_params)
            reports = pl_result.get('Reports', [])
            if reports:
                result['income_statement'] = reports[0]

            # الميزانية العمومية (Balance Sheet)
            bs_params = {
                'date': date_to,
                'standardOnly': 'true' if standard_only else 'false'
            }
            bs_result = self._request('GET', 'Reports/BalanceSheet', bs_params)
            reports = bs_result.get('Reports', [])
            if reports:
                result['balance_sheet'] = reports[0]

            # التدفقات النقدية (Cash Flow)
            cf_params = {
                'fromDate': date_from,
                'toDate': date_to,
                'standardOnly': 'true' if standard_only else 'false'
            }
            cf_result = self._request('GET', 'Reports/CashFlow', cf_params)
            reports = cf_result.get('Reports', [])
            if reports:
                result['cash_flow'] = reports[0]

            return result

        except Exception as e:
            logger.error("خطأ في جلب القوائم المالية: %s", e)
            return result

    # ==================== جلب الفواتير ====================

    def get_invoices(
        self,
        invoice_type: str = 'ACCREC',  # ACCREC = Sales, ACCPAY = Purchase
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page: int = 1
    ) -> List[Dict]:
        """
        جلب الفواتير

        Args:
            invoice_type: نوع الفاتورة (ACCREC, ACCPAY)
            status: الحالة (DRAFT, SUBMITTED, AUTHORISED, PAID, VOIDED)
            date_from: تاريخ البدء
            date_to: تاريخ الانتهاء

        Returns:
            List[Dict]: قائمة الفواتير
        """
        params = {'page': page}

        where_clauses = []
        if invoice_type:
            where_clauses.append(f'Type == "{invoice_type}"')
        if status:
            where_clauses.append(f'Status == "{status}"')
        if date_from:
            where_clauses.append(f'Date >= DateTime("{date_from}T00:00:00")')
        if date_to:
            where_clauses.append(f'Date <= DateTime("{date_to}T23:59:59")')

        if where_clauses:
            params['where'] = ' && '.join(where_clauses)

        try:
            result = self._request('GET', 'Invoices', params)

            invoices = []
            for inv in result.get('Invoices', []):
                invoices.append({
                    'id': inv.get('InvoiceID'),
                    'invoice_number': inv.get('InvoiceNumber'),
                    'reference': inv.get('Reference'),
                    'date': inv.get('Date'),
                    'due_date': inv.get('DueDate'),
                    'contact_id': inv.get('Contact', {}).get('ContactID'),
                    'contact_name': inv.get('Contact', {}).get('Name'),
                    'status': inv.get('Status'),
                    'total_amount': inv.get('Total'),
                    'amount_due': inv.get('AmountDue'),
                    'amount_paid': inv.get('AmountPaid'),
                    'currency': inv.get('CurrencyCode', 'USD'),
                    'type': inv.get('Type')
                })

            return invoices

        except Exception as e:
            logger.error("خطأ في جلب الفواتير: %s", e)
            return []

    # ==================== جلب جهات الاتصال (عملاء/موردين) ====================

    def get_contacts(
        self,
        contact_type: Optional[str] = None,  # CUSTOMER, SUPPLIER
        status: str = 'ACTIVE',
        page: int = 1
    ) -> List[Dict]:
        """
        جلب جهات الاتصال

        Args:
            contact_type: النوع
            status: الحالة
            page: رقم الصفحة

        Returns:
            List[Dict]: قائمة جهات الاتصال
        """
        params = {'page': page}

        where_clauses = []
        if status:
            where_clauses.append(f'Status == "{status}"')

        if where_clauses:
            params['where'] = ' && '.join(where_clauses)

        try:
            result = self._request('GET', 'Contacts', params)

            contacts = []
            for contact in result.get('Contacts', []):
                contacts.append({
                    'id': contact.get('ContactID'),
                    'name': contact.get('Name'),
                    'first_name': contact.get('FirstName'),
                    'last_name': contact.get('LastName'),
                    'email': contact.get('EmailAddress'),
                    'phone': contact.get('Phone'),
                    'mobile': contact.get('Mobile'),
                    'account_number': contact.get('AccountNumber'),
                    'tax_number': contact.get('TaxNumber'),
                    'is_customer': contact.get('IsCustomer', False),
                    'is_supplier': contact.get('IsSupplier', False),
                    'balances': {
                        'accounts_receivable': contact.get('Balances', {}).get('AccountsReceivable', 0),
                        'accounts_payable': contact.get('Balances', {}).get('AccountsPayable', 0)
                    },
                    'status': contact.get('Status')
                })

            return contacts

        except Exception as e:
            logger.error("خطأ في جلب جهات الاتصال: %s", e)
            return []

    # ==================== جلب المنتجات والمخزون ====================

    def get_items(
        self,
        status: str = 'ACTIVE',
        page: int = 1
    ) -> List[Dict]:
        """
        جلب المنتجات والمخزون

        Returns:
            List[Dict]: قائمة المنتجات
        """
        params = {'page': page}

        if status:
            params['where'] = f'Status == "{status}"'

        try:
            result = self._request('GET', 'Items', params)

            items = []
            for item in result.get('Items', []):
                items.append({
                    'id': item.get('ItemID'),
                    'code': item.get('Code'),
                    'name': item.get('Name'),
                    'description': item.get('Description'),
                    'purchase_description': item.get('PurchaseDescription'),
                    'purchase_price': item.get('PurchasePrice', 0),
                    'sale_price': item.get('SalePrice', 0),
                    'is_sold': item.get('IsSold', False),
                    'is_purchased': item.get('IsPurchased', False),
                    'is_tracked_as_inventory': item.get('IsTrackedAsInventory', False),
                    'quantity_on_hand': item.get('QuantityOnHand', 0),
                    'inventory_asset_account_id': item.get('InventoryAssetAccountID'),
                    'cost_of_goods_sold_account_id': item.get('COGSAccountID'),
                    'sales_account_id': item.get('SalesAccountID'),
                    'purchase_account_id': item.get('PurchaseAccountID'),
                    'status': item.get('Status')
                })

            return items

        except Exception as e:
            logger.error("خطأ في جلب المنتجات: %s", e)
            return []

    # ==================== جلب الحسابات ====================

    def get_accounts(
        self,
        account_type: Optional[str] = None,
        status: str = 'ACTIVE'
    ) -> List[Dict]:
        """
        جلب دليل الحسابات

        Args:
            account_type: نوع الحساب
            status: الحالة

        Returns:
            List[Dict]: قائمة الحسابات
        """
        params = {}

        where_clauses = []
        if status:
            where_clauses.append(f'Status == "{status}"')
        if account_type:
            where_clauses.append(f'Type == "{account_type}"')

        if where_clauses:
            params['where'] = ' && '.join(where_clauses)

        try:
            result = self._request('GET', 'Accounts', params)

            accounts = []
            for acc in result.get('Accounts', []):
                accounts.append({
                    'id': acc.get('AccountID'),
                    'code': acc.get('Code'),
                    'name': acc.get('Name'),
                    'type': acc.get('Type'),
                    'reporting_code': acc.get('ReportingCode'),
                    'reporting_code_name': acc.get('ReportingCodeName'),
                    'description': acc.get('Description'),
                    'bank_account_number': acc.get('BankAccountNumber'),
                    'currency_code': acc.get('CurrencyCode'),
                    'enable_payments_to_account': acc.get('EnablePaymentsToAccount', False),
                    'has_attachments': acc.get('HasAttachments', False),
                    'status': acc.get('Status'),
                    'class': acc.get('Class')
                })

            return accounts

        except Exception as e:
            logger.error("خطأ في جلب الحسابات: %s", e)
            return []

    # ==================== معلومات المنظمة ====================

    def get_organization_info(self) -> Dict:
        """
        جلب معلومات المنظمة

        Returns:
            Dict: معلومات المنظمة
        """
        try:
            result = self._request('GET', 'Organisation')

            orgs = result.get('Organisations', [])
            if orgs:
                org = orgs[0]
                return {
                    'erp_type': 'Xero',
                    'organization_id': org.get('OrganisationID'),
                    'name': org.get('Name'),
                    'legal_name': org.get('LegalName'),
                    'short_code': org.get('ShortCode'),
                    'tax_number': org.get('TaxNumber'),
                    'currency': org.get('BaseCurrency'),
                    'country': org.get('CountryCode'),
                    'timezone': org.get('Timezone'),
                    'organisation_type': org.get('OrganisationType'),
                    'financial_year_end_day': org.get('FinancialYearEndDay'),
                    'financial_year_end_month': org.get('FinancialYearEndMonth'),
                    'sales_tax_basis': org.get('SalesTaxBasis'),
                    'connected': self._connected,
                    'last_sync': self.last_sync.isoformat() if self.last_sync else None
                }

            return {'error': 'لم يتم العثور على منظمة'}

        except Exception as e:
            logger.error("خطأ في جلب معلومات المنظمة: %s", e)
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
            invoices = self.get_invoices(page=1)
            synced['invoices_count'] = len(invoices) if invoices else 0

            # جلب القيود
            entries = self.get_journal_entries(page=1)
            synced['journal_entries_count'] = len(entries) if entries else 0

            # جلب جهات الاتصال
            contacts = self.get_contacts(page=1)
            synced['contacts_count'] = len(contacts) if contacts else 0

            # جلب المنتجات
            items = self.get_items(page=1)
            synced['items_count'] = len(items) if items else 0

            # جلب الحسابات
            accounts = self.get_accounts()
            synced['accounts_count'] = len(accounts) if accounts else 0

            self.last_sync = datetime.now()

        except Exception as e:
            logger.error("خطأ في المزامنة: %s", e)

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


    # ==================== إدارة الاتصال ====================

    def connect(self) -> bool:
        """إنشاء الاتصال بـ Xero"""
        try:
            info = self.get_organization_info()
            if 'error' not in info:
                self._connected = True
                return True
            logger.warning("Xero connection failed: %s", info.get('error'))
            self._connected = False
            return False
        except Exception as e:
            logger.error("Xero connection failed: %s", e)
            self._connected = False
            return False

    def disconnect(self) -> None:
        """قطع الاتصال"""
        self.access_token = None
        self.refresh_token = None
        self._connected = False


# دالة مساعدة لإنشاء الموصل

def create_xero_connector(config: Dict[str, Any]) -> XeroConnector:
    """
    إنشاء موصل Xero

    Args:
        config: إعدادات الاتصال

    Returns:
        XeroConnector: موصل جاهز
    """
    connector = XeroConnector(config)
    connector.get_organization_info()  # اختبار الاتصال الأولي
    return connector



