"""Tests for connector loading compatibility helpers."""

from pathlib import Path

from _connector_loader import load_connector


def test_load_connector_returns_module():
    module = load_connector("connectors/sap_connector/connector.py", "sap_connector_test_impl")
    assert module is not None
    assert hasattr(module, "SAPErpConnector")
    assert hasattr(module, "SAPConnectionConfig")


def test_load_connector_raises_for_missing_file():
    missing = "connectors/not_real_connector/connector.py"
    try:
        load_connector(missing, "missing_connector_impl")
        assert False, "Expected ImportError for a missing connector module"
    except ImportError as exc:
        assert "Cannot load connector module" in str(exc)


def test_root_compatibility_module_exports_sap():
    import sap_connector

    assert hasattr(sap_connector, "SAPErpConnector")
    assert hasattr(sap_connector, "SAPConnectionConfig")
    assert "SAPErpConnector" in getattr(sap_connector, "__all__", [])


def test_root_compatibility_modules_import():
    modules = [
        ("dynamics_connector", "DynamicsErpConnector"),
        ("ebs_connector", "EBSErpConnector"),
        ("infor_connector", "InforErpConnector"),
        ("netsuite_connector", "NetSuiteErpConnector"),
        ("oracle_connector", "OracleErpConnector"),
        ("sage_connector", "SageErpConnector"),
        ("sap_connector", "SAPErpConnector"),
        ("workday_connector", "WorkdayErpConnector"),
        ("quickbooks_connector", "QuickBooksConnector"),
        ("xero_connector", "XeroConnector"),
    ]

    for module_name, symbol in modules:
        module = __import__(module_name)
        assert hasattr(module, symbol)


def test_connector_source_file_exists():
    path = Path("connectors/sap_connector/connector.py")
    assert path.exists()


def test_shim_toggle_env_var_behavior(monkeypatch):
    import importlib
    c = importlib.import_module("tests.conftest")

    monkeypatch.setenv("FINOVATE_DISABLE_TEST_SHIMS", "1")
    assert c._should_install_test_shims() is False

    monkeypatch.setenv("FINOVATE_DISABLE_TEST_SHIMS", "0")
    assert c._should_install_test_shims() is True
