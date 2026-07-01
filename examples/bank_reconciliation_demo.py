"""
مثال عملي: التسوية البنكية
Bank Reconciliation Demo
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.bank_agent.agent import BankAuditAgent
from datetime import datetime


def run_bank_reconciliation_demo():
    """تشغيل مثال التسوية البنكية"""
    
    print("=" * 60)
    print("🏦 مثال التسوية البنكية - Bank Reconciliation Demo")
    print("=" * 60)
    print()
    
    # إنشاء وكيل البنك
    bank_agent = BankAuditAgent()
    
    # بيانات الدفتر العام (الشركة)
    company_records = [
        {"id": "CHK001", "date": "2024-01-15", "description": "دفعة مورد", "amount": -15000, "balance": 185000},
        {"id": "DEP001", "date": "2024-01-16", "description": "إيداع عميل", "amount": 25000, "balance": 210000},
        {"id": "CHK002", "date": "2024-01-17", "description": "رواتب", "amount": -45000, "balance": 165000},
        {"id": "CHK003", "date": "2024-01-18", "description": "مصروفات", "amount": -8500, "balance": 156500},
        {"id": "DEP002", "date": "2024-01-19", "description": "إيرادات", "amount": 35000, "balance": 191500},
        {"id": "WTH001", "date": "2024-01-20", "description": "سحب آلي", "amount": -5000, "balance": 186500},
    ]
    
    # بيانات كشف الحساب البنكي
    bank_statement = [
        {"id": "BNK001", "date": "2024-01-15", "description": "تحويل خارجي", "amount": -15000, "balance": 185000},
        {"id": "BNK002", "date": "2024-01-16", "description": "إيداع نقدي", "amount": 25000, "balance": 210000},
        {"id": "BNK003", "date": "2024-01-17", "description": "شيك رواتب", "amount": -45000, "balance": 165000},
        {"id": "BNK004", "date": "2024-01-18", "description": "عمولة بنكية", "amount": -150, "balance": 164850},
        {"id": "BNK005", "date": "2024-01-19", "description": "تحويل وارد", "amount": 35000, "balance": 199850},
        {"id": "BNK006", "date": "2024-01-20", "description": "سحب ATM", "amount": -5000, "balance": 194850},
    ]
    
    print("📊 سجلات الشركة (الدفتر العام):")
    print("-" * 60)
    for rec in company_records:
        sign = "+" if rec["amount"] > 0 else ""
        print(f"  {rec['id']}: {sign}{rec['amount']:>10,} ريال - {rec['description']}")
    print(f"  الرصيد حسب الدفتر: {company_records[-1]['balance']:,.2f} ريال")
    print()
    
    print("🏦 كشف الحساب البنكي:")
    print("-" * 60)
    for stmt in bank_statement:
        sign = "+" if stmt["amount"] > 0 else ""
        print(f"  {stmt['id']}: {sign}{stmt['amount']:>10,} ريال - {stmt['description']}")
    print(f"  الرصيد حسب البنك: {bank_statement[-1]['balance']:,.2f} ريال")
    print()
    
    # التحليل والتسوية
    print("🔍 جاري تحليل الفروقات...")
    print()
    
    company_balance = company_records[-1]["balance"]
    bank_balance = bank_statement[-1]["balance"]
    difference = company_balance - bank_balance
    
    print("📋 ملخص الفروقات:")
    print("-" * 60)
    print(f"  الرصيد حسب الدفتر: {company_balance:>12,.2f} ريال")
    print(f"  الرصيد حسب البنك: {bank_balance:>12,.2f} ريال")
    print(f"  الفرق: {difference:>12,.2f} ريال")
    print()
    
    # تحديد بنود التسوية
    reconciling_items = []
    
    # عمولات بنكية غير مسجلة
    bank_fees = [s for s in bank_statement if "عمولة" in s["description"]]
    for fee in bank_fees:
        reconciling_items.append({
            "type": "عمولة بنكية غير مسجلة",
            "amount": fee["amount"],
            "adjustment": "deduct_from_company"
        })
    
    # شيكات تحت التحصيل
    # (في هذا المثال البسيط نفترض عدم وجودها)
    
    # إيداعات تحت التحصيل
    # (في هذا المثال البسيط نفترض عدم وجودها)
    
    # أخطاء في التسجيل
    # (في هذا المثال البسيط نفترض عدم وجودها)
    
    print("📝 بنود التسوية المطلوبة:")
    print("-" * 60)
    
    if not reconciling_items:
        print("  ✅ لا توجد بنود تسوية مطلوبة")
    else:
        for i, item in enumerate(reconciling_items, 1):
            sign = "+" if item["amount"] > 0 else ""
            print(f"  {i}. {item['type']}")
            print(f"     المبلغ: {sign}{item['amount']:,.2f} ريال")
            print(f"     التعديل: {'خصم من الدفتر' if item['adjustment'] == 'deduct_from_company' else 'إضافة للدفتر'}")
            print()
    
    # حساب الرصيد المعدل
    adjusted_company_balance = company_balance
    for item in reconciling_items:
        if item["adjustment"] == "deduct_from_company":
            adjusted_company_balance += item["amount"]  # amount is negative
    
    print("=" * 60)
    print("قائمة التسوية البنكية النهائية:")
    print("-" * 60)
    print(f"  الرصيد حسب الدفتر: {company_balance:>12,.2f} ريال")
    
    for item in reconciling_items:
        sign = "+" if item["amount"] > 0 else ""
        print(f"  {item['type']}: {sign}{abs(item['amount']):>10,.2f} ريال")
    
    print(f"  ─" * 30)
    print(f"  الرصيد المعدل: {adjusted_company_balance:>12,.2f} ريال")
    print(f"  الرصيد حسب البنك: {bank_balance:>12,.2f} ريال")
    print()
    
    if abs(adjusted_company_balance - bank_balance) < 1:
        print("✅ نجحت التسوية! الرصيدان متطابقان")
    else:
        print("⚠️ لا تزال هناك فروقات تحتاج مراجعة")
    
    print("=" * 60)
    
    return {
        "company_balance": company_balance,
        "bank_balance": bank_balance,
        "difference": difference,
        "reconciling_items": len(reconciling_items),
        "adjusted_balance": adjusted_company_balance,
        "reconciled": abs(adjusted_company_balance - bank_balance) < 1
    }


if __name__ == "__main__":
    result = run_bank_reconciliation_demo()
    
    print()
    print("📊 نتيجة التسوية:")
    print(f"  الحالة: {'متطابقة ✅' if result['reconciled'] else 'غير متطابقة ⚠️'}")
    print(f"  بنود التسوية: {result['reconciling_items']}")
