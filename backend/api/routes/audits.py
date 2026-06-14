"""
Finovate Audit Nexus AI - Audit API Routes
REST API endpoints for audit operations
Enterprise AI Financial Audit & Intelligence Platform
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger
import uuid

from backend.ai_engine.engine_v2 import get_ai_engine_v2
from backend.agents.enhanced_agent_base import AgentResult
from backend.agents.fraud_agent.enhanced_agent import EnhancedFraudDetectionAgent
from backend.agents.compliance_agent.enhanced_agent import EnhancedComplianceAgent

router = APIRouter(prefix="/api/audits", tags=["audits"])

# In-memory storage for audit results (in production, use a database)
audit_storage: Dict[str, Dict[str, Any]] = {}


class AuditRequest:
    """Request model for audit operations"""
    def __init__(
        self,
        project_id: str,
        financial_data: Dict[str, Any],
        audit_type: str = "full",
        standards: Optional[List[str]] = None,
        llm_provider: Optional[str] = None
    ):
        self.project_id = project_id
        self.financial_data = financial_data
        self.audit_type = audit_type
        self.standards = standards or ["IFRS"]
        self.llm_provider = llm_provider


class AuditResponse:
    """Response model for audit operations"""
    def __init__(
        self,
        audit_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None
    ):
        self.audit_id = audit_id
        self.status = status
        self.result = result
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "status": self.status,
            "result": self.result,
            "timestamp": self.timestamp
        }


@router.post("/start")
async def start_audit(
    project_id: str,
    financial_data: Dict[str, Any],
    audit_type: str = Query("full", regex="^(full|fraud|compliance|risk)$"),
    standards: Optional[List[str]] = None,
    llm_provider: Optional[str] = None
) -> Dict[str, Any]:
    """
    Start a new audit
    
    Args:
        project_id: Project identifier
        financial_data: Financial data to audit
        audit_type: Type of audit (full, fraud, compliance, risk)
        standards: Accounting standards to check against
        llm_provider: Preferred LLM provider
    
    Returns:
        Audit response with audit ID and status
    """
    try:
        audit_id = str(uuid.uuid4())
        logger.info(f"Starting audit: {audit_id}, type: {audit_type}")

        # Create audit request
        request = AuditRequest(
            project_id=project_id,
            financial_data=financial_data,
            audit_type=audit_type,
            standards=standards,
            llm_provider=llm_provider
        )

        # Store audit in memory
        audit_storage[audit_id] = {
            "audit_id": audit_id,
            "project_id": project_id,
            "audit_type": audit_type,
            "status": "running",
            "created_at": datetime.now().isoformat(),
            "result": None
        }

        # Execute audit based on type
        if audit_type == "fraud":
            agent = EnhancedFraudDetectionAgent(llm_provider=llm_provider)
            result = await agent.execute(financial_data=financial_data)
        elif audit_type == "compliance":
            agent = EnhancedComplianceAgent(llm_provider=llm_provider)
            result = await agent.execute(
                financial_data=financial_data,
                standards=standards or ["IFRS"]
            )
        else:
            # Full audit - run both
            fraud_agent = EnhancedFraudDetectionAgent(llm_provider=llm_provider)
            compliance_agent = EnhancedComplianceAgent(llm_provider=llm_provider)

            fraud_result = await fraud_agent.execute(financial_data=financial_data)
            compliance_result = await compliance_agent.execute(
                financial_data=financial_data,
                standards=standards or ["IFRS"]
            )

            result = AgentResult(
                success=fraud_result.success and compliance_result.success,
                data={
                    "fraud_analysis": fraud_result.data,
                    "compliance_analysis": compliance_result.data
                },
                message="Full audit completed",
                ai_insights=f"Fraud: {fraud_result.ai_insights}\nCompliance: {compliance_result.ai_insights}",
                confidence_score=(fraud_result.confidence_score + compliance_result.confidence_score) / 2
            )

        # Update audit status
        audit_storage[audit_id]["status"] = "completed" if result.success else "failed"
        audit_storage[audit_id]["result"] = result.to_dict()

        logger.info(f"Audit completed: {audit_id}, success: {result.success}")

        return {
            "success": True,
            "data": {
                "audit_id": audit_id,
                "status": audit_storage[audit_id]["status"],
                "result": audit_storage[audit_id]["result"]
            }
        }

    except Exception as e:
        logger.error(f"Error starting audit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{audit_id}/status")
async def get_audit_status(audit_id: str) -> Dict[str, Any]:
    """
    Get the status of an audit
    
    Args:
        audit_id: Audit identifier
    
    Returns:
        Audit status and metadata
    """
    try:
        if audit_id not in audit_storage:
            raise HTTPException(status_code=404, detail="Audit not found")

        audit = audit_storage[audit_id]
        logger.info(f"Retrieved audit status: {audit_id}")

        return {
            "success": True,
            "data": {
                "audit_id": audit_id,
                "status": audit["status"],
                "created_at": audit["created_at"],
                "project_id": audit["project_id"],
                "audit_type": audit["audit_type"]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{audit_id}/results")
async def get_audit_results(audit_id: str) -> Dict[str, Any]:
    """
    Get the results of a completed audit
    
    Args:
        audit_id: Audit identifier
    
    Returns:
        Audit results and analysis
    """
    try:
        if audit_id not in audit_storage:
            raise HTTPException(status_code=404, detail="Audit not found")

        audit = audit_storage[audit_id]

        if audit["status"] != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Audit is still {audit['status']}"
            )

        logger.info(f"Retrieved audit results: {audit_id}")

        return {
            "success": True,
            "data": {
                "audit_id": audit_id,
                "status": audit["status"],
                "result": audit["result"],
                "created_at": audit["created_at"]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_audits(
    project_id: Optional[str] = None,
    audit_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
) -> Dict[str, Any]:
    """
    List audits with optional filtering
    
    Args:
        project_id: Filter by project ID
        audit_type: Filter by audit type
        status: Filter by status
        limit: Maximum number of results
        offset: Number of results to skip
    
    Returns:
        List of audits matching the filters
    """
    try:
        audits = list(audit_storage.values())

        # Apply filters
        if project_id:
            audits = [a for a in audits if a["project_id"] == project_id]
        if audit_type:
            audits = [a for a in audits if a["audit_type"] == audit_type]
        if status:
            audits = [a for a in audits if a["status"] == status]

        # Sort by creation date (newest first)
        audits.sort(key=lambda x: x["created_at"], reverse=True)

        # Apply pagination
        total = len(audits)
        audits = audits[offset:offset + limit]

        logger.info(f"Listed {len(audits)} audits")

        return {
            "success": True,
            "data": {
                "audits": audits,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        }

    except Exception as e:
        logger.error(f"Error listing audits: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{audit_id}")
async def delete_audit(audit_id: str) -> Dict[str, Any]:
    """
    Delete an audit
    
    Args:
        audit_id: Audit identifier
    
    Returns:
        Success status
    """
    try:
        if audit_id not in audit_storage:
            raise HTTPException(status_code=404, detail="Audit not found")

        del audit_storage[audit_id]
        logger.info(f"Deleted audit: {audit_id}")

        return {
            "success": True,
            "data": {"message": "Audit deleted successfully"}
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting audit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_audit_summary() -> Dict[str, Any]:
    """
    Get summary statistics for all audits
    
    Returns:
        Summary statistics
    """
    try:
        audits = list(audit_storage.values())

        summary = {
            "total_audits": len(audits),
            "completed_audits": len([a for a in audits if a["status"] == "completed"]),
            "failed_audits": len([a for a in audits if a["status"] == "failed"]),
            "running_audits": len([a for a in audits if a["status"] == "running"]),
            "by_type": {
                "fraud": len([a for a in audits if a["audit_type"] == "fraud"]),
                "compliance": len([a for a in audits if a["audit_type"] == "compliance"]),
                "full": len([a for a in audits if a["audit_type"] == "full"]),
                "risk": len([a for a in audits if a["audit_type"] == "risk"])
            }
        }

        logger.info("Retrieved audit summary")

        return {
            "success": True,
            "data": summary
        }

    except Exception as e:
        logger.error(f"Error getting audit summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
