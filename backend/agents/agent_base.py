"""
Finovate Audit Nexus AI - Base Agent Class
Enterprise AI Financial Audit & Intelligence Platform
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid

class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class AgentResult:
    """Result returned by an agent"""
    success: bool
    data: Any = None
    message: str = ""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "success": self.success,
            "data": self.data,
            "message": self.message,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata,
            "timestamp": datetime.now().isoformat()
        }

class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, name: str, description: str = ""):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.created_at = datetime.now()
        self.last_execution: Optional[datetime] = None
        self.execution_count = 0
        self._context: Dict[str, Any] = {}
    
    @abstractmethod
    def execute(self, **kwargs) -> AgentResult:
        """Execute the agent's main task"""
        pass
    
    @abstractmethod
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters"""
        pass
    
    def set_context(self, key: str, value: Any) -> None:
        """Set a context value"""
        self._context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context value"""
        return self._context.get(key, default)
    
    def clear_context(self) -> None:
        """Clear all context"""
        self._context = {}
    
    def before_execute(self, **kwargs) -> None:
        """Hook called before execution"""
        self.status = AgentStatus.RUNNING
        self.last_execution = datetime.now()
        self.execution_count += 1
    
    def after_execute(self, result: AgentResult) -> None:
        """Hook called after execution"""
        if result.success:
            self.status = AgentStatus.COMPLETED
        else:
            self.status = AgentStatus.FAILED
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "execution_count": self.execution_count
        }
