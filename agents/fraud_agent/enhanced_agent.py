"""
Finovate Audit Nexus AI - Enhanced Fraud Detection Agent
Advanced fraud detection using AI-powered pattern recognition
Enterprise AI Financial Audit & Intelligence Platform
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
from loguru import logger

from backend.agents.enhanced_agent_base import AgentResult, EnhancedAgent


class EnhancedFraudDetectionAgent(EnhancedAgent):
    """
    Enhanced Fraud Detection AI Agent
    Uses LLM for intelligent pattern analysis and anomaly detection

    Responsibilities:
    - Detect fraud patterns using AI analysis
    - Analyze anomalies in financial data
    - Identify suspicious transactions
    - Generate fraud risk scores
    - Provide AI-powered recommendations
    """

    def __init__(self, llm_provider: Optional[str] = None) -> None:
        """
        Initialize enhanced fraud detection agent
        Args:
            llm_provider: Preferred LLM provider
        """
        super().__init__(
            name="Enhanced Fraud Detection AI Agent",
            description="Advanced fraud detection using AI-powered analysis",
            agent_type="fraud_detection",
            llm_provider=llm_provider
        )

        # Fraud detection thresholds
        self.thresholds = {
            'duplicate_amount': 0.01,
            'round_amount_threshold': 1000,
            'weekend_transaction_weight': 2.0,
            'after_hours_weight': 1.5,
            'large_transaction_multiplier': 5.0,
            'anomaly_threshold': 0.85
        }

        # Register tools
        self.register_tool("analyze_transactions", self._analyze_transactions_tool)
        self.register_tool("detect_anomalies", self._detect_anomalies_tool)
        self.register_tool("calculate_risk_score", self._calculate_risk_score_tool)

        logger.info(f"{self.name} initialized")

    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters"""
        required_fields = ['financial_data']
        return all(field in kwargs for field in required_fields)

    async def execute(self, **kwargs) -> AgentResult:
        """
        Execute fraud detection analysis
        Args:
            financial_data: Dictionary containing financial transactions
        Returns:
            AgentResult with fraud analysis findings
        """
        self.before_execute(**kwargs)

        try:
            if not self.validate_input(**kwargs):
                return AgentResult(
                    success=False,
                    message="Missing required input parameters",
                    errors=["financial_data is required"]
                )

            financial_data = kwargs.get('financial_data', {})

            logger.info("Starting enhanced fraud detection analysis...")

            # Step 1: Traditional pattern analysis
            traditional_findings = await self._traditional_analysis(financial_data)

            # Step 2: AI-powered analysis
            ai_insights = await self._ai_powered_analysis(financial_data, traditional_findings)

            # Step 3: Generate final report
            final_result = await self._generate_fraud_report(
                traditional_findings,
                ai_insights
            )

            result = AgentResult(
                success=True,
                data=final_result,
                message="Fraud detection analysis completed successfully",
                ai_insights=ai_insights.get('summary', ''),
                confidence_score=final_result.get('overall_confidence', 0.0)
            )

            self.after_execute(result)
            return result

        except Exception as e:
            logger.error(f"Error during fraud detection: {str(e)}")
            result = AgentResult(
                success=False,
                message=f"Fraud detection analysis failed: {str(e)}",
                errors=[str(e)]
            )
            self.after_execute(result)
            return result

    async def _traditional_analysis(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform traditional statistical fraud analysis
        Args:
            financial_data: Financial data to analyze
        Returns:
            Dictionary with traditional analysis results
        """
        logger.info("Performing traditional fraud analysis...")

        findings = {
            'duplicate_entries': [],
            'suspicious_patterns': [],
            'anomalies': [],
            'risk_score': 0.0
        }

        # Analyze journal entries
        if 'journal_entries' in financial_data:
            journal_findings = self._analyze_journal_entries(
                financial_data['journal_entries']
            )
            findings['duplicate_entries'].extend(journal_findings.get('duplicates', []))
            findings['suspicious_patterns'].extend(journal_findings.get('patterns', []))

        # Analyze bank transactions
        if 'bank_transactions' in financial_data:
            bank_findings = self._analyze_bank_transactions(
                financial_data['bank_transactions']
            )
            findings['anomalies'].extend(bank_findings.get('anomalies', []))

        # Calculate initial risk score
        findings['risk_score'] = self._calculate_risk_score(findings)

        return findings

    async def _ai_powered_analysis(
        self,
        financial_data: Dict[str, Any],
        traditional_findings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform AI-powered fraud analysis
        Args:
            financial_data: Financial data to analyze
            traditional_findings: Results from traditional analysis
        Returns:
            Dictionary with AI analysis results
        """
        logger.info("Performing AI-powered fraud analysis...")

        try:
            # Prepare context for AI analysis
            context = {
                "financial_data_summary": self._summarize_financial_data(financial_data),
                "traditional_findings": traditional_findings,
                "risk_score": traditional_findings.get('risk_score', 0.0)
            }

            # Create analysis prompt
            prompt = self._create_fraud_analysis_prompt(context)

            # Get AI insights
            ai_response = await self.analyze_with_ai(
                prompt=prompt,
                context_data=context,
                temperature=0.5,
                max_tokens=2000
            )

            # Parse AI response
            ai_insights = self._parse_ai_response(ai_response)

            return ai_insights

        except Exception as e:
            logger.error(f"Error during AI-powered analysis: {str(e)}")
            return {
                'summary': 'AI analysis could not be completed',
                'recommendations': [],
                'error': str(e)
            }

    async def _generate_fraud_report(
        self,
        traditional_findings: Dict[str, Any],
        ai_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive fraud report
        Args:
            traditional_findings: Results from traditional analysis
            ai_insights: Results from AI analysis
        Returns:
            Comprehensive fraud report
        """
        logger.info("Generating fraud detection report...")

        report = {
            'report_id': f"FRAUD-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'generated_at': datetime.now().isoformat(),
            'agent_name': self.name,
            'traditional_findings': traditional_findings,
            'ai_insights': ai_insights,
            'overall_confidence': self._calculate_overall_confidence(
                traditional_findings,
                ai_insights
            ),
            'recommendations': ai_insights.get('recommendations', []),
            'next_steps': self._generate_next_steps(traditional_findings, ai_insights)
        }

        return report

    def _analyze_journal_entries(self, entries: List[Dict]) -> Dict[str, Any]:
        """Analyze journal entries for fraud patterns"""
        findings = {'duplicates': [], 'patterns': []}

        if not entries:
            return findings

        # Check for duplicate entries
        seen = {}
        for entry in entries:
            key = (entry.get('account'), entry.get('amount'), entry.get('date'))
            if key in seen:
                findings['duplicates'].append({
                    'entry_id': entry.get('id'),
                    'duplicate_of': seen[key],
                    'severity': 'high'
                })
            else:
                seen[key] = entry.get('id')

        return findings

    def _analyze_bank_transactions(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Analyze bank transactions for anomalies"""
        findings = {'anomalies': []}

        if not transactions:
            return findings

        # Calculate statistics
        amounts = [t.get('amount', 0) for t in transactions]
        if amounts:
            mean_amount = np.mean(amounts)
            std_amount = np.std(amounts)

            # Detect outliers
            for transaction in transactions:
                amount = transaction.get('amount', 0)
                if std_amount > 0:
                    z_score = abs((amount - mean_amount) / std_amount)
                    if z_score > 3:  # 3 standard deviations
                        findings['anomalies'].append({
                            'transaction_id': transaction.get('id'),
                            'amount': amount,
                            'z_score': z_score,
                            'severity': 'high' if z_score > 5 else 'medium'
                        })

        return findings

    def _calculate_risk_score(self, findings: Dict[str, Any]) -> float:
        """Calculate fraud risk score"""
        risk_score = 0.0

        # Weight different findings
        risk_score += len(findings.get('duplicate_entries', [])) * 10
        risk_score += len(findings.get('suspicious_patterns', [])) * 15
        risk_score += len(findings.get('anomalies', [])) * 8

        return min(100.0, risk_score)

    def _summarize_financial_data(self, financial_data: Dict[str, Any]) -> str:
        """Create a summary of financial data for AI analysis"""
        summary_parts = []

        if 'journal_entries' in financial_data:
            summary_parts.append(
                f"Journal Entries: {len(financial_data['journal_entries'])} entries"
            )

        if 'bank_transactions' in financial_data:
            summary_parts.append(
                f"Bank Transactions: {len(financial_data['bank_transactions'])} transactions"
            )

        return "; ".join(summary_parts)

    def _create_fraud_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Create a structured prompt for AI fraud analysis"""
        traditional = context.get('traditional_findings', {})
        duplicates = traditional.get('duplicate_entries', [])
        suspicious = traditional.get('suspicious_patterns', [])
        anomalies = traditional.get('anomalies', [])
        risk_score = traditional.get('risk_score', 0)

        dup_detail = ""
        for d in duplicates[:10]:
            dup_detail += f"  - Entry {d.get('entry_id')}: {d.get('description', 'N/A')} ({d.get('amount', 0)})\n"

        sus_detail = ""
        for s in suspicious[:10]:
            sus_detail += f"  - {s.get('description', s.get('pattern', 'N/A'))} (severity: {s.get('severity', 'medium')})\n"

        ano_detail = ""
        for a in anomalies[:10]:
            ano_detail += f"  - Transaction {a.get('transaction_id')}: {a.get('amount')} (z-score: {a.get('z_score', 0)}, severity: {a.get('severity', 'medium')})\n"

        prompt = f"""You are a certified forensic accounting expert with 20+ years of experience in fraud detection at multinational financial institutions. Analyze the following data and traditional analysis results.

Role: Senior Fraud Investigator
Task: Identify fraud indicators and recommend investigation steps
Format: Provide structured analysis with clear severity levels

FINANCIAL DATA SUMMARY
{context.get('financial_data_summary', 'No summary provided')}

TRADITIONAL ANALYSIS RESULTS
- Duplicate Entries Found: {len(duplicates)} (Risk Weight: 10 pts each)
{dup_detail or '  (none)'}
- Suspicious Patterns Detected: {len(suspicious)} (Risk Weight: 15 pts each)
{sus_detail or '  (none)'}
- Transaction Anomalies: {len(anomalies)} (Risk Weight: 8 pts each)
{ano_detail or '  (none)'}
- Overall Traditional Risk Score: {risk_score}/100

Based on the above, provide:

1. KEY RISK INDICATORS (list top 3-5 indicators with severity: HIGH/MEDIUM/LOW)

2. FRAUD PATTERN ASSESSMENT (identify specific patterns suggesting potential fraudulent activity)

3. RECOMMENDED ACTIONS (prioritized list of specific investigation steps with rationale)

4. CONFIDENCE ASSESSMENT (overall confidence: HIGH/MEDIUM/LOW and why)

5. ADDITIONAL DATA NEEDED (what additional information would strengthen the analysis)

Keep analysis concise and actionable. Focus on HIGH and MEDIUM severity items for immediate action."""
        return prompt

    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        return {
            'summary': response,
            'recommendations': self._extract_recommendations(response),
            'confidence': self._extract_confidence(response)
        }

    def _extract_recommendations(self, response: str) -> List[str]:
        """Extract recommendations from AI response"""
        recommendations = []
        lines = response.split('\n')
        for line in lines:
            if 'recommend' in line.lower() or 'suggest' in line.lower():
                recommendations.append(line.strip())
        return recommendations[:5]  # Return top 5 recommendations

    def _extract_confidence(self, response: str) -> float:
        """Extract confidence level from AI response"""
        if 'high' in response.lower():
            return 0.85
        elif 'medium' in response.lower():
            return 0.65
        elif 'low' in response.lower():
            return 0.45
        return 0.70

    def _calculate_overall_confidence(
        self,
        traditional_findings: Dict[str, Any],
        ai_insights: Dict[str, Any]
    ) -> float:
        """Calculate overall confidence in fraud detection"""
        # Combine traditional and AI confidence
        traditional_confidence = min(
            1.0,
            (traditional_findings.get('risk_score', 0) / 100) * 0.7
        )
        ai_confidence = ai_insights.get('confidence', 0.7) * 0.3

        return traditional_confidence + ai_confidence

    def _generate_next_steps(
        self,
        traditional_findings: Dict[str, Any],
        ai_insights: Dict[str, Any]
    ) -> List[str]:
        """Generate recommended next steps"""
        next_steps = []

        if traditional_findings.get('risk_score', 0) > 50:
            next_steps.append("Conduct detailed investigation of high-risk transactions")

        if len(traditional_findings.get('duplicate_entries', [])) > 0:
            next_steps.append("Review and reconcile duplicate entries")

        if len(traditional_findings.get('anomalies', [])) > 0:
            next_steps.append("Investigate unusual transactions and outliers")

        next_steps.extend(ai_insights.get('recommendations', [])[:2])

        return next_steps

    # Compatibility methods for orchestrator / ChiefAgent
    async def detect_fraud(self, financial_data: Any) -> Dict[str, Any]:
        """Called by AgentOrchestrator and ChiefAgent - delegates to execute()"""
        kwargs = {"financial_data": financial_data} if isinstance(financial_data, dict) else {"financial_data": {"data": financial_data}}
        result = await self.execute(**kwargs)
        return {
            "agent": self.name,
            "status": "completed" if getattr(result, 'success', False) else "failed",
            "timestamp": datetime.now().isoformat(),
            "findings": getattr(result, 'data', result) or {},
            "ai_insights": getattr(result, 'ai_insights', None),
            "confidence_score": getattr(result, 'confidence_score', 0.0),
            "risk_score": getattr(result, 'data', {}).get('risk_score', 0) if isinstance(getattr(result, 'data', None), dict) else 0,
        }

    # Tool implementations
    async def _analyze_transactions_tool(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Tool for analyzing transactions"""
        return self._analyze_bank_transactions(transactions)

    async def _detect_anomalies_tool(self, data: List[float]) -> List[Dict]:
        """Tool for detecting anomalies in numerical data"""
        if not data:
            return []

        mean = np.mean(data)
        std = np.std(data)
        anomalies = []

        for i, value in enumerate(data):
            if std > 0:
                z_score = abs((value - mean) / std)
                if z_score > 3:
                    anomalies.append({
                        'index': i,
                        'value': value,
                        'z_score': z_score
                    })

        return anomalies

    async def _calculate_risk_score_tool(self, findings: Dict[str, Any]) -> float:
        """Tool for calculating risk score"""
        return self._calculate_risk_score(findings)
