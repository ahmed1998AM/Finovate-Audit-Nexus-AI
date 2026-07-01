"""
Finovate Audit Nexus AI - Predictive Analytics API Endpoints
نقاط نهاية API للتحليل التنبؤي
"""
from typing import Any, Dict, List

from fastapi import APIRouter

from backend.services.predictive_service import PredictiveService

router = APIRouter()
_service = PredictiveService()

@router.post("/predictive/revenue")
async def predict_revenue(historical_data: List[float], periods: int = 12):
    result = _service.predict_revenue(historical_data, periods)
    return {"success": True, "data": result}

@router.post("/predictive/fraud-risk")
async def predict_fraud_risk(transaction_patterns: Dict[str, Any]):
    result = _service.predict_fraud_risk(transaction_patterns)
    return {"success": True, "data": result}

@router.post("/predictive/cash-flow")
async def predict_cash_flow(cash_flow_history: List[float]):
    result = _service.predict_cash_flow_issues(cash_flow_history)
    return {"success": True, "data": result}
