"""
Finovate Audit Nexus AI - Database Configuration
Professional Database Setup and Management
"""
import os
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .models import Base


class DatabaseConfig:
    """إعدادات وقواعد الاتصال بقاعدة البيانات"""

    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv(
            'DATABASE_URL',
            'sqlite:///./finovate_audit.db'
        )
        self.engine = None
        self.SessionLocal = None

    def initialize(self):
        """تهيئة محرك قاعدة البيانات"""
        if self.database_url.startswith('sqlite'):
            self.engine = create_engine(
                self.database_url,
                connect_args={'check_same_thread': False},
                poolclass=StaticPool,
                echo=False
            )
        else:
            self.engine = create_engine(
                self.database_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                echo=False
            )

        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        return self

    def create_tables(self):
        """إنشاء جميع الجداول"""
        if self.engine:
            Base.metadata.create_all(bind=self.engine)
        return self

    def drop_tables(self):
        """حذف جميع الجداول (للاختبار فقط)"""
        if self.engine:
            Base.metadata.drop_all(bind=self.engine)
        return self

    @contextmanager
    def get_session(self) -> Session:
        """مدير سياق للحصول على جلسة قاعدة بيانات"""
        if not self.SessionLocal:
            self.initialize()
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def save_anomalies(self, session, anomalies: List[Dict[str, Any]]) -> None:
        """Save fraud anomalies to database"""
        from .models import FraudCase
        for anomaly in anomalies:
            fraud_case = FraudCase(
                description=anomaly.get('description', ''),
                severity=anomaly.get('severity', 'medium'),
                status='open',
                detected_at=datetime.utcnow()
            )
            session.add(fraud_case)
        session.commit()

    def save_risk_assessment(self, session, risk_data: Dict[str, Any], engagement_id: int) -> None:
        """Save risk assessment to database"""
        from .models import AuditProject
        project = session.query(AuditProject).filter(AuditProject.id == engagement_id).first()
        if project:
            project.risk_level = risk_data.get('risk_level', 'Medium')
            session.commit()

    def save_financial_data(self, session, financial_data: List[Dict[str, Any]], source: str) -> None:
        """Save financial data to database"""
        from .models import JournalEntry
        for entry in financial_data:
            journal_entry = JournalEntry(
                account=entry.get('account', ''),
                debit=entry.get('debit', 0),
                credit=entry.get('credit', 0),
                date=datetime.utcnow(),
                description=entry.get('description', ''),
                source=source
            )
            session.add(journal_entry)
        session.commit()


# Global singleton config
db_config = DatabaseConfig()


def init_db(database_url: str = None):
    """Initialize the database (cached singleton)."""
    global db_config
    if database_url:
        db_config = DatabaseConfig(database_url)
    if not db_config.SessionLocal:
        db_config.initialize()
        db_config.create_tables()
    return db_config


def get_db_session():
    """Get a database session from the global config."""
    return db_config.get_session()


def get_db():
    """FastAPI dependency that provides a database session."""
    with db_config.get_session() as session:
        yield session
