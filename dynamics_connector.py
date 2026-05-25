"""Compatibility module for tests importing `dynamics_connector` from repo root."""

from _connector_loader import load_connector

_mod = load_connector("connectors/dynamics_connector/connector.py", "dynamics_connector_impl")
DynamicsErpConnector = _mod.DynamicsErpConnector
DynamicsConnectionConfig = _mod.DynamicsConnectionConfig

__all__ = ["DynamicsErpConnector", "DynamicsConnectionConfig"]
