from _connector_loader import load_connector
_mod = load_connector('connectors/oracle_connector/connector.py', 'oracle_connector_impl')
OracleErpConnector = _mod.OracleErpConnector
OracleConnectionConfig = _mod.OracleConnectionConfig
