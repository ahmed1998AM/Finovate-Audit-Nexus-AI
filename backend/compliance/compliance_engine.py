"""
Finovate Audit Nexus AI - Compliance Engine
محرك الالتزام بالقوانين واللوائح المحاسبية والضريبية
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ComplianceStatus(Enum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    PARTIAL = "PARTIAL"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"


@dataclass
class ComplianceFinding:
    rule_id: str
    rule_name: str
    status: ComplianceStatus
    description: str
    recommendation: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    evidence: List[str]
    standard_reference: str


class ComplianceEngine:
    """
    محرك الالتزام الشامل
    يدعم المعايير المصرية وIFRS وISA وقوانين الضرائب
    """

    def __init__(self):
        self.rules = []
        self.findings = []
        self.compliance_score = 0

        # تحميل القواعد الافتراضية
        self._load_egyptian_standards()
        self._load_ifrs_standards()
        self._load_isa_standards()
        self._load_tax_regulations()

    def _load_egyptian_standards(self):
        """تحميل معايير المحاسبة المصرية"""
        self.rules.extend([
            {
                "id": "EGY_001",
                "name": "قائمة المركز المالي",
                "standard": "Egyptian Accounting Standard 1",
                "requirements": [
                    "total_assets == total_liabilities + equity",
                    "current_assets classification",
                    "non_current_assets classification"
                ],
                "severity": "HIGH"
            },
            {
                "id": "EGY_002",
                "name": "قائمة الدخل",
                "standard": "Egyptian Accounting Standard 2",
                "requirements": [
                    "revenue recognition",
                    "expense matching principle",
                    "proper classification"
                ],
                "severity": "HIGH"
            },
            {
                "id": "EGY_003",
                "name": "الإفصاح عن الأطراف ذات العلاقة",
                "standard": "Egyptian Accounting Standard 15",
                "requirements": [
                    "related party transactions disclosure",
                    "outstanding balances disclosure"
                ],
                "severity": "MEDIUM"
            },
            {
                "id": "EGY_004",
                "name": "الأصول الثابتة",
                "standard": "Egyptian Accounting Standard 9",
                "requirements": [
                    "proper depreciation method",
                    "useful life estimation",
                    "impairment testing"
                ],
                "severity": "MEDIUM"
            }
        ])

    def _load_ifrs_standards(self):
        """تحميل معايير IFRS الدولية"""
        self.rules.extend([
            {
                "id": "IFRS_001",
                "name": "IFRS 15 - Revenue from Contracts with Customers",
                "standard": "IFRS 15",
                "requirements": [
                    "five_step_model_application",
                    "performance_obligations_identification",
                    "transaction_price_determination",
                    "revenue_recognition_timing"
                ],
                "severity": "HIGH"
            },
            {
                "id": "IFRS_002",
                "name": "IFRS 16 - Leases",
                "standard": "IFRS 16",
                "requirements": [
                    "right_of_use_asset_recognition",
                    "lease_liability_recognition",
                    "depreciation_and_interest_separation"
                ],
                "severity": "HIGH"
            },
            {
                "id": "IFRS_003",
                "name": "IFRS 9 - Financial Instruments",
                "standard": "IFRS 9",
                "requirements": [
                    "classification_and_measurement",
                    "expected_credit_loss_model",
                    "hedge_accounting"
                ],
                "severity": "HIGH"
            },
            {
                "id": "IFRS_004",
                "name": "IAS 37 - Provisions, Contingent Liabilities",
                "standard": "IAS 37",
                "requirements": [
                    "provision_recognition_criteria",
                    "measurement_at_best_estimate",
                    "contingent_liability_disclosure"
                ],
                "severity": "MEDIUM"
            }
        ])

    def _load_isa_standards(self):
        """تحميل معايير التدقيق الدولية ISA"""
        self.rules.extend([
            {
                "id": "ISA_001",
                "name": "ISA 200 - Overall Objectives of the Independent Auditor",
                "standard": "ISA 200",
                "requirements": [
                    "professional_skepticism",
                    "professional_judgment",
                    "audit_evidence_sufficiency"
                ],
                "severity": "HIGH"
            },
            {
                "id": "ISA_002",
                "name": "ISA 240 - Fraud Responsibilities",
                "standard": "ISA 240",
                "requirements": [
                    "fraud_risk_assessment",
                    "management_inquiry",
                    "unusual_transactions_review"
                ],
                "severity": "CRITICAL"
            },
            {
                "id": "ISA_003",
                "name": "ISA 315 - Identifying and Assessing Risks",
                "standard": "ISA 315",
                "requirements": [
                    "risk_assessment_procedures",
                    "internal_control_understanding",
                    "material_misstatement_identification"
                ],
                "severity": "HIGH"
            },
            {
                "id": "ISA_004",
                "name": "ISA 500 - Audit Evidence",
                "standard": "ISA 500",
                "requirements": [
                    "sufficient_appropriate_evidence",
                    "evidence_reliability",
                    "documentation_requirements"
                ],
                "severity": "HIGH"
            }
        ])

    def _load_tax_regulations(self):
        """تحميل القوانين الضريبية المصرية"""
        self.rules.extend([
            {
                "id": "TAX_001",
                "name": "ضريبة القيمة المضافة - التسجيل",
                "standard": "قانون VAT رقم 67 لسنة 2016",
                "requirements": [
                    "registration_threshold_500k",
                    "vat_number_display",
                    "tax_invoices_issuance"
                ],
                "severity": "HIGH"
            },
            {
                "id": "TAX_002",
                "name": "ضريبة القيمة المضافة - الإقرار",
                "standard": "قانون VAT رقم 67 لسنة 2016",
                "requirements": [
                    "monthly_filing",
                    "input_vat_deduction",
                    "output_vat_calculation",
                    "net_vat_payment"
                ],
                "severity": "HIGH"
            },
            {
                "id": "TAX_003",
                "name": "ضريبة الدخل - الاستقطاع",
                "standard": "قانون ضريبة الدخل رقم 91 لسنة 2005",
                "requirements": [
                    "withholding_tax_calculation",
                    "salary_tax_brackets",
                    "exemptions_application"
                ],
                "severity": "HIGH"
            },
            {
                "id": "TAX_004",
                "name": "الضريبة العقارية",
                "standard": "قانون الضريبة العقارية رقم 196 لسنة 2008",
                "requirements": [
                    "property_registration",
                    "rental_income_declaration",
                    "exemption_claims"
                ],
                "severity": "MEDIUM"
            },
            {
                "id": "TAX_005",
                "name": "ضريبة الجدول - المهن التجارية",
                "standard": "قانون ضريبة الدخل",
                "requirements": [
                    "commercial_license_tax",
                    "annual_payment",
                    "proper_classification"
                ],
                "severity": "LOW"
            }
        ])

    def assess_compliance(
        self,
        financial_data: Dict[str, Any],
        standards: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        تقييم الالتزام بالمعايير المحددة

        Args:
            financial_data: البيانات المالية للتقييم
            standards: قائمة المعايير المطلوبة (Egyptian, IFRS, ISA, Tax)

        Returns:
            نتائج التقييم الشامل
        """
        if standards is None:
            standards = ["Egyptian", "IFRS", "ISA", "Tax"]

        self.findings = []
        applicable_rules = self._filter_rules_by_standards(standards)

        for rule in applicable_rules:
            finding = self._evaluate_rule(rule, financial_data)
            if finding:
                self.findings.append(finding)

        # حساب درجة الالتزام
        self.compliance_score = self._calculate_compliance_score()

        return {
            "assessment_date": datetime.now(),
            "standards_assessed": standards,
            "total_rules": len(applicable_rules),
            "findings_count": len(self.findings),
            "compliance_score": self.compliance_score,
            "findings": [self._finding_to_dict(f) for f in self.findings],
            "summary": self._generate_summary()
        }

    def _filter_rules_by_standards(self, standards: List[str]) -> List[Dict]:
        """تصفية القواعد حسب المعايير المطلوبة"""
        filtered = []
        for rule in self.rules:
            rule_standard = rule.get("standard", "")
            for std in standards:
                if std.lower() in rule_standard.lower():
                    filtered.append(rule)
                    break
        return filtered

    def _evaluate_rule(self, rule: Dict, data: Dict) -> Optional[ComplianceFinding]:
        """تقييم قاعدة محددة"""
        requirements = rule.get("requirements", [])
        unmet_requirements = []
        evidence = []

        for req in requirements:
            is_met = self._check_requirement(req, data)
            if not is_met:
                unmet_requirements.append(req)
            else:
                evidence.append(f"✓ {req}")

        if unmet_requirements:
            status = ComplianceStatus.NON_COMPLIANT
            severity = rule.get("severity", "MEDIUM")
        elif evidence:
            status = ComplianceStatus.COMPLIANT
            severity = "NONE"
        else:
            status = ComplianceStatus.REQUIRES_REVIEW
            severity = "LOW"

        return ComplianceFinding(
            rule_id=rule["id"],
            rule_name=rule["name"],
            status=status,
            description=f"Rule: {rule['name']}",
            recommendation=self._generate_recommendation(rule, unmet_requirements),
            severity=severity,
            evidence=evidence if evidence else unmet_requirements,
            standard_reference=rule["standard"]
        )

    def _check_requirement(self, requirement: str, data: Dict) -> bool:
        """التحقق من متطلب محدد"""
        # تحليل المتطلب وتنفيذ التحقق المناسب
        # هذا تبسيط - في الواقع يحتاج منطق أكثر تعقيداً

        if "total_assets == total_liabilities" in requirement:
            assets = data.get("total_assets", 0)
            liabilities = data.get("total_liabilities", 0)
            equity = data.get("equity", 0)
            return abs(assets - (liabilities + equity)) < 0.01

        if "revenue_recognition" in requirement:
            return "revenue" in data

        if "depreciation" in requirement:
            return "depreciation_method" in data or "accumulated_depreciation" in data

        if "vat" in requirement.lower():
            return "vat_payable" in data or "vat_receivable" in data

        # افتراض الالتزام إذا لم يتم تحديد المتطلب
        return True

    def _generate_recommendation(self, rule: Dict, unmet: List[str]) -> str:
        """توليد توصية للمعالجة"""
        if not unmet:
            return "No action required - fully compliant"

        recommendations = {
            "IFRS 15": "Review revenue recognition policies and ensure five-step model application",
            "IFRS 16": "Recognize all leases on balance sheet as per IFRS 16 requirements",
            "VAT": "Ensure proper VAT calculation, documentation, and timely filing",
            "depreciation": "Apply consistent depreciation method based on asset useful life",
        }

        for key, rec in recommendations.items():
            if key.lower() in rule["name"].lower():
                return rec

        return f"Address the following: {', '.join(unmet)}"

    def _calculate_compliance_score(self) -> float:
        """حساب درجة الالتزام الإجمالية"""
        if not self.findings:
            return 100.0

        compliant_count = sum(
            1 for f in self.findings if f.status == ComplianceStatus.COMPLIANT
        )

        return round((compliant_count / len(self.findings)) * 100, 2)

    def _generate_summary(self) -> Dict[str, Any]:
        """توليد ملخص النتائج"""
        critical = sum(1 for f in self.findings if f.severity == "CRITICAL")
        high = sum(1 for f in self.findings if f.severity == "HIGH")
        medium = sum(1 for f in self.findings if f.severity == "MEDIUM")
        low = sum(1 for f in self.findings if f.severity == "LOW")
        compliant = sum(1 for f in self.findings if f.status == ComplianceStatus.COMPLIANT)

        return {
            "critical_findings": critical,
            "high_findings": high,
            "medium_findings": medium,
            "low_findings": low,
            "compliant_items": compliant,
            "overall_status": self._get_overall_status(),
            "priority_actions": self._get_priority_actions()
        }

    def _get_overall_status(self) -> str:
        """الحالة الإجمالية للالتزام"""
        if any(f.severity == "CRITICAL" for f in self.findings):
            return "CRITICAL - Immediate action required"
        elif any(f.severity == "HIGH" for f in self.findings):
            return "NON-COMPLIANT - High priority issues found"
        elif self.compliance_score >= 80:
            return "MOSTLY COMPLIANT - Minor improvements needed"
        elif self.compliance_score >= 60:
            return "PARTIAL COMPLIANCE - Significant improvements needed"
        else:
            return "NON-COMPLIANT - Major compliance gaps"

    def _get_priority_actions(self) -> List[str]:
        """الحصول على الإجراءات ذات الأولوية"""
        actions = []
        for finding in sorted(self.findings, key=lambda x: x.severity, reverse=True):
            if finding.status != ComplianceStatus.COMPLIANT:
                actions.append(f"[{finding.severity}] {finding.rule_name}: {finding.recommendation}")
        return actions[:5]  # أعلى 5 أولويات

    def _finding_to_dict(self, finding: ComplianceFinding) -> Dict:
        """تحويل النتيجة إلى قاموس"""
        return {
            "rule_id": finding.rule_id,
            "rule_name": finding.rule_name,
            "status": finding.status.value,
            "description": finding.description,
            "recommendation": finding.recommendation,
            "severity": finding.severity,
            "evidence": finding.evidence,
            "standard_reference": finding.standard_reference
        }

    def generate_compliance_report(self, output_format: str = "json") -> Any:
        """توليد تقرير الالتزام"""
        report = {
            "report_title": "Compliance Assessment Report",
            "generated_at": datetime.now(),
            "compliance_score": self.compliance_score,
            "total_findings": len(self.findings),
            "findings_by_severity": {
                "critical": sum(1 for f in self.findings if f.severity == "CRITICAL"),
                "high": sum(1 for f in self.findings if f.severity == "HIGH"),
                "medium": sum(1 for f in self.findings if f.severity == "MEDIUM"),
                "low": sum(1 for f in self.findings if f.severity == "LOW")
            },
            "detailed_findings": [self._finding_to_dict(f) for f in self.findings],
            "recommendations": self._get_priority_actions()
        }

        if output_format == "json":
            return report
        elif output_format == "text":
            return self._format_report_as_text(report)

        return report

    def _format_report_as_text(self, report: Dict) -> str:
        """تنسيق التقرير كنص"""
        lines = [
            "=" * 80,
            "COMPLIANCE ASSESSMENT REPORT",
            "=" * 80,
            f"Generated: {report['generated_at']}",
            f"Compliance Score: {report['compliance_score']}%",
            "",
            "FINDINGS SUMMARY:",
            f"  Critical: {report['findings_by_severity']['critical']}",
            f"  High: {report['findings_by_severity']['high']}",
            f"  Medium: {report['findings_by_severity']['medium']}",
            f"  Low: {report['findings_by_severity']['low']}",
            "",
            "PRIORITY RECOMMENDATIONS:",
        ]

        for i, rec in enumerate(report['recommendations'], 1):
            lines.append(f"  {i}. {rec}")

        lines.append("=" * 80)
        return "\n".join(lines)


# مثال على الاستخدام
if __name__ == "__main__":
    engine = ComplianceEngine()

    # بيانات مالية اختبارية
    test_data = {
        "total_assets": 1000000,
        "total_liabilities": 600000,
        "equity": 400000,
        "revenue": 500000,
        "vat_payable": 70000,
        "depreciation_method": "straight_line"
    }

    # تقييم الالتزام
    results = engine.assess_compliance(test_data, standards=["Egyptian", "IFRS", "Tax"])

    print(engine.generate_compliance_report(output_format="text"))
