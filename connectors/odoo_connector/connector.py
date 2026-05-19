"""
Finovate Audit Nexus AI - Odoo ERP Connector
موصل نظام Odoo ERP المفتوح المصدر
"""
import requests
import xmlrpc.client
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json


class OdooConnector:
    """
    موصل احترافي لنظام Odoo ERP
    يدعم الإصدارات 14+ عبر XML-RPC و JSON-RPC
    """

    def __init__(self, config: Dict[str, Any]):
        """
        تهيئة موصل Odoo
        
        Args:
            config: إعدادات الاتصال
                - url: رابط Odoo
                - db: اسم قاعدة البيانات
                - username: اسم المستخدم
                - password: كلمة المرور أو API Key
                - version: إصدار Odoo
        """
        self.url = config.get('url', '').rstrip('/')
        self.db = config.get('db', 'odoo')
        self.username = config.get('username', 'admin')
        self.password = config.get('password', '')
        self.api_key = config.get('api_key', '')
        self.version = config.get('version', '16')
        
        self.uid = None
        self.common = None
        self.models = None
        self.connected = False
        self.last_sync = None
        
    def connect(self) -> bool:
        """
        إنشاء اتصال مع Odoo عبر XML-RPC
        
        Returns:
            bool: نجاح الاتصال
        """
        try:
            # اتصال مشترك للمصادقة
            self.common = xmlrpc.client.ServerProxy(
                f'{self.url}/xmlrpc/2/common'
            )
            
            # مصادقة
            if self.api_key:
                self.uid = self.common.authenticate(
                    self.db, 
                    self.username, 
                    self.api_key, 
                    {}
                )
            else:
                self.uid = self.common.authenticate(
                    self.db, 
                    self.username, 
                    self.password, 
                    {}
                )
            
            if not self.uid:
                raise Exception("فشل المصادقة - تحقق من بيانات الدخول")
            
            # اتصال للنماذج
            self.models = xmlrpc.client.ServerProxy(
                f'{self.url}/xmlrpc/2/object'
            )
            
            self.connected = True
            self.last_sync = datetime.now()
            
            return True
            
        except Exception as e:
            print(f"خطأ في الاتصال بـ Odoo: {str(e)}")
            self.connected = False
            return False
    
    def disconnect(self):
        """قطع الاتصال"""
        self.common = None
        self.models = None
        self.uid = None
        self.connected = False
    
    def _execute(self, model: str, method: str, *args, **kwargs):
        """تنفيذ عملية على نموذج Odoo"""
        if not self.connected:
            raise Exception("غير متصل بـ Odoo")
        
        return self.models.execute_kw(
            self.db, 
            self.uid, 
            self.password or self.api_key,
            model, 
            method, 
            list(args),
            kwargs
        )
    
    # ==================== جلب القيود المحاسبية ====================
    
    def get_journal_entries(
        self, 
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        journal_ids: Optional[List[int]] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """
        جلب قيود اليومية من Odoo
        
        Args:
            date_from: تاريخ البدء YYYY-MM-DD
            date_to: تاريخ الانتهاء YYYY-MM-DD
            journal_ids: قائمة معرفات الدفاتر
            limit: الحد الأقصى للقيود
            
        Returns:
            List[Dict]: قائمة القيود
        """
        domain = []
        
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        if journal_ids:
            domain.append(('journal_id', 'in', journal_ids))
        
        try:
            move_ids = self._execute(
                'account.move',
                'search',
                domain,
                {'limit': limit, 'order': 'date desc'}
            )
            
            if not move_ids:
                return []
            
            # جلب تفاصيل القيود
            fields = [
                'id', 'name', 'date', 'ref', 'state',
                'journal_id', 'company_id', 'currency_id',
                'amount_total', 'line_ids'
            ]
            
            moves = self._execute(
                'account.move',
                'read',
                move_ids,
                {'fields': fields}
            )
            
            entries = []
            for move in moves:
                entry = {
                    'id': move['id'],
                    'name': move.get('name', '/'),
                    'date': move.get('date', ''),
                    'reference': move.get('ref', ''),
                    'state': move.get('state', 'draft'),
                    'journal_id': move.get('journal_id', [False, ''])[1] if move.get('journal_id') else '',
                    'company_id': move.get('company_id', [False, ''])[1] if move.get('company_id') else '',
                    'amount_total': move.get('amount_total', 0),
                    'lines': []
                }
                
                # جلب أسطر القيود
                if move.get('line_ids'):
                    line_ids = move['line_ids']
                    if isinstance(line_ids, list) and len(line_ids) > 0:
                        line_ids = line_ids[2] if len(line_ids) > 2 else line_ids[0] if isinstance(line_ids[0], int) else []
                        
                        if line_ids:
                            line_fields = [
                                'id', 'name', 'account_id', 'debit', 'credit',
                                'balance', 'partner_id', 'analytic_account_id'
                            ]
                            
                            lines = self._execute(
                                'account.move.line',
                                'read',
                                line_ids if isinstance(line_ids, list) else [line_ids],
                                {'fields': line_fields}
                            )
                            
                            for line in lines:
                                entry['lines'].append({
                                    'id': line['id'],
                                    'description': line.get('name', ''),
                                    'account_id': line.get('account_id', [False, ''])[1] if line.get('account_id') else '',
                                    'account_name': line.get('account_id', [False, ''])[0] if line.get('account_id') else '',
                                    'debit': line.get('debit', 0),
                                    'credit': line.get('credit', 0),
                                    'balance': line.get('balance', 0),
                                    'partner_id': line.get('partner_id', [False, ''])[1] if line.get('partner_id') else '',
                                })
                
                entries.append(entry)
            
            return entries
            
        except Exception as e:
            print(f"خطأ في جلب القيود: {str(e)}")
            return []
    
    # ==================== جلب ميزان المراجعة ====================
    
    def get_trial_balance(
        self,
        date: Optional[str] = None,
        account_ids: Optional[List[int]] = None
    ) -> List[Dict]:
        """
        جلب ميزان المراجعة
        
        Args:
            date: التاريخ YYYY-MM-DD
            account_ids: قائمة الحسابات
            
        Returns:
            List[Dict]: ميزان المراجعة
        """
        try:
            domain = [('reconciled', '=', False)]
            
            if account_ids:
                domain.append(('account_id', 'in', account_ids))
            
            # استخدام تقرير Odoo المدمج
            trial_balance = self._execute(
                'account.report',
                '_get_report_values',
                {'date_to': date, 'account_ids': account_ids}
            )
            
            return trial_balance if trial_balance else []
            
        except Exception as e:
            print(f"خطأ في جلب ميزان المراجعة: {str(e)}")
            # طريقة بديلة
            return self._get_trial_balance_fallback(date, account_ids)
    
    def _get_trial_balance_fallback(
        self,
        date: Optional[str] = None,
        account_ids: Optional[List[int]] = None
    ) -> List[Dict]:
        """طريقة بديلة لحساب ميزان المراجعة"""
        try:
            domain = []
            if date:
                domain.append(('date', '<=', date))
            if account_ids:
                domain.append(('account_id', 'in', account_ids))
            
            # تجميع الأرصدة حسب الحساب
            accounts = self._execute(
                'account.account',
                'search_read',
                domain,
                {
                    'fields': ['code', 'name', 'user_type_id'],
                    'groupby': ['id']
                }
            )
            
            trial_balance = []
            for account in accounts:
                # حساب الرصيد
                moves = self._execute(
                    'account.move.line',
                    'search_read',
                    [('account_id', '=', account['id'][0])] + ([(('date', '<=', date))] if date else []),
                    {'fields': ['debit', 'credit']}
                )
                
                total_debit = sum(m.get('debit', 0) for m in moves)
                total_credit = sum(m.get('credit', 0) for m in moves)
                balance = total_debit - total_credit
                
                trial_balance.append({
                    'account_id': account['id'][0],
                    'account_code': account.get('code', ''),
                    'account_name': account.get('name', ''),
                    'account_type': account.get('user_type_id', [False, ''])[1] if account.get('user_type_id') else '',
                    'debit': total_debit,
                    'credit': total_credit,
                    'balance': balance
                })
            
            return trial_balance
            
        except Exception as e:
            print(f"خطأ في الطريقة البديلة لميزان المراجعة: {str(e)}")
            return []
    
    # ==================== جلب القوائم المالية ====================
    
    def get_financial_statements(
        self,
        date_from: str,
        date_to: str,
        company_id: Optional[int] = None
    ) -> Dict:
        """
        جلب القوائم المالية
        
        Returns:
            Dict: يحتوي على قائمة الدخل والمركز المالي
        """
        try:
            result = {
                'income_statement': [],
                'balance_sheet': [],
                'cash_flow': []
            }
            
            # جلب الأرصدة النهائية
            domain = [('date', '<=', date_to)]
            if company_id:
                domain.append(('company_id', '=', company_id))
            
            # حساب صافي الربح
            pl_accounts = self._execute(
                'account.account',
                'search_read',
                [('internal_group', 'in', ['income', 'expense'])] + domain,
                {'fields': ['code', 'name', 'internal_group']}
            )
            
            income = 0
            expense = 0
            
            for acc in pl_accounts:
                moves = self._execute(
                    'account.move.line',
                    'search_read',
                    [('account_id', '=', acc['id'][0]), ('date', '>=', date_from), ('date', '<=', date_to)],
                    {'fields': ['debit', 'credit']}
                )
                
                total_debit = sum(m.get('debit', 0) for m in moves)
                total_credit = sum(m.get('credit', 0) for m in moves)
                
                if acc['internal_group'] == 'income':
                    income += total_credit - total_debit
                else:
                    expense += total_debit - total_credit
            
            result['income_statement'] = {
                'revenue': income,
                'expenses': expense,
                'net_income': income - expense
            }
            
            # الأصول والخصوم
            asset_accounts = self._execute(
                'account.account',
                'search_read',
                [('internal_group', '=', 'asset')] + domain,
                {'fields': ['code', 'name']}
            )
            
            liability_accounts = self._execute(
                'account.account',
                'search_read',
                [('internal_group', '=', 'liability')] + domain,
                {'fields': ['code', 'name']}
            )
            
            equity_accounts = self._execute(
                'account.account',
                'search_read',
                [('internal_group', '=', 'equity')] + domain,
                {'fields': ['code', 'name']}
            )
            
            result['balance_sheet'] = {
                'assets': asset_accounts,
                'liabilities': liability_accounts,
                'equity': equity_accounts
            }
            
            return result
            
        except Exception as e:
            print(f"خطأ في جلب القوائم المالية: {str(e)}")
            return {'income_statement': {}, 'balance_sheet': {}, 'cash_flow': []}
    
    # ==================== جلب الفواتير ====================
    
    def get_invoices(
        self,
        invoice_type: str = 'out_invoice',
        state: str = 'posted',
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 500
    ) -> List[Dict]:
        """
        جلب الفواتير
        
        Args:
            invoice_type: نوع الفاتورة (out_invoice, in_invoice, out_refund, in_refund)
            state: الحالة (draft, posted, cancel)
            date_from: تاريخ البدء
            date_to: تاريخ الانتهاء
            
        Returns:
            List[Dict]: قائمة الفواتير
        """
        domain = [
            ('move_type', '=', invoice_type),
            ('state', '=', state)
        ]
        
        if date_from:
            domain.append(('invoice_date', '>=', date_from))
        if date_to:
            domain.append(('invoice_date', '<=', date_to))
        
        try:
            invoice_ids = self._execute(
                'account.move',
                'search',
                domain,
                {'limit': limit}
            )
            
            if not invoice_ids:
                return []
            
            fields = [
                'id', 'name', 'invoice_date', 'invoice_date_due',
                'amount_total', 'amount_untaxed', 'amount_tax',
                'partner_id', 'state', 'payment_state',
                'currency_id', 'invoice_line_ids'
            ]
            
            invoices = self._execute(
                'account.move',
                'read',
                invoice_ids,
                {'fields': fields}
            )
            
            result = []
            for inv in invoices:
                result.append({
                    'id': inv['id'],
                    'number': inv.get('name', ''),
                    'date': inv.get('invoice_date', ''),
                    'due_date': inv.get('invoice_date_due', ''),
                    'partner_id': inv.get('partner_id', [False, ''])[1] if inv.get('partner_id') else '',
                    'partner_name': inv.get('partner_id', [False, ''])[0] if inv.get('partner_id') else '',
                    'amount_untaxed': inv.get('amount_untaxed', 0),
                    'amount_tax': inv.get('amount_tax', 0),
                    'amount_total': inv.get('amount_total', 0),
                    'currency': inv.get('currency_id', [False, ''])[1] if inv.get('currency_id') else 'USD',
                    'state': inv.get('state', 'draft'),
                    'payment_state': inv.get('payment_state', 'not_paid')
                })
            
            return result
            
        except Exception as e:
            print(f"خطأ في جلب الفواتير: {str(e)}")
            return []
    
    # ==================== جلب الشركاء (العملاء/الموردين) ====================
    
    def get_partners(
        self,
        partner_type: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """
        جلب الشركاء (عملاء وموردين)
        
        Args:
            partner_type: النوع (customer, supplier, all)
            limit: الحد الأقصى
            
        Returns:
            List[Dict]: قائمة الشركاء
        """
        domain = []
        
        if partner_type == 'customer':
            domain.append(('customer_rank', '>', 0))
        elif partner_type == 'supplier':
            domain.append(('supplier_rank', '>', 0))
        
        try:
            partners = self._execute(
                'res.partner',
                'search_read',
                domain,
                {
                    'fields': [
                        'id', 'name', 'ref', 'vat', 'email', 'phone',
                        'customer_rank', 'supplier_rank', 'property_account_receivable_id',
                        'property_account_payable_id', 'credit_limit'
                    ],
                    'limit': limit
                }
            )
            
            result = []
            for p in partners:
                result.append({
                    'id': p['id'],
                    'name': p.get('name', ''),
                    'reference': p.get('ref', ''),
                    'vat': p.get('vat', ''),
                    'email': p.get('email', ''),
                    'phone': p.get('phone', ''),
                    'is_customer': p.get('customer_rank', 0) > 0,
                    'is_supplier': p.get('supplier_rank', 0) > 0,
                    'credit_limit': p.get('credit_limit', 0)
                })
            
            return result
            
        except Exception as e:
            print(f"خطأ في جلب الشركاء: {str(e)}")
            return []
    
    # ==================== جلب المنتجات والمخزون ====================
    
    def get_products_inventory(self, limit: int = 1000) -> List[Dict]:
        """
        جلب المنتجات وأرصدة المخزون
        
        Returns:
            List[Dict]: قائمة المنتجات مع المخزون
        """
        try:
            products = self._execute(
                'product.product',
                'search_read',
                [],
                {
                    'fields': [
                        'id', 'name', 'default_code', 'categ_id',
                        'list_price', 'standard_price', 'qty_available',
                        'virtual_available', 'incoming_qty', 'outgoing_qty'
                    ],
                    'limit': limit
                }
            )
            
            result = []
            for prod in products:
                result.append({
                    'id': prod['id'],
                    'name': prod.get('name', ''),
                    'code': prod.get('default_code', ''),
                    'category': prod.get('categ_id', [False, ''])[1] if prod.get('categ_id') else '',
                    'sale_price': prod.get('list_price', 0),
                    'cost_price': prod.get('standard_price', 0),
                    'qty_on_hand': prod.get('qty_available', 0),
                    'qty_forecast': prod.get('virtual_available', 0),
                    'qty_incoming': prod.get('incoming_qty', 0),
                    'qty_outgoing': prod.get('outgoing_qty', 0)
                })
            
            return result
            
        except Exception as e:
            print(f"خطأ في جلب المخزون: {str(e)}")
            return []
    
    # ==================== جلب الأصول الثابتة ====================
    
    def get_fixed_assets(self) -> List[Dict]:
        """
        جلب الأصول الثابتة
        
        Returns:
            List[Dict]: قائمة الأصول
        """
        try:
            # التحقق من وجود وحدة الأصول الثابتة
            modules = self._execute(
                'ir.module.module',
                'search_read',
                [('name', '=', 'account_asset'), ('state', '=', 'installed')],
                {'fields': ['name']}
            )
            
            if not modules:
                print("وحدة الأصول الثابتة غير مثبتة")
                return []
            
            assets = self._execute(
                'account.asset',
                'search_read',
                [],
                {
                    'fields': [
                        'id', 'name', 'code', 'purchase_value', 'depreciated_value',
                        'remaining_value', 'method_time', 'method_number',
                        'method_period', 'date', 'profile_id', 'state'
                    ]
                }
            )
            
            result = []
            for asset in assets:
                result.append({
                    'id': asset['id'],
                    'name': asset.get('name', ''),
                    'code': asset.get('code', ''),
                    'purchase_value': asset.get('purchase_value', 0),
                    'depreciated_value': asset.get('depreciated_value', 0),
                    'remaining_value': asset.get('remaining_value', 0),
                    'depreciation_method': asset.get('method_time', 'year'),
                    'depreciation_years': asset.get('method_number', 0),
                    'depreciation_period': asset.get('method_period', 'month'),
                    'acquisition_date': asset.get('date', ''),
                    'state': asset.get('state', 'draft')
                })
            
            return result
            
        except Exception as e:
            print(f"خطأ في جلب الأصول الثابتة: {str(e)}")
            return []
    
    # ==================== المزامنة الذكية ====================
    
    def sync_incremental(
        self,
        last_sync: Optional[datetime] = None,
        models: Optional[List[str]] = None
    ) -> Dict[str, int]:
        """
        مزامنة تزايديّة
        
        Args:
            last_sync: آخر توقيت مزامنة
            models: النماذج المطلوب مزامنتها
            
        Returns:
            Dict: عدد السجلات المزامنة لكل نموذج
        """
        if models is None:
            models = ['account.move', 'account.move.line', 'res.partner', 'product.product']
        
        synced = {}
        
        for model in models:
            domain = []
            
            if last_sync:
                # افتراض وجود حقل write_date
                domain.append(('write_date', '>=', last_sync.strftime('%Y-%m-%d %H:%M:%S')))
            
            try:
                ids = self._execute(
                    model,
                    'search',
                    domain
                )
                
                synced[model] = len(ids) if ids else 0
                
            except Exception as e:
                print(f"خطأ في مزامنة {model}: {str(e)}")
                synced[model] = 0
        
        self.last_sync = datetime.now()
        return synced
    
    # ==================== معلومات النظام ====================
    
    def get_system_info(self) -> Dict:
        """
        جلب معلومات النظام
        
        Returns:
            Dict: معلومات Odoo
        """
        try:
            # إصدار Odoo
            version_info = self._execute(
                'ir.config_parameter',
                'search_read',
                [('key', '=', 'database.uuid')],
                {'fields': ['key', 'value']}
            )
            
            # اسم الشركة
            company = self._execute(
                'res.company',
                'search_read',
                [],
                {'fields': ['name', 'currency_id', 'country_id'], 'limit': 1}
            )
            
            # عدد المستخدمين
            users_count = self._execute(
                'res.users',
                'search_count',
                []
            )
            
            return {
                'erp_type': 'Odoo',
                'version': self.version,
                'url': self.url,
                'database': self.db,
                'company_name': company[0].get('name', '') if company else '',
                'currency': company[0].get('currency_id', [False, ''])[1] if company and company[0].get('currency_id') else '',
                'users_count': users_count,
                'connected': self.connected,
                'last_sync': self.last_sync.isoformat() if self.last_sync else None
            }
            
        except Exception as e:
            print(f"خطأ في جلب معلومات النظام: {str(e)}")
            return {'error': str(e), 'connected': False}
    
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
            if not self.connect():
                result['message'] = 'فشل الاتصال'
                return result
            
            info = self.get_system_info()
            
            result['success'] = True
            result['message'] = 'اتصال ناجح'
            result['details'] = info
            
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

def create_odoo_connector(config: Dict[str, Any]) -> OdooConnector:
    """
    إنشاء موصل Odoo
    
    Args:
        config: إعدادات الاتصال
        
    Returns:
        OdooConnector: موصل جاهز
    """
    connector = OdooConnector(config)
    connector.connect()
    return connector

