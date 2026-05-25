from _connector_loader import load_connector
_mod = load_connector('connectors/dynamics_connector/connector.py', 'dynamics_connector_impl')
DynamicsErpConnector = _mod.DynamicsErpConnector
DynamicsConnectionConfig = _mod.DynamicsConnectionConfig
