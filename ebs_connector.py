"""Compatibility module for tests importing `ebs_connector` from repo root."""

from _connector_loader import load_connector

_mod = load_connector("connectors/ebs_connector/connector.py", "ebs_connector_impl")
EBSErpConnector = _mod.EBSErpConnector
EBSConnectionConfig = _mod.EBSConnectionConfig

__all__ = ["EBSErpConnector", "EBSConnectionConfig"]
