"""
Finovate Audit Nexus AI
AI Quality Assurance Agent
وكيل مراجعة جودة الذكاء الاصطناعي

المهام:
- كشف هلوسة الذكاء الاصطناعي
- كشف التناقضات في النتائج
- تقييم درجة الثقة
- مراجعة نتائج الوكلاء
- التحقق من الدقة والاتساق
- ضمان جودة المخرجات
"""

import re
import statistics
from datetime import datetime
from typing import Any, Dict, List, Tuple


class AIQualityAssuranceAgent:
    """وكيل مراجعة جودة الذكاء الاصطناعي"""

    def __init__(self):
        self.agent_name = "AI Quality Assurance Agent"
        self.agent_type = "QA"
        self.version = "1.0.0"
        self.created_at = datetime.now()

        # عتبات الجودة
        self.confidence_threshold = 0.7
        self.consistency_threshold = 0.8
        self.hallucination_indicators = [
            "ربما", "قد يكون", "من المحتمل", "غير مؤكد",
            "أعتقد", "يبدو", "قد", "يمكن أن"
        ]

    def review_agent_output(self,
                           agent_name: str,
                           output: Dict[str, Any],
                           expected_schema: Dict[str, Any]) -> Dict[str, Any]:
        """مراجعة مخرجات وكيل ذكي"""
        review_result = {
            "agent_name": agent_name,
            "review_timestamp": datetime.now().isoformat(),
            "schema_validation": self._validate_schema(output, expected_schema),
            "consistency_check": self._check_consistency(output),
            "hallucination_detection": self._detect_hallucinations(output),
            "confidence_assessment": self._assess_confidence(output),
            "accuracy_score": self._calculate_accuracy_score(output),
            "issues_found": [],
            "recommendations": [],
            "overall_quality": "pending",
            "passed": False
        }

        review_result["issues_found"] = self._identify_issues(review_result)
        review_result["recommendations"] = self._generate_recommendations(review_result)
        review_result["overall_quality"], review_result["passed"] = self._calculate_overall_quality(review_result)

        return review_result

    def _validate_schema(self, output: Dict[str, Any], expected_schema: Dict[str, Any]) -> Dict[str, Any]:
        """التحقق من صحة هيكل المخرجات"""
        validation = {"is_valid": True, "missing_fields": [], "extra_fields": [], "type_mismatches": []}

        for field in expected_schema.get("required_fields", []):
            if field not in output:
                validation["missing_fields"].append(field)
                validation["is_valid"] = False

        expected_keys = set(expected_schema.get("fields", {}).keys())
        actual_keys = set(output.keys())
        validation["extra_fields"] = list(actual_keys - expected_keys - {"metadata"})

        for field, expected_type in expected_schema.get("field_types", {}).items():
            if field in output:
                actual_type = type(output[field]).__name__
                if actual_type != expected_type:
                    validation["type_mismatches"].append({"field": field, "expected": expected_type, "actual": actual_type})

        return validation

    def _check_consistency(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """التحقق من اتساق النتائج"""
        consistency = {"is_consistent": True, "consistency_score": 1.0, "contradictions": [], "inconsistencies": []}

        numbers = self._extract_numbers(output)
        if len(numbers) >= 2:
            ratios = [numbers[i] / numbers[i+1] if numbers[i+1] != 0 else 0 for i in range(len(numbers)-1)]
            if ratios:
                ratio_variance = statistics.variance(ratios) if len(ratios) > 1 else 0
                if ratio_variance > 100:
                    consistency["inconsistencies"].append("تباين كبير في النسب العددية")
                    consistency["is_consistent"] = False
                    consistency["consistency_score"] -= 0.3

        text_fields = self._extract_text_fields(output)
        for i, text1 in enumerate(text_fields):
            for text2 in text_fields[i+1:]:
                if self._are_contradictory(text1, text2):
                    consistency["contradictions"].append(f"{text1} vs {text2}")
                    consistency["is_consistent"] = False
                    consistency["consistency_score"] -= 0.4

        consistency["consistency_score"] = max(0, consistency["consistency_score"])
        return consistency

    def _detect_hallucinations(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """كشف هلوسة الذكاء الاصطناعي"""
        detection = {"hallucination_detected": False, "hallucination_score": 0.0, "uncertain_statements": [], "unsupported_claims": [], "confidence_warnings": []}

        text_output = str(output).lower()
        uncertainty_count = sum(text_output.count(indicator.lower()) for indicator in self.hallucination_indicators)

        total_words = len(text_output.split())
        if total_words > 0:
            detection["hallucination_score"] = min(1.0, uncertainty_count / (total_words / 10))

        if detection["hallucination_score"] > 0.3:
            detection["hallucination_detected"] = True

        if "facts" in output and "sources" not in output:
            detection["unsupported_claims"].append("ادعاءات بدون مصادر")

        return detection

    def _assess_confidence(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """تقييم درجة الثقة"""
        assessment = {"confidence_level": "unknown", "confidence_score": 0.5, "factors": [], "warnings": []}

        if "confidence_score" in output:
            assessment["confidence_score"] = output["confidence_score"]
        elif "confidence" in output:
            assessment["confidence_score"] = output["confidence"]

        score = assessment["confidence_score"]
        if score >= 0.9:
            assessment["confidence_level"] = "مرتفع جداً"
        elif score >= 0.75:
            assessment["confidence_level"] = "مرتفع"
        elif score >= 0.6:
            assessment["confidence_level"] = "متوسط"
        elif score >= 0.4:
            assessment["confidence_level"] = "منخفض"
        else:
            assessment["confidence_level"] = "منخفض جداً"
            assessment["warnings"].append("درجة الثقة منخفضة جداً")

        if "data_quality" in output:
            assessment["factors"].append(f"جودة البيانات: {output['data_quality']}")
        if "sample_size" in output:
            assessment["factors"].append(f"حجم العينة: {output['sample_size']}")

        return assessment

    def _calculate_accuracy_score(self, output: Dict[str, Any]) -> float:
        """حساب درجة الدقة"""
        score = 1.0
        if "errors" in output and output["errors"]:
            score -= len(output["errors"]) * 0.1
        if "warnings" in output and output["warnings"]:
            score -= len(output["warnings"]) * 0.05
        completeness = len([k for k, v in output.items() if v is not None]) / max(len(output), 1)
        score += completeness * 0.2
        return max(0, min(1.0, score))

    def _extract_numbers(self, data: Any) -> List[float]:
        """استخراج الأرقام من البيانات"""
        numbers = []
        if isinstance(data, (int, float)):
            numbers.append(float(data))
        elif isinstance(data, dict):
            for value in data.values():
                numbers.extend(self._extract_numbers(value))
        elif isinstance(data, list):
            for item in data:
                numbers.extend(self._extract_numbers(item))
        elif isinstance(data, str):
            found = re.findall(r'[-+]?\d*\.?\d+', data)
            numbers.extend([float(n) for n in found])
        return numbers

    def _extract_text_fields(self, data: Any) -> List[str]:
        """استخراج الحقول النصية"""
        texts = []
        if isinstance(data, str):
            texts.append(data)
        elif isinstance(data, dict):
            for value in data.values():
                texts.extend(self._extract_text_fields(value))
        elif isinstance(data, list):
            for item in data:
                texts.extend(self._extract_text_fields(item))
        return texts

    def _are_contradictory(self, text1: str, text2: str) -> bool:
        """التحقق مما إذا كان النصان متناقضين"""
        contradiction_pairs = [("نعم", "لا"), ("صحيح", "خطأ"), ("مرتفع", "منخفض"), ("زيادة", "نقصان"), ("موجب", "سالب")]
        text1_lower, text2_lower = text1.lower(), text2.lower()
        for word1, word2 in contradiction_pairs:
            if (word1 in text1_lower and word2 in text2_lower) or (word2 in text1_lower and word1 in text2_lower):
                return True
        return False

    def _identify_issues(self, review_result: Dict[str, Any]) -> List[Dict[str, str]]:
        """تحديد المشاكل المكتشفة"""
        issues = []
        schema_val = review_result["schema_validation"]
        if not schema_val["is_valid"] and schema_val["missing_fields"]:
            issues.append({"type": "schema_error", "severity": "high", "description": f"حقول مفقودة: {', '.join(schema_val['missing_fields'])}"})

        consistency = review_result["consistency_check"]
        if not consistency["is_consistent"] and consistency["contradictions"]:
            issues.append({"type": "consistency_error", "severity": "high", "description": f"تناقضات مكتشفة: {len(consistency['contradictions'])}"})

        hallucination = review_result["hallucination_detection"]
        if hallucination["hallucination_detected"]:
            issues.append({"type": "hallucination_warning", "severity": "medium", "description": f"مؤشرات هلوسة: {hallucination['hallucination_score']:.2%}"})

        confidence = review_result["confidence_assessment"]
        if confidence["confidence_level"] in ["منخفض", "منخفض جداً"]:
            issues.append({"type": "low_confidence", "severity": "medium", "description": f"درجة الثقة: {confidence['confidence_level']}"})

        return issues

    def _generate_recommendations(self, review_result: Dict[str, Any]) -> List[str]:
        """توليد توصيات لتحسين الجودة"""
        recommendations = []
        for issue in review_result["issues_found"]:
            if issue["type"] == "schema_error":
                recommendations.append("مراجعة هيكل مخرجات الوكيل وإضافة الحقول المفقودة")
            elif issue["type"] == "consistency_error":
                recommendations.append("إجراء مراجعة يدوية للتناقضات المكتشفة")
            elif issue["type"] == "hallucination_warning":
                recommendations.append("تحسين دقة نموذج الذكاء الاصطناعي أو زيادة بيانات التدريب")
            elif issue["type"] == "low_confidence":
                recommendations.append("جمع بيانات إضافية أو تحسين خوارزميات التحليل")
        if not recommendations:
            recommendations.append("الجودة مقبولة - استمر في المراقبة الدورية")
        return recommendations

    def _calculate_overall_quality(self, review_result: Dict[str, Any]) -> Tuple[str, bool]:
        """حساب الجودة الشاملة"""
        scores = [
            1.0 if review_result["schema_validation"]["is_valid"] else 0.5,
            review_result["consistency_check"]["consistency_score"],
            1.0 - review_result["hallucination_detection"]["hallucination_score"],
            review_result["confidence_assessment"]["confidence_score"],
            review_result["accuracy_score"]
        ]
        overall_score = sum(scores) / len(scores)

        if overall_score >= 0.9:
            return "ممتاز", True
        elif overall_score >= 0.75:
            return "جيد", True
        elif overall_score >= 0.6:
            return "مقبول", True
        elif overall_score >= 0.4:
            return "ضعيف", False
        else:
            return "رافض", False

    def generate_qa_report(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """توليد تقرير جودة شامل"""
        return {
            "report_title": "تقرير مراجعة جودة الذكاء الاصطناعي",
            "generated_at": datetime.now().isoformat(),
            "total_agents_reviewed": len(reviews),
            "summary": {
                "passed": sum(1 for r in reviews if r["passed"]),
                "failed": sum(1 for r in reviews if not r["passed"]),
                "quality_distribution": self._calculate_quality_distribution(reviews)
            },
            "detailed_reviews": reviews,
            "critical_issues": self._extract_critical_issues(reviews),
            "action_items": self._generate_action_items(reviews)
        }

    def _calculate_quality_distribution(self, reviews: List[Dict[str, Any]]) -> Dict[str, int]:
        """حساب توزيع مستويات الجودة"""
        distribution = {"ممتاز": 0, "جيد": 0, "مقبول": 0, "ضعيف": 0, "رافض": 0}
        for review in reviews:
            quality = review.get("overall_quality", "مقبول")
            if quality in distribution:
                distribution[quality] += 1
        return distribution

    def _extract_critical_issues(self, reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """استخراج المشاكل الحرجة"""
        return [{"agent": r["agent_name"], "issue": i} for r in reviews for i in r.get("issues_found", []) if i.get("severity") == "high"]

    def _generate_action_items(self, reviews: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """توليد بنود العمل المطلوبة"""
        action_items = []
        for review in reviews:
            if not review["passed"]:
                action_items.append({"priority": "high", "agent": review["agent_name"], "action": "مراجعة عاجلة مطلوبة", "reason": review["overall_quality"]})
            elif review["overall_quality"] == "مقبول":
                action_items.append({"priority": "medium", "agent": review["agent_name"], "action": "تحسين موصى به", "reason": "الجودة مقبولة ولكن يمكن تحسينها"})
        return action_items


if __name__ == "__main__":
    print("=" * 60)
    print("Finovate Audit Nexus AI - QA Agent")
    print("=" * 60)

    qa_agent = AIQualityAssuranceAgent()

    sample_output = {
        "decision": "Fraud Detected",
        "confidence_score": 0.85,
        "risk_level": "high",
        "findings": [{"type": "duplicate", "amount": 50000}, {"type": "anomaly", "amount": 75000}],
        "recommendation": "Investigate immediately"
    }

    expected_schema = {
        "required_fields": ["decision", "confidence_score"],
        "fields": {"decision": "str", "confidence_score": "float", "risk_level": "str", "findings": "list", "recommendation": "str"},
        "field_types": {"decision": "str", "confidence_score": "float"}
    }

    print("\n🔍 مراجعة جودة مخرجات الوكيل:\n")
    review = qa_agent.review_agent_output("Fraud Detection Agent", sample_output, expected_schema)

    print(f"الوكيل: {review['agent_name']}")
    print(f"الجودة الشاملة: {review['overall_quality']}")
    print(f"تم الاجتياز: {'✅ نعم' if review['passed'] else '❌ لا'}")
    print(f"درجة الدقة: {review['accuracy_score']:.2%}")

    if review['issues_found']:
        print("\nالمشاكل المكتشفة:")
        for issue in review['issues_found']:
            print(f"  ⚠️ [{issue['severity']}] {issue['description']}")

    if review['recommendations']:
        print("\nالتوصيات:")
        for rec in review['recommendations']:
            print(f"  • {rec}")

    print("\n✅ تم إكمال مراجعة الجودة بنجاح!")
