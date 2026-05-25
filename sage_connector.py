from _connector_loader import load_connector
_mod = load_connector('connectors/sage_connector/connector.py', 'sage_connector_impl')
SageErpConnector = _mod.SageErpConnector
SageConnectionConfig = _mod.SageConnectionConfig
