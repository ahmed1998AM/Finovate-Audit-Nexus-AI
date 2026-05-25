from _connector_loader import load_connector
_mod = load_connector('connectors/infor_connector/connector.py', 'infor_connector_impl')
InforErpConnector = _mod.InforErpConnector
InforConnectionConfig = _mod.InforConnectionConfig
