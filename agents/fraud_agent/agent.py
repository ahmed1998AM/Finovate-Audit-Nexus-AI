"""
Finovate Audit Nexus AI - Fraud Detection Agent

Advanced fraud detection using pattern recognition, anomaly detection,
and behavioral analysis.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
from loguru import logger


class FraudDetectionAgent:
    """
    Fraud Detection AI Agent

    Responsibilities:
    - Detect fraud patterns
    - Analyze anomalies
    - Identify suspicious transactions
    - Risk scoring
    - Financial forensics
    """

    def __init__(self) -> None:
        self.agent_id = "fraud_detection_agent"
        self.name = "Fraud Detection AI Agent"
        self.description = "Advanced fraud detection and pattern analysis"
        self.status = "initialized"

        # Fraud detection thresholds
        self.thresholds = {
            'duplicate_amount': 0.01,  # Amounts within 1% considered duplicate
            'round_amount_threshold': 1000,  # Round amounts above this are suspicious
            'weekend_transaction_weight': 2.0,
            'after_hours_weight': 1.5,
            'large_transaction_multiplier': 5.0  # Times average transaction
        }

        logger.info(f"{self.name} initialized")

    async def detect_fraud(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Alias for analyze method for orchestrator compatibility"""
        return await self.analyze(financial_data)

    async def analyze(self, financial_data: Any) -> Dict[str, Any]:
        """
        Perform comprehensive fraud analysis

        Args:
            financial_data: Dictionary or DataFrame containing financial transactions and data

        Returns:
            Fraud analysis results with indicators and risk scores
        """
        logger.info("Starting fraud detection analysis...")
        self.status = "analyzing"

        # Handle DataFrame input
        if hasattr(financial_data, 'to_dict'):
            try:
                if hasattr(financial_data, 'head'):
                    df = financial_data
                    # Map common column names to what the agent expects
                    mapping = {
                        'amount': 'amount',
                        'date': 'date',
                        'vendor': 'vendor_name',
                        'payee': 'payee',
                        'description': 'description'
                    }
                    df = df.rename(columns={c: mapping[c] for c in df.columns if c in mapping})
                    
                    # Convert to list of dicts and put in journal_entries or bank_transactions
                    records = df.to_dict(orient='records')
                    financial_data = {
                        'journal_entries': records,
                        'bank_transactions': records,
                        'vendor_payments': records,
                        'employee_expenses': records
                    }
            except Exception as e:
                logger.warning(f"Failed to convert DataFrame in Fraud Agent: {e}")

        try:
            findings = {
                'fraud_indicators': [],
                'suspicious_patterns': [],
                'anomalies': [],
                'risk_score': 0.0,
                'confidence_level': 0.0,
                'recommendations': []
            }

            # Handle empty data
            if not financial_data:
                return findings

            # Analyze journal entries for fraud
            if 'journal_entries' in financial_data:
                journal_findings = await self._analyze_journal_entries(
                    financial_data['journal_entries']
                )
                findings['fraud_indicators'].extend(journal_findings['indicators'])
                findings['suspicious_patterns'].extend(journal_findings['patterns'])

            # Analyze bank transactions
            if 'bank_transactions' in financial_data:
                bank_findings = await self._analyze_bank_transactions(
                    financial_data['bank_transactions']
                )
                findings['fraud_indicators'].extend(bank_findings['indicators'])
                findings['anomalies'].extend(bank_findings['anomalies'])

            # Analyze vendor payments
            if 'vendor_payments' in financial_data:
                vendor_findings = await self._analyze_vendor_payments(
                    financial_data['vendor_payments']
                )
                findings['fraud_indicators'].extend(vendor_findings['indicators'])

            # Analyze employee expenses
            if 'employee_expenses' in financial_data:
                expense_findings = await self._analyze_employee_expenses(
                    financial_data['employee_expenses']
                )
                findings['fraud_indicators'].extend(expense_findings['indicators'])

            # Calculate overall risk score
            findings['risk_score'] = self._calculate_fraud_risk_score(findings)
            findings['confidence_level'] = self._calculate_confidence(findings)

            # Generate recommendations
            findings['recommendations'] = self._generate_recommendations(findings)

            self.status = "completed"
            logger.info(f"Fraud analysis completed. Risk Score: {findings['risk_score']}")

            return findings

        except Exception as e:
            logger.error(f"Fraud detection failed: {str(e)}")
            self.status = "failed"
            return {"status": "error", "error": str(e)}

    async def _analyze_journal_entries(self, entries: List[Dict]) -> Dict[str, List]:
        """Analyze journal entries for fraud indicators"""
        indicators = []
        patterns = []

        # Check for duplicate entries
        duplicates = self._detect_duplicate_entries(entries)
        if duplicates:
            indicators.append({
                'type': 'DUPLICATE_ENTRIES',
                'severity': 'HIGH',
                'count': len(duplicates),
                'details': duplicates[:10],  # First 10 duplicates
                'description': 'Potential duplicate journal entries detected'
            })

        # Check for round amount entries
        round_amounts = self._detect_round_amounts(entries)
        if round_amounts:
            patterns.append({
                'type': 'ROUND_AMOUNTS',
                'severity': 'MEDIUM',
                'count': len(round_amounts),
                'details': round_amounts[:10],
                'description': 'Unusual number of round amount entries'
            })

        # Check for entries made on weekends/holidays
        weekend_entries = self._detect_weekend_entries(entries)
        if weekend_entries:
            patterns.append({
                'type': 'WEEKEND_ENTRIES',
                'severity': 'MEDIUM',
                'count': len(weekend_entries),
                'details': weekend_entries[:10],
                'description': 'Journal entries created on weekends or holidays'
            })

        # Check for manual journal entries
        manual_entries = self._detect_manual_entries(entries)
        if manual_entries:
            patterns.append({
                'type': 'MANUAL_ENTRIES',
                'severity': 'LOW',
                'count': len(manual_entries),
                'details': manual_entries[:10],
                'description': 'High volume of manual journal entries'
            })

        # Check for entries by unauthorized users
        # (Implementation would check against user permissions)

        return {'indicators': indicators, 'patterns': patterns}

    async def _analyze_bank_transactions(self, transactions: List[Dict]) -> Dict[str, List]:
        """Analyze bank transactions for fraud"""
        indicators = []
        anomalies = []

        # Detect duplicate payments
        duplicates = self._detect_duplicate_payments(transactions)
        if duplicates:
            indicators.append({
                'type': 'DUPLICATE_PAYMENTS',
                'severity': 'HIGH',
                'count': len(duplicates),
                'details': duplicates[:10],
                'description': 'Potential duplicate bank payments detected'
            })

        # Detect unusual transaction amounts
        unusual_amounts = self._detect_unusual_amounts(transactions)
        if unusual_amounts:
            anomalies.append({
                'type': 'UNUSUAL_AMOUNTS',
                'severity': 'MEDIUM',
                'count': len(unusual_amounts),
                'details': unusual_amounts[:10],
                'description': 'Transactions with statistically unusual amounts'
            })

        # Detect structuring (smurfing)
        structured = self._detect_structuring(transactions)
        if structured:
            indicators.append({
                'type': 'STRUCTURING',
                'severity': 'CRITICAL',
                'count': len(structured),
                'details': structured[:10],
                'description': 'Potential money laundering through transaction structuring'
            })

        return {'indicators': indicators, 'anomalies': anomalies}

    async def _analyze_vendor_payments(self, payments: List[Dict]) -> Dict[str, List]:
        """Analyze vendor payments for fraud"""
        indicators = []

        # Detect payments to vendors with similar names
        similar_vendors = self._detect_similar_vendor_names(payments)
        if similar_vendors:
            indicators.append({
                'type': 'SIMILAR_VENDOR_NAMES',
                'severity': 'HIGH',
                'count': len(similar_vendors),
                'details': similar_vendors[:10],
                'description': 'Payments to vendors with suspiciously similar names'
            })

        # Detect payments just below approval threshold
        threshold_avoidance = self._detect_threshold_avoidance(payments)
        if threshold_avoidance:
            indicators.append({
                'type': 'THRESHOLD_AVOIDANCE',
                'severity': 'HIGH',
                'count': len(threshold_avoidance),
                'details': threshold_avoidance[:10],
                'description': 'Payments structured to avoid approval thresholds'
            })

        return {'indicators': indicators}

    async def _analyze_employee_expenses(self, expenses: List[Dict]) -> Dict[str, List]:
        """Analyze employee expenses for fraud"""
        indicators = []

        # Detect duplicate expense claims
        duplicates = self._detect_duplicate_expenses(expenses)
        if duplicates:
            indicators.append({
                'type': 'DUPLICATE_EXPENSES',
                'severity': 'HIGH',
                'count': len(duplicates),
                'details': duplicates[:10],
                'description': 'Duplicate expense claims detected'
            })

        # Detect unusual expense patterns
        unusual = self._detect_unusual_expense_patterns(expenses)
        if unusual:
            indicators.append({
                'type': 'UNUSUAL_PATTERNS',
                'severity': 'MEDIUM',
                'count': len(unusual),
                'details': unusual[:10],
                'description': 'Unusual expense patterns detected'
            })

        return {'indicators': indicators}

    def _detect_duplicate_entries(self, entries: List[Dict]) -> List[Dict]:
        """Detect duplicate journal entries"""
        # Implementation would use fuzzy matching on amount, date, description
        duplicates = []
        seen = {}

        for entry in entries:
            key = f"{entry.get('amount', 0):.2f}_{entry.get('date', '')}"
            if key in seen:
                duplicates.append({
                    'entry_1': seen[key],
                    'entry_2': entry,
                    'match_type': 'amount_date'
                })
            else:
                seen[key] = entry

        return duplicates

    def _detect_round_amounts(self, entries: List[Dict]) -> List[Dict]:
        """Detect entries with round amounts"""
        round_entries = []
        threshold = self.thresholds['round_amount_threshold']

        for entry in entries:
            amount = abs(entry.get('amount', 0))
            if amount >= threshold and amount % 1000 == 0:
                round_entries.append(entry)

        return round_entries

    def _detect_weekend_entries(self, entries: List[Dict]) -> List[Dict]:
        """Detect entries made on weekends"""
        weekend_entries = []

        for entry in entries:
            date_str = entry.get('date', '')
            if date_str:
                try:
                    date = datetime.fromisoformat(date_str)
                    if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                        weekend_entries.append(entry)
                except ValueError:
                    pass

        return weekend_entries

    def _detect_manual_entries(self, entries: List[Dict]) -> List[Dict]:
        """Detect manual journal entries"""
        manual = []

        for entry in entries:
            if entry.get('entry_type', '').upper() == 'MANUAL':
                manual.append(entry)

        return manual

    def _detect_duplicate_payments(self, transactions: List[Dict]) -> List[Dict]:
        """Detect duplicate bank payments"""
        # Similar to duplicate entries but for bank transactions
        duplicates = []
        seen = {}

        for txn in transactions:
            key = f"{txn.get('amount', 0):.2f}_{txn.get('payee', '')}_{txn.get('date', '')}"
            if key in seen:
                duplicates.append({
                    'transaction_1': seen[key],
                    'transaction_2': txn
                })
            else:
                seen[key] = txn

        return duplicates

    def _detect_unusual_amounts(self, transactions: List[Dict]) -> List[Dict]:
        """Detect statistically unusual transaction amounts"""
        if not transactions:
            return []

        amounts = [abs(t.get('amount', 0)) for t in transactions if t.get('amount')]
        if not amounts:
            return []

        mean = np.mean(amounts)
        std = np.std(amounts)

        unusual = []
        for txn in transactions:
            amount = abs(txn.get('amount', 0))
            if std > 0 and abs(amount - mean) > 3 * std:
                unusual.append(txn)

        return unusual

    def _detect_structuring(self, transactions: List[Dict]) -> List[Dict]:
        """Detect potential transaction structuring"""
        # Look for multiple transactions just below reporting thresholds
        structured = []

        for txn in transactions:
            amount = abs(txn.get('amount', 0))
            if 9000 <= amount < 10000:  # Just below threshold
                structured.append(txn)

        return structured

    def _detect_similar_vendor_names(self, payments: List[Dict]) -> List[Dict]:
        """Detect payments to vendors with similar names"""
        # Would use string similarity algorithms in production
        similar = []
        vendors = set()

        for payment in payments:
            vendor = payment.get('vendor_name', '')
            if vendor:
                vendors.add(vendor.lower())

        # Simple implementation - look for vendors with same base name
        vendor_list = list(vendors)
        for i, v1 in enumerate(vendor_list):
            for v2 in vendor_list[i+1:]:
                if v1[:-1] == v2[:-1]:  # Same except last character
                    similar.append({'vendor_1': v1, 'vendor_2': v2})

        return similar

    def _detect_threshold_avoidance(self, payments: List[Dict]) -> List[Dict]:
        """Detect payments just below approval thresholds"""
        avoidance = []

        for payment in payments:
            amount = abs(payment.get('amount', 0))
            if 4500 <= amount < 5000:  # Just below threshold
                avoidance.append(payment)

        return avoidance

    def _detect_duplicate_expenses(self, expenses: List[Dict]) -> List[Dict]:
        """Detect duplicate expense claims"""
        duplicates = []
        seen = {}

        for expense in expenses:
            key = f"{expense.get('amount', 0):.2f}_{expense.get('date', '')}_{expense.get('employee_id', '')}"
            if key in seen:
                duplicates.append({
                    'expense_1': seen[key],
                    'expense_2': expense
                })
            else:
                seen[key] = expense

        return duplicates

    def _detect_unusual_expense_patterns(self, expenses: List[Dict]) -> List[Dict]:
        """Detect unusual expense patterns"""
        unusual = []

        # Group expenses by employee
        by_employee = {}
        for expense in expenses:
            emp_id = expense.get('employee_id', 'unknown')
            if emp_id not in by_employee:
                by_employee[emp_id] = []
            by_employee[emp_id].append(expense)

        # Find employees with unusually high expenses
        for emp_id, emp_expenses in by_employee.items():
            total = sum(e.get('amount', 0) for e in emp_expenses)
            avg = total / len(emp_expenses) if emp_expenses else 0

            if avg > 1000:  # Example threshold
                unusual.append({
                    'employee_id': emp_id,
                    'average_expense': avg,
                    'total_expenses': total,
                    'count': len(emp_expenses)
                })

        return unusual

    def _calculate_fraud_risk_score(self, findings: Dict[str, Any]) -> float:
        """Calculate overall fraud risk score (0-100)"""
        score = 0.0

        severity_weights = {
            'CRITICAL': 25.0,
            'HIGH': 15.0,
            'MEDIUM': 8.0,
            'LOW': 3.0
        }

        for indicator in findings.get('fraud_indicators', []):
            severity = indicator.get('severity', 'LOW')
            score += severity_weights.get(severity, 0)

        for pattern in findings.get('suspicious_patterns', []):
            severity = pattern.get('severity', 'LOW')
            score += severity_weights.get(severity, 0) * 0.5

        # Cap at 100
        return min(score, 100.0)

    def _calculate_confidence(self, findings: Dict[str, Any]) -> float:
        """Calculate confidence level of fraud detection"""
        # Based on data quality and quantity
        total_indicators = (
            len(findings.get('fraud_indicators', [])) +
            len(findings.get('suspicious_patterns', [])) +
            len(findings.get('anomalies', []))
        )

        if total_indicators == 0:
            return 95.0  # High confidence when no issues found

        # More indicators = lower confidence (more investigation needed)
        confidence = max(50.0, 100.0 - (total_indicators * 5))
        return confidence

    def _generate_recommendations(self, findings: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on findings"""
        recommendations = []

        risk_score = findings.get('risk_score', 0)

        if risk_score >= 80:
            recommendations.append("IMMEDIATE ACTION: Initiate forensic investigation")
            recommendations.append("Freeze suspicious transactions pending review")
            recommendations.append("Notify senior management and legal counsel")
        elif risk_score >= 60:
            recommendations.append("Conduct detailed review of flagged transactions")
            recommendations.append("Interview relevant personnel")
            recommendations.append("Review internal controls")
        elif risk_score >= 40:
            recommendations.append("Schedule follow-up audit")
            recommendations.append("Enhance monitoring procedures")
        else:
            recommendations.append("Continue regular monitoring")
            recommendations.append("Update fraud detection rules periodically")

        return recommendations

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'status': self.status,
            'thresholds': self.thresholds
        }


# Singleton instance
_fraud_agent_instance: Optional[FraudDetectionAgent] = None


def get_fraud_agent() -> FraudDetectionAgent:
    """Get singleton instance of FraudDetectionAgent"""
    global _fraud_agent_instance
    if _fraud_agent_instance is None:
        _fraud_agent_instance = FraudDetectionAgent()
    return _fraud_agent_instance
