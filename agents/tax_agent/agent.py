"""
Finovate Audit Nexus AI - Tax Compliance Agent

مراجعة الضرائب - VAT وضريبة الدخل والمرتبات
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
from loguru import logger


class TaxComplianceAgent:
    """
    وكيل مراجعة الضرائب
    
    يدعم:
    - VAT (ضريبة القيمة المضافة)
    - Income Tax (ضريبة الدخل)
    - Payroll Tax (ضريبة المرتبات)
    - Withholding Tax (ضريبة الخصم من المنبع)
    
    المهام:
    - مراجعة الإقرارات
    - كشف المخاطر
    - كشف التهرب
    - تحليل الفروقات
    - التحقق من الالتزام
    """
    
    def __init__(self, agent_id: str = "tax_agent_001", country: str = "EG"):
        self.agent_id = agent_id
        self.agent_name = "Tax Compliance Agent"
        self.country = country  # EG for Egypt
        self.status = "initialized"
        
        # معدلات الضريبة المصرية
        self.vat_rate = 14.0  # VAT rate in Egypt
        self.income_tax_brackets = {
            0: 0.0,
            15000: 0.10,
            30000: 0.15,
            45000: 0.20,
            60000: 0.25,
            200000: 0.275
        }
        
        self.risks_identified = []
        
        logger.info(f"{self.agent_name} initialized for country: {country}")
    
    async def analyze_vat_compliance(self, transactions: pd.DataFrame) -> Dict[str, Any]:
        """
        تحليل التزام ضريبة القيمة المضافة
        
        Args:
            transactions: DataFrame يحتوي على المعاملات الخاضعة للضريبة
            
        Returns:
            dict: نتائج التحليل
        """
        logger.info("Starting VAT compliance analysis...")
        self.status = "analyzing_vat"
        
        results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "tax_type": "VAT",
            "total_transactions": len(transactions),
            "vat_calculated": 0,
            "vat_reported": 0,
            "variance": 0,
            "risks": [],
            "recommendations": []
        }
        
        try:
            # حساب ضريبة القيمة المضافة المتوقعة
            if "amount_excluding_vat" in transactions.columns:
                results["vat_calculated"] = transactions["amount_excluding_vat"].sum() * (self.vat_rate / 100)
            
            if "vat_amount" in transactions.columns:
                results["vat_reported"] = transactions["vat_amount"].sum()
            
            # حساب الفارق
            results["variance"] = abs(results["vat_calculated"] - results["vat_reported"])
            
            # كشف المخاطر
            results["risks"] = await self._detect_vat_risks(transactions)
            
            # توليد التوصيات
            results["recommendations"] = await self._generate_vat_recommendations(results)
            
            self.status = "completed"
            logger.info(f"VAT analysis completed. Variance: {results['variance']:.2f}")
            
        except Exception as e:
            logger.error(f"Error during VAT analysis: {str(e)}")
            self.status = "error"
            results["error"] = str(e)
        
        return results
    
    async def _detect_vat_risks(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """كشف مخاطر ضريبة القيمة المضافة"""
        risks = []
        
        # التحقق من وجود معاملات بدون ضريبة
        if "vat_amount" in data.columns:
            zero_vat = data[data["vat_amount"] == 0]
            if len(zero_vat) > 0:
                risks.append({
                    "risk_type": "zero_vat_transactions",
                    "severity": "medium",
                    "count": len(zero_vat),
                    "description": f"Found {len(zero_vat)} transactions with zero VAT",
                    "potential_impact": "May indicate exempt supplies or missing VAT"
                })
        
        # كشف النسب غير الصحيحة
        if "amount_excluding_vat" in data.columns and "vat_amount" in data.columns:
            data["calculated_vat_rate"] = (data["vat_amount"] / data["amount_excluding_vat"].replace(0, 1)) * 100
            
            incorrect_rates = data[
                (data["calculated_vat_rate"] > 0) & 
                (data["calculated_vat_rate"] != self.vat_rate) &
                (data["calculated_vat_rate"] != 0)
            ]
            
            if len(incorrect_rates) > 0:
                risks.append({
                    "risk_type": "incorrect_vat_rate",
                    "severity": "high",
                    "count": len(incorrect_rates),
                    "description": f"Found {len(incorrect_rates)} transactions with incorrect VAT rate",
                    "potential_impact": "Tax authority may assess additional tax + penalties"
                })
        
        # كشف المعاملات الكبيرة بدون فاتورة ضريبية
        if "invoice_number" in data.columns:
            missing_invoices = data[data["invoice_number"].isna() | (data["invoice_number"] == "")]
            if len(missing_invoices) > 0:
                risks.append({
                    "risk_type": "missing_tax_invoices",
                    "severity": "critical",
                    "count": len(missing_invoices),
                    "description": f"Found {len(missing_invoices)} transactions without tax invoice numbers",
                    "potential_impact": "Non-deductible expenses and potential penalties"
                })
        
        return risks
    
    async def _generate_vat_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """توليد توصيات لضريبة القيمة المضافة"""
        recommendations = []
        
        if results["variance"] > 0:
            recommendations.append(
                f"Review VAT variance of {results['variance']:.2f} EGP between calculated and reported amounts"
            )
        
        for risk in results.get("risks", []):
            if risk["severity"] == "critical":
                recommendations.append(
                    f"URGENT: Address {risk['risk_type']} - {risk['description']}"
                )
            elif risk["severity"] == "high":
                recommendations.append(
                    f"Priority: Review {risk['risk_type']} - {risk['description']}"
                )
        
        if not recommendations:
            recommendations.append("No significant VAT compliance issues detected")
        
        return recommendations
    
    async def analyze_income_tax(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        تحليل ضريبة الدخل
        
        Args:
            financial_data: بيانات مالية تحتوي على الإيرادات والمصروفات
            
        Returns:
            dict: نتائج التحليل
        """
        logger.info("Starting income tax analysis...")
        
        results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "tax_type": "Income Tax",
            "revenue": financial_data.get("revenue", 0),
            "expenses": financial_data.get("expenses", 0),
            "taxable_income": 0,
            "estimated_tax": 0,
            "tax_bracket": 0,
            "risks": []
        }
        
        try:
            # حساب الدخل الخاضع للضريبة
            results["taxable_income"] = results["revenue"] - results["expenses"]
            
            if results["taxable_income"] > 0:
                # حساب الضريبة التصاعدية
                results["estimated_tax"] = self._calculate_progressive_tax(results["taxable_income"])
                
                # تحديد الشريحة الضريبية
                for bracket in sorted(self.income_tax_brackets.keys(), reverse=True):
                    if results["taxable_income"] >= bracket:
                        results["tax_bracket"] = self.income_tax_brackets[bracket]
                        break
                
                # كشف المخاطر
                results["risks"] = await self._detect_income_tax_risks(financial_data)
            
            self.status = "completed"
            logger.info(f"Income tax analysis completed. Estimated tax: {results['estimated_tax']:.2f}")
            
        except Exception as e:
            logger.error(f"Error during income tax analysis: {str(e)}")
            self.status = "error"
            results["error"] = str(e)
        
        return results
    
    def _calculate_progressive_tax(self, income: float) -> float:
        """حساب الضريبة التصاعدية حسب الشرائح المصرية"""
        tax = 0
        remaining_income = income
        
        brackets = sorted(self.income_tax_brackets.items())
        
        for i in range(len(brackets) - 1):
            lower_bound, lower_rate = brackets[i]
            upper_bound, upper_rate = brackets[i + 1]
            
            bracket_width = upper_bound - lower_bound
            taxable_in_bracket = min(remaining_income, bracket_width)
            
            if taxable_in_bracket > 0:
                tax += taxable_in_bracket * lower_rate
                remaining_income -= taxable_in_bracket
            else:
                break
        
        # آخر شريحة
        if remaining_income > 0:
            last_bracket_rate = brackets[-1][1]
            tax += remaining_income * last_bracket_rate
        
        return tax
    
    async def _detect_income_tax_risks(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """كشف مخاطر ضريبة الدخل"""
        risks = []
        
        revenue = data.get("revenue", 0)
        expenses = data.get("expenses", 0)
        
        # نسبة المصروفات إلى الإيرادات
        if revenue > 0:
            expense_ratio = (expenses / revenue) * 100
            
            if expense_ratio > 80:
                risks.append({
                    "risk_type": "high_expense_ratio",
                    "severity": "high",
                    "value": expense_ratio,
                    "description": f"Expense ratio of {expense_ratio:.1f}% is unusually high",
                    "potential_impact": "May trigger tax authority audit"
                })
        
        # خسارة متكررة
        if data.get("net_income", 0) < 0:
            risks.append({
                "risk_type": "net_loss",
                "severity": "medium",
                "description": "Company reporting net loss",
                "potential_impact": "May affect future tax positions and attract scrutiny"
            })
        
        return risks
    
    async def analyze_payroll_tax(self, payroll_data: pd.DataFrame) -> Dict[str, Any]:
        """
        تحليل ضريبة مرتبات
        
        Args:
            payroll_data: بيانات كشوف المرتبات
            
        Returns:
            dict: نتائج التحليل
        """
        logger.info("Starting payroll tax analysis...")
        
        results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "tax_type": "Payroll Tax",
            "total_employees": len(payroll_data),
            "total_gross_salaries": 0,
            "total_tax_withheld": 0,
            "estimated_tax": 0,
            "variance": 0,
            "compliance_issues": []
        }
        
        try:
            if "gross_salary" in payroll_data.columns:
                results["total_gross_salaries"] = payroll_data["gross_salary"].sum()
            
            if "tax_withheld" in payroll_data.columns:
                results["total_tax_withheld"] = payroll_data["tax_withheld"].sum()
            
            # حساب الضريبة المتوقعة
            if "gross_salary" in payroll_data.columns:
                estimated_total = 0
                for _, row in payroll_data.iterrows():
                    salary = row.get("gross_salary", 0) * 12  # سنوي
                    estimated_total += self._calculate_progressive_tax(salary)
                results["estimated_tax"] = estimated_total
            
            results["variance"] = abs(results["estimated_tax"] - results["total_tax_withheld"])
            
            # كشف مشاكل الالتزام
            results["compliance_issues"] = await self._detect_payroll_issues(payroll_data)
            
            self.status = "completed"
            logger.info(f"Payroll tax analysis completed. Variance: {results['variance']:.2f}")
            
        except Exception as e:
            logger.error(f"Error during payroll tax analysis: {str(e)}")
            self.status = "error"
            results["error"] = str(e)
        
        return results
    
    async def _detect_payroll_issues(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """كشف مشاكل التزام ضريبة المرتبات"""
        issues = []
        
        # التحقق من خصم الضريبة للعاملين فوق الحد الأدنى
        if "gross_salary" in data.columns and "tax_withheld" in data.columns:
            under_deducted = data[
                (data["gross_salary"] > 15000/12) &  # فوق الحد الأدنى الإعفاء
                (data["tax_withheld"] == 0)
            ]
            
            if len(under_deducted) > 0:
                issues.append({
                    "issue_type": "under_deduction",
                    "severity": "high",
                    "count": len(under_deducted),
                    "description": f"{len(under_deducted)} employees with no tax deducted despite eligible salary"
                })
        
        return issues
    
    def generate_tax_report(self, vat_results: Dict, income_results: Dict, payroll_results: Dict) -> str:
        """توليد تقرير ضريبي شامل"""
        report = []
        report.append("=" * 70)
        report.append("التقرير الضريبي الشامل - Finovate Audit Nexus AI")
        report.append("=" * 70)
        report.append(f"تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # قسم VAT
        report.append("-" * 70)
        report.append("أولاً: ضريبة القيمة المضافة (VAT)")
        report.append("-" * 70)
        if vat_results:
            report.append(f"إجمالي المعاملات: {vat_results.get('total_transactions', 0)}")
            report.append(f"ضريبة محسوبة: {vat_results.get('vat_calculated', 0):,.2f} EGP")
            report.append(f"ضريبة مبلغ عنها: {vat_results.get('vat_reported', 0):,.2f} EGP")
            report.append(f"الفارق: {vat_results.get('variance', 0):,.2f} EGP")
            
            risks = vat_results.get('risks', [])
            if risks:
                report.append(f"\nالمخاطر المكتشفة ({len(risks)}):")
                for risk in risks:
                    report.append(f"  [{risk.get('severity', 'N/A').upper()}] {risk.get('description', '')}")
        report.append("")
        
        # قسم ضريبة الدخل
        report.append("-" * 70)
        report.append("ثانياً: ضريبة الدخل")
        report.append("-" * 70)
        if income_results:
            report.append(f"الإيرادات: {income_results.get('revenue', 0):,.2f} EGP")
            report.append(f"المصروفات: {income_results.get('expenses', 0):,.2f} EGP")
            report.append(f"الدخل الخاضع للضريبة: {income_results.get('taxable_income', 0):,.2f} EGP")
            report.append(f"الضريبة المقدرة: {income_results.get('estimated_tax', 0):,.2f} EGP")
        report.append("")
        
        # قسم ضريبة المرتبات
        report.append("-" * 70)
        report.append("ثالثاً: ضريبة المرتبات")
        report.append("-" * 70)
        if payroll_results:
            report.append(f"إجمالي العاملين: {payroll_results.get('total_employees', 0)}")
            report.append(f"إجمالي المرتبات: {payroll_results.get('total_gross_salaries', 0):,.2f} EGP")
            report.append(f"الضريبة المخصومة: {payroll_results.get('total_tax_withheld', 0):,.2f} EGP")
            report.append(f"الفارق: {payroll_results.get('variance', 0):,.2f} EGP")
        report.append("")
        
        report.append("=" * 70)
        report.append("تنويه: هذا التقرير لأغراض المراجعة الداخلية ولا يغني عن استشارة متخصص")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def get_status(self) -> Dict[str, Any]:
        """الحصول على حالة الوكيل"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "country": self.country,
            "status": self.status,
            "vat_rate": self.vat_rate,
            "risks_identified": len(self.risks_identified)
        }


# مثال للاستخدام
if __name__ == "__main__":
    async def main():
        agent = TaxComplianceAgent(country="EG")
        
        # بيانات تجريبية لـ VAT
        sample_vat_data = pd.DataFrame({
            "invoice_number": ["INV001", "INV002", "INV003", "", "INV005"],
            "amount_excluding_vat": [1000, 2000, 1500, 3000, 2500],
            "vat_amount": [140, 280, 210, 0, 350]
        })
        
        vat_results = await agent.analyze_vat_compliance(sample_vat_data)
        print("VAT Analysis Results:")
        print(f"  Risks Found: {len(vat_results['risks'])}")
        for risk in vat_results['risks']:
            print(f"    - {risk['description']}")
        
        # بيانات تجريبية لضريبة الدخل
        sample_income_data = {
            "revenue": 500000,
            "expenses": 350000,
            "net_income": 150000
        }
        
        income_results = await agent.analyze_income_tax(sample_income_data)
        print(f"\nIncome Tax Results:")
        print(f"  Taxable Income: {income_results['taxable_income']:,.2f} EGP")
        print(f"  Estimated Tax: {income_results['estimated_tax']:,.2f} EGP")
    
    asyncio.run(main())
