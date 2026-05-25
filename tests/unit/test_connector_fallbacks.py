"""Tests fallback behavior for root compatibility connector modules."""

import importlib
import sys

import _connector_loader


def _reload_with_loader_failure(module_name: str):
    original = _connector_loader.load_connector

    def _raiser(*args, **kwargs):
        raise ModuleNotFoundError("optional SDK missing")

    _connector_loader.load_connector = _raiser
    try:
        sys.modules.pop(module_name, None)
        return importlib.import_module(module_name)
    finally:
        _connector_loader.load_connector = original


def test_quickbooks_fallback_class_when_sdk_missing():
    mod = _reload_with_loader_failure("quickbooks_connector")
    instance = mod.QuickBooksConnector(config={"a": 1})
    assert getattr(instance, "config", {}) == {"a": 1}


def test_xero_fallback_class_when_sdk_missing():
    mod = _reload_with_loader_failure("xero_connector")
    instance = mod.XeroConnector(config={"b": 2})
    assert getattr(instance, "config", {}) == {"b": 2}


def test_fallback_exports_are_available():
    qb = _reload_with_loader_failure("quickbooks_connector")
    xr = _reload_with_loader_failure("xero_connector")

    assert "QuickBooksConnector" in getattr(qb, "__all__", [])
    assert "XeroConnector" in getattr(xr, "__all__", [])


def test_fallback_default_config_is_empty_dict():
    qb = _reload_with_loader_failure("quickbooks_connector")
    xr = _reload_with_loader_failure("xero_connector")

    assert qb.QuickBooksConnector().config == {}
    assert xr.XeroConnector().config == {}
