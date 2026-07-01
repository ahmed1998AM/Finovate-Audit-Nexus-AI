"""
Finovate Audit Nexus AI - Task Queue API Endpoints
نقاط API لإدارة المهام غير المتزامنة
"""

from typing import Optional

from fastapi import APIRouter, HTTPException

from backend.core.tasks import TaskStatus, get_task_queue

router = APIRouter()


@router.post("/submit")
async def submit_task(name: str):
    queue = get_task_queue()
    task_id = queue.submit(name, lambda: None)
    return {"success": True, "data": {"task_id": task_id}}


@router.get("/{task_id}")
async def get_task(task_id: str):
    queue = get_task_queue()
    task = queue.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True, "data": {
        "task_id": task.task_id,
        "name": task.name,
        "status": task.status.value,
        "created_at": task.created_at.isoformat(),
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "error": task.error,
    }}


@router.get("/{task_id}/result")
async def get_task_result(task_id: str):
    queue = get_task_queue()
    result = queue.get_result(task_id)
    if result is None:
        task = queue.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.status == TaskStatus.RUNNING:
            raise HTTPException(status_code=202, detail="Task still running")
        if task.status == TaskStatus.FAILED:
            raise HTTPException(status_code=422, detail=f"Task failed: {task.error}")
    return {"success": True, "data": {"result": result}}


@router.post("/{task_id}/cancel")
async def cancel_task(task_id: str):
    queue = get_task_queue()
    if queue.cancel(task_id):
        return {"success": True, "message": "Task cancelled"}
    raise HTTPException(status_code=404, detail="Task not found or already completed")


@router.get("")
async def list_tasks(status: Optional[str] = None, limit: int = 50):
    queue = get_task_queue()
    task_status = TaskStatus(status) if status else None
    return {"success": True, "data": queue.list_tasks(task_status, limit)}
