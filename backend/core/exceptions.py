"""
Finovate Audit Nexus AI - Exceptions Module

Custom exceptions for the entire application
"""


class FinovateError(Exception):
    """Base exception for Finovate Audit Nexus AI"""
    
    def __init__(self, message: str, code: str = None, details: dict = None):
        self.message = message
        self.code = code or "FINOVATE_ERROR"
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """Convert exception to dictionary"""
        return {
            "error": self.__class__.__name__,
            "code": self.code,
            "message": self.message,
            "details": self.details
        }


class ConnectionError(FinovateError):
    """Exception raised when connection fails"""
    
    def __init__(self, message: str, service: str = None, details: dict = None):
        super().__init__(
            message=message,
            code="CONNECTION_ERROR",
            details={"service": service, **(details or {})}
        )


class AuthenticationError(FinovateError):
    """Exception raised when authentication fails"""
    
    def __init__(self, message: str, provider: str = None, details: dict = None):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            details={"provider": provider, **(details or {})}
        )


class AuthorizationError(FinovateError):
    """Exception raised when authorization fails"""
    
    def __init__(self, message: str, resource: str = None, details: dict = None):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            details={"resource": resource, **(details or {})}
        )


class DataValidationError(FinovateError):
    """Exception raised when data validation fails"""
    
    def __init__(self, message: str, field: str = None, details: dict = None):
        super().__init__(
            message=message,
            code="DATA_VALIDATION_ERROR",
            details={"field": field, **(details or {})}
        )


class AIProcessingError(FinovateError):
    """Exception raised when AI processing fails"""
    
    def __init__(self, message: str, model: str = None, details: dict = None):
        super().__init__(
            message=message,
            code="AI_PROCESSING_ERROR",
            details={"model": model, **(details or {})}
        )


class OCRProcessingError(FinovateError):
    """Exception raised when OCR processing fails"""
    
    def __init__(self, message: str, document: str = None, details: dict = None):
        super().__init__(
            message=message,
            code="OCR_PROCESSING_ERROR",
            details={"document": document, **(details or {})}
        )


class FileProcessingError(FinovateError):
    """Exception raised when file processing fails"""
    
    def __init__(self, message: str, filename: str = None, details: dict = None):
        super().__init__(
            message=message,
            code="FILE_PROCESSING_ERROR",
            details={"filename": filename, **(details or {})}
        )


class DatabaseError(FinovateError):
    """Exception raised when database operation fails"""
    
    def __init__(self, message: str, operation: str = None, details: dict = None):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            details={"operation": operation, **(details or {})}
        )


class ConnectorError(FinovateError):
    """Exception raised when ERP connector fails"""
    
    def __init__(self, message: str, connector: str = None, details: dict = None):
        super().__init__(
            message=message,
            code="CONNECTOR_ERROR",
            details={"connector": connector, **(details or {})}
        )


class ComplianceError(FinovateError):
    """Exception raised when compliance check fails"""
    
    def __init__(self, message: str, standard: str = None, details: dict = None):
        super().__init__(
            message=message,
            code="COMPLIANCE_ERROR",
            details={"standard": standard, **(details or {})}
        )


class FraudDetectionError(FinovateError):
    """Exception raised when fraud detection fails"""
    
    def __init__(self, message: str, rule: str = None, details: dict = None):
        super().__init__(
            message=message,
            code="FRAUD_DETECTION_ERROR",
            details={"rule": rule, **(details or {})}
        )


class ReportGenerationError(FinovateError):
    """Exception raised when report generation fails"""
    
    def __init__(self, message: str, report_type: str = None, details: dict = None):
        super().__init__(
            message=message,
            code="REPORT_GENERATION_ERROR",
            details={"report_type": report_type, **(details or {})}
        )


class ConfigurationError(FinovateError):
    """Exception raised when configuration is invalid"""
    
    def __init__(self, message: str, setting: str = None, details: dict = None):
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            details={"setting": setting, **(details or {})}
        )


class AgentExecutionError(FinovateError):
    """Exception raised when AI agent execution fails"""
    
    def __init__(self, message: str, agent: str = None, details: dict = None):
        super().__init__(
            message=message,
            code="AGENT_EXECUTION_ERROR",
            details={"agent": agent, **(details or {})}
        )


class WorkflowError(FinovateError):
    """Exception raised when workflow execution fails"""
    
    def __init__(self, message: str, workflow: str = None, details: dict = None):
        super().__init__(
            message=message,
            code="WORKFLOW_ERROR",
            details={"workflow": workflow, **(details or {})}
        )


class SecurityError(FinovateError):
    """Exception raised when security check fails"""
    
    def __init__(self, message: str, violation_type: str = None, details: dict = None):
        super().__init__(
            message=message,
            code="SECURITY_ERROR",
            details={"violation_type": violation_type, **(details or {})}
        )
