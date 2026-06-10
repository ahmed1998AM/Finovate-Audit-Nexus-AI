"""
Finovate Audit Nexus AI - Journal Entry Audit Agent

مراجعة قيود اليومية - كشف القيود المكررة والوهمية وغير الطبيعية
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from loguru import logger


class JournalEntryAuditAgent:
    """
    وكيل مراجعة قيود اليومية
    
    المهام:
    - كشف القيود المكررة
    - كشف القيود الوهمية
    - كشف القيود غير الطبيعية
    - تحليل توقيت القيود
    - تحليل المستخدمين
    - تحليل التسويات
    - كشف التلاعب
    """
    
    def __init__(self, agent_id: str = "journal_agent_001"):
        self.agent_id = agent_id
        self.agent_name = "Journal Entry Audit Agent"
        self.status = "initialized"
        self.entries_processed = 0
        self.findings = []
        
        logger.info(f"{self.agent_name} initialized with ID: {agent_id}")
    
    async def analyze_journal_entries(self, entries: Any) -> Dict[str, Any]:
        """
        تحليل قيود اليومية
        
        Args:
            entries: البيانات المدخلة (يمكن أن تكون DataFrame أو List of Dicts)
            
        Returns:
            dict: نتائج التحليل
        """
        logger.info("Starting journal entry analysis...")
        self.status = "analyzing"
        
        # تحويل البيانات إلى DataFrame إذا لزم الأمر
        if isinstance(entries, list):
            df = pd.DataFrame(entries)
        elif isinstance(entries, pd.DataFrame):
            df = entries
        else:
            logger.warning("Invalid data format for journal entries. Expected list or DataFrame.")
            return {"status": "error", "error": "Invalid data format"}

        if df.empty:
            logger.warning("No journal entries provided for analysis.")
            return {"status": "empty", "total_entries": 0, "risk_score": 0}

        results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_entries": len(df),
            "duplicate_entries": [],
            "suspicious_entries": [],
            "timing_anomalies": [],
            "user_anomalies": [],
            "round_amount_entries": [],
            "manual_entries": [],
            "risk_score": 0
        }
        
        try:
            # كشف القيود المكررة
            results["duplicate_entries"] = await self._detect_duplicates(df)
            
            # كشف القيود غير الطبيعية
            results["suspicious_entries"] = await self._detect_suspicious_entries(df)
            
            # تحليل توقيت القيود
            results["timing_anomalies"] = await self._analyze_timing(df)
            
            # تحليل المستخدمين
            results["user_anomalies"] = await self._analyze_users(df)
            
            # كشف المبالغ المستديرة
            results["round_amount_entries"] = await self._detect_round_amounts(df)
            
            # كشف القيود اليدوية
            results["manual_entries"] = await self._identify_manual_entries(df)
            
            # حساب درجة المخاطر
            results["risk_score"] = self._calculate_risk_score(results)
            
            self.entries_processed = len(df)
            self.status = "completed"
            logger.info(f"Journal entry analysis completed. Risk Score: {results['risk_score']}")
            
        except Exception as e:
            logger.error(f"Error during journal entry analysis: {str(e)}")
            self.status = "error"
            results["error"] = str(e)
        
        return results
    
    async def _detect_duplicates(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """كشف القيود المكررة"""
        duplicates = []
        
        # كشف التكرار بناءً على多个 معايير
        duplicate_checks = [
            ["amount", "account_code", "posting_date"],
            ["description", "amount", "posting_date"],
            ["reference_number", "amount"]
        ]
        
        for check_fields in duplicate_checks:
            if all(field in data.columns for field in check_fields):
                dupes = data[data.duplicated(subset=check_fields, keep=False)]
                
                if len(dupes) > 0:
                    duplicates.append({
                        "check_type": "_".join(check_fields),
                        "count": len(dupes),
                        "entries": dupes.head(10).to_dict("records"),
                        "severity": "high" if len(dupes) > 5 else "medium"
                    })
        
        return duplicates
    
    async def _detect_suspicious_entries(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """كشف القيود المشبوهة"""
        suspicious = []
        
        # قواعد لكشف القيود المشبوهة
        suspicious_rules = {
            "weekend_posting": lambda row: self._is_weekend(row.get("posting_date")),
            "after_hours_posting": lambda row: self._is_after_hours(row.get("posting_time")),
            "round_amount_large": lambda row: self._is_large_round_amount(row.get("amount", 0)),
            "description_missing": lambda row: self._is_empty(row.get("description")),
            "reference_missing": lambda row: self._is_empty(row.get("reference_number")),
            "unusual_account_combination": lambda row: self._is_unusual_combo(row)
        }
        
        for rule_name, rule_func in suspicious_rules.items():
            violations = []
            for idx, row in data.iterrows():
                try:
                    if rule_func(row):
                        violations.append({
                            "entry_id": row.get("entry_id", idx),
                            "rule_violated": rule_name,
                            "details": self._get_entry_summary(row)
                        })
                except:
                    continue
            
            if violations:
                suspicious.append({
                    "rule": rule_name,
                    "violation_count": len(violations),
                    "entries": violations[:10]
                })
        
        return suspicious
    
    async def _analyze_timing(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """تحليل توقيت القيود"""
        timing_issues = []
        
        if "posting_date" in data.columns:
            data["posting_date"] = pd.to_datetime(data["posting_date"])
            
            # تحليل القيود في نهاية الفترة
            period_end_dates = data[
                (data["posting_date"].dt.day >= 28) |
                (data["posting_date"].dt.month.isin([3, 6, 9, 12])) &
                (data["posting_date"].dt.day >= 25)
            ]
            
            if len(period_end_dates) > 0:
                timing_issues.append({
                    "issue_type": "period_end_concentration",
                    "count": len(period_end_dates),
                    "description": f"{len(period_end_dates)} entries posted near period end",
                    "risk_level": "medium"
                })
            
            # تحليل القيود اللاحقة للإغلاق
            # (يتطلب معرفة تواريخ الإغلاق)
        
        return timing_issues
    
    async def _analyze_users(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """تحليل سلوك المستخدمين"""
        user_issues = []
        
        if "created_by" in data.columns:
            user_activity = data.groupby("created_by").agg({
                "amount": ["count", "sum"],
                "entry_id": "count"
            }).reset_index()
            
            # كشف المستخدمين ذوي النشاط غير الطبيعي
            for _, row in user_activity.iterrows():
                entry_count = row[("entry_id", "count")]
                total_amount = row[("amount", "sum")]
                
                if entry_count > data.shape[0] * 0.3:  # أكثر من 30% من القيود
                    user_issues.append({
                        "user": row["created_by"],
                        "issue": "high_activity_concentration",
                        "entry_count": int(entry_count),
                        "total_amount": float(total_amount) if total_amount else 0
                    })
        
        return user_issues
    
    async def _detect_round_amounts(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """كشف المبالغ المستديرة"""
        round_amounts = []
        
        if "amount" in data.columns:
            # كشف المبالغ المستديرة الكبيرة
            large_round = data[
                (data["amount"] >= 10000) &
                (data["amount"] % 1000 == 0)
            ]
            
            if len(large_round) > 0:
                round_amounts.append({
                    "threshold": ">= 10,000 and divisible by 1,000",
                    "count": len(large_round),
                    "entries": large_round.head(10).to_dict("records")
                })
        
        return round_amounts
    
    async def _identify_manual_entries(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """تحديد القيود اليدوية"""
        manual_entries = []
        
        # البحث عن مؤشرات القيود اليدوية
        manual_indicators = [
            "manual", "adjustment", "correction", "reversal",
            "يدوي", "تسوية", "تصحيح", "عكس"
        ]
        
        if "description" in data.columns:
            for indicator in manual_indicators:
                matches = data[data["description"].str.contains(indicator, case=False, na=False)]
                if len(matches) > 0:
                    manual_entries.append({
                        "indicator": indicator,
                        "count": len(matches),
                        "entries": matches.head(5).to_dict("records")
                    })
        
        return manual_entries
    
    def _calculate_risk_score(self, results: Dict[str, Any]) -> int:
        """حساب درجة المخاطر الإجمالية"""
        score = 0
        
        # وزن كل نوع من الاكتشافات
        score += len(results.get("duplicate_entries", [])) * 10
        score += sum(len(e.get("entries", [])) for e in results.get("suspicious_entries", [])) * 5
        score += len(results.get("timing_anomalies", [])) * 8
        score += len(results.get("user_anomalies", [])) * 7
        score += sum(e.get("count", 0) for e in results.get("round_amount_entries", [])) * 3
        
        # تطبيع النتيجة إلى مقياس 0-100
        return min(100, score)
    
    def _is_weekend(self, date_str: Optional[str]) -> bool:
        """التحقق مما إذا كان التاريخ في عطلة نهاية الأسبوع"""
        if not date_str:
            return False
        try:
            date = pd.to_datetime(date_str)
            return date.dayofweek >= 5  # Saturday = 5, Sunday = 6
        except:
            return False
    
    def _is_after_hours(self, time_str: Optional[str]) -> bool:
        """التحقق مما إذا كان الوقت خارج ساعات العمل"""
        if not time_str:
            return False
        try:
            time = pd.to_datetime(time_str).time()
            hour = time.hour
            return hour < 8 or hour > 18  # قبل 8 صباحاً أو بعد 6 مساءً
        except:
            return False
    
    def _is_large_round_amount(self, amount: float) -> bool:
        """التحقق مما إذا كان المبلغ مستديراً وكبيراً"""
        if not amount:
            return False
        return amount >= 50000 and amount % 10000 == 0
    
    def _is_empty(self, value: Any) -> bool:
        """التحقق مما إذا كانت القيمة فارغة"""
        if value is None:
            return True
        if isinstance(value, str) and value.strip() == "":
            return True
        return False
    
    def _is_unusual_combo(self, row: pd.Series) -> bool:
        """التحقق من توليفة الحسابات غير العادية"""
        # يمكن توسيع هذا المنطق ليشمل قواعد محاسبية محددة
        return False
    
    def _get_entry_summary(self, row: pd.Series) -> Dict[str, Any]:
        """الحصول على ملخص القيد"""
        return {
            "entry_id": row.get("entry_id", "Unknown"),
            "amount": row.get("amount", 0),
            "date": row.get("posting_date", "Unknown"),
            "description": row.get("description", "")[:50]
        }
    
    def generate_findings_report(self, results: Dict[str, Any]) -> str:
        """توليد تقرير النتائج"""
        report = []
        report.append("=" * 70)
        report.append("تقرير مراجعة قيود اليومية - Finovate Audit Nexus AI")
        report.append("=" * 70)
        report.append(f"تاريخ التحليل: {results.get('analysis_timestamp', 'N/A')}")
        report.append(f"إجمالي القيود: {results.get('total_entries', 0)}")
        report.append(f"درجة المخاطر: {results.get('risk_score', 0)}/100")
        report.append("")
        
        # القيود المكررة
        duplicates = results.get("duplicate_entries", [])
        if duplicates:
            report.append("-" * 70)
            report.append("القيود المكررة:")
            for dup in duplicates:
                report.append(f"  [{dup.get('severity', 'N/A').upper()}] {dup.get('count', 0)} قيود مكررة")
                report.append(f"    معيار التكرار: {dup.get('check_type', 'N/A')}")
        
        # القيود المشبوهة
        suspicious = results.get("suspicious_entries", [])
        if suspicious:
            report.append("-" * 70)
            report.append("القيود المشبوهة:")
            for sus in suspicious:
                report.append(f"  القاعدة: {sus.get('rule', 'N/A')}")
                report.append(f"    عدد الانتهاكات: {sus.get('violation_count', 0)}")
        
        # مشاكل التوقيت
        timing = results.get("timing_anomalies", [])
        if timing:
            report.append("-" * 70)
            report.append("مشاكل التوقيت:")
            for t in timing:
                report.append(f"  [{t.get('risk_level', 'N/A').upper()}] {t.get('description', '')}")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def get_status(self) -> Dict[str, Any]:
        """الحصول على حالة الوكيل"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": self.status,
            "entries_processed": self.entries_processed,
            "findings_count": len(self.findings)
        }


# مثال للاستخدام
if __name__ == "__main__":
    async def main():
        agent = JournalEntryAuditAgent()
        
        # بيانات تجريبية لقيود اليومية
        sample_entries = pd.DataFrame({
            "entry_id": [1, 2, 3, 4, 5, 6],
            "posting_date": ["2024-01-15", "2024-01-15", "2024-01-20", "2024-01-30", "2024-02-01", "2024-01-15"],
            "posting_time": ["10:00", "14:00", "22:00", "11:00", "09:00", "10:00"],
            "account_code": ["1001", "1002", "2001", "1001", "4001", "1001"],
            "amount": [1000, 5000, 100000, 50000, 2000, 1000],
            "description": ["Cash receipt", "Payment", "Manual adjustment", "Large transfer", "Revenue", "Cash receipt"],
            "reference_number": ["REF001", "REF002", "", "REF004", "REF005", "REF001"],
            "created_by": ["user1", "user1", "admin", "user2", "user1", "user1"]
        })
        
        results = await agent.analyze_journal_entries(sample_entries)
        print(agent.generate_findings_report(results))
    
    asyncio.run(main())
