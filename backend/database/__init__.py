"""
Finovate Audit Nexus AI - Database Configuration
Professional Database Setup and Management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import os

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
        # استخدام SQLite للتطوير و PostgreSQL للإنتاج
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
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

# نسخة عامة للاستخدام السريع
db_config = DatabaseConfig()

def init_db(database_url: str = None):
    """دالة مساعدة لتهيئة قاعدة البيانات"""
    config = DatabaseConfig(database_url)
    config.initialize()
    config.create_tables()
    return config

def get_db_session():
    """دالة مساعدة للحصول على جلسة قاعدة بيانات"""
    if not db_config.SessionLocal:
        db_config.initialize()
    return db_config.get_session()
