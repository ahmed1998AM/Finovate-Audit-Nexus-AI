"""
Finovate Audit Nexus AI - Backup Management API Endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.database.backup import create_backup, list_backups, restore_backup

router = APIRouter(prefix="/api/v1/backups", tags=["Backups"])


class RestoreRequest(BaseModel):
    filename: str


@router.get("/")
async def get_backups():
    backups = list_backups()
    return {"success": True, "backups": backups}


@router.post("/create")
async def trigger_backup():
    path = create_backup()
    if path:
        return {"success": True, "path": path, "message": "Backup created successfully"}
    raise HTTPException(status_code=500, detail="Backup failed")


@router.post("/restore")
async def restore(req: RestoreRequest):
    ok = restore_backup(req.filename)
    if ok:
        return {"success": True, "message": f"Restored from {req.filename}"}
    raise HTTPException(status_code=500, detail="Restore failed")
