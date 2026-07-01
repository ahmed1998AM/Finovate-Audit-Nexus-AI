"""Tests for connector loading from connectors/ directory."""

from pathlib import Path
import importlib.util


def _load_connector(module_path: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load connector module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_load_connector_returns_module():
    module = _load_connector("connectors/sap_connector/connector.py", "sap_connector_test_impl")
    assert module is not None
    assert hasattr(module, "SAPErpConnector")
    assert hasattr(module, "SAPConnectionConfig")


def test_load_connector_raises_for_missing_file():
    import pytest
    with pytest.raises((ImportError, FileNotFoundError)):
        _load_connector("connectors/not_real_connector/connector.py", "missing_connector_impl")


def test_connector_source_file_exists():
    path = Path("connectors/sap_connector/connector.py")
    assert path.exists()


def test_all_connector_dirs_have_connector_py():
    connector_types = [
        "sap_connector", "oracle_connector", "dynamics_connector",
        "ebs_connector", "infor_connector", "netsuite_connector",
        "quickbooks_connector", "sage_connector", "workday_connector",
        "xero_connector", "odoo_connector", "zoho_connector",
        "excel_connector", "sql_connector", "api_connector",
    ]
    for ctype in connector_types:
        path = Path(f"connectors/{ctype}/connector.py")
        assert path.exists(), f"Missing connector file: {path}"


def test_connector_modules_import_cleanly():
    connector_types = ["sap_connector", "oracle_connector", "quickbooks_connector", "xero_connector"]
    for ctype in connector_types:
        path = Path(f"connectors/{ctype}/connector.py")
        mod = _load_connector(str(path), f"{ctype}_test")
        symbols = [s for s in dir(mod) if not s.startswith("_")]
        assert len(symbols) > 0, f"No symbols in {ctype}"
