"""
Database Schema Models
======================
Complete database schema for Finovate Audit Nexus AI.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Engagement(Base):
    """Audit engagement table."""
    __tablename__ = 'engagements'
    
    id = Column(Integer, primary_key=True)
    engagement_id = Column(String(50), unique=True, nullable=False)
    client_name = Column(String(200), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    status = Column(String(50), default='planning')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    team_members = relationship('TeamMember', back_populates='engagement')
    findings = relationship('Finding', back_populates='engagement')


class TeamMember(Base):
    """Audit team member table."""
    __tablename__ = 'team_members'
    
    id = Column(Integer, primary_key=True)
    engagement_id = Column(Integer, ForeignKey('engagements.id'))
    name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)
    hours_allocated = Column(Float, default=0)
    hours_worked = Column(Float, default=0)
    
    engagement = relationship('Engagement', back_populates='team_members')


class Finding(Base):
    """Audit findings table."""
    __tablename__ = 'findings'
    
    id = Column(Integer, primary_key=True)
    engagement_id = Column(Integer, ForeignKey('engagements.id'))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    severity = Column(String(20))  # low, medium, high, critical
    status = Column(String(50), default='identified')
    recommendation = Column(Text)
    management_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    engagement = relationship('Engagement', back_populates='findings')


class FinancialData(Base):
    """Financial data extracted from ERP systems."""
    __tablename__ = 'financial_data'
    
    id = Column(Integer, primary_key=True)
    source_system = Column(String(50), nullable=False)  # SAP, Oracle, etc.
    entity_type = Column(String(50), nullable=False)  # account, transaction, etc.
    entity_id = Column(String(100), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    period = Column(Integer)
    amount = Column(Float)
    currency = Column(String(3), default='USD')
    data_json = Column(JSON)
    extracted_at = Column(DateTime, default=datetime.utcnow)


class RiskAssessment(Base):
    """Risk assessment records."""
    __tablename__ = 'risk_assessments'
    
    id = Column(Integer, primary_key=True)
    engagement_id = Column(Integer, ForeignKey('engagements.id'))
    risk_area = Column(String(100), nullable=False)
    risk_level = Column(String(20))  # low, medium, high
    risk_score = Column(Float)
    mitigation_strategy = Column(Text)
    assessed_at = Column(DateTime, default=datetime.utcnow)


class ComplianceCheck(Base):
    """Compliance monitoring records."""
    __tablename__ = 'compliance_checks'
    
    id = Column(Integer, primary_key=True)
    standard = Column(String(50), nullable=False)  # IFRS 15, GAAP, SOX, etc.
    requirement = Column(String(200))
    status = Column(String(20))  # compliant, non_compliant, partial
    issues_count = Column(Integer, default=0)
    checked_at = Column(DateTime, default=datetime.utcnow)


class Anomaly(Base):
    """Detected anomalies and fraud indicators."""
    __tablename__ = 'anomalies'
    
    id = Column(Integer, primary_key=True)
    anomaly_type = Column(String(100), nullable=False)
    severity = Column(String(20))
    description = Column(Text)
    transaction_ids = Column(JSON)  # Array of related transaction IDs
    detected_at = Column(DateTime, default=datetime.utcnow)
    investigated = Column(Boolean, default=False)


class Workpaper(Base):
    """Audit workpapers."""
    __tablename__ = 'workpapers'
    
    id = Column(Integer, primary_key=True)
    engagement_id = Column(Integer, ForeignKey('engagements.id'))
    reference = Column(String(50), unique=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    prepared_by = Column(String(100))
    reviewed_by = Column(String(100))
    status = Column(String(50), default='draft')
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


class Document(Base):
    """Document storage metadata."""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    engagement_id = Column(Integer, ForeignKey('engagements.id'))
    filename = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    uploaded_by = Column(String(100))
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    """User accounts."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    role = Column(String(50), nullable=False)  # admin, manager, auditor, viewer
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)


class AuditLog(Base):
    """System audit trail."""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow)


class ESGMetric(Base):
    """ESG metrics and sustainability data."""
    __tablename__ = 'esg_metrics'
    
    id = Column(Integer, primary_key=True)
    engagement_id = Column(Integer, ForeignKey('engagements.id'))
    metric_name = Column(String(100), nullable=False)
    value = Column(Float)
    unit = Column(String(50))
    reporting_period = Column(String(20))
    verified = Column(Boolean, default=False)
    reported_at = Column(DateTime, default=datetime.utcnow)


class KnowledgeArticle(Base):
    """Knowledge base articles."""
    __tablename__ = 'knowledge_articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    category = Column(String(50))
    content = Column(Text)
    tags = Column(JSON)
    author_id = Column(Integer, ForeignKey('users.id'))
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
