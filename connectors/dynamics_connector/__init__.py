"""Dynamics Connector for Finovate Audit Nexus AI"""
from .connector import DynamicsErpConnector, DynamicsConnectionConfig

__all__ = ['DynamicsErpConnector', 'DynamicsConnectionConfig']

# Alias for backward compatibility
MicrosoftDynamicsConnector = DynamicsErpConnector
