"""Tests fallback behavior for connector modules."""

import importlib.util
from pathlib import Path


def _load_connector(module_path: str):
    spec = importlib.util.spec_from_file_location("connector", module_path)
    if spec is None or spec.loader is None:
        raise ModuleNotFoundError(f"Cannot load {module_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_quickbooks_connector_loads():
    mod = _load_connector(str(Path("connectors/quickbooks_connector/connector.py")))
    instance = mod.QuickBooksConnector(config={"client_id": "test", "client_secret": "test"})
    assert instance.client_id == "test"


def test_xero_connector_loads():
    mod = _load_connector(str(Path("connectors/xero_connector/connector.py")))
    instance = mod.XeroConnector(config={"client_id": "test", "client_secret": "test"})
    assert instance.client_id == "test"


def test_sap_connector_loads():
    mod = _load_connector(str(Path("connectors/sap_connector/connector.py")))
    assert hasattr(mod, "SAPErpConnector")
    assert hasattr(mod, "SAPConnectionConfig")


def test_connector_has_expected_attributes():
    mod = _load_connector(str(Path("connectors/quickbooks_connector/connector.py")))
    instance = mod.QuickBooksConnector(config={"client_id": "x", "client_secret": "y"})
    assert hasattr(instance, "is_connected")
    assert hasattr(instance, "last_sync")
    assert hasattr(instance, "base_url")
