"""
Base ERP Connector Interface
واجهة برمجية موحدة للموصلات مع أنظمة ERP المختلفة
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime

class BaseERPConnector(ABC):
    """
    Abstract base class for all ERP connectors (SAP, Odoo, Oracle, etc.)
    """
    
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
    
    @abstractmethod
    def get_journal_entries(self, company_code: str, fiscal_year: str, 
                           start_period: int = 1, end_period: int = 12) -> List[Dict[str, Any]]:
        """Fetch journal entries"""
        pass
    
    @abstractmethod
    def get_trial_balance(self, company_code: str, fiscal_year: str, 
                         period: int = 12) -> List[Dict[str, Any]]:
        """Fetch trial balance"""
        pass
    
    @abstractmethod
    def get_financial_statements(self, company_code: str, fiscal_year: str,
                                statement_type: str = "balance_sheet") -> Dict[str, Any]:
        """Fetch financial statements"""
        pass
