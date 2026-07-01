"""
Finovate Audit Nexus AI - Database Models
Professional Financial Audit Database Schema
"""
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models using SQLAlchemy 2.0"""
    pass

class User(Base):
    """نظام إدارة المستخدمين والصلاحيات"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # Admin, Auditor, Accountant, CFO, etc.
    is_active = Column(Boolean, default=True)
    must_change_password = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    audit_logs = relationship('AuditLog', back_populates='user')
    sessions = relationship('UserSession', back_populates='user')

class UserSession(Base):
    """إدارة الجلسات الأمنية"""
    __tablename__ = 'user_sessions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    device_info = Column(JSON)
    ip_address = Column(String(45))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    user = relationship('User', back_populates='sessions')

class Company(Base):
    """بيانات الشركات والعملاء"""
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    tax_id = Column(String(50), unique=True)
    commercial_registration = Column(String(50))
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(100))
    fiscal_year_start = Column(Integer, default=1)  # شهر بداية السنة المالية
    currency = Column(String(3), default='EGP')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    chart_of_accounts = relationship('ChartOfAccount', back_populates='company')
    journal_entries = relationship('JournalEntry', back_populates='company')
    audit_projects = relationship('AuditProject', back_populates='company')

class ChartOfAccount(Base):
    """دليل الحسابات الموحد"""
    __tablename__ = 'chart_of_accounts'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    account_code = Column(String(20), nullable=False)
    account_name_ar = Column(String(200), nullable=False)
    account_name_en = Column(String(200))
    account_type = Column(String(50))  # Asset, Liability, Equity, Revenue, Expense
    parent_account_id = Column(Integer, ForeignKey('chart_of_accounts.id'))
    level = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship('Company', back_populates='chart_of_accounts')
    parent_account = relationship('ChartOfAccount', remote_side=[id], backref='child_accounts')
    journal_lines = relationship('JournalLine', back_populates='account')

class JournalEntry(Base):
    """قيود اليومية"""
    __tablename__ = 'journal_entries'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    entry_number = Column(String(50), nullable=False)
    entry_date = Column(DateTime, nullable=False)
    posting_date = Column(DateTime)
    description = Column(Text)
    source_system = Column(String(100))  # SAP, Oracle, Excel, etc.
    source_document = Column(String(100))
    created_by = Column(String(100))
    posted_by = Column(String(100))
    is_posted = Column(Boolean, default=True)
    is_reversed = Column(Boolean, default=False)
    reversal_date = Column(DateTime)
    fiscal_year = Column(Integer)
    fiscal_period = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    company = relationship('Company', back_populates='journal_entries')
    lines = relationship('JournalLine', back_populates='entry', cascade='all, delete-orphan')

class JournalLine(Base):
    """أسطر قيود اليومية"""
    __tablename__ = 'journal_lines'

    id = Column(Integer, primary_key=True)
    entry_id = Column(Integer, ForeignKey('journal_entries.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('chart_of_accounts.id'), nullable=False)
    line_number = Column(Integer, nullable=False)
    description = Column(Text)
    debit_amount = Column(Float, default=0.0)
    credit_amount = Column(Float, default=0.0)
    cost_center = Column(String(50))
    project_code = Column(String(50))
    tax_code = Column(String(20))
    tax_amount = Column(Float, default=0.0)
    currency = Column(String(3))
    exchange_rate = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    entry = relationship('JournalEntry', back_populates='lines')
    account = relationship('ChartOfAccount', back_populates='journal_lines')

class AuditProject(Base):
    """مشاريع المراجعة والتدقيق"""
    __tablename__ = 'audit_projects'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    project_name = Column(String(200), nullable=False)
    audit_type = Column(String(50))  # Financial, Tax, Fraud, Compliance, etc.
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(20), default='Planning')  # Planning, Fieldwork, Review, Completed
    risk_level = Column(String(20))  # Low, Medium, High, Critical
    lead_auditor_id = Column(Integer, ForeignKey('users.id'))
    team_members = Column(JSON)  # قائمة بأعضاء الفريق
    scope = Column(Text)
    objectives = Column(Text)
    findings_count = Column(Integer, default=0)
    recommendations_count = Column(Integer, default=0)
    results = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    company = relationship('Company', back_populates='audit_projects')
    findings = relationship('AuditFinding', back_populates='project')
    workpapers = relationship('WorkPaper', back_populates='project')

class AuditFinding(Base):
    """نتائج وملاحظات المراجعة"""
    __tablename__ = 'audit_findings'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('audit_projects.id'), nullable=False)
    finding_number = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50))  # Error, Fraud, Compliance, Control Weakness, etc.
    severity = Column(String(20))  # Low, Medium, High, Critical
    risk_score = Column(Float)
    financial_impact = Column(Float)
    root_cause = Column(Text)
    recommendation = Column(Text)
    management_response = Column(Text)
    action_plan = Column(Text)
    responsible_person = Column(String(100))
    due_date = Column(DateTime)
    status = Column(String(20), default='Open')  # Open, In Progress, Closed, Accepted
    evidence_files = Column(JSON)
    created_by_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    project = relationship('AuditProject', back_populates='findings')
    creator = relationship('User', foreign_keys=[created_by_id])

class WorkPaper(Base):
    """أوراق العمل والمراجع"""
    __tablename__ = 'work_papers'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('audit_projects.id'), nullable=False)
    wp_number = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    wp_type = Column(String(50))  # Program, Test, Analysis, Summary, etc.
    prepared_by_id = Column(Integer, ForeignKey('users.id'))
    reviewed_by_id = Column(Integer, ForeignKey('users.id'))
    review_status = Column(String(20), default='Draft')  # Draft, Under Review, Approved
    file_path = Column(String(500))
    file_hash = Column(String(64))  # SHA-256 للتحقق من السلامة
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    project = relationship('AuditProject', back_populates='workpapers')
    preparer = relationship('User', foreign_keys=[prepared_by_id])
    reviewer = relationship('User', foreign_keys=[reviewed_by_id])

class AuditLog(Base):
    """سجل التدقيق الأمني"""
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    old_value = Column(JSON)
    new_value = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship('User', back_populates='audit_logs')

class AIAgentLog(Base):
    """سجل عمليات الوكلاء الذكية"""
    __tablename__ = 'ai_agent_logs'

    id = Column(Integer, primary_key=True)
    agent_name = Column(String(100), nullable=False)
    task_id = Column(String(100))
    input_data = Column(JSON)
    output_data = Column(JSON)
    confidence_score = Column(Float)
    execution_time = Column(Float)
    tokens_used = Column(Integer)
    model_used = Column(String(100))
    status = Column(String(20))  # Success, Error, Warning
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class FraudCase(Base):
    """حالات الاحتيال المكتشفة"""
    __tablename__ = 'fraud_cases'

    id = Column(Integer, primary_key=True)
    case_number = Column(String(20), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    fraud_type = Column(String(50))  # Embezzlement, False Invoice, Money Laundering, etc.
    severity = Column(String(20))
    detected_by = Column(String(100))  # Agent name
    detection_date = Column(DateTime, default=datetime.utcnow)
    amount_involved = Column(Float)
    suspects = Column(JSON)
    evidence = Column(JSON)
    investigation_status = Column(String(20), default='Open')
    assigned_to_id = Column(Integer, ForeignKey('users.id'))
    report_file = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class TaxCompliance(Base):
    """الامتثال الضريبي"""
    __tablename__ = 'tax_compliance'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    tax_type = Column(String(50), nullable=False)  # VAT, Income Tax, Payroll Tax, etc.
    tax_period = Column(String(20), nullable=False)
    filing_date = Column(DateTime)
    due_date = Column(DateTime)
    status = Column(String(20), default='Pending')  # Pending, Filed, Paid, Overdue
    declared_amount = Column(Float)
    calculated_amount = Column(Float)
    difference = Column(Float)
    risk_score = Column(Float)
    issues_found = Column(JSON)
    recommendations = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class Document(Base):
    """إدارة المستندات والملفات"""
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    document_type = Column(String(50))  # Invoice, Contract, Bank Statement, etc.
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    file_hash = Column(String(64))
    mime_type = Column(String(100))
    ocr_text = Column(Text)
    extracted_data = Column(JSON)
    upload_date = Column(DateTime, default=datetime.utcnow)
    uploaded_by_id = Column(Integer, ForeignKey('users.id'))
    is_processed = Column(Boolean, default=False)

    company = relationship('Company')
    uploader = relationship('User')


class WebhookSubscriptionModel(Base):
    __tablename__ = 'webhook_subscriptions'

    id = Column(Integer, primary_key=True)
    subscription_id = Column(String(36), unique=True, nullable=False, index=True)
    url = Column(String(500), nullable=False)
    events = Column(JSON)
    secret = Column(String(255), default="")
    enabled = Column(Boolean, default=True)
    retry_count = Column(Integer, default=3)
    timeout = Column(Integer, default=30)
    headers = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class EventLogModel(Base):
    __tablename__ = 'event_logs'

    id = Column(Integer, primary_key=True)
    event_id = Column(String(36), unique=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    source = Column(String(100), default="system")
    priority = Column(Integer, default=1)
    data = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class TaskRecordModel(Base):
    __tablename__ = 'task_records'

    id = Column(Integer, primary_key=True)
    task_id = Column(String(36), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    status = Column(String(20), default='pending')
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
