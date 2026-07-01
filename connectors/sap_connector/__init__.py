"""SAP Connector for Finovate Audit Nexus AI"""
from .connector import SAPConnectionConfig, SAPErpConnector

__all__ = ['SAPErpConnector', 'SAPConnectionConfig']

# Alias for backward compatibility and test compatibility
SAPConnector = SAPErpConnector
