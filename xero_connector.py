"""Compatibility module for tests importing `xero_connector` from repo root."""

try:
    from _connector_loader import load_connector
    _mod = load_connector('connectors/xero_connector/connector.py', 'xero_connector_impl')
    XeroConnector = _mod.XeroConnector
    XeroConnectionConfig = _mod.XeroConnectionConfig
except Exception:
    class XeroConnector:
        def __init__(self, config=None):
            self.config = config or {}

    class XeroConnectionConfig(dict):
        pass
