"""
Finovate Audit Nexus AI - Connectors Package
حزمة موصلات أنظمة ERP المحاسبية

All connector imports are lazy to avoid failing when optional dependencies are missing.
Usage:
    from connectors import SAPErpConnector
    from connectors import create_sap_connector
"""

import logging as _logging

_logger = _logging.getLogger(__name__)

def __getattr__(name):
    """Lazy import of connector classes and factory functions"""
    connector_map = {
        'APIConnector': ('api_connector', 'APIConnector'),
        'DynamicsErpConnector': ('dynamics_connector', 'DynamicsErpConnector'),
        'EBSErpConnector': ('ebs_connector', 'EBSErpConnector'),
        'ExcelConnector': ('excel_connector', 'ExcelConnector'),
        'InforErpConnector': ('infor_connector', 'InforErpConnector'),
        'NetSuiteErpConnector': ('netsuite_connector', 'NetSuiteErpConnector'),
        'OdooConnector': ('odoo_connector', 'OdooConnector'),
        'OracleErpConnector': ('oracle_connector', 'OracleErpConnector'),
        'QuickBooksConnector': ('quickbooks_connector', 'QuickBooksConnector'),
        'SageErpConnector': ('sage_connector', 'SageErpConnector'),
        'SAPErpConnector': ('sap_connector', 'SAPErpConnector'),
        'SQLConnector': ('sql_connector', 'SQLConnector'),
        'WorkdayErpConnector': ('workday_connector', 'WorkdayErpConnector'),
        'XeroConnector': ('xero_connector', 'XeroConnector'),
        'ZohoBooksConnector': ('zoho_connector', 'ZohoBooksConnector'),
        'create_api_connector': ('api_connector', 'create_api_connector'),
        'create_dynamics_connector': ('dynamics_connector', 'create_dynamics_connector'),
        'create_ebs_connector': ('ebs_connector', 'create_ebs_connector'),
        'create_excel_connector': ('excel_connector', 'create_excel_connector'),
        'create_infor_connector': ('infor_connector', 'create_infor_connector'),
        'create_netsuite_connector': ('netsuite_connector', 'create_netsuite_connector'),
        'create_odoo_connector': ('odoo_connector', 'create_odoo_connector'),
        'create_oracle_connector': ('oracle_connector', 'create_oracle_connector'),
        'create_quickbooks_connector': ('quickbooks_connector', 'create_quickbooks_connector'),
        'create_sage_connector': ('sage_connector', 'create_sage_connector'),
        'create_sap_connector': ('sap_connector', 'create_sap_connector'),
        'create_sql_connector': ('sql_connector', 'create_sql_connector'),
        'create_workday_connector': ('workday_connector', 'create_workday_connector'),
        'create_xero_connector': ('xero_connector', 'create_xero_connector'),
        'create_zoho_connector': ('zoho_connector', 'create_zoho_connector'),
    }
    if name in connector_map:
        module_name, attr_name = connector_map[name]
        import importlib as _il
        mod = _il.import_module(f'.{module_name}.connector', __package__)
        attr = getattr(mod, attr_name)
        globals()[name] = attr
        return attr
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    'APIConnector',
    'DynamicsErpConnector',
    'EBSErpConnector',
    'ExcelConnector',
    'InforErpConnector',
    'NetSuiteErpConnector',
    'OdooConnector',
    'OracleErpConnector',
    'QuickBooksConnector',
    'SageErpConnector',
    'SAPErpConnector',
    'SQLConnector',
    'WorkdayErpConnector',
    'XeroConnector',
    'ZohoBooksConnector',
    'create_api_connector',
    'create_dynamics_connector',
    'create_ebs_connector',
    'create_excel_connector',
    'create_infor_connector',
    'create_netsuite_connector',
    'create_odoo_connector',
    'create_oracle_connector',
    'create_quickbooks_connector',
    'create_sage_connector',
    'create_sap_connector',
    'create_sql_connector',
    'create_workday_connector',
    'create_xero_connector',
    'create_zoho_connector',
]
