"""
Finovate Audit Nexus AI - Audit Projects API Endpoints
Audit Project Management
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.database.models import AuditFinding
from backend.database.models import AuditProject as AuditProjectModel

router = APIRouter()

class AuditProjectCreate(BaseModel):
    company_id: int
    project_name: str
    audit_type: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    scope: Optional[str] = None
    objectives: Optional[str] = None

class AuditProjectResponse(BaseModel):
    id: int
    company_id: int
    project_name: str
    audit_type: str
    status: str
    risk_level: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime

@router.get("/", response_model=List[AuditProjectResponse])
async def get_audit_projects(status_filter: str = None, db: Session = Depends(get_db)):
    query = db.query(AuditProjectModel)
    if status_filter:
        query = query.filter(AuditProjectModel.status == status_filter)
    projects = query.order_by(AuditProjectModel.created_at.desc()).all()
    return [
        AuditProjectResponse(
            id=p.id, company_id=p.company_id, project_name=p.project_name,
            audit_type=p.audit_type, status=p.status, risk_level=p.risk_level,
            start_date=p.start_date, end_date=p.end_date, created_at=p.created_at
        ) for p in projects
    ]

@router.post("/", response_model=AuditProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_audit_project(project: AuditProjectCreate, db: Session = Depends(get_db)):
    db_project = AuditProjectModel(
        company_id=project.company_id, project_name=project.project_name,
        audit_type=project.audit_type, status="Planning", risk_level="Medium",
        start_date=project.start_date, end_date=project.end_date,
        scope=project.scope, objectives=project.objectives
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return AuditProjectResponse(
        id=db_project.id, company_id=db_project.company_id,
        project_name=db_project.project_name, audit_type=db_project.audit_type,
        status=db_project.status, risk_level=db_project.risk_level,
        start_date=db_project.start_date, end_date=db_project.end_date,
        created_at=db_project.created_at
    )

@router.get("/{project_id}")
async def get_audit_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(AuditProjectModel).filter(AuditProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "id": project.id, "company_id": project.company_id,
        "project_name": project.project_name, "audit_type": project.audit_type,
        "status": project.status, "risk_level": project.risk_level,
        "scope": project.scope, "objectives": project.objectives,
        "start_date": project.start_date, "end_date": project.end_date,
        "created_at": project.created_at, "updated_at": project.updated_at
    }

@router.get("/{project_id}/findings")
async def get_project_findings(project_id: int, db: Session = Depends(get_db)):
    findings = db.query(AuditFinding).filter(AuditFinding.project_id == project_id).all()
    return {
        "findings": [
            {
                "id": f.id, "finding_number": f.finding_number, "title": f.title,
                "description": f.description, "category": f.category,
                "severity": f.severity, "status": f.status,
                "financial_impact": f.financial_impact, "recommendation": f.recommendation
            } for f in findings
        ]
    }

@router.get("/{project_id}/workpapers")
async def get_project_workpapers(project_id: int, db: Session = Depends(get_db)):
    from backend.database.models import WorkPaper
    workpapers = db.query(WorkPaper).filter(WorkPaper.project_id == project_id).all()
    return {
        "workpapers": [
            {
                "id": w.id, "wp_number": w.wp_number, "title": w.title,
                "wp_type": w.wp_type, "review_status": w.review_status,
                "file_path": w.file_path, "created_at": w.created_at
            } for w in workpapers
        ]
    }
