from _connector_loader import load_connector
_mod = load_connector('connectors/sap_connector/connector.py', 'sap_connector_impl')
SAPErpConnector = _mod.SAPErpConnector
SAPConnectionConfig = _mod.SAPConnectionConfig
