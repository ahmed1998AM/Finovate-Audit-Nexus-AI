"""
مثال عملي: الامتثال الضريبي
Tax Compliance Demo
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.tax_agent.agent import TaxAgent
from backend.core.models import AuditProject, Document
from datetime import datetime


def run_tax_compliance_demo():
    """تشغيل مثال الامتثال الضريبي"""
    
    print("=" * 60)
    print("🧾 مثال الامتثال الضريبي - Tax Compliance Demo")
    print("=" * 60)
    print()
    
    # إنشاء وكيل الضرائب
    tax_agent = TaxAgent()
    
    # بيانات تجريبية
    sample_transactions = [
        {"id": 1, "type": "sale", "amount": 15000, "tax_rate": 0.15, "category": "goods"},
        {"id": 2, "type": "sale", "amount": 8500, "tax_rate": 0.15, "category": "services"},
        {"id": 3, "type": "purchase", "amount": 5000, "tax_rate": 0.15, "category": "raw_materials"},
        {"id": 4, "type": "sale", "amount": 22000, "tax_rate": 0.15, "category": "goods"},
        {"id": 5, "type": "purchase", "amount": 3200, "tax_rate": 0.15, "category": "equipment"},
    ]
    
    print("📋 المعاملات الضريبية:")
    print("-" * 60)
    for tx in sample_transactions:
        tax_amount = tx["amount"] * tx["tax_rate"]
        print(f"  #{tx['id']}: {tx['type']} - {tx['amount']:,.2f} ريال (ضريبة: {tax_amount:,.2f})")
    print()
    
    # حساب الالتزامات الضريبية
    print("🔍 جاري حساب الالتزامات الضريبية...")
    print()
    
    total_sales = sum(tx["amount"] for tx in sample_transactions if tx["type"] == "sale")
    total_purchases = sum(tx["amount"] for tx in sample_transactions if tx["type"] == "purchase")
    
    output_tax = total_sales * 0.15
    input_tax = total_purchases * 0.15
    net_tax = output_tax - input_tax
    
    print("📊 ملخص الحسابات الضريبية:")
    print("-" * 60)
    print(f"  إجمالي المبيعات: {total_sales:,.2f} ريال")
    print(f"  إجمالي المشتريات: {total_purchases:,.2f} ريال")
    print()
    print(f"  ضريبة المخرجات: {output_tax:,.2f} ريال")
    print(f"  ضريبة المدخلات: {input_tax:,.2f} ريال")
    print()
    print(f"  صافي الضريبة المستحقة: {net_tax:,.2f} ريال")
    print()
    
    # التحقق من الامتثال
    print("✅ جاري التحقق من الامتثال الضريبي...")
    print()
    
    compliance_checks = [
        ("جميع الفواتير مسجلة", True),
        ("نسب الضريبة صحيحة", True),
        ("تواريخ الفواتير صحيحة", True),
        ("الأصناف مصنفة بشكل صحيح", True),
        ("لا توجد فواتير مفقودة", True),
    ]
    
    all_passed = True
    for check, passed in compliance_checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("🎉 النتيجة: متوافق تماماً مع المتطلبات الضريبية!")
    else:
        print("⚠️ النتيجة: توجد مخالفات ضريبية تحتاج معالجة")
    
    print()
    print("=" * 60)
    print("تم الانتهاء من مثال الامتثال الضريبي")
    print("=" * 60)
    
    return {
        "total_sales": total_sales,
        "total_purchases": total_purchases,
        "output_tax": output_tax,
        "input_tax": input_tax,
        "net_tax": net_tax,
        "compliance_status": "compliant" if all_passed else "non-compliant"
    }


if __name__ == "__main__":
    result = run_tax_compliance_demo()
    
    print()
    print("📄 التقرير الضريبي:")
    print(f"  الحالة: {result['compliance_status']}")
    print(f"  الضريبة المستحقة: {result['net_tax']:,.2f} ريال")
