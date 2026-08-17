"""
Finovate Audit Nexus AI - Multi-Agent Orchestrator

نظام تنسيق وإدارة الوكلاء الذكية المتعددة
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from loguru import logger

from backend.orchestrator.audit_context import AgentOutput, AuditContext


class AgentOrchestrator:
    """
    منسق الوكلاء الذكية

    المهام:
    - إدارة كل الوكلاء
    - تنسيق العمل بين الوكلاء
    - تجميع النتائج
    - إدارة سير العمل
    - توزيع المهام
    """

    def __init__(self, auto_register_agents: bool = True):
        self.orchestrator_id = "chief_orchestrator_001"
        self.agents = {}
        self.active_workflows = []
        self.status = "initialized"
        self.workflow_configs = {}  # Custom workflow configurations

        logger.info(f"Agent Orchestrator initialized: {self.orchestrator_id}")

        # Auto-register all agents if requested
        if auto_register_agents:
            self._auto_register_all_agents()

    def _auto_register_all_agents(self) -> int:
        """تسجيل جميع الوكلاء تلقائياً"""
        try:
            from backend.orchestrator.agent_registry import register_agents_in_orchestrator
            count = register_agents_in_orchestrator(self)
            logger.info(f"Auto-registered {count} agents")
            return count
        except Exception as e:
            logger.error(f"Failed to auto-register agents: {str(e)}")
            return 0

    def register_agent(self, agent_name: str, agent_instance: Any) -> bool:
        """تسجيل وكيل في النظام"""
        try:
            self.agents[agent_name] = {
                "instance": agent_instance,
                "status": "registered",
                "registered_at": datetime.now().isoformat()
            }
            logger.info(f"Agent registered: {agent_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register agent {agent_name}: {str(e)}")
            return False

    def register_workflow_config(self, workflow_name: str, config: Dict[str, Any]) -> bool:
        """تسجيل تكوين سير عمل مخصص"""
        try:
            self.workflow_configs[workflow_name] = config
            logger.info(f"Workflow config registered: {workflow_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register workflow config {workflow_name}: {str(e)}")
            return False

    def get_workflow_config(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """الحصول على تكوين سير عمل"""
        return self.workflow_configs.get(workflow_name)

    @staticmethod
    def _normalize_to_dataframe(data: Any) -> pd.DataFrame:
        """تحويل البيانات إلى DataFrame إذا لم تكن كذلك"""
        if data is None:
            return pd.DataFrame()
        if isinstance(data, pd.DataFrame):
            return data
        if isinstance(data, dict):
            return pd.DataFrame([data])
        if isinstance(data, list):
            return pd.DataFrame(data)
        return pd.DataFrame()

    @staticmethod
    def _extract_kwargs(agent_name: str, audit_data: dict, data_key: str) -> dict:
        """استخراج الوسائط المسماة لكل وكيل حسب توقيع دالته"""
        param_map = {
            "journal_agent": "entries",
            "ledger_agent": "ledger_data",
            "tb_agent": "tb_data",
            "tax_agent": "transactions",
            "fs_agent": "data",
            "bank_agent": "bank_statement",
        }
        if agent_name == "inventory_agent":
            base_data = audit_data.get(data_key)
            kwargs = {"inventory_data": AgentOrchestrator._normalize_to_dataframe(base_data)}
            movement = audit_data.get("inventory_movement")
            if movement is not None:
                kwargs["movement_data"] = AgentOrchestrator._normalize_to_dataframe(movement)
            kwargs["warehouse_name"] = audit_data.get("warehouse_name", "Main Warehouse")
            return kwargs
        param_name = param_map.get(agent_name, "data")
        raw = audit_data.get(data_key)
        # fs_agent expects raw dict, others get DataFrame
        if agent_name == "fs_agent":
            return {param_name: raw} if raw is not None else {param_name: {}}
        return {param_name: AgentOrchestrator._normalize_to_dataframe(raw)}

    async def execute_audit_workflow(self, audit_data: Dict[str, Any], workflow_name: str = "default") -> Dict[str, Any]:
        """
        تنفيذ سير عمل المراجعة الكاملة باستخدام AuditContext

        Args:
            audit_data: بيانات المراجعة
            workflow_name: اسم سير العمل المخصص (اختياري)

        Returns:
            dict: نتائج المراجعة الشاملة
        """
        ctx = AuditContext(
            workflow_id=f"wf_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            status="executing",
            raw_data=audit_data,
        )
        logger.info(f"Starting audit workflow: {workflow_name}")
        self.status = "executing"

        try:
            # Use custom workflow config if provided
            config = self.get_workflow_config(workflow_name)
            if config:
                await self._run_custom_workflow(ctx, audit_data, config)
            else:
                await self._run_stage_core(ctx, audit_data)
                await self._run_stage_intelligence(ctx)
            self._finalize_context(ctx)

            self.status = "completed"
            logger.info(f"Audit workflow completed. Risk Score: {ctx.overall_risk_score}")

        except Exception as e:
            logger.error(f"Error during audit workflow: {str(e)}")
            ctx.status = "error"
            self.status = "error"

        return self._context_to_dict(ctx)

    async def _run_stage_core(self, ctx: AuditContext, audit_data: Dict[str, Any]):
        """Stage 1: Execute core audit agents in parallel."""
        configs = [
            ("journal_agent", "analyze_journal_entries", "journal_entries"),
            ("ledger_agent", "analyze_ledger", "ledger_data"),
            ("tb_agent", "analyze_trial_balance", "trial_balance"),
            ("tax_agent", "analyze_vat_compliance", "vat_transactions"),
            ("fs_agent", "analyze_financial_statements", "financial_statements"),
            ("bank_agent", "analyze_bank_statement", "bank_transactions"),
            ("inventory_agent", "analyze_inventory", "inventory_data"),
        ]
        tasks = []
        names = []
        for agent_name, method_name, data_key in configs:
            if agent_name not in self.agents:
                continue
            inst = self.agents[agent_name]["instance"]
            method = getattr(inst, method_name, None)
            if method is None:
                continue
            kwargs = self._extract_kwargs(agent_name, audit_data, data_key)
            logger.info(f"Queueing core agent {agent_name}...")
            if asyncio.iscoroutinefunction(method):
                tasks.append(method(**kwargs))
            else:
                tasks.append(asyncio.to_thread(method, **kwargs))
            names.append(agent_name)
        if tasks:
            logger.info(f"Executing {len(tasks)} core agents in parallel...")
            for name, result in zip(names, await asyncio.gather(*tasks, return_exceptions=True)):
                self._record_result(ctx, name, result)

    async def _run_stage_intelligence(self, ctx: AuditContext):
        """Stage 2: Execute intelligence agents that consume core results."""
        configs = [
            ("fraud_agent", "detect_fraud"),
            ("risk_agent", "assess_risks"),
            ("compliance_agent", "check_compliance"),
        ]
        combined = {**ctx.raw_data, "core_results": {name: out.raw_result for name, out in ctx.agent_outputs.items()}}
        tasks = []
        names = []
        for agent_name, method_name in configs:
            if agent_name not in self.agents:
                continue
            inst = self.agents[agent_name]["instance"]
            method = getattr(inst, method_name, None)
            if method is None:
                continue
            logger.info(f"Queueing intelligence agent {agent_name}...")
            if asyncio.iscoroutinefunction(method):
                tasks.append(method(combined))
            else:
                tasks.append(asyncio.to_thread(method, combined))
            names.append(agent_name)
        if tasks:
            logger.info(f"Executing {len(tasks)} intelligence agents...")
            for name, result in zip(names, await asyncio.gather(*tasks, return_exceptions=True)):
                self._record_result(ctx, name, result)

    async def _run_custom_workflow(self, ctx: AuditContext, audit_data: Dict[str, Any], config: Dict[str, Any]):
        """Execute a custom workflow based on configuration."""
        stages = config.get("stages", [])
        for stage in stages:
            stage_name = stage.get("name", "unnamed")
            agent_configs = stage.get("agents", [])
            parallel = stage.get("parallel", True)
            
            logger.info(f"Running custom stage: {stage_name}")
            tasks = []
            names = []
            
            for agent_cfg in agent_configs:
                agent_name = agent_cfg.get("name")
                method_name = agent_cfg.get("method")
                data_key = agent_cfg.get("data_key")
                
                if agent_name not in self.agents:
                    continue
                inst = self.agents[agent_name]["instance"]
                method = getattr(inst, method_name, None)
                if method is None:
                    continue
                    
                kwargs = self._extract_kwargs(agent_name, audit_data, data_key) if data_key else {}
                logger.info(f"Queueing agent {agent_name} in stage {stage_name}...")
                
                if asyncio.iscoroutinefunction(method):
                    tasks.append(method(**kwargs))
                else:
                    tasks.append(asyncio.to_thread(method, **kwargs))
                names.append(agent_name)
            
            if tasks:
                if parallel:
                    logger.info(f"Executing {len(tasks)} agents in parallel...")
                    for name, result in zip(names, await asyncio.gather(*tasks, return_exceptions=True)):
                        self._record_result(ctx, name, result)
                else:
                    logger.info(f"Executing {len(tasks)} agents sequentially...")
                    for name, task in zip(names, tasks):
                        result = await task if asyncio.iscoroutinefunction(task) else task
                        self._record_result(ctx, name, result)

    def _record_result(self, ctx: AuditContext, agent_name: str, result: Any):
        """Record an agent's result into the shared context."""
        if isinstance(result, Exception):
            logger.error(f"Agent {agent_name} failed: {str(result)}")
            ctx.register_agent_output(agent_name, AgentOutput(
                agent_name=agent_name, status="error", error=str(result)))
            return
        out = AgentOutput(
            agent_name=agent_name,
            status="completed",
            raw_result=result if isinstance(result, dict) else {},
        )
        if isinstance(result, dict):
            out.risk_score = result.get("risk_score")
            out.summary = result.get("summary") or result.get("status")
            out.findings = self._extract_findings(agent_name, result)
        ctx.register_agent_output(agent_name, out)

    def _extract_findings(self, agent_name: str, result: dict) -> List[Dict[str, Any]]:
        """Extract structured findings from a raw agent result."""
        findings = []
        for key, severity in [("duplicate_entries", "medium"), ("suspicious_entries", "high"),
                              ("risks", "medium"), ("anomalies", "medium"),
                              ("discrepancies", "high"), ("timing_anomalies", "medium"),
                              ("user_anomalies", "medium"), ("round_amount_entries", "medium"),
                              ("suspicious_activities", "high"), ("issues", "medium"),
                              ("warnings", "low")]:
            for item in (result.get(key) or []):
                findings.append({
                    "source_agent": agent_name,
                    "finding_type": key.rstrip("s"),
                    "severity": item.get("severity", severity) if isinstance(item, dict) else severity,
                    "details": item,
                })
        return findings

    def _finalize_context(self, ctx: AuditContext):
        """Consolidate findings, compute risk, and generate recommendations."""
        ctx.consolidated_findings = ctx.all_findings
        scores = [out.risk_score for out in ctx.agent_outputs.values()
                  if out.risk_score is not None]
        if scores:
            ctx.overall_risk_score = min(100.0, sum(scores) / len(scores))
        ctx.recommendations = self._generate_recommendations_from(ctx)
        ctx.end_time = datetime.now().isoformat()
        ctx.status = "completed"

    def _generate_recommendations_from(self, ctx: AuditContext) -> List[str]:
        """توليد التوصيات بناءً على سياق النتائج المجمعة"""
        recs = []
        risk = ctx.overall_risk_score
        if risk >= 75:
            recs.append("URGENT: High overall risk detected. Immediate review required.")
        elif risk >= 50:
            recs.append("WARNING: Moderate risk level. Detailed review recommended.")
        elif risk >= 25:
            recs.append("CAUTION: Some issues detected. Standard review advised.")
        else:
            recs.append("Low risk level. Continue with standard monitoring.")

        findings = ctx.consolidated_findings
        dcount = sum(1 for f in findings if f.get("finding_type") in ("duplicate", "duplicate_entries"))
        if dcount:
            recs.append(f"Investigate {dcount} duplicate entry findings.")
        scount = sum(1 for f in findings if f.get("finding_type") in ("suspicious", "suspicious_entries", "high"))
        if scount:
            recs.append(f"Review {scount} suspicious entries for potential fraud.")

        for out in ctx.agent_outputs.values():
            if out.status == "error":
                recs.append(f"Agent '{out.agent_name}' encountered an error: {out.error}")
        return recs

    @staticmethod
    def _context_to_dict(ctx: AuditContext) -> Dict[str, Any]:
        """Serialize the AuditContext back to a plain dict for API responses."""
        return {
            "workflow_id": ctx.workflow_id,
            "start_time": ctx.start_time,
            "end_time": ctx.end_time,
            "status": ctx.status,
            "agent_results": {name: out.raw_result for name, out in ctx.agent_outputs.items()},
            "consolidated_findings": ctx.consolidated_findings,
            "overall_risk_score": ctx.overall_risk_score,
            "recommendations": ctx.recommendations,
            "agent_statuses": {name: {"status": out.status, "risk_score": out.risk_score, "error": out.error}
                               for name, out in ctx.agent_outputs.items()},
        }

    def get_registered_agents(self) -> Dict[str, Any]:
        """الحصول على قائمة الوكلاء المسجلين"""
        return {
            name: {
                "status": info["status"],
                "registered_at": info["registered_at"]
            }
            for name, info in self.agents.items()
        }

    def get_status(self) -> Dict[str, Any]:
        """الحصول على حالة المنسق"""
        return {
            "orchestrator_id": self.orchestrator_id,
            "status": self.status,
            "registered_agents_count": len(self.agents),
            "active_workflows_count": len(self.active_workflows)
        }


# مثال للاستخدام
if __name__ == "__main__":
    async def main():
        orchestrator = AgentOrchestrator()
        print(f"Orchestrator Status: {orchestrator.get_status()}")

    asyncio.run(main())
