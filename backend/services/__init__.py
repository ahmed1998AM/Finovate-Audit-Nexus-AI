"""
Finovate Audit Nexus AI - Services Layer
طبقة الخدمات الأساسية للنظام
"""

from .analytics_service import AnalyticsService
from .document_service import DocumentService
from .notification_service import NotificationService
from .user_service import UserService


# Lazy imports to avoid cascading dependency issues at module load
def get_audit_service():
    from .audit_service import AuditService
    return AuditService

def get_connector_service():
    from .connector_service import ConnectorService
    return ConnectorService

def get_ai_orchestration_service():
    from .ai_orchestration_service import AIOrchestrationService
    return AIOrchestrationService

def get_reporting_service():
    from .reporting_service import ReportingService
    return ReportingService

def get_sync_service():
    from .sync_service import get_sync_service as _get_sync
    return _get_sync

def get_predictive_service():
    from .predictive_service import PredictiveService
    return PredictiveService

def get_email_service():
    from .email_service import get_email_service as _get_email
    return _get_email

__all__ = [
    'UserService',
    'NotificationService',
    'AnalyticsService',
    'DocumentService',
    'get_audit_service',
    'get_connector_service',
    'get_ai_orchestration_service',
    'get_reporting_service',
    'get_sync_service',
    'get_predictive_service',
    'get_email_service',
]
