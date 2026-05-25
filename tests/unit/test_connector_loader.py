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


def test_root_compatibility_module_exports():
    import sap_connector

    assert hasattr(sap_connector, "SAPErpConnector")
    assert hasattr(sap_connector, "SAPConnectionConfig")
    assert "SAPErpConnector" in getattr(sap_connector, "__all__", [])


def test_connector_source_file_exists():
    path = Path("connectors/sap_connector/connector.py")
    assert path.exists()
