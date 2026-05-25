"""Compatibility module for tests importing `oracle_connector` from repo root."""

from _connector_loader import load_connector

_mod = load_connector("connectors/oracle_connector/connector.py", "oracle_connector_impl")
OracleErpConnector = _mod.OracleErpConnector
OracleConnectionConfig = _mod.OracleConnectionConfig

__all__ = ["OracleErpConnector", "OracleConnectionConfig"]
