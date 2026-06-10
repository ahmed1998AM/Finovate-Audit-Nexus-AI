"""
Database Manager for Finovate Audit Nexus AI
"""
import os
from typing import Any, List, Dict, Optional
from sqlalchemy import create_all, create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.models.schema import Base, Engagement, Finding, FinancialData, Anomaly, RiskAssessment

class DatabaseManager:
    def __init__(self, db_url: str = None):
        if not db_url:
            db_url = os.getenv("DATABASE_URL", "sqlite:///./audit_nexus.db")
        
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self) -> Session:
        return self.SessionLocal()

    def save_financial_data(self, session: Session, data: List[Dict[str, Any]], source: str):
        for item in data:
            db_item = FinancialData(
                source_system=source,
                entity_type=item.get("entity_type", "transaction"),
                entity_id=item.get("doc_number", item.get("id", "unknown")),
                fiscal_year=int(item.get("fiscal_year", 2024)),
                period=int(item.get("period", 1)),
                amount=float(item.get("amount", 0)),
                currency=item.get("currency", "EGP"),
                data_json=item
            )
            session.add(db_item)
        session.commit()

    def save_anomalies(self, session: Session, anomalies: List[Dict[str, Any]]):
        for item in anomalies:
            db_item = Anomaly(
                anomaly_type=item.get("type", "unknown"),
                severity=item.get("severity", "medium"),
                description=item.get("description", ""),
                transaction_ids=item.get("transaction_ids", []),
                investigated=False
            )
            session.add(db_item)
        session.commit()

    def save_risk_assessment(self, session: Session, assessment: Dict[str, Any], engagement_id: int):
        db_item = RiskAssessment(
            engagement_id=engagement_id,
            risk_area="Overall",
            risk_level=assessment.get("risk_level", "low"),
            risk_score=assessment.get("overall_risk_score", 0.0),
            mitigation_strategy="\n".join(assessment.get("recommendations", []))
        )
        session.add(db_item)
        session.commit()

# Singleton instance
_db_manager_instance = None

def get_db_manager() -> DatabaseManager:
    global _db_manager_instance
    if _db_manager_instance is None:
        _db_manager_instance = DatabaseManager()
    return _db_manager_instance
