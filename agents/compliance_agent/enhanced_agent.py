"""
Finovate Audit Nexus AI - Enhanced Compliance Agent
AI-powered compliance checking against accounting standards
Enterprise AI Financial Audit & Intelligence Platform
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

from backend.agents.enhanced_agent_base import EnhancedAgent, AgentResult
from backend.ai_engine.llm_interface import LLMMessage


class EnhancedComplianceAgent(EnhancedAgent):
    """
    Enhanced Compliance Standards AI Agent
    Uses LLM for intelligent compliance checking and recommendations
    
    Responsibilities:
    - Check compliance against accounting standards (IFRS, GAAP, ISA, Egyptian standards)
    - Identify compliance violations
    - Generate compliance recommendations
    - Provide compliance risk assessment
    - Generate compliance reports
    """

    def __init__(self, llm_provider: Optional[str] = None):
        """
        Initialize enhanced compliance agent
        Args:
            llm_provider: Preferred LLM provider
        """
        super().__init__(
            name="Enhanced Compliance Standards AI Agent",
            description="AI-powered compliance checking against accounting standards",
            agent_type="compliance",
            llm_provider=llm_provider
        )

        # Supported standards
        self.supported_standards = {
            'IFRS': 'International Financial Reporting Standards',
            'GAAP': 'Generally Accepted Accounting Principles',
            'ISA': 'International Standards on Auditing',
            'EGYPTIAN_GAAP': 'Egyptian Accounting Standards',
            'VAT': 'Value Added Tax Regulations',
            'SOX': 'Sarbanes-Oxley Act'
        }

        # Register tools
        self.register_tool("check_standard_compliance", self._check_standard_compliance_tool)
        self.register_tool("identify_violations", self._identify_violations_tool)
        self.register_tool("generate_recommendations", self._generate_recommendations_tool)

        logger.info(f"{self.name} initialized")

    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters"""
        required_fields = ['financial_data', 'standards']
        return all(field in kwargs for field in required_fields)

    async def execute(self, **kwargs) -> AgentResult:
        """
        Execute compliance analysis
        Args:
            financial_data: Dictionary containing financial data
            standards: List of standards to check against
        Returns:
            AgentResult with compliance analysis findings
        """
        self.before_execute(**kwargs)

        try:
            if not self.validate_input(**kwargs):
                return AgentResult(
                    success=False,
                    message="Missing required input parameters",
                    errors=["financial_data and standards are required"]
                )

            financial_data = kwargs.get('financial_data', {})
            standards = kwargs.get('standards', ['IFRS'])

            logger.info(f"Starting compliance analysis for standards: {standards}")

            # Step 1: Check compliance for each standard
            compliance_results = await self._check_compliance(financial_data, standards)

            # Step 2: AI-powered analysis and recommendations
            ai_insights = await self._ai_compliance_analysis(
                financial_data,
                compliance_results,
                standards
            )

            # Step 3: Generate compliance report
            final_report = await self._generate_compliance_report(
                compliance_results,
                ai_insights,
                standards
            )

            result = AgentResult(
                success=True,
                data=final_report,
                message="Compliance analysis completed successfully",
                ai_insights=ai_insights.get('summary', ''),
                confidence_score=final_report.get('overall_compliance_score', 0.0)
            )

            self.after_execute(result)
            return result

        except Exception as e:
            logger.error(f"Error during compliance analysis: {str(e)}")
            result = AgentResult(
                success=False,
                message=f"Compliance analysis failed: {str(e)}",
                errors=[str(e)]
            )
            self.after_execute(result)
            return result

    async def _check_compliance(
        self,
        financial_data: Dict[str, Any],
        standards: List[str]
    ) -> Dict[str, Any]:
        """
        Check compliance against specified standards
        Args:
            financial_data: Financial data to check
            standards: List of standards to check against
        Returns:
            Dictionary with compliance check results
        """
        logger.info(f"Checking compliance against {len(standards)} standards...")

        results = {
            'standards_checked': standards,
            'compliance_by_standard': {},
            'total_violations': 0,
            'overall_compliance_score': 100.0
        }

        for standard in standards:
            if standard in self.supported_standards:
                standard_results = self._check_standard(financial_data, standard)
                results['compliance_by_standard'][standard] = standard_results
                results['total_violations'] += len(standard_results.get('violations', []))
                results['overall_compliance_score'] -= standard_results.get('violations_impact', 0)

        results['overall_compliance_score'] = max(0.0, results['overall_compliance_score'])
        return results

    def _check_standard(self, financial_data: Dict[str, Any], standard: str) -> Dict[str, Any]:
        """Check compliance for a specific standard"""
        violations = []
        warnings = []

        if standard == 'IFRS':
            violations, warnings = self._check_ifrs_compliance(financial_data)
        elif standard == 'GAAP':
            violations, warnings = self._check_gaap_compliance(financial_data)
        elif standard == 'ISA':
            violations, warnings = self._check_isa_compliance(financial_data)
        elif standard == 'EGYPTIAN_GAAP':
            violations, warnings = self._check_egyptian_gaap_compliance(financial_data)
        elif standard == 'VAT':
            violations, warnings = self._check_vat_compliance(financial_data)
        elif standard == 'SOX':
            violations, warnings = self._check_sox_compliance(financial_data)

        return {
            'standard': standard,
            'violations': violations,
            'warnings': warnings,
            'violations_impact': len(violations) * 5 + len(warnings) * 2
        }

    def _check_ifrs_compliance(self, data: Dict[str, Any]) -> tuple:
        """Check IFRS compliance"""
        violations = []
        warnings = []

        # Check for required disclosures
        if 'financial_statements' not in data:
            violations.append({
                'type': 'missing_disclosure',
                'requirement': 'Financial statements must be presented',
                'severity': 'high'
            })

        return violations, warnings

    def _check_gaap_compliance(self, data: Dict[str, Any]) -> tuple:
        """Check GAAP compliance"""
        violations = []
        warnings = []

        # Check for revenue recognition
        if 'revenue' not in data:
            warnings.append({
                'type': 'missing_data',
                'requirement': 'Revenue data should be provided',
                'severity': 'medium'
            })

        return violations, warnings

    def _check_isa_compliance(self, data: Dict[str, Any]) -> tuple:
        """Check ISA compliance"""
        violations = []
        warnings = []

        # Check for audit evidence
        if 'audit_evidence' not in data:
            warnings.append({
                'type': 'missing_evidence',
                'requirement': 'Audit evidence should be documented',
                'severity': 'high'
            })

        return violations, warnings

    def _check_egyptian_gaap_compliance(self, data: Dict[str, Any]) -> tuple:
        """Check Egyptian GAAP compliance"""
        violations = []
        warnings = []

        # Egyptian-specific checks
        if 'vat_compliance' not in data:
            warnings.append({
                'type': 'missing_vat_data',
                'requirement': 'VAT compliance must be documented',
                'severity': 'high'
            })

        return violations, warnings

    def _check_vat_compliance(self, data: Dict[str, Any]) -> tuple:
        """Check VAT compliance"""
        violations = []
        warnings = []

        # VAT-specific checks
        if 'vat_returns' not in data:
            violations.append({
                'type': 'missing_vat_returns',
                'requirement': 'VAT returns must be filed',
                'severity': 'critical'
            })

        return violations, warnings

    def _check_sox_compliance(self, data: Dict[str, Any]) -> tuple:
        """Check SOX compliance"""
        violations = []
        warnings = []

        # SOX-specific checks
        if 'internal_controls' not in data:
            warnings.append({
                'type': 'missing_controls',
                'requirement': 'Internal controls must be documented',
                'severity': 'high'
            })

        return violations, warnings

    async def _ai_compliance_analysis(
        self,
        financial_data: Dict[str, Any],
        compliance_results: Dict[str, Any],
        standards: List[str]
    ) -> Dict[str, Any]:
        """
        Perform AI-powered compliance analysis
        Args:
            financial_data: Financial data
            compliance_results: Results from compliance checks
            standards: Standards being checked
        Returns:
            Dictionary with AI analysis results
        """
        logger.info("Performing AI-powered compliance analysis...")

        try:
            # Create analysis prompt
            prompt = self._create_compliance_analysis_prompt(
                compliance_results,
                standards
            )

            # Get AI insights
            ai_response = await self.analyze_with_ai(
                prompt=prompt,
                context_data={
                    'standards': standards,
                    'total_violations': compliance_results.get('total_violations', 0),
                    'compliance_score': compliance_results.get('overall_compliance_score', 0)
                },
                temperature=0.5,
                max_tokens=2000
            )

            # Parse AI response
            ai_insights = self._parse_compliance_response(ai_response)

            return ai_insights

        except Exception as e:
            logger.error(f"Error during AI compliance analysis: {str(e)}")
            return {
                'summary': 'AI analysis could not be completed',
                'recommendations': [],
                'error': str(e)
            }

    async def _generate_compliance_report(
        self,
        compliance_results: Dict[str, Any],
        ai_insights: Dict[str, Any],
        standards: List[str]
    ) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        logger.info("Generating compliance report...")

        report = {
            'report_id': f"COMPLIANCE-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'generated_at': datetime.now().isoformat(),
            'agent_name': self.name,
            'standards_checked': standards,
            'compliance_results': compliance_results,
            'ai_insights': ai_insights,
            'overall_compliance_score': compliance_results.get('overall_compliance_score', 0),
            'recommendations': ai_insights.get('recommendations', []),
            'next_steps': self._generate_compliance_next_steps(compliance_results, ai_insights)
        }

        return report

    def _create_compliance_analysis_prompt(
        self,
        compliance_results: Dict[str, Any],
        standards: List[str]
    ) -> str:
        """Create prompt for AI compliance analysis"""
        violations_summary = "\n".join([
            f"- {standard}: {len(compliance_results.get('compliance_by_standard', {}).get(standard, {}).get('violations', []))} violations"
            for standard in standards
        ])

        prompt = f"""
        You are a compliance expert. Analyze the following compliance check results:
        
        Standards Checked: {', '.join(standards)}
        
        Compliance Status by Standard:
        {violations_summary}
        
        Overall Compliance Score: {compliance_results.get('overall_compliance_score', 0)}/100
        Total Violations: {compliance_results.get('total_violations', 0)}
        
        Based on this analysis:
        1. What are the most critical compliance issues?
        2. What are the root causes of these violations?
        3. What corrective actions should be taken?
        4. What is the timeline for remediation?
        5. What preventive measures should be implemented?
        
        Provide a detailed compliance analysis and recommendations.
        """
        return prompt

    def _parse_compliance_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        return {
            'summary': response,
            'recommendations': self._extract_compliance_recommendations(response),
            'priority_level': self._extract_priority_level(response)
        }

    def _extract_compliance_recommendations(self, response: str) -> List[str]:
        """Extract recommendations from AI response"""
        recommendations = []
        lines = response.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['recommend', 'should', 'must', 'implement']):
                recommendations.append(line.strip())
        return recommendations[:5]

    def _extract_priority_level(self, response: str) -> str:
        """Extract priority level from AI response"""
        if 'critical' in response.lower():
            return 'critical'
        elif 'high' in response.lower():
            return 'high'
        elif 'medium' in response.lower():
            return 'medium'
        return 'low'

    def _generate_compliance_next_steps(
        self,
        compliance_results: Dict[str, Any],
        ai_insights: Dict[str, Any]
    ) -> List[str]:
        """Generate recommended next steps"""
        next_steps = []

        if compliance_results.get('total_violations', 0) > 0:
            next_steps.append("Address identified compliance violations immediately")

        if compliance_results.get('overall_compliance_score', 100) < 80:
            next_steps.append("Conduct comprehensive compliance audit")

        next_steps.extend(ai_insights.get('recommendations', [])[:2])

        return next_steps

    # Tool implementations
    async def _check_standard_compliance_tool(
        self,
        financial_data: Dict[str, Any],
        standard: str
    ) -> Dict[str, Any]:
        """Tool for checking specific standard compliance"""
        return self._check_standard(financial_data, standard)

    async def _identify_violations_tool(
        self,
        compliance_results: Dict[str, Any]
    ) -> List[Dict]:
        """Tool for identifying violations"""
        violations = []
        for standard, results in compliance_results.get('compliance_by_standard', {}).items():
            violations.extend(results.get('violations', []))
        return violations

    async def _generate_recommendations_tool(
        self,
        violations: List[Dict]
    ) -> List[str]:
        """Tool for generating recommendations"""
        recommendations = []
        for violation in violations:
            recommendations.append(
                f"Address {violation.get('type', 'issue')}: {violation.get('requirement', '')}"
            )
        return recommendations
