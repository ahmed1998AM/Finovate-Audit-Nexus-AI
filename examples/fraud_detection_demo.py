"""
مثال عملي: كشف الاحتيال
Fraud Detection Demo
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.fraud_agent.agent import FraudDetectionAgent
from datetime import datetime, timedelta


def run_fraud_detection_demo():
    """تشغيل مثال كشف الاحتيال"""
    
    print("=" * 60)
    print("🔍 مثال كشف الاحتيال - Fraud Detection Demo")
    print("=" * 60)
    print()
    
    # إنشاء وكيل كشف الاحتيال
    fraud_agent = FraudDetectionAgent()
    
    # معاملات تجريبية (بعضها مشبوه)
    sample_transactions = [
        {"id": "TXN001", "amount": 5000, "vendor": "شركة الأمل", "date": "2024-01-15", "category": "supplies"},
        {"id": "TXN002", "amount": 45000, "vendor": "مؤسسة النور", "date": "2024-01-15", "category": "equipment"},
        {"id": "TXN003", "amount": 4999, "vendor": "شركة الأمل", "date": "2024-01-16", "category": "supplies"},
        {"id": "TXN004", "amount": 4999, "vendor": "شركة الأمل", "date": "2024-01-17", "category": "supplies"},
        {"id": "TXN005", "amount": 150000, "vendor": "استشارات عالمية", "date": "2024-01-18", "category": "consulting"},
        {"id": "TXN006", "amount": 8500, "vendor": "مورد جديد LLC", "date": "2024-01-18", "category": "services"},
        {"id": "TXN007", "amount": 8500, "vendor": "مورد جديد LLC", "date": "2024-01-18", "category": "services"},
        {"id": "TXN008", "amount": 25000, "vendor": "شركة التقنية", "date": "2024-01-19", "category": "software"},
        {"id": "TXN009", "amount": 3000, "vendor": "مصروفات متنوعة", "date": "2024-01-20", "category": "misc"},
        {"id": "TXN010", "amount": 2999, "vendor": "مصروفات متنوعة", "date": "2024-01-20", "category": "misc"},
    ]
    
    print("📋 المعاملات قيد التحليل:")
    print("-" * 60)
    for tx in sample_transactions:
        print(f"  {tx['id']}: {tx['amount']:>10,} ريال - {tx['vendor']} ({tx['category']})")
    print()
    
    # تحليل الاحتيال
    print("🔍 جاري تحليل الأنماط المشبوهة...")
    print()
    
    flags = []
    
    # التحقق من التجزئة (Structuring)
    small_payments = [tx for tx in sample_transactions if 4900 <= tx["amount"] <= 5000]
    if len(small_payments) >= 2:
        flags.append({
            "type": "⚠️ تجزئة معاملات",
            "severity": "HIGH",
            "details": f"تم رصد {len(small_payments)} معاملات قريبة من حد 5000 ريال"
        })
    
    # التحقق من التكرار
    amount_counts = {}
    for tx in sample_transactions:
        key = (tx["amount"], tx["vendor"])
        amount_counts[key] = amount_counts.get(key, 0) + 1
    
    for (amount, vendor), count in amount_counts.items():
        if count >= 2:
            flags.append({
                "type": "🔄 معاملات مكررة",
                "severity": "MEDIUM",
                "details": f"{count} معاملات متطابقة: {amount} ريال لـ {vendor}"
            })
    
    # التحقق من المبالغ الكبيرة
    large_tx = [tx for tx in sample_transactions if tx["amount"] > 100000]
    for tx in large_tx:
        flags.append({
            "type": "💰 مبلغ كبير غير عادي",
            "severity": "HIGH",
            "details": f"مبلغ {tx['amount']:,} ريال لـ {tx['vendor']} في {tx['category']}"
        })
    
    # التحقق من الموردين الجدد
    new_vendors = [tx for tx in sample_transactions if "جديد" in tx["vendor"]]
    for tx in new_vendors:
        flags.append({
            "type": "🆼 مورد جديد",
            "severity": "LOW",
            "details": f"مورد جديد: {tx['vendor']} - مبلغ {tx['amount']:,} ريال"
        })
    
    # عرض النتائج
    print("🚨 المعاملات المشبوهة المكتشفة:")
    print("-" * 60)
    
    if not flags:
        print("  ✅ لا توجد معاملات مشبوهة")
    else:
        for i, flag in enumerate(flags, 1):
            severity_color = {
                "HIGH": "🔴",
                "MEDIUM": "🟡",
                "LOW": "🟢"
            }
            icon = severity_color[flag['severity']]
            print(f"  {i}. {icon} {flag['type']}")
            print(f"     الخطورة: {flag['severity']}")
            print(f"     التفاصيل: {flag['details']}")
            print()
    
    print()
    print("=" * 60)
    print("ملخص التحليل:")
    print("-" * 60)
    print(f"  إجمالي المعاملات: {len(sample_transactions)}")
    print(f"  عدد flags: {len(flags)}")
    
    high_severity = sum(1 for f in flags if f["severity"] == "HIGH")
    medium_severity = sum(1 for f in flags if f["severity"] == "MEDIUM")
    low_severity = sum(1 for f in flags if f["severity"] == "LOW")
    
    print(f"  🟥 عالية الخطورة: {high_severity}")
    print(f"  🟨 متوسطة الخطورة: {medium_severity}")
    print(f"  🟩 منخفضة الخطورة: {low_severity}")
    print()
    
    if high_severity > 0:
        print("❗ توصية: مراجعة فورية للمعاملات عالية الخطورة")
    elif medium_severity > 0:
        print("⚠️ توصية: إجراء تحقق إضافي من المعاملات المتوسطة")
    else:
        print("✅ التوصية:可以继续 المراقبة الروتينية")
    
    print("=" * 60)
    
    return {
        "total_transactions": len(sample_transactions),
        "total_flags": len(flags),
        "high_severity": high_severity,
        "medium_severity": medium_severity,
        "low_severity": low_severity,
        "risk_level": "HIGH" if high_severity > 0 else "MEDIUM" if medium_severity > 0 else "LOW"
    }


if __name__ == "__main__":
    result = run_fraud_detection_demo()
    
    print()
    print("📊 تقييم المخاطر النهائي:")
    print(f"  مستوى الخطورة: {result['risk_level']}")
    print(f"  يحتاج مراجعة: {'نعم' if result['high_severity'] > 0 else 'لا'}")
