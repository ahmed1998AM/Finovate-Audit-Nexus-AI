"""Tests fallback behavior for root compatibility connector modules."""

import importlib
import sys

import _connector_loader


def _reload_with_loader_failure(module_name: str, monkeypatch):
    def _raiser(*args, **kwargs):
        raise ModuleNotFoundError("optional SDK missing")

    monkeypatch.setattr(_connector_loader, "load_connector", _raiser)
    sys.modules.pop(module_name, None)
    return importlib.import_module(module_name)


def test_quickbooks_fallback_class_when_sdk_missing(monkeypatch):
    mod = _reload_with_loader_failure("quickbooks_connector", monkeypatch)
    instance = mod.QuickBooksConnector(config={"a": 1})
    assert getattr(instance, "config", {}) == {"a": 1}


def test_xero_fallback_class_when_sdk_missing(monkeypatch):
    mod = _reload_with_loader_failure("xero_connector", monkeypatch)
    instance = mod.XeroConnector(config={"b": 2})
    assert getattr(instance, "config", {}) == {"b": 2}


def test_fallback_exports_are_available(monkeypatch):
    qb = _reload_with_loader_failure("quickbooks_connector", monkeypatch)
    xr = _reload_with_loader_failure("xero_connector", monkeypatch)

    assert "QuickBooksConnector" in getattr(qb, "__all__", [])
    assert "XeroConnector" in getattr(xr, "__all__", [])


def test_fallback_default_config_is_empty_dict(monkeypatch):
    qb = _reload_with_loader_failure("quickbooks_connector", monkeypatch)
    xr = _reload_with_loader_failure("xero_connector", monkeypatch)

    assert qb.QuickBooksConnector().config == {}
    assert xr.XeroConnector().config == {}
