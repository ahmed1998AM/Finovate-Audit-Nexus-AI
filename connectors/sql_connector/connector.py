"""
Finovate Audit Nexus AI - SQL Database Connector
موصل قواعد البيانات SQL للربط المباشر مع الأنظمة المحاسبية
"""

import pandas as pd
import sqlite3
from typing import Dict, List, Any, Optional, Generator
from datetime import datetime
import os


class SQLConnector:
    """
    موصل قواعد البيانات SQL
    يدعم PostgreSQL, MySQL, SQL Server, SQLite
    للربط المباشر مع الأنظمة المحاسبية
    """
    
    def __init__(self, connection_string: Optional[str] = None, db_type: str = 'sqlite'):
        """
        Args:
            connection_string: سلسلة الاتصال بقاعدة البيانات
            db_type: نوع قاعدة البيانات (sqlite, postgresql, mysql, sqlserver)
        """
        self.connection_string = connection_string
        self.db_type = db_type
        self.connection = None
        self.cursor = None
        
    def connect_sqlite(self, db_path: str) -> bool:
        """الاتصال بقاعدة بيانات SQLite"""
        try:
            if not os.path.exists(db_path):
                print(f"Warning: Database file '{db_path}' does not exist. Will create new one.")
                
            self.connection = sqlite3.connect(db_path)
            self.cursor = self.connection.cursor()
            self.db_type = 'sqlite'
            return True
        except Exception as e:
            print(f"Error connecting to SQLite: {e}")
            return False
            
    def connect_postgresql(self, host: str, port: int, database: str, 
                          user: str, password: str) -> bool:
        """الاتصال بقاعدة بيانات PostgreSQL"""
        try:
            import psycopg2
            self.connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
            self.connection = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            self.cursor = self.connection.cursor()
            self.db_type = 'postgresql'
            return True
        except ImportError:
            print("Error: psycopg2 not installed. Run: pip install psycopg2-binary")
            return False
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            return False
            
    def connect_mysql(self, host: str, port: int, database: str,
                     user: str, password: str) -> bool:
        """الاتصال بقاعدة بيانات MySQL"""
        try:
            import pymysql
            self.connection = pymysql.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            self.cursor = self.connection.cursor()
            self.db_type = 'mysql'
            return True
        except ImportError:
            print("Error: pymysql not installed. Run: pip install pymysql")
            return False
        except Exception as e:
            print(f"Error connecting to MySQL: {e}")
            return False
            
    def execute_query(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        """
        تنفيذ استعلام SQL وإرجاع النتائج كـ DataFrame
        
        Args:
            query: استعلام SQL
            params: معاملات الاستعلام
            
        Returns:
            DataFrame يحتوي على نتائج الاستعلام
        """
        if not self.connection:
            raise Exception("No active database connection")
            
        try:
            if params:
                df = pd.read_sql_query(query, self.connection, params=params)
            else:
                df = pd.read_sql_query(query, self.connection)
            return df
        except Exception as e:
            print(f"Error executing query: {e}")
            return pd.DataFrame()
            
    def read_journal_entries(self, table_name: str = 'journal_entries',
                            limit: int = 1000) -> pd.DataFrame:
        """قراءة قيود اليومية من قاعدة البيانات"""
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return self.execute_query(query)
        
    def read_general_ledger(self, table_name: str = 'general_ledger',
                           account_code: Optional[str] = None,
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> pd.DataFrame:
        """قراءة دفتر الأستاذ مع فلترة اختيارية"""
        conditions = []
        
        if account_code:
            conditions.append(f"account_code = '{account_code}'")
        if start_date:
            conditions.append(f"transaction_date >= '{start_date}'")
        if end_date:
            conditions.append(f"transaction_date <= '{end_date}'")
            
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"SELECT * FROM {table_name}{where_clause} ORDER BY transaction_date"
        return self.execute_query(query)
        
    def read_trial_balance(self, table_name: str = 'trial_balance',
                          period: Optional[str] = None) -> pd.DataFrame:
        """قراءة ميزان المراجعة"""
        if period:
            query = f"SELECT * FROM {table_name} WHERE period = '{period}'"
        else:
            query = f"SELECT * FROM {table_name}"
        return self.execute_query(query)
        
    def read_chart_of_accounts(self, table_name: str = 'chart_of_accounts') -> pd.DataFrame:
        """قراءة دليل الحسابات"""
        query = f"SELECT * FROM {table_name} ORDER BY account_code"
        return self.execute_query(query)
        
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """الحصول على هيكل الجدول"""
        if self.db_type == 'sqlite':
            query = f"PRAGMA table_info({table_name})"
        elif self.db_type == 'postgresql':
            query = f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = '{table_name.lower()}'
            """
        elif self.db_type == 'mysql':
            query = f"DESCRIBE {table_name}"
        else:
            raise Exception(f"Unsupported database type: {self.db_type}")
            
        schema_df = self.execute_query(query)
        
        return {
            'table_name': table_name,
            'columns': schema_df.to_dict('records') if not schema_df.empty else [],
            'row_count': self.get_table_row_count(table_name)
        }
        
    def get_table_row_count(self, table_name: str) -> int:
        """الحصول على عدد الصفوف في الجدول"""
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.execute_query(query)
        if not result.empty:
            return result['count'].iloc[0]
        return 0
        
    def list_tables(self) -> List[str]:
        """سرد جميع الجداول في قاعدة البيانات"""
        if self.db_type == 'sqlite':
            query = "SELECT name FROM sqlite_master WHERE type='table'"
        elif self.db_type == 'postgresql':
            query = """
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
            """
        elif self.db_type == 'mysql':
            query = "SHOW TABLES"
        else:
            raise Exception(f"Unsupported database type: {self.db_type}")
            
        tables_df = self.execute_query(query)
        if tables_df.empty:
            return []
            
        # الحصول على اسم العمود الصحيح
        column_name = tables_df.columns[0]
        return tables_df[column_name].tolist()
        
    def test_connection(self) -> Dict[str, Any]:
        """اختبار الاتصال بقاعدة البيانات"""
        result = {
            'connected': False,
            'db_type': self.db_type,
            'tables_count': 0,
            'tables': [],
            'error': None
        }
        
        try:
            if not self.connection:
                result['error'] = "No active connection"
                return result
                
            # اختبار بسيط
            if self.db_type == 'sqlite':
                test_query = "SELECT 1"
            else:
                test_query = "SELECT 1"
                
            self.execute_query(test_query)
            
            result['connected'] = True
            result['tables'] = self.list_tables()
            result['tables_count'] = len(result['tables'])
            
        except Exception as e:
            result['error'] = str(e)
            
        return result
        
    def export_to_excel(self, query: str, output_path: str) -> str:
        """تصدير نتائج استعلام إلى Excel"""
        df = self.execute_query(query)
        if not df.empty:
            df.to_excel(output_path, index=False)
            return output_path
        else:
            raise Exception("Query returned no results")
            
    def close(self):
        """إغلاق الاتصال بقاعدة البيانات"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def get_journal_entries(self, table_name: str = 'journal_entries',
                            date_from: Optional[str] = None,
                            date_to: Optional[str] = None,
                            account_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        استخراج قيود اليومية من قاعدة البيانات
        
        Args:
            table_name: اسم الجدول
            date_from: تاريخ البدء (اختياري)
            date_to: تاريخ الانتهاء (اختياري)
            account_code: كود الحساب (اختياري)
            
        Returns:
            قائمة بقيود اليومية
        """
        conditions = []
        
        if date_from:
            conditions.append(f"date >= '{date_from}'")
        if date_to:
            conditions.append(f"date <= '{date_to}'")
        if account_code:
            conditions.append(f"account_code = '{account_code}'")
        
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"SELECT * FROM {table_name}{where_clause} ORDER BY date"
        
        df = self.execute_query(query)
        
        entries = []
        for _, row in df.iterrows():
            entry = {
                'id': row.get('id', row.get('reference', '')),
                'date': row.get('date', row.get('transaction_date', '')),
                'account_code': row.get('account_code', ''),
                'account_name': row.get('account_name', ''),
                'description': row.get('description', row.get('narration', '')),
                'debit': float(row.get('debit', 0)),
                'credit': float(row.get('credit', 0)),
                'balance': float(row.get('balance', 0)),
                'currency': row.get('currency', 'USD'),
                'reference': row.get('reference', ''),
                'cost_center': row.get('cost_center', ''),
                'project': row.get('project', '')
            }
            entries.append(entry)
        
        return entries
    
    def get_trial_balance(self, table_name: str = 'trial_balance',
                          period: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        استخراج ميزان المراجعة من قاعدة البيانات
        
        Args:
            table_name: اسم الجدول
            period: الفترة (اختياري)
            
        Returns:
            قائمة بحسابات ميزان المراجعة
        """
        df = self.read_trial_balance(table_name, period)
        
        accounts = []
        for _, row in df.iterrows():
            account = {
                'account_code': row.get('account_code', ''),
                'account_name': row.get('account_name', ''),
                'opening_debit': float(row.get('opening_debit', 0)),
                'opening_credit': float(row.get('opening_credit', 0)),
                'period_debit': float(row.get('period_debit', 0)),
                'period_credit': float(row.get('period_credit', 0)),
                'closing_debit': float(row.get('closing_debit', 0)),
                'closing_credit': float(row.get('closing_credit', 0)),
                'account_type': row.get('account_type', ''),
                'parent_account': row.get('parent_account', '')
            }
            accounts.append(account)
        
        return accounts
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def create_sample_database(db_path: str) -> str:
    """إنشاء قاعدة بيانات تجريبية للتدقيق"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # إنشاء جدول دليل الحسابات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chart_of_accounts (
            account_code TEXT PRIMARY KEY,
            account_name TEXT,
            account_type TEXT,
            parent_account TEXT,
            balance_type TEXT
        )
    ''')
    
    # إنشاء جدول قيود اليومية
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY,
            entry_date DATE,
            entry_number TEXT,
            account_code TEXT,
            description TEXT,
            debit REAL,
            credit REAL,
            user_id TEXT,
            created_at TIMESTAMP
        )
    ''')
    
    # إنشاء جدول دفتر الأستاذ
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS general_ledger (
            id INTEGER PRIMARY KEY,
            transaction_date DATE,
            entry_number TEXT,
            account_code TEXT,
            account_name TEXT,
            description TEXT,
            debit REAL,
            credit REAL,
            balance REAL
        )
    ''')
    
    # إنشاء جدول ميزان المراجعة
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trial_balance (
            id INTEGER PRIMARY KEY,
            period TEXT,
            account_code TEXT,
            account_name TEXT,
            debit_balance REAL,
            credit_balance REAL
        )
    ''')
    
    # إدراج بيانات تجريبية
    accounts = [
        ('1001', 'Cash', 'Asset', None, 'Debit'),
        ('1002', 'Accounts Receivable', 'Asset', None, 'Debit'),
        ('1003', 'Inventory', 'Asset', None, 'Debit'),
        ('2001', 'Accounts Payable', 'Liability', None, 'Credit'),
        ('2002', 'Bank Loan', 'Liability', None, 'Credit'),
        ('3001', 'Share Capital', 'Equity', None, 'Credit'),
        ('4001', 'Sales Revenue', 'Revenue', None, 'Credit'),
        ('5001', 'Cost of Goods Sold', 'Expense', None, 'Debit'),
        ('6001', 'Salaries Expense', 'Expense', None, 'Debit'),
        ('6002', 'Rent Expense', 'Expense', None, 'Debit')
    ]
    
    cursor.executemany(
        'INSERT OR REPLACE INTO chart_of_accounts VALUES (?, ?, ?, ?, ?)',
        accounts
    )
    
    # قيود يومية تجريبية
    entries = [
        (1, '2024-01-01', 'JE-001', '1001', 'Opening cash balance', 100000, 0, 'admin', '2024-01-01 10:00:00'),
        (2, '2024-01-01', 'JE-001', '3001', 'Opening cash balance', 0, 100000, 'admin', '2024-01-01 10:00:00'),
        (3, '2024-01-05', 'JE-002', '1002', 'Sale on credit', 50000, 0, 'user1', '2024-01-05 11:30:00'),
        (4, '2024-01-05', 'JE-002', '4001', 'Sale on credit', 0, 50000, 'user1', '2024-01-05 11:30:00'),
        (5, '2024-01-10', 'JE-003', '1003', 'Purchase inventory', 30000, 0, 'user2', '2024-01-10 09:15:00'),
        (6, '2024-01-10', 'JE-003', '2001', 'Purchase inventory', 0, 30000, 'user2', '2024-01-10 09:15:00'),
        (7, '2024-01-15', 'JE-004', '6001', 'Salaries payment', 15000, 0, 'admin', '2024-01-15 14:00:00'),
        (8, '2024-01-15', 'JE-004', '1001', 'Salaries payment', 0, 15000, 'admin', '2024-01-15 14:00:00'),
        (9, '2024-01-20', 'JE-005', '1001', 'Cash collection from customer', 25000, 0, 'user1', '2024-01-20 16:45:00'),
        (10, '2024-01-20', 'JE-005', '1002', 'Cash collection from customer', 0, 25000, 'user1', '2024-01-20 16:45:00')
    ]
    
    cursor.executemany(
        '''INSERT OR REPLACE INTO journal_entries 
           (id, entry_date, entry_number, account_code, description, debit, credit, user_id, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        entries
    )
    
    conn.commit()
    conn.close()
    
    return db_path



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

if __name__ == "__main__":
    # مثال اختباري
    print("=" * 60)
    print("Finovate SQL Connector - Test")
    print("=" * 60)
    
    # إنشاء قاعدة بيانات تجريبية
    db_path = "/workspace/database/sample_audit_db.sqlite"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    create_sample_database(db_path)
    print(f"\n✅ Sample database created: {db_path}")
    
    # اختبار الاتصال
    connector = SQLConnector()
    
    if connector.connect_sqlite(db_path):
        print("✅ Connected to SQLite database")
        
        # اختبار الاتصال
        test_result = connector.test_connection()
        print(f"\n📋 Connection Test:")
        print(f"Connected: {test_result['connected']}")
        print(f"DB Type: {test_result['db_type']}")
        print(f"Tables Count: {test_result['tables_count']}")
        print(f"Tables: {test_result['tables']}")
        
        # قراءة دليل الحسابات
        print("\n📊 Chart of Accounts:")
        coa = connector.read_chart_of_accounts()
        print(coa.to_string())
        
        # قراءة قيود اليومية
        print("\n📝 Journal Entries:")
        journals = connector.read_journal_entries(limit=5)
        print(journals.to_string())
        
        # الحصول على هيكل جدول
        print("\n🏗️ Table Schema (journal_entries):")
        schema = connector.get_table_schema('journal_entries')
        print(f"Table: {schema['table_name']}")
        print(f"Row Count: {schema['row_count']}")
        print(f"Columns: {len(schema['columns'])}")
        for col in schema['columns']:
            print(f"  - {col}")
            
        # تصدير إلى Excel
        excel_path = "/workspace/exports/sql_export_test.xlsx"
        connector.export_to_excel(
            "SELECT * FROM journal_entries",
            excel_path
        )
        print(f"\n✅ Exported to Excel: {excel_path}")
        
        connector.close()
        print("\n✅ SQL Connector Test Complete!")
    else:
        print("❌ Failed to connect to database")


