"""
Finovate Audit Nexus AI - Bootstrap Data
إنشاء البيانات الافتراضية عند أول تشغيل
"""
import logging
import os
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from backend.database.models import (
    AuditFinding,
    AuditProject,
    Company,
    FraudCase,
    TaxCompliance,
    User,
)
from backend.security import hash_password

logger = logging.getLogger(__name__)

def seed_default_data(db: Session):
    if db.query(User).count() == 0:
        import secrets
        admin_pw = secrets.token_urlsafe(16)
        auditor_pw = secrets.token_urlsafe(16)
        db.add(User(username="admin", email="admin@finovate.ai",
                    password_hash=hash_password(admin_pw),
                    role="Admin", is_active=True,
                    must_change_password=True))
        db.add(User(username="auditor1", email="auditor1@finovate.ai",
                    password_hash=hash_password(auditor_pw),
                    role="Auditor", is_active=True,
                    must_change_password=True))
        # Save initial passwords to file instead of logging
        pw_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".initial_passwords")
        with open(pw_path, "w") as f:
            f.write("INITIAL PASSWORDS - CHANGE ON FIRST LOGIN\n")
            f.write(f"admin    : {admin_pw}\n")
            f.write(f"auditor1 : {auditor_pw}\n")
        logger.warning("=" * 60)
        logger.warning(f"Initial passwords saved to {pw_path}")
        logger.warning(f"Delete {pw_path} after recording passwords.")
        logger.warning("=" * 60)

    if db.query(Company).count() == 0:
        db.add(Company(name="Finovate Audit Client", tax_id="FINOVATE-001",
                       address="Cairo, Egypt", is_active=True))
        db.add(Company(name="TechCorp Egypt", tax_id="TECH-002",
                       address="Alexandria, Egypt", is_active=True))
        logger.info("Created sample companies")

    db.commit()

    company = db.query(Company).first()
    user = db.query(User).first()
    if company and user and db.query(AuditProject).count() == 0:
        proj = AuditProject(company_id=company.id, project_name="Q1 Financial Audit",
                            audit_type="full", status="Completed", risk_level="Medium",
                            scope="Full financial statement audit for Q1 2026",
                            findings_count=5, recommendations_count=3,
                            start_date=datetime.now() - timedelta(days=30),
                            end_date=datetime.now() - timedelta(days=2))
        db.add(proj)
        db.flush()

        findings_data = [
            ("F-2026-001", "Duplicate Journal Entries", "Found 12 duplicate journal entries in accounts payable",
             "Error", "Medium", 45.0, "Manual entry without proper validation"),
            ("F-2026-002", "VAT Reconciliation Gap", "VAT payable differs from filed returns by EGP 15,000",
             "Compliance", "High", 72.0, "Mismatch between accounting records and tax filing"),
            ("F-2026-003", "Missing Supporting Documents", "3 fixed asset purchases lack proper invoices",
             "Control Weakness", "Medium", 38.0, "Inadequate document retention policy"),
            ("F-2026-004", "Suspicious Wire Transfer", "Wire transfer of EGP 250,000 to unregistered vendor",
             "Fraud", "Critical", 92.0, "Possible shell company transaction"),
            ("F-2026-005", "Revenue Recognition Error", "EGP 75,000 recognized before delivery completion",
             "Error", "High", 68.0, "Premature revenue recognition"),
        ]
        for num, title, desc, cat, sev, risk, cause in findings_data:
            db.add(AuditFinding(project_id=proj.id, finding_number=num, title=title,
                                description=desc, category=cat, severity=sev,
                                risk_score=risk, root_cause=cause, status="Open",
                                recommendation=f"Review and address: {title}",
                                created_by_id=user.id))

        db.add(FraudCase(case_number="FC-2026-001",
                         title="Suspicious Vendor Payment",
                         description="Wire transfer EGP 250,000 to unregistered vendor",
                         fraud_type="False Invoice", severity="Critical",
                         detected_by="Fraud Detection AI Agent",
                         amount_involved=250000.0, investigation_status="Under Investigation"))
        db.add(FraudCase(case_number="FC-2026-002",
                         title="Expense Report Anomalies",
                         description="Duplicate expense claims totaling EGP 12,500",
                         fraud_type="Expense Fraud", severity="Medium",
                         detected_by="Journal Entry Audit Agent",
                         amount_involved=12500.0, investigation_status="Open"))

        db.add(TaxCompliance(company_id=company.id, tax_type="VAT", tax_period="2026-Q1",
                             status="Filed", due_date=datetime.now() + timedelta(days=15), declared_amount=85000.0))
        db.add(TaxCompliance(company_id=company.id, tax_type="Corporate Tax", tax_period="2025",
                             status="Paid", due_date=datetime.now() - timedelta(days=10),
                             declared_amount=320000.0))
        db.add(TaxCompliance(company_id=company.id, tax_type="Payroll Tax", tax_period="2026-03",
                             status="Pending", due_date=datetime.now() + timedelta(days=5), declared_amount=28000.0))

        db.commit()
        logger.info("Created sample audit project with 5 findings, 2 fraud cases, 3 tax records")
