"""
Finovate Audit Nexus AI - Trial Balance Audit Agent

مراجعة ميزان المراجعة - التحقق من التطابق والتوازن
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
from loguru import logger


class TrialBalanceAuditAgent:
    """
    وكيل مراجعة ميزان المراجعة

    المهام:
    - التحقق من التطابق
    - مراجعة التوازن
    - كشف فروقات الترصيد
    - تحليل العلاقات المحاسبية
    """

    def __init__(self, agent_id: str = "tb_agent_001"):
        self.agent_id = agent_id
        self.agent_name = "Trial Balance Audit Agent"
        self.status = "initialized"
        self.processed_accounts = 0
        self.discrepancies_found = []

        logger.info(f"{self.agent_name} initialized with ID: {agent_id}")

    async def analyze_trial_balance(self, tb_data: pd.DataFrame) -> Dict[str, Any]:
        """
        تحليل ميزان المراجعة

        Args:
            tb_data: DataFrame يحتوي على بيانات ميزان المراجعة

        Returns:
            dict: نتائج التحليل
        """
        logger.info("Starting trial balance analysis...")
        self.status = "analyzing"

        results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_accounts": len(tb_data),
            "is_balanced": False,
            "discrepancies": [],
            "warnings": [],
            "account_analysis": {}
        }

        try:
            # التحقق من التطابق
            balance_check = await self._check_balance(tb_data)
            results["is_balanced"] = balance_check["is_balanced"]
            results["balance_difference"] = balance_check["difference"]

            if not balance_check["is_balanced"]:
                results["discrepancies"].append({
                    "type": "trial_balance_mismatch",
                    "severity": "critical",
                    "debit_total": float(balance_check["debit_total"]),
                    "credit_total": float(balance_check["credit_total"]),
                    "difference": float(balance_check["difference"])
                })

            # كشف فروقات الترصيد
            results["posting_discrepancies"] = await self._detect_posting_discrepancies(tb_data)

            # تحليل العلاقات المحاسبية
            results["account_relationships"] = await self._analyze_account_relationships(tb_data)

            # كشف الحسابات ذات الأرصدة غير الطبيعية
            results["abnormal_balances"] = await self._detect_abnormal_balances(tb_data)

            # مراجعة الحسابات الصفرية
            results["zero_balance_accounts"] = await self._identify_zero_accounts(tb_data)

            self.processed_accounts = len(tb_data)
            self.status = "completed"
            logger.info(f"TB analysis completed. Balanced: {results['is_balanced']}")

        except Exception as e:
            logger.error(f"Error during TB analysis: {str(e)}")
            self.status = "error"
            results["error"] = str(e)

        return results

    async def _check_balance(self, data: pd.DataFrame) -> Dict[str, Any]:
        """التحقق من توازن ميزان المراجعة"""
        result = {
            "is_balanced": False,
            "debit_total": 0,
            "credit_total": 0,
            "difference": 0
        }

        # حساب مجموع المدين والدائن
        if "debit" in data.columns and "credit" in data.columns:
            result["debit_total"] = data["debit"].sum()
            result["credit_total"] = data["credit"].sum()
            result["difference"] = abs(result["debit_total"] - result["credit_total"])

            # السماح بهامش خطأ بسيط جداً (لأخطاء التقريب)
            tolerance = 0.01
            result["is_balanced"] = result["difference"] < tolerance

        elif "balance" in data.columns and "account_type" in data.columns:
            # طريقة بديلة باستخدام نوع الحساب
            debit_accounts = data[data["account_type"].isin(["asset", "expense"])]
            credit_accounts = data[data["account_type"].isin(["liability", "equity", "revenue"])]

            result["debit_total"] = abs(debit_accounts["balance"].sum())
            result["credit_total"] = abs(credit_accounts["balance"].sum())
            result["difference"] = abs(result["debit_total"] - result["credit_total"])
            result["is_balanced"] = result["difference"] < tolerance

        return result

    async def _detect_posting_discrepancies(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """كشف فروقات الترصيد"""
        discrepancies = []

        # كشف الحسابات التي تظهر في طرف واحد فقط
        if "account_code" in data.columns:
            if "debit" in data.columns and "credit" in data.columns:
                # حساب صافي الرصيد لكل حساب
                data["net_balance"] = data["debit"] - data["credit"]

                # كشف الحسابات ذات الحركات من طرف واحد فقط
                for _, row in data.iterrows():
                    has_debit = row.get("debit", 0) > 0
                    has_credit = row.get("credit", 0) > 0

                    if has_debit and not has_credit:
                        discrepancies.append({
                            "account_code": row["account_code"],
                            "issue": "debit_only",
                            "amount": float(row["debit"])
                        })
                    elif has_credit and not has_debit:
                        discrepancies.append({
                            "account_code": row["account_code"],
                            "issue": "credit_only",
                            "amount": float(row["credit"])
                        })

        return discrepancies

    async def _analyze_account_relationships(self, data: pd.DataFrame) -> Dict[str, Any]:
        """تحليل العلاقات المحاسبية"""
        relationships = {
            "contra_accounts": [],
            "related_accounts": [],
            "suspicious_pairs": []
        }

        # تحليل الحسابات المقابلة المتوقعة
        _expected_pairs = [
            ("cash", "accounts_receivable"),
            ("inventory", "cost_of_goods_sold"),
            ("fixed_assets", "accumulated_depreciation"),
            ("accounts_payable", "cash")
        ]

        # يمكن توسيع هذا التحليل ليشمل أكثر
        relationships["analysis_note"] = "Account relationship analysis requires chart of accounts mapping"

        return relationships

    async def _detect_abnormal_balances(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """كشف الأرصدة غير الطبيعية"""
        abnormal = []

        # قواعد لكشف الأرصدة غير الطبيعية
        abnormal_rules = {
            "asset_negative": lambda row: row.get("account_type") == "asset" and row.get("balance", 0) < 0,
            "liability_positive": lambda row: row.get("account_type") == "liability" and row.get("balance", 0) > 0,
            "revenue_debit": lambda row: row.get("account_type") == "revenue" and row.get("debit", 0) > row.get("credit", 0),
            "expense_credit": lambda row: row.get("account_type") == "expense" and row.get("credit", 0) > row.get("debit", 0)
        }

        for _, row in data.iterrows():
            for rule_name, rule_func in abnormal_rules.items():
                try:
                    if rule_func(row):
                        abnormal.append({
                            "account_code": row.get("account_code", "Unknown"),
                            "account_name": row.get("account_name", "Unknown"),
                            "rule_violated": rule_name,
                            "balance": float(row.get("balance", 0)),
                            "severity": "warning"
                        })
                except Exception:
                    continue

        return abnormal

    async def _identify_zero_accounts(self, data: pd.DataFrame) -> List[str]:
        """تحديد الحسابات ذات الأرصدة الصفرية"""
        zero_accounts = []

        if "account_code" in data.columns:
            if "balance" in data.columns:
                zero_accounts = data[data["balance"] == 0]["account_code"].tolist()
            elif "debit" in data.columns and "credit" in data.columns:
                data["net"] = data["debit"] - data["credit"]
                zero_accounts = data[data["net"] == 0]["account_code"].tolist()

        return zero_accounts

    def generate_summary_report(self, analysis_results: Dict[str, Any]) -> str:
        """توليد تقرير ملخص"""
        report = []
        report.append("=" * 60)
        report.append("تقرير مراجعة ميزان المراجعة")
        report.append("=" * 60)
        report.append(f"تاريخ التحليل: {analysis_results.get('analysis_timestamp', 'N/A')}")
        report.append(f"عدد الحسابات: {analysis_results.get('total_accounts', 0)}")
        report.append(f"حالة التوازن: {'متوازن ✓' if analysis_results.get('is_balanced') else 'غير متوازن ✗'}")

        if not analysis_results.get('is_balanced'):
            diff = analysis_results.get('balance_difference', 0)
            report.append(f"فارق الترصيد: {diff:,.2f}")

        discrepancies = analysis_results.get('discrepancies', [])
        if discrepancies:
            report.append(f"\nالفروقات المكتشفة: {len(discrepancies)}")
            for disc in discrepancies[:5]:
                report.append(f"  - {disc.get('type', 'Unknown')}: {disc.get('severity', 'N/A')}")

        report.append("=" * 60)
        return "\n".join(report)

    def get_status(self) -> Dict[str, Any]:
        """الحصول على حالة الوكيل"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": self.status,
            "processed_accounts": self.processed_accounts,
            "discrepancies_found": len(self.discrepancies_found)
        }


# مثال للاستخدام
if __name__ == "__main__":
    async def main():
        agent = TrialBalanceAuditAgent()

        # بيانات تجريبية لميزان المراجعة
        sample_tb = pd.DataFrame({
            "account_code": ["1001", "1002", "2001", "3001", "4001", "5001"],
            "account_name": ["Cash", "Accounts Receivable", "Accounts Payable", "Equity", "Revenue", "Expenses"],
            "account_type": ["asset", "asset", "liability", "equity", "revenue", "expense"],
            "debit": [100000, 50000, 0, 0, 0, 80000],
            "credit": [0, 0, 30000, 150000, 70000, 0]
        })

        results = await agent.analyze_trial_balance(sample_tb)
        print(agent.generate_summary_report(results))

    asyncio.run(main())
