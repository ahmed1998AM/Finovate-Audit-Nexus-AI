"""
Forensic Accounting Agent
وكيل التحقيق الجنائي المالي

المهام:
- تتبع الأموال
- كشف الفواتير الوهمية
- كشف الشركات الوهمية
- كشف غسل الأموال
- التحقيق المالي الجنائي
- تحليل الشبكات المالية
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class FraudType(Enum):
    """أنواع الاحتيال"""
    FAKE_INVOICE = "fake_invoice"
    SHELL_COMPANY = "shell_company"
    MONEY_LAUNDERING = "money_laundering"
    ROUND_TRIPPING = "round_tripping"
    PHANTOM_VENDOR = "phantom_vendor"
    PAYMENT_SCHEME = "payment_scheme"
    ASSET_MISAPPROPRIATION = "asset_misappropriation"


@dataclass
class SuspiciousTransaction:
    """معاملة مشبوهة"""
    transaction_id: str
    amount: float
    date: str
    parties: List[str]
    fraud_type: FraudType
    risk_score: float
    indicators: List[str]
    evidence: List[str]
    description: str


@dataclass
class ForensicInvestigationResult:
    """نتيجة التحقيق الجنائي"""
    investigation_id: str
    investigation_date: str
    total_transactions_analyzed: int
    suspicious_transactions: List[SuspiciousTransaction]
    fraud_networks: List[Dict[str, Any]]
    money_flow_analysis: Dict[str, Any]
    red_flags: List[Dict[str, Any]]
    recommendations: List[str]
    overall_risk_score: float
    confidence_level: float


class ForensicAccountingAgent:
    """
    وكيل التحقيق الجنائي المالي
    
    متخصص في:
    - كشف الفواتير الوهمية
    - تحديد الشركات الوهمية
    - تتبع تدفقات الأموال المشبوهة
    - كشف مخططات غسل الأموال
    - تحليل الشبكات المالية المعقدة
    """
    
    def __init__(self, llm_provider: Optional[str] = None):
        self.llm_provider = llm_provider or "default"
        self.name = "Forensic_Accounting_Agent"
        self.version = "1.0.0"
        
        # مؤشرات الاحتيال
        self.fraud_indicators = {
            "round_amount": 0.3,  # مبالغ مستديرة
            "weekend_transaction": 0.2,  # معاملات في عطلة
            "high_frequency": 0.4,  # تكرار عالي
            "new_vendor": 0.3,  # مورد جديد
            "no_invoice_details": 0.5,  #缺少 تفاصيل الفاتورة
            "similar_addresses": 0.6,  # عناوين متشابهة
            "related_parties": 0.7,  # أطراف ذات علاقة
            "cash_heavy": 0.5,  # معاملات نقدية كبيرة
        }
        
        # عتبات الكشف
        self.thresholds = {
            "large_cash_transaction": 50000,  # معاملة نقدية كبيرة
            "frequent_payment_days": 7,  # أيام دفع متقاربة
            "vendor_concentration": 0.25,  # تركيز الموردين
            "invoice_sequence_gap": 100,  # فجوة في تسلسل الفواتير
        }
    
    def analyze_vendor_payments(self, 
                                 payments: List[Dict[str, Any]],
                                 vendors: List[Dict[str, Any]]) -> List[SuspiciousTransaction]:
        """
        تحليل مدفوعات الموردين لكشف الفواتير الوهمية
        
        Args:
            payments: قائمة المدفوعات
            vendors: بيانات الموردين
            
        Returns:
            قائمة بالمعاملات المشبوهة
        """
        logger.info("Analyzing vendor payments for fake invoices...")
        
        suspicious = []
        
        # تجميع المدفوعات حسب المورد
        vendor_payments = defaultdict(list)
        for payment in payments:
            vendor_id = payment.get("vendor_id")
            vendor_payments[vendor_id].append(payment)
        
        # تحليل كل مورد
        for vendor_id, vendor_pmts in vendor_payments.items():
            vendor_info = next((v for v in vendors if v.get("id") == vendor_id), {})
            
            # فحص 1: مدفوعات لمورد بدون تفاصيل كافية
            if not vendor_info.get("tax_id") or not vendor_info.get("address"):
                for pmt in vendor_pmts:
                    suspicious.append(SuspiciousTransaction(
                        transaction_id=pmt.get("id", "Unknown"),
                        amount=pmt.get("amount", 0),
                        date=pmt.get("date", ""),
                        parties=[vendor_info.get("name", "Unknown Vendor")],
                        fraud_type=FraudType.PHANTOM_VENDOR,
                        risk_score=0.7,
                        indicators=["missing_tax_id", "missing_address"],
                        evidence=["Vendor lacks basic registration information"],
                        description=f"مدفوعات لمورد بدون معلومات ضريبية أو عنوان: {vendor_info.get('name', 'Unknown')}"
                    ))
            
            # فحص 2: مبالغ مستديرة (دليل على التلاعب)
            round_amount_pmts = [p for p in vendor_pmts if p.get("amount", 0) % 10000 == 0 and p.get("amount", 0) > 50000]
            for pmt in round_amount_pmts:
                suspicious.append(SuspiciousTransaction(
                    transaction_id=pmt.get("id", "Unknown"),
                    amount=pmt.get("amount", 0),
                    date=pmt.get("date", ""),
                    parties=[vendor_info.get("name", "Unknown Vendor")],
                    fraud_type=FraudType.FAKE_INVOICE,
                    risk_score=0.5,
                    indicators=["round_amount", "large_value"],
                    evidence=[f"Amount is perfectly rounded: {pmt.get('amount')}"],
                    description=f"مبلغ مستدير كبير قد يشير إلى فاتورة وهمية: {pmt.get('amount'):,.0f} جنيه"
                ))
            
            # فحص 3: تكرار غير طبيعي
            if len(vendor_pmts) > 10:
                dates = [p.get("date", "") for p in vendor_pmts]
                # التحقق من التكرار في فترة قصيرة
                suspicious.append(SuspiciousTransaction(
                    transaction_id=f"VENDOR_{vendor_id}_PATTERN",
                    amount=sum(p.get("amount", 0) for p in vendor_pmts),
                    date=min(dates) if dates else "",
                    parties=[vendor_info.get("name", "Unknown Vendor")],
                    fraud_type=FraudType.PAYMENT_SCHEME,
                    risk_score=0.6,
                    indicators=["high_frequency", "pattern_anomaly"],
                    evidence=[f"{len(vendor_pmts)} payments to single vendor"],
                    description=f"تكرار غير طبيعي للمدفوعات: {len(vendor_pmts)} عملية لنفس المورد"
                ))
        
        return suspicious
    
    def detect_shell_companies(self,
                                companies: List[Dict[str, Any]],
                                transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        كشف الشركات الوهمية
        
        Args:
            companies: بيانات الشركات
            transactions: المعاملات المرتبطة
            
        Returns:
            قائمة بالشركات الوهمية المشتبه بها
        """
        logger.info("Detecting shell companies...")
        
        shell_indicators = []
        
        for company in companies:
            indicators = []
            risk_score = 0.0
            
            # مؤشر 1: شركة حديثة التأسيس مع معاملات كبيرة
            establishment_date = company.get("establishment_date", "")
            if establishment_date:
                try:
                    est_date = datetime.fromisoformat(establishment_date)
                    age_days = (datetime.now() - est_date).days
                    if age_days < 180:  # أقل من 6 أشهر
                        indicators.append("newly_established")
                        risk_score += 0.3
                except:
                    pass
            
            # مؤشر 2: رأس مال منخفض ومعاملات عالية
            capital = company.get("capital", 0)
            company_txns = [t for t in transactions if t.get("party_id") == company.get("id")]
            total_volume = sum(t.get("amount", 0) for t in company_txns)
            
            if capital > 0 and total_volume > capital * 10:
                indicators.append("volume_exceeds_capital")
                risk_score += 0.4
            
            # مؤشر 3: عنوان مشترك مع شركات أخرى
            address = company.get("address", "")
            if address:
                companies_at_same_address = [c for c in companies if c.get("address") == address and c.get("id") != company.get("id")]
                if len(companies_at_same_address) > 2:
                    indicators.append("shared_address")
                    risk_score += 0.3
            
            # مؤشر 4: نشاط تجاري غير واضح
            if not company.get("business_activity") or company.get("business_activity") == "General Trading":
                indicators.append("vague_business_activity")
                risk_score += 0.2
            
            # مؤشر 5: مساهمين مجهولين
            shareholders = company.get("shareholders", [])
            if not shareholders or any(s.get("name") == "Unknown" for s in shareholders):
                indicators.append("unknown_shareholders")
                risk_score += 0.3
            
            if risk_score >= 0.5:
                shell_indicators.append({
                    "company_id": company.get("id"),
                    "company_name": company.get("name"),
                    "risk_score": min(1.0, risk_score),
                    "indicators": indicators,
                    "total_transaction_volume": total_volume,
                    "capital": capital,
                    "recommendation": "Investigate for potential shell company" if risk_score >= 0.7 else "Monitor closely"
                })
        
        return sorted(shell_indicators, key=lambda x: x["risk_score"], reverse=True)
    
    def detect_money_laundering(self,
                                 transactions: List[Dict[str, Any]],
                                 accounts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        كشف عمليات غسل الأموال
        
        Args:
            transactions: قائمة المعاملات
            accounts: الحسابات البنكية
            
        Returns:
            تحليل شامل لغسل الأموال
        """
        logger.info("Detecting money laundering patterns...")
        
        red_flags = []
        suspicious_patterns = []
        
        # نمط 1: Structuring/Smurfing (تقسيم المبالغ الكبيرة)
        account_transactions = defaultdict(list)
        for txn in transactions:
            account_id = txn.get("account_id")
            account_transactions[account_id].append(txn)
        
        for account_id, txns in account_transactions.items():
            # البحث عن معاملات متتالية تحت حد الإبلاغ
            amounts = [t.get("amount", 0) for t in txns]
            large_amounts = [a for a in amounts if 40000 <= a <= 60000]  # حول حد 50,000
            
            if len(large_amounts) >= 3:
                red_flags.append({
                    "type": "structuring",
                    "account_id": account_id,
                    "count": len(large_amounts),
                    "total_amount": sum(large_amounts),
                    "severity": "high",
                    "description": "تقسيم محتمل للمبالغ لتجنب حدود الإبلاغ"
                })
        
        # نمط 2: Round-tripping (إعادة الأموال لدورات)
        # البحث عن معاملات ذهاب وإياب بين نفس الأطراف
        party_pairs = defaultdict(list)
        for txn in transactions:
            from_party = txn.get("from_party")
            to_party = txn.get("to_party")
            if from_party and to_party:
                pair_key = tuple(sorted([from_party, to_party]))
                party_pairs[pair_key].append(txn)
        
        for pair, txns in party_pairs.items():
            if len(txns) >= 4:  # معاملتان في كل اتجاه على الأقل
                directions = set()
                for txn in txns:
                    if txn.get("from_party") == pair[0]:
                        directions.add("A_to_B")
                    else:
                        directions.add("B_to_A")
                
                if len(directions) == 2:
                    total_amount = sum(t.get("amount", 0) for t in txns)
                    suspicious_patterns.append({
                        "type": "round_tripping",
                        "parties": list(pair),
                        "transaction_count": len(txns),
                        "total_volume": total_amount,
                        "severity": "critical",
                        "description": "تدوير أموال محتمل بين طرفين"
                    })
        
        # نمط 3: معاملات مع دول عالية الخطورة
        high_risk_countries = ["XX", "YY", "ZZ"]  # أمثلة
        international_txns = [t for t in transactions if t.get("country") in high_risk_countries]
        
        if international_txns:
            red_flags.append({
                "type": "high_risk_jurisdiction",
                "count": len(international_txns),
                "total_amount": sum(t.get("amount", 0) for t in international_txns),
                "severity": "high",
                "description": "معاملات مع دول مصنفة عالية الخطورة"
            })
        
        # نمط 4: إيداعات نقدية كبيرة متتالية
        cash_deposits = [t for t in transactions if t.get("type") == "cash_deposit"]
        if len(cash_deposits) >= 5:
            total_cash = sum(t.get("amount", 0) for t in cash_deposits)
            avg_cash = total_cash / len(cash_deposits)
            
            if avg_cash > self.thresholds["large_cash_transaction"]:
                red_flags.append({
                    "type": "large_cash_deposits",
                    "count": len(cash_deposits),
                    "total_amount": total_cash,
                    "average_amount": avg_cash,
                    "severity": "critical",
                    "description": "سلسلة إيداعات نقدية كبيرة"
                })
        
        return {
            "analysis_date": datetime.now().isoformat(),
            "total_transactions_analyzed": len(transactions),
            "red_flags_count": len(red_flags),
            "suspicious_patterns_count": len(suspicious_patterns),
            "red_flags": red_flags,
            "suspicious_patterns": suspicious_patterns,
            "overall_risk_level": "critical" if len(suspicious_patterns) > 0 else ("high" if len(red_flags) > 2 else "medium")
        }
    
    def trace_money_flow(self,
                          source_account: str,
                          transactions: List[Dict[str, Any]],
                          max_depth: int = 5) -> Dict[str, Any]:
        """
        تتبع تدفق الأموال من حساب مصدر
        
        Args:
            source_account: الحساب المصدر
            transactions: جميع المعاملات
            max_depth: أقصى عمق للتتبع
            
        Returns:
            خريطة تدفق الأموال
        """
        logger.info(f"Tracing money flow from account: {source_account}")
        
        flow_tree = {
            "account": source_account,
            "outflows": [],
            "total_outflow": 0,
            "depth": 0
        }
        
        visited = set()
        
        def trace_recursive(account: str, depth: int) -> Dict:
            if depth > max_depth or account in visited:
                return {"account": account, "depth": depth, "terminal": True}
            
            visited.add(account)
            
            # العثور على المعاملات الخارجة من هذا الحساب
            outflows = [t for t in transactions if t.get("from_account") == account]
            
            node = {
                "account": account,
                "depth": depth,
                "outflows": [],
                "total_outflow": sum(t.get("amount", 0) for t in outflows),
                "terminal": False
            }
            
            for txn in outflows[:10]:  # الحد الأقصى 10 معاملات
                to_account = txn.get("to_account")
                if to_account:
                    child_node = trace_recursive(to_account, depth + 1)
                    child_node["transaction_id"] = txn.get("id")
                    child_node["amount"] = txn.get("amount", 0)
                    child_node["date"] = txn.get("date")
                    node["outflows"].append(child_node)
            
            return node
        
        result = trace_recursive(source_account, 0)
        
        return {
            "source_account": source_account,
            "trace_date": datetime.now().isoformat(),
            "max_depth_reached": max_depth,
            "flow_map": result,
            "unique_accounts_visited": len(visited),
            "recommendations": [
                "Review all accounts in the flow chain",
                "Verify business purpose of each transaction",
                "Check for circular flows"
            ] if len(visited) > 3 else []
        }
    
    def generate_forensic_report(self,
                                  payments: List[Dict[str, Any]],
                                  vendors: List[Dict[str, Any]],
                                  companies: List[Dict[str, Any]],
                                  transactions: List[Dict[str, Any]],
                                  accounts: List[Dict[str, Any]]) -> ForensicInvestigationResult:
        """
        إنشاء تقرير تحقيق جنائي شامل
        
        Returns:
            تقرير مفصل بجميع النتائج
        """
        logger.info("Generating comprehensive forensic report...")
        
        # تحليل مدفوعات الموردين
        suspicious_payments = self.analyze_vendor_payments(payments, vendors)
        
        # كشف الشركات الوهمية
        shell_companies = self.detect_shell_companies(companies, transactions)
        
        # كشف غسل الأموال
        ml_analysis = self.detect_money_laundering(transactions, accounts)
        
        # تجميع جميع الأعلام الحمراء
        all_red_flags = []
        
        for sp in suspicious_payments:
            all_red_flags.append({
                "type": sp.fraud_type.value,
                "transaction_id": sp.transaction_id,
                "amount": sp.amount,
                "risk_score": sp.risk_score,
                "indicators": sp.indicators,
                "description": sp.description
            })
        
        for sc in shell_companies:
            all_red_flags.append({
                "type": "shell_company",
                "company_id": sc["company_id"],
                "company_name": sc["company_name"],
                "risk_score": sc["risk_score"],
                "indicators": sc["indicators"],
                "description": f"شركة وهمية مشتبه بها: {sc['company_name']}"
            })
        
        all_red_flags.extend(ml_analysis.get("red_flags", []))
        
        # بناء شبكات الاحتيال
        fraud_networks = []
        if len(suspicious_payments) > 5:
            vendor_groups = defaultdict(list)
            for sp in suspicious_payments:
                for party in sp.parties:
                    vendor_groups[party].append(sp)
            
            for vendor, cases in vendor_groups.items():
                if len(cases) >= 2:
                    fraud_networks.append({
                        "network_type": "vendor_fraud_ring",
                        "central_entity": vendor,
                        "case_count": len(cases),
                        "total_amount": sum(c.amount for c in cases),
                        "severity": "high"
                    })
        
        # إضافة أنماط غسل الأموال كشبكات
        for pattern in ml_analysis.get("suspicious_patterns", []):
            fraud_networks.append({
                "network_type": pattern["type"],
                "entities": pattern["parties"] if "parties" in pattern else [pattern.get("account_id")],
                "transaction_count": pattern.get("transaction_count", 0),
                "total_volume": pattern.get("total_volume", 0),
                "severity": pattern.get("severity", "medium")
            })
        
        # حساب درجة المخاطر الإجمالية
        if all_red_flags:
            avg_risk = sum(rf.get("risk_score", 0.5) for rf in all_red_flags) / len(all_red_flags)
            critical_count = len([rf for rf in all_red_flags if rf.get("risk_score", 0) >= 0.7])
            overall_risk = min(1.0, avg_risk + (critical_count * 0.1))
        else:
            overall_risk = 0.0
        
        # التوصيات
        recommendations = []
        
        if len(suspicious_payments) > 0:
            recommendations.append("مراجعة شاملة لجميع المدفوعات للموردين المشتبه بهم")
            recommendations.append("طلب وثائق داعمة للفواتير المشكوك فيها")
        
        if len(shell_companies) > 0:
            recommendations.append("التحقق من السجلات التجارية للشركات المشتبه بها")
            recommendations.append("فحص العلاقات بين المساهمين والمديرين")
        
        if ml_analysis.get("red_flags"):
            recommendations.append("إعداد تقرير للجهات الرقابية عن المعاملات المشبوهة")
            recommendations.append("تعزيز إجراءات اعرف عميلك (KYC)")
        
        if fraud_networks:
            recommendations.append("إجراء تحقيق موسع في شبكات الاحتيال المكتشفة")
            recommendations.append("التنسيق مع الجهات القانونية للتحقيق الجنائي")
        
        # مستوى الثقة
        confidence = 0.9 - (len(all_red_flags) * 0.02)
        confidence = max(0.5, min(0.95, confidence))
        
        return ForensicInvestigationResult(
            investigation_id=f"FORENSIC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            investigation_date=datetime.now().isoformat(),
            total_transactions_analyzed=len(transactions) + len(payments),
            suspicious_transactions=suspicious_payments,
            fraud_networks=fraud_networks,
            money_flow_analysis=ml_analysis,
            red_flags=all_red_flags,
            recommendations=recommendations,
            overall_risk_score=overall_risk,
            confidence_level=confidence
        )
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        تنفيذ الوكيل على البيانات المقدمة
        
        Args:
            data: بيانات التحقيق
            
        Returns:
            تقرير التحقيق الجنائي
        """
        logger.info(f"Executing {self.name}...")
        
        try:
            result = self.generate_forensic_report(
                payments=data.get("payments", []),
                vendors=data.get("vendors", []),
                companies=data.get("companies", []),
                transactions=data.get("transactions", []),
                accounts=data.get("accounts", [])
            )
            
            # تحويل النتيجة إلى قاموس
            return {
                "investigation_id": result.investigation_id,
                "investigation_date": result.investigation_date,
                "total_transactions_analyzed": result.total_transactions_analyzed,
                "suspicious_transactions_count": len(result.suspicious_transactions),
                "suspicious_transactions": [
                    {
                        "transaction_id": st.transaction_id,
                        "amount": st.amount,
                        "date": st.date,
                        "parties": st.parties,
                        "fraud_type": st.fraud_type.value,
                        "risk_score": st.risk_score,
                        "indicators": st.indicators,
                        "description": st.description
                    }
                    for st in result.suspicious_transactions
                ],
                "fraud_networks": result.fraud_networks,
                "money_flow_analysis": result.money_flow_analysis,
                "red_flags": result.red_flags,
                "recommendations": result.recommendations,
                "overall_risk_score": result.overall_risk_score,
                "confidence_level": result.confidence_level,
                "agent": self.name,
                "version": self.version
            }
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
        "payments": [
            {"id": "PMT001", "vendor_id": "V001", "amount": 100000, "date": "2024-01-15"},
            {"id": "PMT002", "vendor_id": "V001", "amount": 150000, "date": "2024-01-20"},
            {"id": "PMT003", "vendor_id": "V001", "amount": 200000, "date": "2024-01-25"},
            {"id": "PMT004", "vendor_id": "V002", "amount": 50000, "date": "2024-02-01"},
        ],
        "vendors": [
            {"id": "V001", "name": "شركة الأمل للتجارة", "tax_id": "", "address": ""},
            {"id": "V002", "name": "مؤسسة النور", "tax_id": "123456", "address": "القاهرة"},
        ],
        "companies": [
            {
                "id": "C001",
                "name": "شركة الأفق الجديد",
                "establishment_date": "2024-01-01",
                "capital": 10000,
                "address": "شارع التحرير 100",
                "business_activity": "General Trading",
                "shareholders": [{"name": "Unknown"}]
            }
        ],
        "transactions": [
            {"id": "T001", "account_id": "ACC001", "from_party": "P1", "to_party": "P2", "amount": 45000, "type": "transfer"},
            {"id": "T002", "account_id": "ACC001", "from_party": "P1", "to_party": "P2", "amount": 48000, "type": "transfer"},
            {"id": "T003", "account_id": "ACC001", "from_party": "P1", "to_party": "P2", "amount": 49000, "type": "transfer"},
            {"id": "T004", "account_id": "ACC001", "from_party": "P2", "to_party": "P1", "amount": 140000, "type": "transfer"},
        ],
        "accounts": [
            {"id": "ACC001", "name": "حساب رئيسي", "type": "current"}
        ]
    }
    
    # تشغيل الوكيل
    agent = ForensicAccountingAgent()
    result = agent.execute(sample_data)
    
    print("=" * 80)
    print("Forensic Accounting Investigation Report")
    print("=" * 80)
    print(json.dumps(result, indent=2, ensure_ascii=False))
