"""
Finovate Audit Nexus AI - Multi-Agent Orchestrator

نظام تنسيق وإدارة الوكلاء الذكية المتعددة
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger


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
    
    async def execute_audit_workflow(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        تنفيذ سير عمل المراجعة الكاملة
        
        Args:
            audit_data: بيانات المراجعة
            
        Returns:
            dict: نتائج المراجعة الشاملة
        """
        logger.info("Starting comprehensive audit workflow...")
        self.status = "executing"
        
        results = {
            "workflow_id": f"wf_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "status": "in_progress",
            "agent_results": {},
            "consolidated_findings": [],
            "overall_risk_score": 0,
            "recommendations": []
        }
        
        try:
            # Execute core agents in parallel for better performance
            core_tasks = []
            agent_names = []

            # Stage 1: Define core audit tasks
            core_agent_configs = [
                ("journal_agent", "analyze_journal_entries", "journal_entries"),
                ("ledger_agent", "analyze_ledger", "ledger_data"),
                ("tb_agent", "analyze_trial_balance", "trial_balance"),
                ("tax_agent", "analyze_vat_compliance", "vat_transactions"),
                ("fs_agent", "analyze_financial_statements", "financial_statements"),
                ("bank_agent", "analyze_bank_transactions", "bank_transactions"),
                ("inventory_agent", "analyze_inventory", "inventory_data")
            ]

            for agent_name, method_name, data_key in core_agent_configs:
                if agent_name in self.agents:
                    agent_instance = self.agents[agent_name]["instance"]
                    if hasattr(agent_instance, method_name):
                        method = getattr(agent_instance, method_name)
                        data = audit_data.get(data_key)
                        
                        logger.info(f"Queueing {agent_name}...")
                        if asyncio.iscoroutinefunction(method):
                            core_tasks.append(method(data))
                        else:
                            # Wrap sync methods in a thread or just run if lightweight
                            core_tasks.append(asyncio.to_thread(method, data))
                        agent_names.append(agent_name)

            # Execute all core tasks in parallel
            if core_tasks:
                logger.info(f"Executing {len(core_tasks)} core agents in parallel...")
                core_results = await asyncio.gather(*core_tasks, return_exceptions=True)
                
                for name, result in zip(agent_names, core_results):
                    if isinstance(result, Exception):
                        logger.error(f"Agent {name} failed: {str(result)}")
                        results["agent_results"][name] = {"status": "error", "error": str(result)}
                    else:
                        results["agent_results"][name] = result

            # Stage 2: Execute intelligence agents that depend on core results
            intel_tasks = []
            intel_agent_names = []
            
            intel_agent_configs = [
                ("fraud_agent", "detect_fraud"),
                ("risk_agent", "assess_risks"),
                ("compliance_agent", "check_compliance")
            ]
            
            # Combine original data with core results for intelligence agents
            combined_data = {**audit_data, "core_results": results["agent_results"]}
            
            for agent_name, method_name in intel_agent_configs:
                if agent_name in self.agents:
                    agent_instance = self.agents[agent_name]["instance"]
                    if hasattr(agent_instance, method_name):
                        method = getattr(agent_instance, method_name)
                        
                        logger.info(f"Queueing intelligence agent {agent_name}...")
                        if asyncio.iscoroutinefunction(method):
                            intel_tasks.append(method(combined_data))
                        else:
                            intel_tasks.append(asyncio.to_thread(method, combined_data))
                        intel_agent_names.append(agent_name)
            
            if intel_tasks:
                logger.info(f"Executing {len(intel_tasks)} intelligence agents...")
                intel_results = await asyncio.gather(*intel_tasks, return_exceptions=True)
                
                for name, result in zip(intel_agent_names, intel_results):
                    if isinstance(result, Exception):
                        logger.error(f"Intelligence agent {name} failed: {str(result)}")
                        results["agent_results"][name] = {"status": "error", "error": str(result)}
                    else:
                        results["agent_results"][name] = result
            
            # تجميع النتائج
            results["consolidated_findings"] = self._consolidate_findings(results["agent_results"])
            results["overall_risk_score"] = self._calculate_overall_risk(results["agent_results"])
            results["recommendations"] = self._generate_recommendations(results)
            
            results["end_time"] = datetime.now().isoformat()
            results["status"] = "completed"
            self.status = "completed"
            
            logger.info(f"Audit workflow completed. Overall Risk Score: {results['overall_risk_score']}")
            
        except Exception as e:
            logger.error(f"Error during audit workflow: {str(e)}")
            results["status"] = "error"
            results["error"] = str(e)
            self.status = "error"
        
        return results
    
    def _consolidate_findings(self, agent_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """تجميع النتائج من جميع الوكلاء"""
        consolidated = []
        
        for agent_name, results in agent_results.items():
            if isinstance(results, dict):
                # استخراج الاكتشافات من كل وكيل
                findings = []
                
                if "duplicate_entries" in results:
                    for finding in results["duplicate_entries"]:
                        findings.append({
                            "source_agent": agent_name,
                            "finding_type": "duplicate",
                            "severity": finding.get("severity", "medium"),
                            "details": finding
                        })
                
                if "suspicious_entries" in results:
                    for finding in results["suspicious_entries"]:
                        findings.append({
                            "source_agent": agent_name,
                            "finding_type": "suspicious",
                            "severity": "high",
                            "details": finding
                        })
                
                if "risks" in results:
                    for risk in results["risks"]:
                        findings.append({
                            "source_agent": agent_name,
                            "finding_type": "risk",
                            "severity": risk.get("severity", "medium"),
                            "details": risk
                        })
                
                consolidated.extend(findings)
        
        return consolidated
    
    def _calculate_overall_risk(self, agent_results: Dict[str, Any]) -> int:
        """حساب درجة المخاطر الإجمالية"""
        total_risk = 0
        agent_count = 0
        
        for agent_name, results in agent_results.items():
            if isinstance(results, dict):
                # جمع درجات المخاطر من كل وكيل
                if "risk_score" in results:
                    total_risk += results["risk_score"]
                    agent_count += 1
                
                # وكلاء آخرون قد يكون لديهم مقاييس مختلفة
                if "discrepancies" in results:
                    total_risk += len(results["discrepancies"]) * 5
        
        # حساب المتوسط
        if agent_count > 0:
            return min(100, total_risk // agent_count)
        return 0
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """توليد التوصيات بناءً على النتائج"""
        recommendations = []
        
        overall_risk = results.get("overall_risk_score", 0)
        
        if overall_risk >= 75:
            recommendations.append("URGENT: High overall risk detected. Immediate review required.")
        elif overall_risk >= 50:
            recommendations.append("WARNING: Moderate risk level. Detailed review recommended.")
        elif overall_risk >= 25:
            recommendations.append("CAUTION: Some issues detected. Standard review advised.")
        else:
            recommendations.append("Low risk level. Continue with standard monitoring.")
        
        # توصيات محددة بناءً على الاكتشافات
        findings = results.get("consolidated_findings", [])
        
        duplicate_count = sum(1 for f in findings if f.get("finding_type") == "duplicate")
        if duplicate_count > 0:
            recommendations.append(f"Investigate {duplicate_count} duplicate entry findings.")
        
        suspicious_count = sum(1 for f in findings if f.get("finding_type") == "suspicious")
        if suspicious_count > 0:
            recommendations.append(f"Review {suspicious_count} suspicious entries for potential fraud.")
        
        return recommendations
    
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
