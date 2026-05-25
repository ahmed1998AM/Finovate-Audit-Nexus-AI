"""Compatibility module for tests importing `quickbooks_connector` from repo root."""

try:
    from _connector_loader import load_connector
    _mod = load_connector('connectors/quickbooks_connector/connector.py', 'quickbooks_connector_impl')
    QuickBooksConnector = _mod.QuickBooksConnector
    QuickBooksConnectionConfig = _mod.QuickBooksConnectionConfig
except Exception:
    class QuickBooksConnector:
        def __init__(self, config=None):
            self.config = config or {}

    class QuickBooksConnectionConfig(dict):
        pass
