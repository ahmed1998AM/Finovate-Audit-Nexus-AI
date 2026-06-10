"""
Finovate Audit Nexus AI - General Ledger Audit Agent

مراجعة دفتر الأستاذ - تحليل الحركات واكتشاف الانحرافات
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
from loguru import logger


class GeneralLedgerAuditAgent:
    """
    وكيل مراجعة دفتر الأستاذ
    
    المهام:
    - تحليل الحركات
    - كشف الحسابات غير الطبيعية
    - تحليل الأنماط
    - كشف الانحرافات
    - تحليل الأرصدة
    """
    
    def __init__(self, agent_id: str = "ledger_agent_001"):
        self.agent_id = agent_id
        self.agent_name = "General Ledger Audit Agent"
        self.status = "initialized"
        self.processed_entries = 0
        self.anomalies_detected = []
        
        logger.info(f"{self.agent_name} initialized with ID: {agent_id}")
    
    async def analyze_ledger(self, ledger_data: Any) -> Dict[str, Any]:
        """
        تحليل دفتر الأستاذ
        
        Args:
            ledger_data: البيانات المدخلة (يمكن أن تكون DataFrame أو List of Dicts)
            
        Returns:
            dict: نتائج التحليل
        """
        logger.info("Starting general ledger analysis...")
        self.status = "analyzing"
        
        # تحويل البيانات إلى DataFrame إذا لزم الأمر
        if isinstance(ledger_data, list):
            df = pd.DataFrame(ledger_data)
        elif isinstance(ledger_data, pd.DataFrame):
            df = ledger_data
        else:
            logger.warning("Invalid data format for ledger data. Expected list or DataFrame.")
            return {"status": "error", "error": "Invalid data format"}

        if df.empty:
            logger.warning("No ledger data provided for analysis.")
            return {"status": "empty", "total_entries": 0}

        results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_entries": len(df),
            "anomalies": [],
            "patterns": {},
            "account_analysis": {},
            "risk_indicators": []
        }
        
        try:
            # تحليل الحركات
            results["transaction_analysis"] = await self._analyze_transactions(df)
            
            # كشف الحسابات غير الطبيعية
            results["abnormal_accounts"] = await self._detect_abnormal_accounts(df)
            
            # تحليل الأنماط
            results["patterns"] = await self._analyze_patterns(df)
            
            # كشف الانحرافات
            results["deviations"] = await self._detect_deviations(df)
            
            # تحليل الأرصدة
            results["balance_analysis"] = await self._analyze_balances(df)
            
            # Populate anomalies list from deviations
            results["anomalies"] = results["deviations"]
            
            self.status = "completed"
            logger.info(f"Ledger analysis completed. Found {len(results['anomalies'])} anomalies")
            
        except Exception as e:
            logger.error(f"Error during ledger analysis: {str(e)}")
            self.status = "error"
            results["error"] = str(e)
        
        return results
    
    async def _analyze_transactions(self, data: pd.DataFrame) -> Dict[str, Any]:
        """تحليل الحركات"""
        analysis = {
            "total_transactions": len(data),
            "by_account_type": {},
            "by_period": {},
            "large_transactions": [],
            "round_amount_transactions": []
        }
        
        if "amount" in data.columns:
            # كشف الحركات الكبيرة
            threshold = data["amount"].mean() + 3 * data["amount"].std()
            large_txns = data[data["amount"] > threshold]
            analysis["large_transactions"] = large_txns.to_dict("records")[:10]
            
            # كشف المبالغ المستديرة (مؤشر محتمل للتلاعب)
            if "amount" in data.columns:
                round_amounts = data[data["amount"].apply(lambda x: x % 1000 == 0)]
                analysis["round_amount_transactions"] = round_amounts.to_dict("records")[:10]
        
        return analysis
    
    async def _detect_abnormal_accounts(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """كشف الحسابات غير الطبيعية"""
        abnormal = []
        
        if "account_code" in data.columns:
            account_activity = data.groupby("account_code").agg({
                "amount": ["count", "sum", "mean", "std"]
            }).reset_index()
            
            # كشف الحسابات ذات النشاط غير الطبيعي
            for _, row in account_activity.iterrows():
                if row[("amount", "std")] and row[("amount", "mean")]:
                    cv = row[("amount", "std")] / abs(row[("amount", "mean")]) if row[("amount", "mean")] != 0 else 0
                    if cv > 5:  # معامل اختلاف عالي
                        abnormal.append({
                            "account_code": row["account_code"],
                            "reason": "high_variance",
                            "coefficient_of_variation": cv,
                            "transaction_count": row[("amount", "count")],
                            "total_amount": row[("amount", "sum")]
                        })
        
        return abnormal
    
    async def _analyze_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """تحليل الأنماط"""
        patterns = {
            "seasonal_patterns": {},
            "periodic_patterns": {},
            "user_patterns": {},
            "time_patterns": {}
        }
        
        if "posting_date" in data.columns:
            data["posting_date"] = pd.to_datetime(data["posting_date"])
            data["month"] = data["posting_date"].dt.month
            data["day_of_week"] = data["posting_date"].dt.dayofweek
            
            # تحليل按月
            monthly_pattern = data.groupby("month")["amount"].sum().to_dict()
            patterns["seasonal_patterns"]["monthly"] = monthly_pattern
            
            # تحليل بيوم الأسبوع
            dow_pattern = data.groupby("day_of_week")["amount"].sum().to_dict()
            patterns["time_patterns"]["day_of_week"] = dow_pattern
        
        return patterns
    
    async def _detect_deviations(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """كشف الانحرافات"""
        deviations = []
        
        if "amount" in data.columns:
            # استخدام Z-score لكشف القيم الشاذة
            mean = data["amount"].mean()
            std = data["amount"].std()
            
            if std > 0:
                data["z_score"] = (data["amount"] - mean) / std
                outliers = data[abs(data["z_score"]) > 3]
                
                for _, row in outliers.iterrows():
                    deviations.append({
                        "type": "statistical_outlier",
                        "z_score": float(row["z_score"]),
                        "amount": float(row["amount"]),
                        "account": row.get("account_code", "Unknown"),
                        "date": str(row.get("posting_date", "Unknown"))
                    })
        
        return deviations
    
    async def _analyze_balances(self, data: pd.DataFrame) -> Dict[str, Any]:
        """تحليل الأرصدة"""
        balance_analysis = {
            "account_balances": {},
            "balance_trends": {},
            "negative_balances": [],
            "zero_balances": []
        }
        
        if all(col in data.columns for col in ["account_code", "amount"]):
            # حساب أرصدة الحسابات
            balances = data.groupby("account_code")["amount"].sum()
            
            for account, balance in balances.items():
                if balance < 0:
                    balance_analysis["negative_balances"].append({
                        "account_code": account,
                        "balance": float(balance)
                    })
                elif balance == 0:
                    balance_analysis["zero_balances"].append(account)
            
            balance_analysis["account_balances"] = balances.to_dict()
        
        return balance_analysis
    
    def get_status(self) -> Dict[str, Any]:
        """الحصول على حالة الوكيل"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": self.status,
            "processed_entries": self.processed_entries,
            "anomalies_detected": len(self.anomalies_detected)
        }


# مثال للاستخدام
if __name__ == "__main__":
    async def main():
        agent = GeneralLedgerAuditAgent()
        
        # بيانات تجريبية
        sample_data = pd.DataFrame({
            "account_code": ["1001", "1002", "1001", "2001", "1001"],
            "amount": [1000, 5000, 1500, 3000, 50000],
            "posting_date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
        })
        
        results = await agent.analyze_ledger(sample_data)
        print(f"Analysis Results: {results}")
    
    asyncio.run(main())
