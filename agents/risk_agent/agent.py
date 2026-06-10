"""
Risk Scoring Agent
وكيل تقييم المخاطر المالية

المهام:
- حساب Risk Score شامل
- حساب Fraud Score
- حساب Compliance Score
- تقييم المخاطر الضريبية
- تحليل المخاطر التشغيلية
- مصفوفة المخاطر (Risk Matrix)
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import math


class RiskCategory(Enum):
    FINANCIAL = "FINANCIAL"
    FRAUD = "FRAUD"
    COMPLIANCE = "COMPLIANCE"
    TAX = "TAX"
    OPERATIONAL = "OPERATIONAL"
    STRATEGIC = "STRATEGIC"


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class RiskFactor:
    factor_id: str
    category: str
    name: str
    description: str
    weight: float  # 0.0 to 1.0
    score: float  # 0.0 to 100.0
    evidence: List[str]
    trend: str  # INCREASING, DECREASING, STABLE


@dataclass
class RiskAssessment:
    assessment_id: str
    entity_type: str
    entity_id: str
    overall_risk_score: float
    risk_level: str
    category_scores: Dict[str, float]
    top_risks: List[RiskFactor]
    recommendations: List[str]
    timestamp: str
    confidence_level: float


class RiskScoringAgent:
    """
    وكيل تقييم المخاطر الشامل
    """
    
    def __init__(self):
        self.risk_factors: List[RiskFactor] = []
        self.assessments: List[RiskAssessment] = []
        
        # أوزان الفئات
        self.category_weights = {
            RiskCategory.FINANCIAL.value: 0.25,
            RiskCategory.FRAUD.value: 0.30,
            RiskCategory.COMPLIANCE.value: 0.20,
            RiskCategory.TAX.value: 0.15,
            RiskCategory.OPERATIONAL.value: 0.10
        }
        
        # عتبات مستويات الخطر
        self.risk_thresholds = {
            RiskLevel.LOW.value: (0, 25),
            RiskLevel.MEDIUM.value: (25, 50),
            RiskLevel.HIGH.value: (50, 75),
            RiskLevel.CRITICAL.value: (75, 100)
        }
        
    def add_risk_factor(self, factor: RiskFactor):
        """إضافة عامل خطر"""
        self.risk_factors.append(factor)
        
    def calculate_financial_risk(self, financial_data: Dict[str, Any]) -> float:
        """
        حساب المخاطر المالية بناءً على البيانات المالية
        
        العوامل:
        - نسبة الدين إلى الأصول
        - النسبة الحالية
        - هامش الربح
        - التدفق النقدي
        """
        risk_score = 0.0
        factors = []
        
        # نسبة الدين إلى الأصول
        debt_ratio = financial_data.get('debt_to_assets', 0)
        if debt_ratio > 0.7:
            debt_score = 90
        elif debt_ratio > 0.5:
            debt_score = 70
        elif debt_ratio > 0.3:
            debt_score = 40
        else:
            debt_score = 15
            
        factors.append(("Debt Ratio", debt_score, 0.25))
        
        # النسبة الحالية
        current_ratio = financial_data.get('current_ratio', 1)
        if current_ratio < 1:
            current_score = 85
        elif current_ratio < 1.5:
            current_score = 60
        elif current_ratio < 2:
            current_score = 30
        else:
            current_score = 10
            
        factors.append(("Current Ratio", current_score, 0.25))
        
        # هامش الربح
        profit_margin = financial_data.get('profit_margin', 0)
        if profit_margin < 0:
            margin_score = 90
        elif profit_margin < 0.05:
            margin_score = 65
        elif profit_margin < 0.10:
            margin_score = 40
        else:
            margin_score = 15
            
        factors.append(("Profit Margin", margin_score, 0.25))
        
        # التدفق النقدي
        cash_flow = financial_data.get('cash_flow_status', 'positive')
        if cash_flow == 'negative':
            cash_score = 85
        elif cash_flow == 'weak':
            cash_score = 55
        else:
            cash_score = 20
            
        factors.append(("Cash Flow", cash_score, 0.25))
        
        # حساب النتيجة الموزونة
        for _, score, weight in factors:
            risk_score += score * weight
            
        # إضافة عوامل الخطر
        for name, score, weight in factors:
            self.add_risk_factor(RiskFactor(
                factor_id=f"FIN-{hashlib.md5(name.encode()).hexdigest()[:6].upper()}",
                category=RiskCategory.FINANCIAL.value,
                name=name,
                description=f"مخاطر {name}: {score}/100",
                weight=weight,
                score=score,
                evidence=[f"القيمة المحسوبة: {score}"],
                trend="STABLE"
            ))
            
        return min(100, risk_score)
        
    def calculate_fraud_risk(self, fraud_indicators: Dict[str, Any]) -> float:
        """
        حساب مخاطر الاحتيال
        
        العوامل:
        - قيود يومية غير عادية
        - معاملات مع أطراف ذات صلة
        - تعديلات يدوية متكررة
        - فروقات في المطابقات
        """
        risk_score = 0.0
        max_score = 0.0
        
        # القيود غير العادية
        unusual_entries = fraud_indicators.get('unusual_journal_entries', 0)
        if unusual_entries > 50:
            score = 95
        elif unusual_entries > 20:
            score = 75
        elif unusual_entries > 5:
            score = 50
        else:
            score = 15
        risk_score += score * 0.25
        max_score += 100 * 0.25
        
        # الأطراف ذات الصلة
        related_party = fraud_indicators.get('related_party_transactions', 0)
        if related_party > 100:
            score = 90
        elif related_party > 50:
            score = 70
        elif related_party > 10:
            score = 45
        else:
            score = 10
        risk_score += score * 0.25
        max_score += 100 * 0.25
        
        # التعديلات اليدوية
        manual_adjustments = fraud_indicators.get('manual_adjustments', 0)
        if manual_adjustments > 100:
            score = 85
        elif manual_adjustments > 50:
            score = 65
        elif manual_adjustments > 20:
            score = 40
        else:
            score = 15
        risk_score += score * 0.25
        max_score += 100 * 0.25
        
        # فروقات المطابقة
        reconciliation_gaps = fraud_indicators.get('reconciliation_gaps', 0)
        if reconciliation_gaps > 50:
            score = 90
        elif reconciliation_gaps > 20:
            score = 70
        elif reconciliation_gaps > 5:
            score = 45
        else:
            score = 10
        risk_score += score * 0.25
        max_score += 100 * 0.25
        
        # إضافة عوامل الخطر
        self.add_risk_factor(RiskFactor(
            factor_id="FRD-UNUSUAL",
            category=RiskCategory.FRAUD.value,
            name="Unusual Journal Entries",
            description=f"قيود غير عادية: {unusual_entries}",
            weight=0.25,
            score=min(100, (unusual_entries / 50) * 100),
            evidence=[f"عدد القيود: {unusual_entries}"],
            trend="INCREASING" if unusual_entries > 20 else "STABLE"
        ))
        
        return min(100, (risk_score / max_score) * 100) if max_score > 0 else 0
        
    def calculate_compliance_risk(self, compliance_data: Dict[str, Any]) -> float:
        """
        حساب مخاطر عدم الامتثال
        
        العوامل:
        - مخالفات ضريبية سابقة
        - تأخر في الإقرارات
        - نقص في المستندات
        - مخالفات معايير محاسبية
        """
        risk_score = 0.0
        
        # مخالفات ضريبية سابقة
        prior_violations = compliance_data.get('prior_tax_violations', 0)
        if prior_violations >= 5:
            risk_score += 90 * 0.30
        elif prior_violations >= 2:
            risk_score += 70 * 0.30
        elif prior_violations >= 1:
            risk_score += 50 * 0.30
        else:
            risk_score += 10 * 0.30
            
        # تأخر في الإقرارات
        late_filings = compliance_data.get('late_filings', 0)
        if late_filings >= 5:
            risk_score += 85 * 0.25
        elif late_filings >= 2:
            risk_score += 60 * 0.25
        elif late_filings >= 1:
            risk_score += 35 * 0.25
        else:
            risk_score += 5 * 0.25
            
        # نقص المستندات
        missing_docs = compliance_data.get('missing_documents_percentage', 0)
        risk_score += min(100, missing_docs * 2) * 0.25
        
        # مخالفات معايير
        standards_violations = compliance_data.get('ifrs_violations', 0)
        if standards_violations >= 10:
            risk_score += 90 * 0.20
        elif standards_violations >= 5:
            risk_score += 70 * 0.20
        elif standards_violations >= 1:
            risk_score += 45 * 0.20
        else:
            risk_score += 10 * 0.20
            
        return min(100, risk_score)
        
    def calculate_tax_risk(self, tax_data: Dict[str, Any]) -> float:
        """
        حساب المخاطر الضريبية
        
        العوامل:
        - فروقات ضريبية
        - نسب خصم غير عادية
        - معاملات مشبوهة
        - تأخر سداد
        """
        risk_score = 0.0
        
        # فروقات ضريبية
        tax_diffs = tax_data.get('tax_discrepancies', 0)
        if tax_diffs > 1000000:
            risk_score += 90 * 0.30
        elif tax_diffs > 500000:
            risk_score += 75 * 0.30
        elif tax_diffs > 100000:
            risk_score += 55 * 0.30
        else:
            risk_score += 20 * 0.30
            
        # نسب الخصم
        deduction_ratio = tax_data.get('deduction_ratio', 0)
        if deduction_ratio > 0.5:
            risk_score += 80 * 0.25
        elif deduction_ratio > 0.3:
            risk_score += 60 * 0.25
        else:
            risk_score += 25 * 0.25
            
        # تأخر السداد
        payment_delays = tax_data.get('payment_delays_count', 0)
        risk_score += min(100, payment_delays * 15) * 0.25
        
        # معاملات مشبوهة
        suspicious_transactions = tax_data.get('suspicious_transactions', 0)
        risk_score += min(100, suspicious_transactions * 20) * 0.20
        
        return min(100, risk_score)
        
    def get_risk_level(self, score: float) -> str:
        """تحديد مستوى الخطر بناءً على النتيجة"""
        if score >= 75:
            return RiskLevel.CRITICAL.value
        elif score >= 50:
            return RiskLevel.HIGH.value
        elif score >= 25:
            return RiskLevel.MEDIUM.value
        else:
            return RiskLevel.LOW.value
            
    async def assess_risks(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate the risk assessment process
        
        Args:
            data: Combined financial data and core agent results
            
        Returns:
            Comprehensive risk assessment results
        """
        # Calculate scores for each category
        financial_score = self.calculate_financial_risk(data)
        
        # Extract indicators from core results if available
        core_results = data.get('core_results', {})
        fraud_indicators = core_results.get('fraud_agent', {})
        compliance_data = core_results.get('compliance_agent', {})
        
        fraud_score = self.calculate_fraud_risk(fraud_indicators)
        compliance_score = self.calculate_compliance_risk(compliance_data)
        tax_score = self.calculate_tax_risk(data.get('tax_data', {}))
        
        category_scores = {
            RiskCategory.FINANCIAL.value: financial_score,
            RiskCategory.FRAUD.value: fraud_score,
            RiskCategory.COMPLIANCE.value: compliance_score,
            RiskCategory.TAX.value: tax_score,
            RiskCategory.OPERATIONAL.value: 20.0  # Default value
        }
        
        assessment = self.create_assessment("ENTITY", data.get("entity_id", "DEFAULT"), category_scores)
        return asdict(assessment)

    def create_assessment(self, entity_type: str, entity_id: str, 
                         category_scores: Dict[str, float]) -> RiskAssessment:
        """إنشاء تقييم مخاطر شامل"""
        
        # حساب النتيجة الإجمالية الموزونة
        overall_score = 0.0
        total_weight = 0.0
        
        for category, score in category_scores.items():
            weight = self.category_weights.get(category, 0.1)
            overall_score += score * weight
            total_weight += weight
            
        if total_weight > 0:
            overall_score = overall_score / total_weight
            
        # تحديد مستوى الخطر
        risk_level = self.get_risk_level(overall_score)
        
        # الحصول على أعلى المخاطر
        top_risks = sorted(self.risk_factors, key=lambda x: x.score, reverse=True)[:10]
        
        # توليد التوصيات
        recommendations = self._generate_recommendations(category_scores, top_risks)
        
        assessment = RiskAssessment(
            assessment_id=f"RISK-{hashlib.md5(f'{entity_type}{entity_id}{datetime.now()}'.encode()).hexdigest()[:8].upper()}",
            entity_type=entity_type,
            entity_id=entity_id,
            overall_risk_score=round(overall_score, 2),
            risk_level=risk_level,
            category_scores={k: round(v, 2) for k, v in category_scores.items()},
            top_risks=top_risks,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat(),
            confidence_level=0.85
        )
        
        self.assessments.append(assessment)
        return assessment
        
    def _generate_recommendations(self, category_scores: Dict[str, float], 
                                  top_risks: List[RiskFactor]) -> List[str]:
        """توليد توصيات بناءً على التقييم"""
        recommendations = []
        
        if category_scores.get(RiskCategory.FRAUD.value, 0) > 50:
            recommendations.append("⚠️ تنفيذ مراجعة فورية للكشف عن الاحتيال")
            recommendations.append("📋 تعزيز ضوابط العمليات المالية")
            
        if category_scores.get(RiskCategory.TAX.value, 0) > 50:
            recommendations.append("💰 مراجعة الإقرارات الضريبية المقدمة")
            recommendations.append("📝 توثيق جميع المعاملات الضريبية")
            
        if category_scores.get(RiskCategory.COMPLIANCE.value, 0) > 50:
            recommendations.append("✅ مراجعة الالتزام بمعايير IFRS و ISA")
            recommendations.append("📚 تحديث سياسات الامتثال الداخلية")
            
        if category_scores.get(RiskCategory.FINANCIAL.value, 0) > 50:
            recommendations.append("📊 تحسين إدارة التدفقات النقدية")
            recommendations.append("💵 مراجعة هيكل الديون")
            
        if not recommendations:
            recommendations.append("✓ الاستمرار في المراقبة الدورية")
            recommendations.append("📈 الحفاظ على مستويات التحكم الحالية")
            
        return recommendations
        
    def get_risk_matrix(self) -> Dict[str, Any]:
        """إنشاء مصفوفة المخاطر"""
        matrix = {
            "likelihood": ["Rare", "Unlikely", "Possible", "Likely", "Almost Certain"],
            "impact": ["Insignificant", "Minor", "Moderate", "Major", "Catastrophic"],
            "risks": []
        }
        
        for risk in self.risk_factors:
            # تحويل النتيجة إلى إحداثيات في المصفوفة
            likelihood = min(4, int(risk.score / 20))
            impact = min(4, int(risk.score / 20))
            
            matrix["risks"].append({
                "name": risk.name,
                "category": risk.category,
                "score": risk.score,
                "likelihood_idx": likelihood,
                "impact_idx": impact,
                "level": self.get_risk_level(risk.score)
            })
            
        return matrix
        
    def export_assessment(self, assessment: RiskAssessment, format: str = "json") -> str:
        """تصدير تقييم المخاطر"""
        if format == "json":
            data = {
                "assessment_id": assessment.assessment_id,
                "entity_type": assessment.entity_type,
                "entity_id": assessment.entity_id,
                "overall_risk_score": assessment.overall_risk_score,
                "risk_level": assessment.risk_level,
                "category_scores": assessment.category_scores,
                "top_risks": [asdict(r) for r in assessment.top_risks],
                "recommendations": assessment.recommendations,
                "timestamp": assessment.timestamp,
                "confidence_level": assessment.confidence_level
            }
            return json.dumps(data, indent=2, ensure_ascii=False)
        return ""
    
    def calculate_risk_score(self, entity_data: Dict[str, Any]) -> float:
        """
        حساب نتيجة المخاطر الشاملة للكيان
        
        Args:
            entity_data: بيانات الكيان المالية والتشغيلية
            
        Returns:
            float: نتيجة المخاطر من 0 إلى 100
        """
        financial_risk = self.calculate_financial_risk(
            entity_data.get('financial', {})
        )
        fraud_risk = self.calculate_fraud_risk(
            entity_data.get('fraud_indicators', {})
        )
        compliance_risk = self.calculate_compliance_risk(
            entity_data.get('compliance', {})
        )
        tax_risk = self.calculate_tax_risk(
            entity_data.get('tax', {})
        )
        
        category_scores = {
            RiskCategory.FINANCIAL.value: financial_risk,
            RiskCategory.FRAUD.value: fraud_risk,
            RiskCategory.COMPLIANCE.value: compliance_risk,
            RiskCategory.TAX.value: tax_risk
        }
        
        # حساب النتيجة الإجمالية
        overall_score = sum(
            score * self.category_weights.get(cat, 0.1)
            for cat, score in category_scores.items()
        )
        
        return min(100, overall_score)
    
    def assess(self, entity_type: str, entity_id: str, 
               entity_data: Dict[str, Any]) -> RiskAssessment:
        """
        إجراء تقييم مخاطر شامل للكيان
        
        Args:
            entity_type: نوع الكيان (company, account, transaction)
            entity_id: معرف الكيان
            entity_data: بيانات الكيان
            
        Returns:
            RiskAssessment: تقييم المخاطر الكامل
        """
        # حساب جميع أنواع المخاطر
        financial_risk = self.calculate_financial_risk(
            entity_data.get('financial', {})
        )
        fraud_risk = self.calculate_fraud_risk(
            entity_data.get('fraud_indicators', {})
        )
        compliance_risk = self.calculate_compliance_risk(
            entity_data.get('compliance', {})
        )
        tax_risk = self.calculate_tax_risk(
            entity_data.get('tax', {})
        )
        
        category_scores = {
            RiskCategory.FINANCIAL.value: financial_risk,
            RiskCategory.FRAUD.value: fraud_risk,
            RiskCategory.COMPLIANCE.value: compliance_risk,
            RiskCategory.TAX.value: tax_risk
        }
        
        # إنشاء التقييم الشامل
        return self.create_assessment(
            entity_type=entity_type,
            entity_id=entity_id,
            category_scores=category_scores
        )


# مثال استخدام
if __name__ == "__main__":
    print("=" * 80)
    print("Risk Scoring Agent - وكيل تقييم المخاطر")
    print("=" * 80)
    
    agent = RiskScoringAgent()
    
    # بيانات مالية تجريبية
    financial_data = {
        'debt_to_assets': 0.65,
        'current_ratio': 1.2,
        'profit_margin': 0.03,
        'cash_flow_status': 'weak'
    }
    
    # مؤشرات احتيال
    fraud_indicators = {
        'unusual_journal_entries': 35,
        'related_party_transactions': 75,
        'manual_adjustments': 45,
        'reconciliation_gaps': 12
    }
    
    # بيانات امتثال
    compliance_data = {
        'prior_tax_violations': 2,
        'late_filings': 3,
        'missing_documents_percentage': 15,
        'ifrs_violations': 4
    }
    
    # بيانات ضريبية
    tax_data = {
        'tax_discrepancies': 750000,
        'deduction_ratio': 0.42,
        'payment_delays_count': 2,
        'suspicious_transactions': 8
    }
    
    print("\n📊 حساب نتائج المخاطر...")
    
    # حساب المخاطر لكل فئة
    financial_risk = agent.calculate_financial_risk(financial_data)
    fraud_risk = agent.calculate_fraud_risk(fraud_indicators)
    compliance_risk = agent.calculate_compliance_risk(compliance_data)
    tax_risk = agent.calculate_tax_risk(tax_data)
    
    print(f"\n✓ المخاطر المالية: {financial_risk:.2f}/100")
    print(f"✓ مخاطر الاحتيال: {fraud_risk:.2f}/100")
    print(f"✓ مخاطر الامتثال: {compliance_risk:.2f}/100")
    print(f"✓ المخاطر الضريبية: {tax_risk:.2f}/100")
    
    # إنشاء التقييم الشامل
    category_scores = {
        RiskCategory.FINANCIAL.value: financial_risk,
        RiskCategory.FRAUD.value: fraud_risk,
        RiskCategory.COMPLIANCE.value: compliance_risk,
        RiskCategory.TAX.value: tax_risk,
        RiskCategory.OPERATIONAL.value: 35.0
    }
    
    assessment = agent.create_assessment(
        entity_type="Company",
        entity_id="COMP-2025-001",
        category_scores=category_scores
    )
    
    print("\n" + "=" * 80)
    print("📋 تقرير تقييم المخاطر الشامل")
    print("=" * 80)
    
    print(f"\nمعرف التقييم: {assessment.assessment_id}")
    print(f"الكيان: {assessment.entity_type} - {assessment.entity_id}")
    print(f"نتيجة الخطر الإجمالية: {assessment.overall_risk_score}/100")
    print(f"مستوى الخطر: {assessment.risk_level}")
    print(f"مستوى الثقة: {assessment.confidence_level * 100:.1f}%")
    
    print("\n📊 النتائج حسب الفئة:")
    for category, score in assessment.category_scores.items():
        level = agent.get_risk_level(score)
        print(f"  {category}: {score}/100 ({level})")
    
    print("\n⚠️ أعلى 5 مخاطر:")
    for i, risk in enumerate(assessment.top_risks[:5], 1):
        print(f"  {i}. {risk.name} - {risk.score:.1f}/100 ({risk.trend})")
        
    print("\n💡 التوصيات:")
    for rec in assessment.recommendations:
        print(f"  • {rec}")
        
    # مصفوفة المخاطر
    print("\n" + "=" * 80)
    print("🎯 مصفوفة المخاطر")
    print("=" * 80)
    
    matrix = agent.get_risk_matrix()
    print(f"إجمالي المخاطر المسجلة: {len(matrix['risks'])}")
    
    critical_risks = [r for r in matrix['risks'] if r['level'] == 'CRITICAL']
    high_risks = [r for r in matrix['risks'] if r['level'] == 'HIGH']
    
    print(f"مخاطر حرجة: {len(critical_risks)}")
    print(f"مخاطر عالية: {len(high_risks)}")
    
    print("\n✅ تم تقييم المخاطر بنجاح!")
