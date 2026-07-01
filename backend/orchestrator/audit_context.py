"""
Finovate Audit Nexus AI - Inter-Agent Audit Context
بروتوكول مشاركة السياق بين الوكلاء الذكية

Provides a typed shared context that flows through the audit pipeline,
enabling agents to publish results and consume outputs from other agents.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class AgentOutput:
    """Standardized output envelope for any agent execution."""
    agent_name: str
    status: str = "pending"  # pending | running | completed | error
    risk_score: Optional[float] = None
    findings: List[Dict[str, Any]] = field(default_factory=list)
    summary: Optional[str] = None
    raw_result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AuditContext:
    """
    Shared audit context passed between agents.

    Carries raw input data, normalized DataFrames, and results from
    every agent execution. Agents read their inputs from this context
    and write their outputs back.
    """
    workflow_id: str = ""
    status: str = "initialized"
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None

    raw_data: Dict[str, Any] = field(default_factory=dict)

    agent_outputs: Dict[str, AgentOutput] = field(default_factory=dict)

    consolidated_findings: List[Dict[str, Any]] = field(default_factory=list)
    overall_risk_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)

    def register_agent_output(self, agent_name: str, output: AgentOutput):
        self.agent_outputs[agent_name] = output

    def get_agent_output(self, agent_name: str) -> Optional[AgentOutput]:
        return self.agent_outputs.get(agent_name)

    def get_findings_from(self, agent_name: str) -> List[Dict[str, Any]]:
        out = self.agent_outputs.get(agent_name)
        return out.findings if out else []

    @property
    def all_findings(self) -> List[Dict[str, Any]]:
        result = []
        for out in self.agent_outputs.values():
            result.extend(out.findings)
        return result

    @property
    def completed_agents(self) -> List[str]:
        return [name for name, out in self.agent_outputs.items()
                if out.status == "completed"]

    @property
    def failed_agents(self) -> List[str]:
        return [name for name, out in self.agent_outputs.items()
                if out.status == "error"]
