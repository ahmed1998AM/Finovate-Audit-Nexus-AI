"""Compatibility module for tests importing `workday_connector` from repo root."""

from _connector_loader import load_connector

_mod = load_connector("connectors/workday_connector/connector.py", "workday_connector_impl")
WorkdayErpConnector = _mod.WorkdayErpConnector
WorkdayConnectionConfig = _mod.WorkdayConnectionConfig

__all__ = ["WorkdayErpConnector", "WorkdayConnectionConfig"]
