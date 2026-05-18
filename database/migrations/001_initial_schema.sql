-- Initial Database Schema Migration
-- Finovate Audit Nexus AI
-- Version: 1.0.0

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'auditor',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Engagements table
CREATE TABLE engagements (
    id SERIAL PRIMARY KEY,
    engagement_id VARCHAR(50) UNIQUE NOT NULL,
    client_name VARCHAR(200) NOT NULL,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'planning',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Team members table
CREATE TABLE team_members (
    id SERIAL PRIMARY KEY,
    engagement_id INTEGER REFERENCES engagements(id),
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,
    hours_allocated DECIMAL(10,2) DEFAULT 0,
    hours_worked DECIMAL(10,2) DEFAULT 0
);

-- Findings table
CREATE TABLE findings (
    id SERIAL PRIMARY KEY,
    engagement_id INTEGER REFERENCES engagements(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    severity VARCHAR(20),
    status VARCHAR(50) DEFAULT 'identified',
    recommendation TEXT,
    management_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Financial data table
CREATE TABLE financial_data (
    id SERIAL PRIMARY KEY,
    source_system VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    fiscal_year INTEGER NOT NULL,
    period INTEGER,
    amount DECIMAL(20,2),
    currency VARCHAR(3) DEFAULT 'USD',
    data_json JSONB,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Risk assessments table
CREATE TABLE risk_assessments (
    id SERIAL PRIMARY KEY,
    engagement_id INTEGER REFERENCES engagements(id),
    risk_area VARCHAR(100) NOT NULL,
    risk_level VARCHAR(20),
    risk_score DECIMAL(5,4),
    mitigation_strategy TEXT,
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Compliance checks table
CREATE TABLE compliance_checks (
    id SERIAL PRIMARY KEY,
    standard VARCHAR(50) NOT NULL,
    requirement VARCHAR(200),
    status VARCHAR(20),
    issues_count INTEGER DEFAULT 0,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Anomalies table
CREATE TABLE anomalies (
    id SERIAL PRIMARY KEY,
    anomaly_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20),
    description TEXT,
    transaction_ids JSONB,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    investigated BOOLEAN DEFAULT FALSE
);

-- Workpapers table
CREATE TABLE workpapers (
    id SERIAL PRIMARY KEY,
    engagement_id INTEGER REFERENCES engagements(id),
    reference VARCHAR(50) UNIQUE,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    prepared_by VARCHAR(100),
    reviewed_by VARCHAR(100),
    status VARCHAR(50) DEFAULT 'draft',
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    engagement_id INTEGER REFERENCES engagements(id),
    filename VARCHAR(200) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    uploaded_by VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit logs table
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    details JSONB,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ESG metrics table
CREATE TABLE esg_metrics (
    id SERIAL PRIMARY KEY,
    engagement_id INTEGER REFERENCES engagements(id),
    metric_name VARCHAR(100) NOT NULL,
    value DECIMAL(20,4),
    unit VARCHAR(50),
    reporting_period VARCHAR(20),
    verified BOOLEAN DEFAULT FALSE,
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge articles table
CREATE TABLE knowledge_articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    category VARCHAR(50),
    content TEXT,
    tags JSONB,
    author_id INTEGER REFERENCES users(id),
    views INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_engagements_status ON engagements(status);
CREATE INDEX idx_findings_severity ON findings(severity);
CREATE INDEX idx_financial_data_source ON financial_data(source_system);
CREATE INDEX idx_financial_data_fiscal_year ON financial_data(fiscal_year);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_workpapers_engagement ON workpapers(engagement_id);

-- Insert default admin user
INSERT INTO users (username, email, role) VALUES 
('admin', 'admin@finovate.audit', 'admin'),
('system', 'system@finovate.audit', 'system');

-- Add trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_engagements_updated_at BEFORE UPDATE ON engagements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_articles_updated_at BEFORE UPDATE ON knowledge_articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
