"""Compatibility module for tests importing `netsuite_connector` from repo root."""

from _connector_loader import load_connector

_mod = load_connector("connectors/netsuite_connector/connector.py", "netsuite_connector_impl")
NetSuiteErpConnector = _mod.NetSuiteErpConnector
NetSuiteConnectionConfig = _mod.NetSuiteConnectionConfig

__all__ = ["NetSuiteErpConnector", "NetSuiteConnectionConfig"]
