"""
Finovate Audit Nexus AI - Connector Integration Tests
اختبارات تكامل الموصلات
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestConnectorFactories:
    def test_all_factories_exist(self):
        from connectors import __all__
        factory_names = [n for n in __all__ if n.startswith("create_")]
        assert len(factory_names) == 15, f"Expected 15 factories, got {len(factory_names)}"
        expected = [
            "create_api_connector", "create_dynamics_connector", "create_ebs_connector",
            "create_excel_connector", "create_infor_connector", "create_netsuite_connector",
            "create_odoo_connector", "create_oracle_connector", "create_quickbooks_connector",
            "create_sage_connector", "create_sap_connector", "create_sql_connector",
            "create_workday_connector", "create_xero_connector", "create_zoho_connector",
        ]
        for name in expected:
            assert name in factory_names, f"Missing factory: {name}"

    def test_all_connector_classes_exist(self):
        from connectors import __all__
        class_names = [n for n in __all__ if not n.startswith("create_")]
        assert len(class_names) == 15, f"Expected 15 classes, got {len(class_names)}"

    def test_all_connectors_inherit_base(self):
        from connectors.base_connector import BaseERPConnector
        from connectors import __all__
        import connectors as conn_pkg
        for name in __all__:
            if name.startswith("create_") or name == "BaseERPConnector":
                continue
            cls = getattr(conn_pkg, name)
            assert issubclass(cls, BaseERPConnector), f"{name} does not inherit BaseERPConnector"


class TestConnectorBase:
    def test_base_has_required_abstract_methods(self):
        from connectors.base_connector import BaseERPConnector
        methods = ["connect", "disconnect", "test_connection"]
        for m in methods:
            assert hasattr(BaseERPConnector, m), f"Missing method: {m}"

    def test_base_has_optional_data_methods(self):
        from connectors.base_connector import BaseERPConnector
        methods = ["get_journal_entries", "get_trial_balance",
                   "get_financial_statements", "get_accounts",
                   "get_system_info", "get_health_status"]
        for m in methods:
            assert hasattr(BaseERPConnector, m), f"Missing method: {m}"

    def test_base_is_connected_property(self):
        from connectors.base_connector import BaseERPConnector
        assert isinstance(BaseERPConnector.is_connected, property), "is_connected must be @property"


class TestSAPConnector:
    def test_create_sap_connector(self):
        from connectors import create_sap_connector, SAPErpConnector
        conn = create_sap_connector({"host": "test", "client": "800"})
        assert isinstance(conn, SAPErpConnector)

    def test_sap_test_connection_no_creds(self):
        from connectors import create_sap_connector
        conn = create_sap_connector({"host": "nonexistent"})
        result = conn.test_connection()
        assert isinstance(result, dict)
        assert "status" in result


class TestExcelConnector:
    def test_create_excel_connector(self):
        from connectors import create_excel_connector, ExcelConnector
        conn = create_excel_connector({"file_path": "test.xlsx"})
        assert isinstance(conn, ExcelConnector)

    def test_excel_test_connection(self):
        from connectors import create_excel_connector
        conn = create_excel_connector({"file_path": "nofile.xlsx"})
        result = conn.test_connection()
        assert isinstance(result, dict)


class TestAPIConnector:
    def test_create_api_connector(self):
        from connectors import create_api_connector, APIConnector
        conn = create_api_connector({"base_url": "https://api.test.com"})
        assert isinstance(conn, APIConnector)

    def test_api_connect_invalid(self):
        from connectors import create_api_connector
        conn = create_api_connector({"base_url": "https://nonexistent.api.test"})
        result = conn.test_connection()
        assert isinstance(result, dict)


class TestConnectorMockTests:
    """Mock-based tests for connectors to avoid external dependencies."""
    
    @patch('connectors.odoo_connector.connector.xmlrpclib.ServerProxy')
    def test_odoo_connector_mock(self, mock_server):
        """Test Odoo connector with mocked XML-RPC."""
        from connectors import create_odoo_connector
        
        # Mock the XML-RPC server
        mock_server.return_value = MagicMock()
        
        conn = create_odoo_connector({
            "url": "http://test.odoo.com",
            "db": "test_db",
            "username": "admin",
            "password": "admin"
        })
        
        result = conn.test_connection()
        assert isinstance(result, dict)
        assert "status" in result
    
    @patch('connectors.oracle_connector.connector.oracledb')
    def test_oracle_connector_mock(self, mock_oracledb):
        """Test Oracle connector with mocked oracledb."""
        from connectors import create_oracle_connector
        
        # Mock oracledb connection
        mock_conn = MagicMock()
        mock_oracledb.connect.return_value = mock_conn
        
        conn = create_oracle_connector({
            "user": "test",
            "password": "test",
            "dsn": "localhost:1521/XE"
        })
        
        result = conn.test_connection()
        assert isinstance(result, dict)
        assert "status" in result
    
    @patch('connectors.sap_connector.connector.pyrfc')
    def test_sap_connector_mock(self, mock_pyrfc):
        """Test SAP connector with mocked pyrfc."""
        from connectors import create_sap_connector
        
        # Mock pyrfc connection
        mock_conn = MagicMock()
        mock_pyrfc.Connection.return_value = mock_conn
        
        conn = create_sap_connector({
            "ashost": "test.sap.com",
            "sysnr": "00",
            "client": "800",
            "user": "test",
            "passwd": "test"
        })
        
        result = conn.test_connection()
        assert isinstance(result, dict)
        assert "status" in result
    
    def test_sql_connector_mock(self):
        """Test SQL connector with mocked database."""
        from connectors import create_sql_connector
        from unittest.mock import patch
        
        with patch('connectors.sql_connector.connector.create_engine') as mock_engine:
            mock_conn = MagicMock()
            mock_engine.return_value.connect.return_value = mock_conn
            
            conn = create_sql_connector({
                "connection_string": "sqlite:///test.db"
            })
            
            result = conn.test_connection()
            assert isinstance(result, dict)
            assert "status" in result
    
    def test_connector_data_retrieval_mock(self):
        """Test data retrieval methods with mocked connectors."""
        from connectors.base_connector import BaseERPConnector
        
        # Create a mock connector
        class MockConnector(BaseERPConnector):
            def __init__(self):
                self._connected = True
            
            def connect(self):
                return {"status": "connected"}
            
            def disconnect(self):
                self._connected = False
            
            def test_connection(self):
                return {"status": "connected" if self._connected else "disconnected"}
            
            def get_journal_entries(self, **kwargs):
                return pd.DataFrame([
                    {"id": 1, "account": "Cash", "debit": 1000, "credit": 0},
                    {"id": 2, "account": "Revenue", "debit": 0, "credit": 1000},
                ])
            
            def get_trial_balance(self, **kwargs):
                return pd.DataFrame([
                    {"account": "Cash", "debit": 1000, "credit": 0},
                    {"account": "Revenue", "debit": 0, "credit": 1000},
                ])
        
        conn = MockConnector()
        
        # Test connection
        assert conn.test_connection()["status"] == "connected"
        
        # Test data retrieval
        journal = conn.get_journal_entries()
        assert isinstance(journal, pd.DataFrame)
        assert len(journal) == 2
        
        tb = conn.get_trial_balance()
        assert isinstance(tb, pd.DataFrame)
        assert len(tb) == 2
    
    def test_connector_error_handling_mock(self):
        """Test connector error handling with mock."""
        from connectors.base_connector import BaseERPConnector
        
        class ErrorConnector(BaseERPConnector):
            def __init__(self):
                self._connected = False
            
            def connect(self):
                raise Exception("Connection failed")
            
            def disconnect(self):
                pass
            
            def test_connection(self):
                try:
                    return self.connect()
                except Exception as e:
                    return {"status": "error", "message": str(e)}
        
        conn = ErrorConnector()
        result = conn.test_connection()
        assert result["status"] == "error"
        assert "Connection failed" in result["message"]


class TestSQLConnector:
    def test_create_sql_connector(self):
        from connectors import create_sql_connector, SQLConnector
        conn = create_sql_connector({"connection_string": "sqlite:///:memory:"})
        assert isinstance(conn, SQLConnector)

    def test_sql_connect_invalid(self):
        from connectors import create_sql_connector
        conn = create_sql_connector({"connection_string": "invalid://bad"})
        result = conn.test_connection()
        assert isinstance(result, dict)
        assert "error" in result or "connected" in result


class TestConnectorService:
    def test_connector_service_imports(self):
        from backend.services.connector_service import ConnectorService
        service = ConnectorService()
        types = service.get_available_types()
        assert isinstance(types, list)
        assert len(types) >= 15, f"Expected 15+ types, got {len(types)}"

    def test_connector_service_all_types_listed(self):
        from backend.services.connector_service import ConnectorService
        service = ConnectorService()
        types = service.get_available_types()
        type_names = [t["type"].lower() for t in types]
        expected = {"sap", "odoo", "xero", "quickbooks", "zoho", "dynamics",
                    "oracle", "excel", "sql", "api", "ebs", "infor", "netsuite", "sage", "workday"}
        for e in expected:
            assert e in type_names, f"Missing type: {e} in {type_names}"


class TestOtherConnectors:
    def test_create_odoo_connector(self):
        from connectors import create_odoo_connector, OdooConnector
        conn = create_odoo_connector({"host": "localhost", "database": "test"})
        assert isinstance(conn, OdooConnector)

    def test_create_xero_connector(self):
        from connectors import create_xero_connector, XeroConnector
        conn = create_xero_connector({"client_id": "test", "client_secret": "secret"})
        assert isinstance(conn, XeroConnector)

    def test_create_dynamics_connector(self):
        from connectors import create_dynamics_connector, DynamicsErpConnector
        conn = create_dynamics_connector({"tenant_id": "test", "client_id": "test"})
        assert isinstance(conn, DynamicsErpConnector)

    def test_create_oracle_connector(self):
        from connectors import create_oracle_connector, OracleErpConnector
        conn = create_oracle_connector({"host": "localhost", "port": 1521})
        assert isinstance(conn, OracleErpConnector)
