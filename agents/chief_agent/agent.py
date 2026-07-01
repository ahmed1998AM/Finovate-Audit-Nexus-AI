"""
Finovate Audit Nexus AI - Chief Audit AI Agent

The master agent that manages all other agents, aggregates results,
and produces final audit reports.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger


class ChiefAuditAgent:
    """
    Chief Audit AI Agent - Master Agent for Finovate Audit Nexus AI

    Responsibilities:
    - Manage all other agents
    - Aggregate results from all agents
    - Perform final analysis
    - Issue final audit report
    - Risk assessment
    - Confidence level evaluation
    - Final decision making
    """

    def __init__(self) -> None:
        self.agent_id = "chief_audit_agent"
        self.name = "Chief Audit AI Agent"
        self.description = "Master agent managing all audit operations"
        self.status = "initialized"
        self.results = {}
        self.agents_managed = []

        logger.info(f"{self.name} initialized")

    async def initialize_agents(self, agents: List[Any]) -> None:
        """Initialize and register all subordinate agents"""
        self.agents_managed = agents
        logger.info(f"Initialized {len(agents)} subordinate agents")

    async def orchestrate_audit(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate the complete audit process across all agents

        Args:
            audit_data: Dictionary containing financial data to audit

        Returns:
            Comprehensive audit results
        """
        logger.info("Starting orchestrated audit process...")
        self.status = "running"

        try:
            # Execute all agents in parallel where possible
            tasks = []

            # Core audit agents
            if 'journal_entries' in audit_data:
                tasks.append(self._execute_agent('journal_agent', audit_data['journal_entries']))

            if 'general_ledger' in audit_data:
                tasks.append(self._execute_agent('ledger_agent', audit_data['general_ledger']))

            if 'trial_balance' in audit_data:
                tasks.append(self._execute_agent('tb_agent', audit_data['trial_balance']))

            if 'financial_statements' in audit_data:
                tasks.append(self._execute_agent('fs_agent', audit_data['financial_statements']))

            # Specialized agents
            if 'bank_transactions' in audit_data:
                tasks.append(self._execute_agent('bank_agent', audit_data['bank_transactions']))

            if 'inventory_data' in audit_data:
                tasks.append(self._execute_agent('inventory_agent', audit_data['inventory_data']))

            if 'fixed_assets' in audit_data:
                tasks.append(self._execute_agent('assets_agent', audit_data['fixed_assets']))

            # Intelligence agents
            tasks.append(self._execute_agent('fraud_agent', audit_data))
            tasks.append(self._execute_agent('risk_agent', audit_data))
            tasks.append(self._execute_agent('compliance_agent', audit_data))

            # Execute all tasks
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"Agent execution failed: {result}")
                    else:
                        self.results[f"agent_{i}"] = result

            # Aggregate and analyze results
            final_analysis = await self._aggregate_results()

            # Generate final report
            final_report = await self._generate_final_report(final_analysis)

            self.status = "completed"
            logger.info("Orchestrated audit completed successfully")

            return final_report

        except Exception as e:
            logger.error(f"Audit orchestration failed: {e}")
            self.status = "failed"
            raise

    ENHANCED_MAPPING = {
        'fraud_agent': ('agents.fraud_agent.enhanced_agent', 'EnhancedFraudDetectionAgent'),
        'compliance_agent': ('agents.compliance_agent.enhanced_agent', 'EnhancedComplianceAgent'),
    }

    BASE_MAPPING = {
        'journal_agent': ('agents.journal_agent.agent', 'JournalEntryAuditAgent', 'analyze_journal_entries'),
        'ledger_agent': ('agents.ledger_agent.agent', 'GeneralLedgerAuditAgent', 'analyze_ledger'),
        'tb_agent': ('agents.tb_agent.agent', 'TrialBalanceAuditAgent', 'analyze_trial_balance'),
        'fs_agent': ('agents.fs_agent.agent', 'FinancialStatementsAuditAgent', 'analyze_financial_statements'),
        'bank_agent': ('agents.bank_agent.agent', 'BankAuditAgent', 'analyze_bank_statement'),
        'inventory_agent': ('agents.inventory_agent.agent', 'InventoryAuditAgent', 'analyze_inventory'),
        'assets_agent': ('agents.assets_agent.agent', 'FixedAssetsAuditAgent', 'analyze_fixed_assets'),
        'fraud_agent': ('agents.fraud_agent.agent', 'FraudDetectionAgent', 'detect_fraud'),
        'risk_agent': ('agents.risk_agent.agent', 'RiskScoringAgent', 'assess_risks'),
        'compliance_agent': ('agents.compliance_agent.agent', 'ComplianceStandardsAgent', 'check_compliance'),
    }

    async def _execute_enhanced_agent(self, agent_name: str, data: Any) -> Optional[Dict[str, Any]]:
        entry = self.ENHANCED_MAPPING.get(agent_name)
        if not entry:
            return None
        module_path, class_name = entry
        import importlib
        try:
            module = importlib.import_module(module_path)
            agent_class = getattr(module, class_name)
            agent_instance = agent_class()
            kwargs = {"financial_data": data} if agent_name == "fraud_agent" else {"financial_data": data, "standards": ["IFRS", "GAAP", "SOX"]}
            if hasattr(agent_instance, 'execute') and asyncio.iscoroutinefunction(agent_instance.execute):
                result = await agent_instance.execute(**kwargs)
                return {
                    "agent": agent_name,
                    "status": "completed" if getattr(result, 'success', False) else "failed",
                    "timestamp": datetime.now().isoformat(),
                    "findings": getattr(result, 'data', result) or {},
                    "ai_insights": getattr(result, 'ai_insights', None),
                    "confidence_score": getattr(result, 'confidence_score', 0.0),
                    "llm_used": True
                }
        except (ImportError, AttributeError, Exception) as e:
            logger.warning(f"Enhanced agent '{agent_name}' unavailable ({e}), falling back to base")
        return None

    async def _execute_base_agent(self, agent_name: str, data: Any) -> Optional[Dict[str, Any]]:
        entry = self.BASE_MAPPING.get(agent_name)
        if not entry or len(entry) != 3:
            return None
        module_path, class_name, method_name = entry
        import importlib
        module = importlib.import_module(module_path)
        agent_class = getattr(module, class_name)
        agent_instance = agent_class()
        method = getattr(agent_instance, method_name)
        if asyncio.iscoroutinefunction(method):
            result = await method(data)
        else:
            result = method(data)
        return {
            "agent": agent_name,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "findings": result or {},
            "llm_used": False
        }

    async def _execute_agent(self, agent_name: str, data: Any) -> Dict[str, Any]:
        logger.info(f"Executing agent: {agent_name}")
        try:
            result = await self._execute_enhanced_agent(agent_name, data)
            if result is not None:
                return result
            result = await self._execute_base_agent(agent_name, data)
            if result is not None:
                return result
            logger.warning(f"No mapping found for agent: {agent_name}")
            return {
                "agent": agent_name,
                "status": "not_implemented",
                "timestamp": datetime.now().isoformat(),
                "findings": []
            }
        except Exception as e:
            logger.error(f"Error executing agent {agent_name}: {str(e)}")
            return {
                "agent": agent_name,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _aggregate_results(self) -> Dict[str, Any]:
        """Aggregate results from all agents"""
        logger.info("Aggregating results from all agents...")

        aggregated = {
            "total_agents_executed": len(self.results),
            "critical_findings": [],
            "warnings": [],
            "recommendations": [],
            "risk_score": 0.0,
            "fraud_indicators": [],
            "compliance_issues": [],
            "confidence_level": 0.0
        }

        # Analyze and aggregate findings from all agents
        for agent_key, result in self.results.items():
            if isinstance(result, dict):
                if 'critical_findings' in result:
                    aggregated['critical_findings'].extend(result['critical_findings'])
                if 'warnings' in result:
                    aggregated['warnings'].extend(result['warnings'])
                if 'risk_score' in result:
                    aggregated['risk_score'] = max(
                        aggregated['risk_score'],
                        result['risk_score']
                    )

        # Calculate overall confidence level
        aggregated['confidence_level'] = self._calculate_confidence()

        return aggregated

    def _calculate_confidence(self) -> float:
        """Calculate overall confidence level based on agent results"""
        # Placeholder implementation
        # In production, this would use sophisticated algorithms
        if not self.results:
            return 0.0

        successful_agents = sum(
            1 for r in self.results.values()
            if isinstance(r, dict) and r.get('status') == 'completed'
        )

        return (successful_agents / len(self.results)) * 100.0

    async def _generate_final_report(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive final audit report"""
        logger.info("Generating final audit report...")

        report = {
            "report_id": f"AUDIT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "generated_by": self.name,
            "audit_summary": {
                "overall_status": "COMPLETED" if analysis['critical_findings'] == [] else "ISSUES_FOUND",
                "risk_level": self._assess_risk_level(analysis['risk_score']),
                "confidence_level": analysis['confidence_level'],
                "total_findings": len(analysis['critical_findings']) + len(analysis['warnings'])
            },
            "critical_findings": analysis['critical_findings'],
            "warnings": analysis['warnings'],
            "recommendations": analysis['recommendations'],
            "risk_assessment": {
                "overall_risk_score": analysis['risk_score'],
                "fraud_indicators": analysis['fraud_indicators'],
                "compliance_issues": analysis['compliance_issues']
            },
            "agent_results": self.results,
            "next_steps": self._generate_next_steps(analysis)
        }

        return report

    def _assess_risk_level(self, risk_score: float) -> str:
        """Assess overall risk level based on risk score"""
        if risk_score >= 80:
            return "CRITICAL"
        elif risk_score >= 60:
            return "HIGH"
        elif risk_score >= 40:
            return "MEDIUM"
        elif risk_score >= 20:
            return "LOW"
        else:
            return "MINIMAL"

    def _generate_next_steps(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommended next steps based on analysis"""
        next_steps = []

        if analysis['critical_findings']:
            next_steps.append("Immediate review of critical findings required")
            next_steps.append("Schedule meeting with management")

        if analysis['fraud_indicators']:
            next_steps.append("Initiate forensic investigation")
            next_steps.append("Preserve evidence")

        if analysis['compliance_issues']:
            next_steps.append("Review compliance procedures")
            next_steps.append("Update internal controls")

        if not next_steps:
            next_steps.append("Continue regular monitoring")
            next_steps.append("Schedule next audit cycle")

        return next_steps

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status,
            "agents_managed": len(self.agents_managed),
            "results_count": len(self.results)
        }


# Singleton instance
_chief_agent_instance: Optional[ChiefAuditAgent] = None


def get_chief_agent() -> ChiefAuditAgent:
    """Get singleton instance of ChiefAuditAgent"""
    global _chief_agent_instance
    if _chief_agent_instance is None:
        _chief_agent_instance = ChiefAuditAgent()
    return _chief_agent_instance
