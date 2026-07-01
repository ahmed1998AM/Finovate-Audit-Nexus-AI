"""
Base ERP Connector Interface
واجهة برمجية موحدة للموصلات مع أنظمة ERP المختلفة
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional


class BaseERPConnector(ABC):
    """
    Abstract base class for all ERP connectors (SAP, Odoo, Oracle, etc.)

    Core methods (must implement):
        connect(), disconnect(), test_connection()

    Data methods (override as needed):
        get_journal_entries(), get_trial_balance(), get_financial_statements()
        get_accounts(), get_system_info(), get_health_status()
    """

    def __init__(self):
        self._connected = False
        self.last_sync: Optional[datetime] = None

    @property
    def is_connected(self) -> bool:
        """Check connection status"""
        return self._connected

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the ERP system"""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close the connection"""
        pass

    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """Test if the connection is active and return system info"""
        pass

    def get_journal_entries(self, company_code: str = "", fiscal_year: str = "",
                           start_period: int = 1, end_period: int = 12,
                           **kwargs) -> List[Dict[str, Any]]:
        """Fetch journal entries (override with ERP-specific signature)"""
        raise NotImplementedError(f"{self.__class__.__name__} does not implement get_journal_entries")

    def get_trial_balance(self, company_code: str = "", fiscal_year: str = "",
                         period: int = 12, **kwargs) -> List[Dict[str, Any]]:
        """Fetch trial balance (override with ERP-specific signature)"""
        raise NotImplementedError(f"{self.__class__.__name__} does not implement get_trial_balance")

    def get_financial_statements(self, company_code: str = "", fiscal_year: str = "",
                                statement_type: str = "balance_sheet",
                                **kwargs) -> Dict[str, Any]:
        """Fetch financial statements (override with ERP-specific signature)"""
        raise NotImplementedError(f"{self.__class__.__name__} does not implement get_financial_statements")

    def get_accounts(self, account_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch chart of accounts (optional override)"""
        return []

    def get_system_info(self) -> Dict[str, Any]:
        """Fetch system/ERP information (optional override)"""
        return {"erp_type": "Unknown", "connected": self._connected}

    def get_health_status(self) -> Dict[str, Any]:
        """Return health check data (optional override)"""
        return {
            "connector": self.__class__.__name__,
            "status": "healthy" if self._connected else "unhealthy",
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "read_only_mode": True
        }
