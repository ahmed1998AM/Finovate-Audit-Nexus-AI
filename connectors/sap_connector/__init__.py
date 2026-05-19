"""SAP Connector for Finovate Audit Nexus AI"""
from .connector import SAPErpConnector, SAPConnectionConfig

__all__ = ['SAPErpConnector', 'SAPConnectionConfig']

# Alias for backward compatibility
SAPConnector = SAPErpConnector
