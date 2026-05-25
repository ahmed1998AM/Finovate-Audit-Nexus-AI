"""Tests for connector loading compatibility helpers."""

from pathlib import Path

from _connector_loader import load_connector


def test_load_connector_returns_module():
    module = load_connector("connectors/sap_connector/connector.py", "sap_connector_test_impl")
    assert module is not None
    assert hasattr(module, "SAPErpConnector")
    assert hasattr(module, "SAPConnectionConfig")


def test_load_connector_raises_for_missing_file():
    import pytest

    missing = "connectors/not_real_connector/connector.py"
    with pytest.raises(ImportError, match="Cannot load connector module"):
        load_connector(missing, "missing_connector_impl")


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


def test_load_connector_raises_on_missing_loader(monkeypatch):
    import pytest
    import _connector_loader as cl

    class _Spec:
        loader = None

    monkeypatch.setattr(cl, "spec_from_file_location", lambda *a, **k: _Spec())

    with pytest.raises(ImportError, match="Cannot load connector module"):
        cl.load_connector("connectors/sap_connector/connector.py", "sap_connector_missing_loader")


def test_load_connector_raises_on_missing_spec(monkeypatch):
    import pytest
    import _connector_loader as cl

    monkeypatch.setattr(cl, "spec_from_file_location", lambda *a, **k: None)

    with pytest.raises(ImportError, match="Cannot load connector module"):
        cl.load_connector("connectors/sap_connector/connector.py", "sap_connector_missing_spec")
