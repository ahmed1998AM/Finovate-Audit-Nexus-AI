"""
Finovate Audit Nexus AI
Explainable AI (XAI) Agent
وكيل تفسير قرارات الذكاء الاصطناعي

المهام:
- شرح قرارات الذكاء الاصطناعي
- توضيح الأسباب وراء النتائج
- شرح الأدلة المكتشفة
- توضيح تأثير المشكلات
- تقديم توصيات قابلة للتنفيذ
"""

import json
from datetime import datetime
from typing import Any, Dict, List


class ExplainableAIAgent:
    """وكيل تفسير قرارات الذكاء الاصطناعي"""

    def __init__(self):
        self.agent_name = "Explainable AI Agent"
        self.agent_type = "XAI"
        self.version = "1.0.0"
        self.created_at = datetime.now()

    def explain_decision(self,
                        decision: str,
                        context: Dict[str, Any],
                        confidence_score: float) -> Dict[str, Any]:
        """
        شرح قرار اتخذ بواسطة الذكاء الاصطناعي

        Args:
            decision: القرار المتخذ
            context: سياق القرار
            confidence_score: درجة الثقة

        Returns:
            dict: شرح مفصل للقرار
        """
        explanation = {
            "decision": decision,
            "confidence_score": confidence_score,
            "confidence_level": self._get_confidence_level(confidence_score),
            "explanation": self._generate_explanation(decision, context),
            "key_factors": self._identify_key_factors(context),
            "evidence": self._collect_evidence(context),
            "reasoning_chain": self._build_reasoning_chain(decision, context),
            "alternative_considerations": self._get_alternatives(context),
            "recommendations": self._generate_recommendations(decision, context),
            "timestamp": datetime.now().isoformat()
        }

        return explanation

    def _get_confidence_level(self, score: float) -> str:
        """تحديد مستوى الثقة بناءً على الدرجة"""
        if score >= 0.9:
            return "مرتفع جداً"
        elif score >= 0.75:
            return "مرتفع"
        elif score >= 0.6:
            return "متوسط"
        elif score >= 0.4:
            return "منخفض"
        else:
            return "منخفض جداً"

    def _generate_explanation(self, decision: str, context: Dict[str, Any]) -> str:
        """توليد شرح للقرار"""
        explanations = {
            "fraud_detected": "تم كشف عملية احتيالية محتملة بناءً على تحليل الأنماط غير الطبيعية في البيانات المالية",
            "anomaly_found": "تم رصد انحراف عن النمط الطبيعي للحركات المالية",
            "compliance_issue": "تم اكتشاف عدم التزام بمعايير محاسبية أو ضريبية",
            "risk_identified": "تم تحديد مستوى خطر يتطلب الانتباه",
            "normal_transaction": "العملية تبدو طبيعية ولا توجد مؤشرات على مشاكل"
        }

        for key in explanations:
            if key in decision.lower():
                return explanations[key]

        return f"تم اتخاذ القرار بناءً على تحليل شامل للبيانات المتاحة: {decision}"

    def _identify_key_factors(self, context: Dict[str, Any]) -> List[str]:
        """تحديد العوامل الرئيسية التي أثرت في القرار"""
        factors = []

        if "amount" in context:
            factors.append(f"قيمة العملية: {context['amount']}")

        if "frequency" in context:
            factors.append(f"التكرار: {context['frequency']} مرة")

        if "deviation" in context:
            factors.append(f"نسبة الانحراف: {context['deviation']:.2%}")

        if "pattern_match" in context:
            factors.append(f"مطابقة النمط: {context['pattern_match']}")

        if "user_behavior" in context:
            factors.append("سلوك المستخدم غير معتاد")

        if "timing" in context:
            factors.append(f"توقيت غير طبيعي: {context['timing']}")

        return factors if factors else ["تحليل شامل للبيانات"]

    def _collect_evidence(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """جمع الأدلة الداعمة للقرار"""
        evidence_list = []

        if "transaction_id" in context:
            evidence_list.append({
                "type": "معرف العملية",
                "value": context["transaction_id"],
                "relevance": "عالية"
            })

        if "account" in context:
            evidence_list.append({
                "type": "الحساب المتأثر",
                "value": context["account"],
                "relevance": "عالية"
            })

        if "date" in context:
            evidence_list.append({
                "type": "تاريخ العملية",
                "value": context["date"],
                "relevance": "متوسطة"
            })

        if "user" in context:
            evidence_list.append({
                "type": "المستخدم المنفذ",
                "value": context["user"],
                "relevance": "متوسطة"
            })

        return evidence_list

    def _build_reasoning_chain(self, decision: str, context: Dict[str, Any]) -> List[str]:
        """بناء سلسلة الاستدلال المنطقي"""
        chain = [
            "1. جمع البيانات المالية ذات الصلة",
            "2. تطبيق خوارزميات كشف الأنماط",
            "3. مقارنة البيانات مع المعايير المرجعية",
            "4. حساب درجات الخطر والانحراف",
            "5. تقييم النتائج بناءً على قواعد الأعمال",
            f"6. اتخاذ القرار: {decision}"
        ]

        return chain

    def _get_alternatives(self, context: Dict[str, Any]) -> List[str]:
        """الحصول على البدائل التي تم النظر فيها"""
        return [
            "مراجعة يدوية إضافية",
            "طلب وثائق داعمة",
            "إجراء مقابلة مع المسؤول",
            "مراقبة الحساب لفترة أطول",
            "تصنيف العملية كطبيعية مع المراقبة"
        ]

    def _generate_recommendations(self, decision: str, context: Dict[str, Any]) -> List[str]:
        """توليد توصيات قابلة للتنفيذ"""
        recommendations = []

        if "fraud" in decision.lower() or "risk" in decision.lower():
            recommendations.extend([
                "إجراء تحقيق فوري في العملية",
                "تجميد الحسابات المشتبه بها",
                "إبلاغ الإدارة العليا",
                "توثيق جميع الأدلة",
                "التشاور مع المستشار القانوني"
            ])
        elif "compliance" in decision.lower():
            recommendations.extend([
                "مراجعة المعالجة المحاسبية",
                "تعديل القيود إذا لزم الأمر",
                "تحديث السياسات والإجراءات",
                "تدريب الموظفين على المعايير"
            ])
        else:
            recommendations.extend([
                "متابعة روتينية",
                "توثيق النتيجة في سجل المراجعة",
                "استمرار المراقبة الدورية"
            ])

        return recommendations

    def explain_fraud_detection(self,
                               fraud_result: Dict[str, Any]) -> Dict[str, Any]:
        """شرح نتائج كشف الاحتيال بشكل مفصل"""
        explanation = {
            "summary": "تحليل مفصل لكشف الاحتيال",
            "detected_patterns": fraud_result.get("patterns", []),
            "risk_indicators": self._explain_risk_indicators(fraud_result),
            "statistical_analysis": self._explain_statistics(fraud_result),
            "behavioral_flags": fraud_result.get("behavioral_flags", []),
            "action_plan": self._generate_action_plan(fraud_result),
            "legal_implications": self._explain_legal_aspects(fraud_result),
            "timestamp": datetime.now().isoformat()
        }

        return explanation

    def _explain_risk_indicators(self, result: Dict[str, Any]) -> List[Dict[str, str]]:
        """شرح مؤشرات الخطر المكتشفة"""
        indicators = []

        if result.get("duplicate_entries"):
            indicators.append({
                "indicator": "قيود مكررة",
                "explanation": "تم رصد عمليات متطابقة تماماً مما يشير إلى احتمال التكرار المتعمد",
                "severity": "عالية"
            })

        if result.get("round_amounts"):
            indicators.append({
                "indicator": "مبالغ مدورة",
                "explanation": "كثرة المبالغ المدورة تماماً قد تشير إلى عمليات مصطنعة",
                "severity": "متوسطة"
            })

        if result.get("unusual_timing"):
            indicators.append({
                "indicator": "توقيت غير اعتيادي",
                "explanation": "تم تنفيذ العمليات في أوقات غير العمل الرسمية",
                "severity": "عالية"
            })

        return indicators

    def _explain_statistics(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """شرح التحليل الإحصائي"""
        return {
            "z_score_explanation": "يقيس عدد الانحرافات المعيارية عن المتوسط",
            "benford_analysis": "تحليل توزيع الأرقام الأولى لاكتشاف التلاعب",
            "trend_deviation": "انحراف عن الاتجاه التاريخي المتوقع",
            "peer_comparison": "مقارنة مع أداء الوحدات المماثلة"
        }

    def _generate_action_plan(self, result: Dict[str, Any]) -> List[Dict[str, str]]:
        """توليد خطة عمل مفصلة"""
        risk_score = result.get("risk_score", 0)

        if risk_score >= 80:
            return [
                {"step": "1", "action": "إيقاف فوري للعمليات المشتبه بها", "timeline": "فوراً"},
                {"step": "2", "action": "تشكيل لجنة تحقيق", "timeline": "24 ساعة"},
                {"step": "3", "action": "جمع وحفظ جميع الأدلة", "timeline": "48 ساعة"},
                {"step": "4", "action": "إبلاغ الجهات الرقابية إذا لزم", "timeline": "72 ساعة"},
                {"step": "5", "action": "إعداد تقرير مفصل", "timeline": "أسبوع"}
            ]
        elif risk_score >= 50:
            return [
                {"step": "1", "action": "مراجعة موسعة للعمليات", "timeline": "أسبوع"},
                {"step": "2", "action": "طلب وثائق داعمة", "timeline": "أسبوعين"},
                {"step": "3", "action": "مقابلة المسؤولين", "timeline": "أسبوعين"},
                {"step": "4", "action": "تقييم النتائج واتخاذ القرار", "timeline": "3 أسابيع"}
            ]
        else:
            return [
                {"step": "1", "action": "توثيق الملاحظة", "timeline": "3 أيام"},
                {"step": "2", "action": "متابعة روتينية", "timeline": "شهر"},
                {"step": "3", "action": "مراجعة دورية", "timeline": "ربع سنوي"}
            ]

    def _explain_legal_aspects(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """شرح الجوانب القانونية"""
        return {
            "applicable_laws": [
                "قانون العقوبات المصري - باب جرائم الأموال",
                "قانون مكافحة غسيل الأموال رقم 80 لسنة 2002",
                "قانون الضرائب المصرية",
                "قانون الشركات التجارية"
            ],
            "potential_violations": result.get("violations", ["لم يتم تحديد انتهاكات محددة"]),
            "reporting_requirements": "قد يتطلب الإبلاغ للجهات الرقابية حسب شدة الحالة",
            "statute_of_limitations": "تختلف مدة التقادم حسب نوع الجريمة"
        }

    def generate_audit_trail_explanation(self,
                                        audit_findings: List[Dict[str, Any]]) -> str:
        """توليد شرح لمسار التدقيق الكامل"""
        explanation_parts = [
            "# تقرير شرح مسار التدقيق",
            f"تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## ملخص تنفيذي",
            f"عدد النتائج: {len(audit_findings)}",
            "",
            "## التفاصيل"
        ]

        for i, finding in enumerate(audit_findings, 1):
            explanation_parts.append(f"\n### نتيجة {i}")
            explanation_parts.append(f"- النوع: {finding.get('type', 'غير محدد')}")
            explanation_parts.append(f"- الوصف: {finding.get('description', 'لا يوجد وصف')}")
            explanation_parts.append(f"- مستوى الخطر: {finding.get('risk_level', 'غير محدد')}")
            explanation_parts.append(f"- التوصية: {finding.get('recommendation', 'لا توجد')}")

        return "\n".join(explanation_parts)

    def export_explanation(self,
                          explanation: Dict[str, Any],
                          format: str = "json") -> str:
        """تصدير الشرح بصيغة محددة"""
        if format == "json":
            return json.dumps(explanation, indent=2, ensure_ascii=False)
        elif format == "text":
            return self._to_text_format(explanation)
        else:
            return json.dumps(explanation, indent=2, ensure_ascii=False)

    def _to_text_format(self, explanation: Dict[str, Any]) -> str:
        """تحويل الشرح إلى نص مقروء"""
        lines = [
            "=" * 60,
            "تقرير شرح قرار الذكاء الاصطناعي",
            "=" * 60,
            f"القرار: {explanation.get('decision', 'غير محدد')}",
            f"مستوى الثقة: {explanation.get('confidence_level', 'غير محدد')} ({explanation.get('confidence_score', 0):.1%})",
            "",
            "الشرح:",
            explanation.get('explanation', 'لا يوجد شرح'),
            "",
            "العوامل الرئيسية:"
        ]

        for factor in explanation.get('key_factors', []):
            lines.append(f"  • {factor}")

        lines.extend([
            "",
            "التوصيات:"
        ])

        for rec in explanation.get('recommendations', []):
            lines.append(f"  • {rec}")

        lines.append("=" * 60)

        return "\n".join(lines)


# مثال على الاستخدام
if __name__ == "__main__":
    print("=" * 60)
    print("Finovate Audit Nexus AI - Explainable AI Agent")
    print("=" * 60)

    # إنشاء وكيل XAI
    xai_agent = ExplainableAIAgent()

    # مثال: شرح قرار كشف احتيال
    fraud_context = {
        "transaction_id": "TXN-2025-001234",
        "amount": 500000,
        "account": "1100-现金",
        "date": "2025-01-15",
        "user": "user_123",
        "frequency": 5,
        "deviation": 0.85,
        "pattern_match": "duplicate_entries",
        "timing": "23:45",
        "duplicate_entries": True,
        "round_amounts": True,
        "unusual_timing": True
    }

    fraud_result = {
        "risk_score": 87.5,
        "patterns": ["duplicate_entries", "round_amounts", "unusual_timing"],
        "behavioral_flags": ["after_hours_transaction", "high_frequency"],
        "violations": ["احتيال مالي محتمل", "تلاعب بالسجلات"]
    }

    print("\n📊 شرح قرار كشف الاحتيال:\n")
    explanation = xai_agent.explain_decision(
        decision="Fraud Detected - High Risk Transaction",
        context=fraud_context,
        confidence_score=0.92
    )

    print(xai_agent.export_explanation(explanation, format="text"))

    print("\n\n🔍 تحليل مفصل لكشف الاحتيال:\n")
    detailed_fraud_explanation = xai_agent.explain_fraud_detection(fraud_result)
    print(json.dumps(detailed_fraud_explanation, indent=2, ensure_ascii=False))

    print("\n\n✅ تم توليد شرح تفصيلي لقرار الذكاء الاصطناعي بنجاح!")
