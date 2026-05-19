"""Oracle Connector for Finovate Audit Nexus AI"""
from .connector import OracleErpConnector, OracleConnectionConfig

__all__ = ['OracleErpConnector', 'OracleConnectionConfig']

# Alias for backward compatibility
OracleConnector = OracleErpConnector
