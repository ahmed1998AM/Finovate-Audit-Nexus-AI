import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel

from backend.orchestrator.agent_orchestrator import AgentOrchestrator

router = APIRouter()

_orchestrator: AgentOrchestrator = None

def _get_orchestrator() -> AgentOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator

class AgentTaskRequest(BaseModel):
    agent_name: str
    task_type: str
    parameters: Dict[str, Any] = {}

class AgentStatusResponse(BaseModel):
    agent_name: str
    status: str
    last_execution: Optional[datetime] = None
    tasks_completed: int = 0
    success_rate: float = 0.0

@router.get("/", response_model=List[AgentStatusResponse])
async def get_agents():
    orch = _get_orchestrator()
    agents_list = []
    for name, info in orch.agents.items():
        inst = info.get("instance")
        agents_list.append({
            "agent_name": name,
            "status": info.get("status", "registered"),
            "last_execution": datetime.now(),
            "tasks_completed": getattr(inst, "tasks_completed", 0) if inst else 0,
            "success_rate": getattr(inst, "success_rate", 100.0) if inst else 0.0,
        })
    if not agents_list:
        from backend.orchestrator.agent_registry import register_agents_in_orchestrator
        register_agents_in_orchestrator(orch)
        for name, info in orch.agents.items():
            agents_list.append({
                "agent_name": name,
                "status": info.get("status", "registered"),
                "last_execution": datetime.now(),
                "tasks_completed": 0,
                "success_rate": 100.0,
            })
    return agents_list

@router.get("/{agent_name}/status")
async def get_agent_status(agent_name: str):
    orch = _get_orchestrator()
    info = orch.agents.get(agent_name)
    if not info:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    inst = info.get("instance")
    return {
        "agent_name": agent_name,
        "status": info.get("status", "registered"),
        "class_name": type(inst).__name__ if inst else "",
        "has_execute": hasattr(inst, "execute") if inst else False,
        "has_analyze": hasattr(inst, "analyze") if inst else False,
    }

@router.post("/execute")
async def execute_agent_task(task: AgentTaskRequest):
    orch = _get_orchestrator()
    info = orch.agents.get(task.agent_name)
    if not info:
        from backend.orchestrator.agent_registry import register_agents_in_orchestrator
        register_agents_in_orchestrator(orch)
        info = orch.agents.get(task.agent_name)
    if not info:
        raise HTTPException(status_code=404, detail=f"Agent '{task.agent_name}' not found")
    inst = info.get("instance")
    if inst is None:
        raise HTTPException(status_code=500, detail=f"Agent '{task.agent_name}' failed to load")
    try:
        kwargs = task.parameters or {}
        if hasattr(inst, "execute") and callable(inst.execute):
            if asyncio.iscoroutinefunction(inst.execute):
                result = await inst.execute(**kwargs)
            else:
                result = inst.execute(**kwargs)
        elif hasattr(inst, "analyze") and callable(inst.analyze):
            if asyncio.iscoroutinefunction(inst.analyze):
                result = await inst.analyze(**kwargs)
            else:
                result = inst.analyze(**kwargs)
        else:
            raise HTTPException(status_code=400, detail=f"Agent '{task.agent_name}' has no executable method")
        return {"success": True, "agent_name": task.agent_name, "status": "Completed", "results": result}
    except Exception as e:
        logger.error(f"Agent execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{agent_name}/logs")
async def get_agent_logs(agent_name: str, limit: int = 50):
    orch = _get_orchestrator()
    if agent_name not in orch.agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    return {"agent_name": agent_name, "logs": [], "message": "Logging not yet implemented for individual agents"}

@router.post("/{agent_name}/stop")
async def stop_agent(agent_name: str):
    orch = _get_orchestrator()
    if agent_name not in orch.agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    orch.agents[agent_name]["status"] = "stopped"
    return {"success": True, "message": f"Agent {agent_name} stopped"}

@router.post("/{agent_name}/start")
async def start_agent(agent_name: str):
    orch = _get_orchestrator()
    if agent_name not in orch.agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    orch.agents[agent_name]["status"] = "active"
    return {"success": True, "message": f"Agent {agent_name} started"}
