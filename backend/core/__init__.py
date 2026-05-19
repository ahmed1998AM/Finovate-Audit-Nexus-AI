"""
Finovate Audit Nexus AI - Core Package
Enterprise AI Financial Audit & Intelligence Platform
"""

__version__ = "1.0.0"
__author__ = "Ahmed Mostafa Ibrahim"
__email__ = "gogom8870@gmail.com"
__copyright__ = "© 2025 Ahmed Mostafa Ibrahim — All Rights Reserved"

from .config import Config, Settings, get_settings
from .logger import setup_logger, get_logger, FinovateLogger
from .exceptions import (
    FinovateError,
    ConnectionError,
    AuthenticationError,
    AuthorizationError,
    DataValidationError,
    AIProcessingError,
    OCRProcessingError,
    FileProcessingError,
    DatabaseError,
    ConnectorError,
    ComplianceError,
    FraudDetectionError,
    ReportGenerationError,
    ConfigurationError,
    AgentExecutionError,
    WorkflowError,
    SecurityError
)

__all__ = [
    # Config
    'Config',
    'Settings',
    'get_settings',
    
    # Logger
    'setup_logger',
    'get_logger',
    'FinovateLogger',
    
    # Exceptions
    'FinovateError',
    'ConnectionError',
    'AuthenticationError',
    'AuthorizationError',
    'DataValidationError',
    'AIProcessingError',
    'OCRProcessingError',
    'FileProcessingError',
    'DatabaseError',
    'ConnectorError',
    'ComplianceError',
    'FraudDetectionError',
    'ReportGenerationError',
    'ConfigurationError',
    'AgentExecutionError',
    'WorkflowError',
    'SecurityError'
]