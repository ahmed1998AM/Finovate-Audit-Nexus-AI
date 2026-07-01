"""
Finovate Audit Nexus AI - Reports API Endpoints
نقاط نهاية API للتقارير
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.database.models import AuditFinding
from backend.services import get_reporting_service

router = APIRouter()

@router.post("/reports/create")
async def create_report(
    project_id: str,
    report_type: str = "audit",
    include_recommendations: bool = True,
    db: Session = Depends(get_db),
):
    findings = db.query(AuditFinding).filter(AuditFinding.project_id == int(project_id)).all() if project_id.isdigit() else []
    ReportingService = get_reporting_service()
    service = ReportingService()
    findings_list = [
        {"severity": f.severity or "low", "description": f.description or "", "recommendation": f.recommendation or ""}
        for f in findings
    ]
    report = service.create_audit_report(project_id, report_type, findings_list, include_recommendations)
    return {"success": True, "data": report}

@router.post("/reports/{report_id}/summary")
async def generate_summary(report_id: str):
    ReportingService = get_reporting_service()
    service = ReportingService()
    summary = service.generate_executive_summary(report_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"success": True, "data": summary}

@router.post("/reports/{report_id}/export")
async def export_report(report_id: str, format: str = "pdf"):
    ReportingService = get_reporting_service()
    service = ReportingService()
    result = service.export_report(report_id, format)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail="Report not found")
    return {"success": True, "data": result}

@router.get("/reports")
async def list_reports(project_id: Optional[str] = None):
    ReportingService = get_reporting_service()
    service = ReportingService()
    reports = service.list_reports(project_id)
    return {"success": True, "data": reports}
