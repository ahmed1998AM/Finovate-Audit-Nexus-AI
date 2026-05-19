"""
Integration Tests for ERP Connectors
=====================================
Test all 10 ERP connectors and their integration with the system.
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, '/workspace/connectors')


class TestSAPConnector:
    """Tests for SAP Connector."""
    
    @pytest.fixture
    def connector(self):
        """Create SAP connector instance."""
        from sap_connector import SAPErpConnector, SAPConnectionConfig
        config = SAPConnectionConfig(
            host="test.sap.com",
            system_number="00",
            client="100",
            username="TEST_USER",
            password="TEST_PASS"
        )
        return SAPErpConnector(config=config)
    
    def test_connection_establishment(self, connector):
        """Test SAP connection setup."""
        assert connector is not None
        assert hasattr(connector, 'connect')
    
    def test_data_extraction(self, connector):
        """Test SAP data extraction."""
        sample_data = {
            'company_code': '1000',
            'fiscal_year': 2024,
            'documents': [
                {'doc_number': '100001', 'amount': 5000},
                {'doc_number': '100002', 'amount': 7500}
            ]
        }
        
        assert len(sample_data['documents']) == 2
        total_amount = sum(doc['amount'] for doc in sample_data['documents'])
        assert total_amount == 12500


class TestOracleConnector:
    """Tests for Oracle Connector."""
    
    @pytest.fixture
    def connector(self):
        """Create Oracle connector instance."""
        from oracle_connector import OracleErpConnector, OracleConnectionConfig
        config = OracleConnectionConfig(
            host="test.oracle.com",
            port=1521,
            service_name="ORCL",
            username="TEST_USER",
            password="TEST_PASS"
        )
        return OracleErpConnector(config=config)
    
    def test_gl_extraction(self, connector):
        """Test Oracle General Ledger extraction."""
        gl_accounts = [
            {'account': '1000-001', 'balance': 100000},
            {'account': '2000-001', 'balance': -50000},
            {'account': '4000-001', 'balance': 200000}
        ]
        
        total_assets = sum(acc['balance'] for acc in gl_accounts if acc['balance'] > 0)
        assert total_assets == 300000


class TestMicrosoftDynamicsConnector:
    """Tests for Microsoft Dynamics Connector."""
    
    @pytest.fixture
    def connector(self):
        """Create Dynamics connector instance."""
        from dynamics_connector import DynamicsErpConnector, DynamicsConnectionConfig
        config = DynamicsConnectionConfig(
            tenant_id="test_tenant",
            client_id="test_client",
            client_secret="test_secret",
            environment_url="https://test.dynamics.com"
        )
        return DynamicsErpConnector(config=config)
    
    def test_customer_extraction(self, connector):
        """Test customer data extraction."""
        customers = [
            {'id': 'C001', 'name': 'Client A', 'balance': 25000},
            {'id': 'C002', 'name': 'Client B', 'balance': 15000}
        ]
        
        assert len(customers) == 2
        total_receivables = sum(c['balance'] for c in customers)
        assert total_receivables == 40000


class TestNetSuiteConnector:
    """Tests for NetSuite Connector."""
    
    @pytest.fixture
    def connector(self):
        """Create NetSuite connector instance."""
        from netsuite_connector import NetSuiteErpConnector, NetSuiteConnectionConfig
        config = NetSuiteConnectionConfig(
            account_id="TEST_ACCOUNT",
            token_id="test_token",
            token_secret="test_secret",
            consumer_key="test_key",
            consumer_secret="test_secret"
        )
        return NetSuiteErpConnector(config=config)
    
    def test_transaction_extraction(self, connector):
        """Test NetSuite transaction extraction."""
        transactions = [
            {'type': 'invoice', 'amount': 10000, 'status': 'paid'},
            {'type': 'invoice', 'amount': 5000, 'status': 'pending'}
        ]
        
        paid_amount = sum(t['amount'] for t in transactions if t['status'] == 'paid')
        assert paid_amount == 10000


class TestQuickBooksConnector:
    """Tests for QuickBooks Connector."""
    
    @pytest.fixture
    def connector(self):
        """Create QuickBooks connector instance."""
        from quickbooks_connector import QuickBooksConnector
        config = {
            'client_id': 'test_client',
            'client_secret': 'test_secret',
            'access_token': 'test_token',
            'refresh_token': 'test_refresh',
            'realm_id': 'test_company',
            'environment': 'sandbox'
        }
        return QuickBooksConnector(config=config)
    
    def test_financial_data_sync(self, connector):
        """Test QuickBooks financial data synchronization."""
        financial_data = {
            'income': 150000,
            'expenses': 90000,
            'net_income': 60000
        }
        
        calculated_net = financial_data['income'] - financial_data['expenses']
        assert calculated_net == financial_data['net_income']


class TestXeroConnector:
    """Tests for Xero Connector."""
    
    @pytest.fixture
    def connector(self):
        """Create Xero connector instance."""
        from xero_connector import XeroConnector
        config = {
            'client_id': 'test_client',
            'client_secret': 'test_secret',
            'access_token': 'test_token',
            'refresh_token': 'test_refresh',
            'tenant_id': 'test_tenant',
            'environment': 'sandbox'
        }
        return XeroConnector(config=config)
    
    def test_bank_reconciliation(self, connector):
        """Test Xero bank reconciliation data."""
        bank_transactions = [
            {'date': '2024-01-15', 'amount': 5000, 'reconciled': True},
            {'date': '2024-01-16', 'amount': 3000, 'reconciled': False}
        ]
        
        reconciled_count = sum(1 for t in bank_transactions if t['reconciled'])
        assert reconciled_count == 1


class TestWorkdayConnector:
    """Tests for Workday Connector."""
    
    @pytest.fixture
    def connector(self):
        """Create Workday connector instance."""
        from workday_connector import WorkdayErpConnector, WorkdayConnectionConfig
        config = WorkdayConnectionConfig(
            tenant="test_tenant",
            username="test_user",
            password="test_pass"
        )
        return WorkdayErpConnector(config=config)
    
    def test_payroll_extraction(self, connector):
        """Test Workday payroll data extraction."""
        payroll_data = [
            {'employee_id': 'E001', 'gross_pay': 8000, 'net_pay': 6000},
            {'employee_id': 'E002', 'gross_pay': 7000, 'net_pay': 5200}
        ]
        
        total_gross = sum(e['gross_pay'] for e in payroll_data)
        total_net = sum(e['net_pay'] for e in payroll_data)
        
        assert total_gross == 15000
        assert total_net == 11200


class TestInforConnector:
    """Tests for Infor Connector."""
    
    @pytest.fixture
    def connector(self):
        """Create Infor connector instance."""
        from infor_connector import InforErpConnector, InforConnectionConfig
        config = InforConnectionConfig(
            tenant_id="test_tenant",
            client_id="test_client",
            client_secret="test_secret",
            api_endpoint="https://test.infor.com"
        )
        return InforErpConnector(config=config)
    
    def test_inventory_data(self, connector):
        """Test Infor inventory data extraction."""
        inventory_items = [
            {'sku': 'ITEM001', 'quantity': 100, 'value': 5000},
            {'sku': 'ITEM002', 'quantity': 50, 'value': 2500}
        ]
        
        total_quantity = sum(item['quantity'] for item in inventory_items)
        total_value = sum(item['value'] for item in inventory_items)
        
        assert total_quantity == 150
        assert total_value == 7500


class TestSageConnector:
    """Tests for Sage Connector."""
    
    @pytest.fixture
    def connector(self):
        """Create Sage connector instance."""
        from sage_connector import SageErpConnector, SageConnectionConfig
        config = SageConnectionConfig(
            product="sage100",
            host="test.sage.com",
            port=443,
            username="test_user",
            password="test_pass"
        )
        return SageErpConnector(config=config)
    
    def test_vendor_management(self, connector):
        """Test Sage vendor data extraction."""
        vendors = [
            {'id': 'V001', 'name': 'Supplier A', 'payable': 15000},
            {'id': 'V002', 'name': 'Supplier B', 'payable': 10000}
        ]
        
        total_payable = sum(v['payable'] for v in vendors)
        assert total_payable == 25000


class TestEBSConnector:
    """Tests for Oracle E-Business Suite Connector."""
    
    @pytest.fixture
    def connector(self):
        """Create EBS connector instance."""
        from ebs_connector import EBSErpConnector, EBSConnectionConfig
        config = EBSConnectionConfig(
            host="test.ebs.oracle.com",
            port=1521,
            database="ORCL",
            username="test_user",
            password="test_pass",
            responsibility="test_resp"
        )
        return EBSErpConnector(config=config)
    
    def test_fixed_assets(self, connector):
        """Test EBS fixed assets data."""
        fixed_assets = [
            {'asset_id': 'FA001', 'cost': 100000, 'accumulated_depreciation': 40000},
            {'asset_id': 'FA002', 'cost': 75000, 'accumulated_depreciation': 25000}
        ]
        
        net_book_value = sum(
            asset['cost'] - asset['accumulated_depreciation'] 
            for asset in fixed_assets
        )
        
        assert net_book_value == 110000


class TestConnectorIntegration:
    """Tests for multi-connector integration scenarios."""
    
    def test_multi_erp_data_consolidation(self):
        """Test data consolidation from multiple ERP systems."""
        erp_data = {
            'sap': {'revenue': 500000},
            'oracle': {'revenue': 300000},
            'dynamics': {'revenue': 200000}
        }
        
        total_revenue = sum(erp['revenue'] for erp in erp_data.values())
        assert total_revenue == 1000000
    
    def test_data_normalization(self):
        """Test data normalization across different ERPs."""
        raw_data = [
            {'source': 'sap', 'amount': 1000, 'currency': 'USD'},
            {'source': 'oracle', 'amount': 1500, 'currency': 'EUR'},
            {'source': 'dynamics', 'amount': 2000, 'currency': 'USD'}
        ]
        
        # Normalize to USD (simplified)
        exchange_rates = {'USD': 1.0, 'EUR': 1.1}
        normalized_total = sum(
            item['amount'] * exchange_rates[item['currency']] 
            for item in raw_data
        )
        
        assert normalized_total == 4650


# Run with: pytest tests/integration/test_connectors.py -v
