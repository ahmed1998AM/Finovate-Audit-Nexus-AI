"""
Finovate Audit Nexus AI - Configuration Module

Central configuration management for the entire application
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Finovate Audit Nexus AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/finovate_audit"
    SQLITE_DB_PATH: str = "database/finovate.db"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Vector Database (Qdrant)
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    
    # AI Providers
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    MISTRAL_API_KEY: Optional[str] = None
    XAI_API_KEY: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None
    
    # Local AI (Ollama)
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Encryption
    ENCRYPTION_KEY: str = "your-encryption-key-32-chars-long!"
    
    # File Paths
    UPLOAD_DIR: str = "uploads"
    EXPORT_DIR: str = "exports"
    REPORTS_DIR: str = "reports"
    LOGS_DIR: str = "logs"
    VECTOR_STORE_DIR: str = "vector_store"
    
    # OCR
    OCR_LANGUAGE: str = "ara+eng"  # Arabic + English
    PADDLEOCR_MODEL: str = "en_PP-OCRv3"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_DEBUG: bool = True
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_RETENTION_DAYS: int = 30
    LOG_MAX_SIZE_MB: int = 10
    
    # UI
    DEFAULT_THEME: str = "dark_professional"
    AVAILABLE_THEMES: List[str] = [
        "dark_professional",
        "light_enterprise",
        "neon_finance",
        "glassmorphism"
    ]
    
    # ERP Connectors
    SAP_ENABLED: bool = False
    ORACLE_ENABLED: bool = False
    DYNAMICS_ENABLED: bool = False
    ODOO_ENABLED: bool = False
    ZOHO_ENABLED: bool = False
    QUICKBOOKS_ENABLED: bool = False
    XERO_ENABLED: bool = False
    
    # Compliance
    EGYPTIAN_STANDARDS_ENABLED: bool = True
    IFRS_ENABLED: bool = True
    ISA_ENABLED: bool = True
    
    # Tax
    VAT_RATE: float = 14.0  # Egyptian VAT rate
    INCOME_TAX_BRACKETS: dict = {
        0: 0.0,
        15000: 0.10,
        30000: 0.15,
        45000: 0.20,
        60000: 0.25,
        200000: 0.275
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get global settings instance"""
    return settings
