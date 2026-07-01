"""
Finovate Audit Nexus AI - Audit Findings API Endpoints
Audit Findings Management
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.database.models import AuditFinding as FindingModel

router = APIRouter()

class FindingCreate(BaseModel):
    project_id: int
    title: str
    description: str
    category: str
    severity: str
    financial_impact: Optional[float] = None
    recommendation: Optional[str] = None

class FindingResponse(BaseModel):
    id: int
    project_id: int
    finding_number: str
    title: str
    description: str
    category: str
    severity: str
    status: str
    created_at: datetime

@router.get("/", response_model=List[FindingResponse])
async def get_findings(project_id: int = None, severity: str = None, db: Session = Depends(get_db)):
    query = db.query(FindingModel)
    if project_id:
        query = query.filter(FindingModel.project_id == project_id)
    if severity:
        query = query.filter(FindingModel.severity == severity)
    findings = query.order_by(FindingModel.created_at.desc()).all()
    return [
        FindingResponse(
            id=f.id, project_id=f.project_id, finding_number=f.finding_number,
            title=f.title, description=f.description, category=f.category,
            severity=f.severity, status=f.status, created_at=f.created_at
        ) for f in findings
    ]

@router.post("/", response_model=FindingResponse, status_code=status.HTTP_201_CREATED)
async def create_finding(finding: FindingCreate, db: Session = Depends(get_db)):
    count = db.query(FindingModel).filter(FindingModel.project_id == finding.project_id).count()
    fnum = f"F-{datetime.now().year}-{count + 1:04d}"
    db_finding = FindingModel(
        project_id=finding.project_id, title=finding.title,
        description=finding.description, category=finding.category,
        severity=finding.severity, finding_number=fnum, status="Open",
        financial_impact=finding.financial_impact, recommendation=finding.recommendation
    )
    db.add(db_finding)
    db.commit()
    db.refresh(db_finding)
    return FindingResponse(
        id=db_finding.id, project_id=db_finding.project_id,
        finding_number=db_finding.finding_number, title=db_finding.title,
        description=db_finding.description, category=db_finding.category,
        severity=db_finding.severity, status=db_finding.status,
        created_at=db_finding.created_at
    )

@router.put("/{finding_id}/status")
async def update_finding_status(finding_id: int, status: str, db: Session = Depends(get_db)):
    finding = db.query(FindingModel).filter(FindingModel.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    finding.status = status
    db.commit()
    return {"success": True, "message": f"Finding {finding_id} status updated to {status}"}

@router.delete("/{finding_id}")
async def delete_finding(finding_id: int, db: Session = Depends(get_db)):
    finding = db.query(FindingModel).filter(FindingModel.id == finding_id).first()
    if finding:
        db.delete(finding)
        db.commit()
    return {"success": True, "message": "Finding deleted successfully"}
