"""
Financial Statements Audit Agent
وكيل مراجعة القوائم المالية

يدعم:
- قائمة الدخل
- المركز المالي (الميزانية)
- التدفقات النقدية
- حقوق الملكية
- النسب المالية
- التحليل الرأسي والأفقي
- كشف التلاعب
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class StatementType(Enum):
    """أنواع القوائم المالية"""
    INCOME_STATEMENT = "income_statement"
    BALANCE_SHEET = "balance_sheet"
    CASH_FLOW = "cash_flow"
    EQUITY = "equity"


@dataclass
class FinancialStatement:
    """تمثيل القائمة المالية"""
    statement_type: StatementType
    period: str
    currency: str = "EGP"
    items: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FSAnalysisResult:
    """نتيجة تحليل القوائم المالية"""
    statement_type: str
    period: str
    is_balanced: bool
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    ratios: Dict[str, float]
    horizontal_analysis: Dict[str, float]
    vertical_analysis: Dict[str, float]
    manipulation_score: float
    recommendations: List[str]
    confidence_level: float


class FinancialStatementsAuditAgent:
    """
    وكيل مراجعة القوائم المالية

    المهام:
    - التحقق من توازن الميزانية
    - تحليل قائمة الدخل
    - مراجعة التدفقات النقدية
    - حساب النسب المالية
    - التحليل الرأسي والأفقي
    - كشف التلاعب في القوائم
    """

    def __init__(self, llm_provider: Optional[str] = None):
        self.llm_provider = llm_provider or "default"
        self.name = "Financial_Statements_Audit_Agent"
        self.version = "1.0.0"
        self.supported_standards = ["IFRS", "IAS", "Egyptian_GAAP"]

        # حدود الكشف عن التلاعب
        self.manipulation_thresholds = {
            "revenue_growth_anomaly": 0.50,  # نمو غير طبيعي > 50%
            "margin_change_anomaly": 0.20,   # تغير هامش > 20%
            "receivables_ratio_anomaly": 0.30,
            "inventory_turnover_anomaly": 0.40,
            "cash_flow_divergence": 0.25
        }

    async def analyze_financial_statements(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate the financial statements analysis process

        Args:
            data: Financial statements data

        Returns:
            Comprehensive analysis results
        """
        results = {
            "income_statement": None,
            "balance_sheet": None,
            "cash_flow": None,
            "overall_status": "completed",
            "timestamp": datetime.now().isoformat()
        }

        if not data:
            return results

        # Analyze Income Statement
        if 'income_statement' in data:
            is_data = data['income_statement']
            is_result = self.analyze_income_statement(
                is_data.get('current', {}),
                is_data.get('prior')
            )
            results["income_statement"] = vars(is_result)

        # Analyze Balance Sheet
        if 'balance_sheet' in data:
            bs_data = data['balance_sheet']
            bs_result = self.analyze_balance_sheet(
                bs_data.get('assets', {}),
                bs_data.get('liabilities', {}),
                bs_data.get('equity', {}),
                bs_data.get('prior')
            )
            results["balance_sheet"] = vars(bs_result)

        # Analyze Cash Flow
        if 'cash_flow' in data:
            cf_data = data['cash_flow']
            cf_result = self.analyze_cash_flow(
                cf_data.get('operating', 0),
                cf_data.get('investing', 0),
                cf_data.get('financing', 0),
                cf_data.get('net_income', 0),
                cf_data.get('prior')
            )
            results["cash_flow"] = vars(cf_result)

        return results

    def analyze_income_statement(self,
                                  current_period: Dict[str, float],
                                  prior_period: Optional[Dict[str, float]] = None,
                                  currency: str = "EGP") -> FSAnalysisResult:
        """
        تحليل قائمة الدخل

        Args:
            current_period: بيانات الفترة الحالية
            prior_period: بيانات الفترة السابقة (للتحليل الأفقي)

        Returns:
            نتيجة التحليل
        """
        logger.info("Analyzing Income Statement...")

        errors = []
        warnings = []
        recommendations = []

        revenue = current_period.get("revenue", 0)
        cogs = current_period.get("cost_of_goods_sold", 0)
        gross_profit = current_period.get("gross_profit", revenue - cogs)
        operating_expenses = current_period.get("operating_expenses", 0)
        operating_income = current_period.get("operating_income", gross_profit - operating_expenses)
        net_income = current_period.get("net_income", operating_income)

        # التحقق من صحة الحسابات
        calculated_gross_profit = revenue - cogs
        if abs(calculated_gross_profit - gross_profit) > 0.01:
            errors.append({
                "type": "calculation_error",
                "field": "gross_profit",
                "expected": calculated_gross_profit,
                "reported": gross_profit,
                "severity": "high"
            })

        calculated_operating_income = gross_profit - operating_expenses
        if abs(calculated_operating_income - operating_income) > 0.01:
            errors.append({
                "type": "calculation_error",
                "field": "operating_income",
                "expected": calculated_operating_income,
                "reported": operating_income,
                "severity": "high"
            })

        # حساب النسب
        ratios = {}
        if revenue > 0:
            ratios["gross_margin"] = gross_profit / revenue
            ratios["operating_margin"] = operating_income / revenue
            ratios["net_margin"] = net_income / revenue
            ratios["expense_ratio"] = operating_expenses / revenue

        # التحليل الأفقي
        horizontal_analysis = {}
        if prior_period:
            prior_revenue = prior_period.get("revenue", 0)
            if prior_revenue > 0:
                horizontal_analysis["revenue_growth"] = (revenue - prior_revenue) / prior_revenue

                # كشف النمو غير الطبيعي
                if horizontal_analysis["revenue_growth"] > self.manipulation_thresholds["revenue_growth_anomaly"]:
                    warnings.append({
                        "type": "anomaly",
                        "description": f"نمو غير طبيعي في الإيرادات: {horizontal_analysis['revenue_growth']*100:.1f}%",
                        "severity": "medium",
                        "recommendation": "مراجعة أسباب النمو المفاجئ والتحقق من صحته"
                    })
                    recommendations.append("فحص إيرادات الفترة الحالية للتأكد من عدم وجود إيرادات وهمية")

        # التحليل الرأسي
        vertical_analysis = {}
        if revenue > 0:
            vertical_analysis["cogs_percentage"] = cogs / revenue
            vertical_analysis["gross_profit_percentage"] = gross_profit / revenue
            vertical_analysis["opex_percentage"] = operating_expenses / revenue
            vertical_analysis["net_income_percentage"] = net_income / revenue

            # فحص الهوامش غير الطبيعية
            if ratios.get("gross_margin", 0) < 0.05:
                warnings.append({
                    "type": "low_margin",
                    "description": f"هامش إجمالي منخفض جداً: {ratios['gross_margin']*100:.1f}%",
                    "severity": "high"
                })
                recommendations.append("مراجعة تكلفة البضاعة المباعة والتحقق من اكتمالها")

        # حساب درجة التلاعب
        manipulation_score = self._calculate_manipulation_score(
            ratios=ratios,
            horizontal=horizontal_analysis,
            current=current_period,
            prior=prior_period,
            balance_sheet=None,
            cash_flow=None
        )

        if manipulation_score > 0.7:
            errors.append({
                "type": "manipulation_risk",
                "score": manipulation_score,
                "severity": "critical",
                "description": "خطر عالي للتلاعب في القوائم المالية"
            })

        # تحديد مستوى الثقة
        confidence = 1.0 - (len(errors) * 0.15 + len(warnings) * 0.05)
        confidence = max(0.0, min(1.0, confidence))

        return FSAnalysisResult(
            statement_type="income_statement",
            period=current_period.get("period", "Unknown"),
            is_balanced=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            ratios=ratios,
            horizontal_analysis=horizontal_analysis,
            vertical_analysis=vertical_analysis,
            manipulation_score=manipulation_score,
            recommendations=recommendations,
            confidence_level=confidence
        )

    def analyze_balance_sheet(self,
                               assets: Dict[str, float],
                               liabilities: Dict[str, float],
                               equity: Dict[str, float],
                               prior_period: Optional[Dict[str, Dict[str, float]]] = None) -> FSAnalysisResult:
        """
        تحليل قائمة المركز المالي (الميزانية العمومية)

        Args:
            assets: الأصول (متداولة، ثابتة، إلخ)
            liabilities: الخصوم (متداولة، طويلة الأجل)
            equity: حقوق الملكية

        Returns:
            نتيجة التحليل
        """
        logger.info("Analyzing Balance Sheet...")

        errors = []
        warnings = []
        recommendations = []

        # حساب المجاميع
        total_assets = sum(assets.values())
        total_liabilities = sum(liabilities.values())
        total_equity = sum(equity.values())

        # التحقق من معادلة الميزانية
        accounting_equation = total_assets - (total_liabilities + total_equity)
        is_balanced = abs(accounting_equation) < 0.01

        if not is_balanced:
            errors.append({
                "type": "balance_sheet_imbalance",
                "description": "الميزانية غير متوازنة",
                "total_assets": total_assets,
                "total_liabilities_plus_equity": total_liabilities + total_equity,
                "difference": accounting_equation,
                "severity": "critical"
            })
            recommendations.append("مراجعة فروقات الترصيد وتحديد سببها")

        # حساب النسب المالية
        ratios = {}
        current_assets = assets.get("current_assets", 0)
        current_liabilities = liabilities.get("current_liabilities", 0)

        if current_liabilities > 0:
            ratios["current_ratio"] = current_assets / current_liabilities

            if ratios["current_ratio"] < 1.0:
                warnings.append({
                    "type": "liquidity_risk",
                    "description": f"نسبة التداول منخفضة: {ratios['current_ratio']:.2f}",
                    "severity": "high"
                })
                recommendations.append("مراجعة السيولة والقدرة على سداد الالتزامات قصيرة الأجل")

        if total_assets > 0:
            ratios["debt_to_assets"] = total_liabilities / total_assets
            ratios["equity_ratio"] = total_equity / total_assets

            if ratios["debt_to_assets"] > 0.7:
                warnings.append({
                    "type": "high_leverage",
                    "description": f"نسبة المديونية عالية: {ratios['debt_to_assets']*100:.1f}%",
                    "severity": "medium"
                })

        # التحليل الأفقي
        horizontal_analysis = {}
        if prior_period:
            prior_assets = prior_period.get("assets", {})
            for key in assets:
                if key in prior_assets and prior_assets[key] > 0:
                    growth = (assets[key] - prior_assets[key]) / prior_assets[key]
                    horizontal_analysis[f"{key}_growth"] = growth

                    # كشف الزيادات غير الطبيعية
                    if growth > 0.50:
                        warnings.append({
                            "type": "asset_growth_anomaly",
                            "field": key,
                            "growth": growth,
                            "severity": "medium"
                        })

        # التحليل الرأسي
        vertical_analysis = {}
        if total_assets > 0:
            for key, value in assets.items():
                vertical_analysis[f"asset_{key}_pct"] = value / total_assets
            for key, value in liabilities.items():
                vertical_analysis[f"liability_{key}_pct"] = value / total_assets

        # حساب درجة التلاعب
        manipulation_score = self._calculate_manipulation_score(
            ratios=ratios,
            horizontal=horizontal_analysis,
            current=None,
            prior=None,
            balance_sheet={"assets": assets, "liabilities": liabilities, "equity": equity},
            cash_flow=None
        )

        confidence = 1.0 - (len(errors) * 0.2 + len(warnings) * 0.05)
        confidence = max(0.0, min(1.0, confidence))

        return FSAnalysisResult(
            statement_type="balance_sheet",
            period=datetime.now().strftime("%Y-%m"),
            is_balanced=is_balanced,
            errors=errors,
            warnings=warnings,
            ratios=ratios,
            horizontal_analysis=horizontal_analysis,
            vertical_analysis=vertical_analysis,
            manipulation_score=manipulation_score,
            recommendations=recommendations,
            confidence_level=confidence
        )

    def analyze_cash_flow(self,
                          operating_cf: float,
                          investing_cf: float,
                          financing_cf: float,
                          net_income: float,
                          prior_period: Optional[Dict[str, float]] = None) -> FSAnalysisResult:
        """
        تحليل قائمة التدفقات النقدية

        Args:
            operating_cf: التدفق النقدي من الأنشطة التشغيلية
            investing_cf: التدفق النقدي من الأنشطة الاستثمارية
            financing_cf: التدفق النقدي من الأنشطة التمويلية
            net_income: صافي الدخل
        """
        logger.info("Analyzing Cash Flow Statement...")

        errors = []
        warnings = []
        recommendations = []

        # حساب النسب
        ratios = {}

        # جودة الأرباح (Operating CF / Net Income)
        if net_income != 0:
            ratios["earnings_quality"] = operating_cf / net_income

            if ratios["earnings_quality"] < 0.8:
                warnings.append({
                    "type": "low_earnings_quality",
                    "description": f"جودة الأرباح منخفضة: {ratios['earnings_quality']:.2f}",
                    "severity": "high"
                })
                recommendations.append("التحقق من الفروقات بين صافي الدخل والتدفق النقدي التشغيلي")

        # نسبة التغطية النقدية
        if financing_cf < 0:  # هناك مدفوعات تمويلية
            coverage = operating_cf / abs(financing_cf)
            ratios["cash_coverage"] = coverage

            if coverage < 1.0:
                warnings.append({
                    "type": "insufficient_cash_coverage",
                    "description": f"التدفق التشغيلي لا يغطي الالتزامات التمويلية: {coverage:.2f}",
                    "severity": "high"
                })

        # كشف التباعد بين صافي الدخل والتدفق النقدي
        if net_income > 0 and operating_cf < 0:
            divergence = abs(net_income - operating_cf) / net_income
            if divergence > self.manipulation_thresholds["cash_flow_divergence"]:
                errors.append({
                    "type": "cash_flow_divergence",
                    "description": "تباعد كبير بين صافي الدخل والتدفق النقدي",
                    "net_income": net_income,
                    "operating_cf": operating_cf,
                    "divergence": divergence,
                    "severity": "critical"
                })
                recommendations.append("فحص بنود المصروفات غير النقدية والتغيرات في رأس المال العامل")

        # التحليل الأفقي
        horizontal_analysis = {}
        if prior_period:
            prior_operating = prior_period.get("operating_cf", 0)
            if prior_operating != 0:
                horizontal_analysis["operating_cf_growth"] = (operating_cf - prior_operating) / prior_operating

        # التحليل الرأسي
        total_cf = abs(operating_cf) + abs(investing_cf) + abs(financing_cf)
        vertical_analysis = {}
        if total_cf > 0:
            vertical_analysis["operating_pct"] = abs(operating_cf) / total_cf
            vertical_analysis["investing_pct"] = abs(investing_cf) / total_cf
            vertical_analysis["financing_pct"] = abs(financing_cf) / total_cf

        manipulation_score = self._calculate_manipulation_score(
            ratios=ratios,
            horizontal={},
            current=None,
            prior=None,
            balance_sheet=None,
            cash_flow={
                "operating": operating_cf,
                "investing": investing_cf,
                "financing": financing_cf
            }
        )

        confidence = 1.0 - (len(errors) * 0.2 + len(warnings) * 0.05)
        confidence = max(0.0, min(1.0, confidence))

        return FSAnalysisResult(
            statement_type="cash_flow",
            period=datetime.now().strftime("%Y-%m"),
            is_balanced=True,
            errors=errors,
            warnings=warnings,
            ratios=ratios,
            horizontal_analysis=horizontal_analysis,
            vertical_analysis=vertical_analysis,
            manipulation_score=manipulation_score,
            recommendations=recommendations,
            confidence_level=confidence
        )

    def calculate_financial_ratios(self,
                                    income_statement: Dict[str, float],
                                    balance_sheet: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        حساب مجموعة شاملة من النسب المالية

        Returns:
            قاموس يحتوي على جميع النسب المالية
        """
        ratios = {}

        # استخراج البيانات
        revenue = income_statement.get("revenue", 0)
        net_income = income_statement.get("net_income", 0)
        cogs = income_statement.get("cost_of_goods_sold", 0)

        assets = balance_sheet.get("assets", {})
        liabilities = balance_sheet.get("liabilities", {})
        equity = balance_sheet.get("equity", {})

        total_assets = sum(assets.values())
        total_liabilities = sum(liabilities.values())
        total_equity = sum(equity.values())

        current_assets = assets.get("current_assets", 0)
        current_liabilities = liabilities.get("current_liabilities", 0)

        # نسب الربحية
        if revenue > 0:
            ratios["gross_profit_margin"] = (revenue - cogs) / revenue
            ratios["operating_profit_margin"] = income_statement.get("operating_income", 0) / revenue
            ratios["net_profit_margin"] = net_income / revenue

        if total_assets > 0:
            ratios["return_on_assets"] = net_income / total_assets

        if total_equity > 0:
            ratios["return_on_equity"] = net_income / total_equity

        # نسب السيولة
        if current_liabilities > 0:
            quick_assets = current_assets - assets.get("inventory", 0)
            ratios["current_ratio"] = current_assets / current_liabilities
            ratios["quick_ratio"] = quick_assets / current_liabilities
            ratios["cash_ratio"] = assets.get("cash_and_equivalents", 0) / current_liabilities

        # نسب المديونية
        if total_assets > 0:
            ratios["debt_to_assets"] = total_liabilities / total_assets
            ratios["equity_multiplier"] = total_assets / total_equity if total_equity > 0 else 0

        if net_income > 0:
            ratios["interest_coverage"] = income_statement.get("operating_income", 0) / income_statement.get("interest_expense", 1)

        # نسب النشاط
        avg_receivables = assets.get("accounts_receivable", 0)
        if avg_receivables > 0:
            ratios["receivables_turnover"] = revenue / avg_receivables
            ratios["days_sales_outstanding"] = 365 / ratios["receivables_turnover"]

        inventory = assets.get("inventory", 0)
        if inventory > 0:
            ratios["inventory_turnover"] = cogs / inventory
            ratios["days_inventory_outstanding"] = 365 / ratios["inventory_turnover"]

        return ratios

    def _calculate_manipulation_score(self,
                                       ratios: Dict[str, float],
                                       horizontal: Dict[str, float],
                                       current: Optional[Dict[str, float]] = None,
                                       prior: Optional[Dict[str, float]] = None,
                                       balance_sheet: Optional[Dict] = None,
                                       cash_flow: Optional[Dict] = None) -> float:
        """
        حساب درجة احتمالية التلاعب في القوائم المالية

        يستخدم خوارزمية Beneish M-Score المبسطة
        """
        score = 0.0
        risk_factors = 0

        # DSRI - Days Sales Receivable Index
        if "receivables_turnover" in ratios:
            dsri = 1.0 / ratios["receivables_turnover"] if ratios["receivables_turnover"] > 0 else 0
            if dsri > 0.5:
                score += 0.15
                risk_factors += 1

        # GMI - Gross Margin Index
        if horizontal.get("revenue_growth", 0) > 0.3:
            score += 0.1
            risk_factors += 1

        # AQI - Asset Quality Index
        if balance_sheet:
            total_assets = sum(balance_sheet.get("assets", {}).values())
            intangible = balance_sheet.get("assets", {}).get("intangible_assets", 0)
            if total_assets > 0 and intangible / total_assets > 0.3:
                score += 0.15
                risk_factors += 1

        # SGI - Sales Growth Index
        if horizontal.get("revenue_growth", 0) > 0.5:
            score += 0.2
            risk_factors += 1

        # DEPI - Depreciation Index
        # (يمكن إضافته عند توفر بيانات الإهلاك)

        # SGAI - Sales General Admin Index
        if "expense_ratio" in ratios and ratios["expense_ratio"] < 0.1:
            score += 0.1
            risk_factors += 1

        # LVGI - Leverage Index
        if "debt_to_assets" in ratios and ratios["debt_to_assets"] > 0.7:
            score += 0.15
            risk_factors += 1

        # TATA - Total Accruals to Total Assets
        if cash_flow and balance_sheet:
            net_income = current.get("net_income", 0) if current else 0
            operating_cf = cash_flow.get("operating", 0)
            total_assets = sum(balance_sheet.get("assets", {}).values())

            if total_assets > 0:
                accruals = abs(net_income - operating_cf) / total_assets
                if accruals > 0.1:
                    score += 0.15
                    risk_factors += 1

        return min(1.0, score)

    def generate_full_audit_report(self,
                                    income_statement: Dict[str, float],
                                    balance_sheet_data: Dict[str, Dict[str, float]],
                                    cash_flow: Dict[str, float],
                                    prior_year: Optional[Dict] = None) -> Dict[str, Any]:
        """
        إنشاء تقرير مراجعة كامل للقوائم المالية

        Returns:
            تقرير شامل بجميع النتائج
        """
        logger.info("Generating Full Financial Statements Audit Report...")

        # تحليل كل قائمة
        is_result = self.analyze_income_statement(income_statement, prior_year.get("income_statement") if prior_year else None)
        bs_result = self.analyze_balance_sheet(
            balance_sheet_data.get("assets", {}),
            balance_sheet_data.get("liabilities", {}),
            balance_sheet_data.get("equity", {}),
            prior_year.get("balance_sheet") if prior_year else None
        )
        cf_result = self.analyze_cash_flow(
            cash_flow.get("operating_cf", 0),
            cash_flow.get("investing_cf", 0),
            cash_flow.get("financing_cf", 0),
            income_statement.get("net_income", 0)
        )

        # حساب النسب الشاملة
        all_ratios = self.calculate_financial_ratios(income_statement, balance_sheet_data)

        # تجميع التقرير
        report = {
            "audit_date": datetime.now().isoformat(),
            "agent": self.name,
            "version": self.version,
            "standards_applied": self.supported_standards,
            "statements_audited": ["income_statement", "balance_sheet", "cash_flow"],
            "overall_assessment": {
                "is_reliable": is_result.is_balanced and bs_result.is_balanced,
                "manipulation_risk": max(
                    is_result.manipulation_score,
                    bs_result.manipulation_score,
                    cf_result.manipulation_score
                ),
                "confidence_level": min(
                    is_result.confidence_level,
                    bs_result.confidence_level,
                    cf_result.confidence_level
                ),
                "total_errors": len(is_result.errors) + len(bs_result.errors) + len(cf_result.errors),
                "total_warnings": len(is_result.warnings) + len(bs_result.warnings) + len(cf_result.warnings)
            },
            "detailed_results": {
                "income_statement": {
                    "is_balanced": is_result.is_balanced,
                    "errors": is_result.errors,
                    "warnings": is_result.warnings,
                    "ratios": is_result.ratios,
                    "manipulation_score": is_result.manipulation_score,
                    "recommendations": is_result.recommendations
                },
                "balance_sheet": {
                    "is_balanced": bs_result.is_balanced,
                    "errors": bs_result.errors,
                    "warnings": bs_result.warnings,
                    "ratios": bs_result.ratios,
                    "manipulation_score": bs_result.manipulation_score,
                    "recommendations": bs_result.recommendations
                },
                "cash_flow": {
                    "is_balanced": cf_result.is_balanced,
                    "errors": cf_result.errors,
                    "warnings": cf_result.warnings,
                    "ratios": cf_result.ratios,
                    "manipulation_score": cf_result.manipulation_score,
                    "recommendations": cf_result.recommendations
                }
            },
            "comprehensive_ratios": all_ratios,
            "all_recommendations": list(set(
                is_result.recommendations +
                bs_result.recommendations +
                cf_result.recommendations
            ))
        }

        return report

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        تنفيذ الوكيل على البيانات المقدمة

        Args:
            data: بيانات القوائم المالية

        Returns:
            تقرير المراجعة الكامل
        """
        logger.info(f"Executing {self.name}...")

        try:
            return self.generate_full_audit_report(
                income_statement=data.get("income_statement", {}),
                balance_sheet_data=data.get("balance_sheet", {}),
                cash_flow=data.get("cash_flow", {}),
                prior_year=data.get("prior_year")
            )
        except Exception as e:
            logger.error(f"Error executing agent: {e}")
            return {
                "error": str(e),
                "agent": self.name,
                "status": "failed"
            }


# مثال للاستخدام
if __name__ == "__main__":
    # بيانات تجريبية
    sample_data = {
        "income_statement": {
            "period": "2024-Q4",
            "revenue": 10000000,
            "cost_of_goods_sold": 6000000,
            "gross_profit": 4000000,
            "operating_expenses": 2500000,
            "operating_income": 1500000,
            "interest_expense": 100000,
            "net_income": 1200000
        },
        "balance_sheet": {
            "assets": {
                "current_assets": 5000000,
                "cash_and_equivalents": 1500000,
                "accounts_receivable": 2000000,
                "inventory": 1500000,
                "fixed_assets": 8000000,
                "intangible_assets": 500000
            },
            "liabilities": {
                "current_liabilities": 3000000,
                "long_term_debt": 4000000
            },
            "equity": {
                "share_capital": 3000000,
                "retained_earnings": 3000000
            }
        },
        "cash_flow": {
            "operating_cf": 1800000,
            "investing_cf": -1200000,
            "financing_cf": -400000
        },
        "prior_year": {
            "income_statement": {
                "revenue": 8000000,
                "net_income": 900000
            }
        }
    }

    # تشغيل الوكيل
    agent = FinancialStatementsAuditAgent()
    result = agent.execute(sample_data)

    print("=" * 80)
    print("Financial Statements Audit Report")
    print("=" * 80)
    print(json.dumps(result, indent=2, ensure_ascii=False))
