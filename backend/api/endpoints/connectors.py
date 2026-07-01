"""
Connectors API Endpoints
نقاط نهاية API لإدارة موصلات ERP
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services import get_connector_service

router = APIRouter()

_service = None


def _get_service():
    global _service
    if _service is None:
        ConnectorService = get_connector_service()
        _service = ConnectorService()
    return _service


class ConnectorCreate(BaseModel):
    connector_name: str
    connector_type: str
    company_id: int = 1
    config: Dict[str, Any] = {}


@router.get("/connectors")
async def list_connectors(company_id: Optional[int] = None):
    service = _get_service()
    connectors = service.list_connectors(company_id)
    return {"success": True, "data": connectors}


@router.post("/connectors")
async def register_connector(body: ConnectorCreate):
    service = _get_service()
    try:
        connector = service.register_connector(
            connector_name=body.connector_name,
            connector_type=body.connector_type,
            config=body.config,
            company_id=body.company_id,
        )
        return {"success": True, "data": connector}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/connectors/{connector_id}/test")
async def test_connector(connector_id: str):
    service = _get_service()
    ok = service.connect(connector_id)
    return {
        "success": ok,
        "data": {
            "connector_id": connector_id,
            "status": "connected" if ok else "failed",
        },
    }


@router.post("/connectors/{connector_id}/sync")
async def sync_connector(connector_id: str):
    service = _get_service()
    if connector_id not in service.registered_connectors:
        raise HTTPException(status_code=404, detail="Connector not found")
    result = service.sync_data(connector_id, data_types=['journal_entries', 'trial_balance', 'accounts'])
    return {"success": True, "data": result}


@router.delete("/connectors/{connector_id}")
async def delete_connector(connector_id: str):
    service = _get_service()
    if connector_id not in service.registered_connectors:
        raise HTTPException(status_code=404, detail="Connector not found")
    service.disconnect(connector_id)
    del service.registered_connectors[connector_id]
    return {"success": True, "data": {"connector_id": connector_id, "deleted": True}}
