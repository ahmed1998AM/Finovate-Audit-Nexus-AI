from _connector_loader import load_connector
_mod = load_connector('connectors/workday_connector/connector.py', 'workday_connector_impl')
WorkdayErpConnector = _mod.WorkdayErpConnector
WorkdayConnectionConfig = _mod.WorkdayConnectionConfig
