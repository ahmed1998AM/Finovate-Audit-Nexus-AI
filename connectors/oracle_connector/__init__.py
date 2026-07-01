"""Oracle Connector for Finovate Audit Nexus AI"""
from .connector import OracleConnectionConfig, OracleErpConnector

__all__ = ['OracleErpConnector', 'OracleConnectionConfig']

# Alias for backward compatibility
OracleConnector = OracleErpConnector
