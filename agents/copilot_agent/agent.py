"""
Finovate Audit Nexus AI - AI Copilot Agent
المساعد الذكي للتدقيق المالي
"""
from datetime import datetime
from typing import Any, Dict


class AICopilotAgent:
    """
    مساعد مالي ذكي يجيب على الأسئلة ويقدم التوصيات
    """

    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        self.conversation_history = []

    def _load_knowledge_base(self) -> Dict:
        """تحميل قاعدة المعرفة بالمعايير والقوانين"""
        return {
            "vat_egypt": {
                "rate": 0.14,
                "description": "ضريبة القيمة المضافة في مصر 14%",
                "exemptions": ["الخدمات التعليمية", "الخدمات الطبية", "السلع الأساسية"],
                "law": "قانون الضريبة على القيمة المضافة رقم 67 لسنة 2016"
            },
            "income_tax_brackets": {
                "brackets": [
                    {"min": 0, "max": 15000, "rate": 0},
                    {"min": 15000, "max": 30000, "rate": 0.10},
                    {"min": 30000, "max": 45000, "rate": 0.15},
                    {"min": 45000, "max": 60000, "rate": 0.20},
                    {"min": 60000, "max": 200000, "rate": 0.25},
                    {"min": 200000, "max": 400000, "rate": 0.275},
                    {"min": 400000, "max": None, "rate": 0.30}
                ],
                "law": "قانون ضريبة الدخل رقم 91 لسنة 2005"
            },
            "ifrs_standards": {
                "IFRS_1": "أول تطبيق للمعايير الدولية للتقارير المالية",
                "IFRS_2": "المدفوعات القائمة على الأسهم",
                "IFRS_9": "الأدوات المالية",
                "IFRS_15": "الإيرادات من العقود مع العملاء",
                "IFRS_16": "الإيجارات"
            },
            "fraud_indicators": [
                "قيود يومية يدوية في نهاية الفترة",
                "تعديلات متكررة على القيود",
                "حركات غير عادية في الحسابات",
                "فروقات كبيرة في الجرد",
                "مستندات ناقصة أو غير مكتملة"
            ]
        }

    def ask(self, question: str) -> Dict[str, Any]:
        """
        الإجابة على سؤال المستخدم
        """
        question_lower = question.lower()
        self.conversation_history.append({
            "role": "user",
            "content": question,
            "timestamp": datetime.now()
        })

        # تطبيع النص العربي
        import re
        normalized = re.sub(r'[ًٌٍَُِّْ~`]', '', question_lower)
        normalized = normalized.replace('ة', 'ه').replace('ى', 'ي').replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')

        # كلمات مفتاحية منفصلة للبحث
        has_vat = any(k in normalized for k in ["ضريبه", "vat"]) and any(k in normalized for k in ["قيمه", "مضافه", "value"])
        has_income_tax = "ضريبه" in normalized and ("دخل" in normalized or "income" in normalized or "شريحه" in normalized)
        has_ifrs = any(k in normalized for k in ["معيار", "ifrs", "ias", "المعايير"])
        has_fraud = any(k in normalized for k in ["احتيال", "fraud", "كشف", "مؤشر", "غش", "تلاعب"])
        has_ratio = any(k in normalized for k in ["نسبه", "ratio", "تحليل", "النسب", "نسبة"])

        if has_vat:
            answer = self._answer_vat_question(question)
        elif has_income_tax:
            answer = self._answer_income_tax_question(question)
        elif has_ifrs:
            answer = self._answer_ifrs_question(question)
        elif has_fraud:
            answer = self._answer_fraud_question(question)
        elif has_ratio:
            answer = self._answer_ratio_question(question)

        else:
            answer = {
                "answer": "عذراً، لم أفهم السؤال تماماً. يمكنك سؤالي عن:\n" +
                         "- ضريبة القيمة المضافة المصرية\n" +
                         "- شرائح ضريبة الدخل\n" +
                         "- المعايير المحاسبية IFRS\n" +
                         "- مؤشرات كشف الاحتيال\n" +
                         "- النسب المالية والتحليل",
                "confidence": 0.5,
                "sources": []
            }

        self.conversation_history.append({
            "role": "assistant",
            "content": answer.get("answer", ""),
            "timestamp": datetime.now()
        })

        return answer

    def _answer_vat_question(self, question: str) -> Dict:
        """الإجابة على أسئلة VAT"""
        vat_info = self.knowledge_base["vat_egypt"]

        return {
            "answer": f"""
📌 ضريبة القيمة المضافة في مصر:

✅ المعدل الحالي: {vat_info['rate'] * 100}%

📜 القانون: {vat_info['law']}

🔸 السلع والخدمات المعفاة:
{chr(10).join('• ' + item for item in vat_info['exemptions'])}

💡 مثال عملي:
إذا كانت قيمة السلعة 1000 جنيه:
- صافي القيمة: 1000 جنيه
- ضريبة القيمة المضافة (14%): {1000 * vat_info['rate']:.2f} جنيه
- الإجمالي: {1000 * (1 + vat_info['rate']):.2f} جنيه
            """.strip(),
            "confidence": 0.95,
            "sources": [vat_info['law']],
            "related_topics": ["الإقرارات الضريبية", "الفواتير الإلكترونية", "الخصم الضريبي"]
        }

    def _answer_income_tax_question(self, question: str) -> Dict:
        """الإجابة على أسئلة ضريبة الدخل"""
        brackets = self.knowledge_base["income_tax_brackets"]["brackets"]

        bracket_text = ""
        for i, b in enumerate(brackets):
            max_val = b['max'] if b['max'] else "فما فوق"
            bracket_text += f"{i+1}. من {b['min']:,.0f} إلى {max_val}: {b['rate']*100}%\n"

        return {
            "answer": f"""
📌 شرائح ضريبة الدخل في مصر (للأفراد):

{bracket_text}
📜 القانون: {self.knowledge_base['income_tax_brackets']['law']}

💡 لحساب الضريبة:
يتم تطبيق كل شريحة على الجزء الواقع في نطاقها فقط (نظام تصاعدي).

مثال: لدخل سنوي 50,000 جنيه:
- أول 15,000: معفى
- من 15,000 إلى 30,000 (15,000 × 10%): 1,500 جنيه
- من 30,000 إلى 45,000 (15,000 × 15%): 2,250 جنيه
- من 45,000 إلى 50,000 (5,000 × 20%): 1,000 جنيه
- إجمالي الضريبة: 4,750 جنيه
            """.strip(),
            "confidence": 0.95,
            "sources": [self.knowledge_base['income_tax_brackets']['law']],
            "related_topics": ["الخصومات المسموحة", "الإقرار الضريبي", "الضريبة النهائية"]
        }

    def _answer_ifrs_question(self, question: str) -> Dict:
        """الإجابة على أسئلة المعايير المحاسبية"""
        standards = self.knowledge_base["ifrs_standards"]

        # البحث عن معيار محدد
        for code in standards.keys():
            if code.lower() in question.lower():
                return {
                    "answer": f"📌 {code}\n\n{standards[code]}",
                    "confidence": 0.9,
                    "sources": ["International Financial Reporting Standards"],
                    "related_topics": list(standards.keys())
                }

        # عرض جميع المعايير
        standards_list = "\n".join([f"• {k}: {v}" for k, v in standards.items()])

        return {
            "answer": f"""
📌 المعايير الدولية للتقارير المالية (IFRS):

{standards_list}

💡 اذكر رقم المعيار للحصول على تفاصيل أكثر (مثال: IFRS 15)
            """.strip(),
            "confidence": 0.8,
            "sources": ["IFRS Foundation"],
            "related_topics": ["المعايير المصرية", "التطبيق العملي", "الاختلافات المحلية"]
        }

    def _answer_fraud_question(self, question: str) -> Dict:
        """الإجابة على أسئلة كشف الاحتيال"""
        indicators = self.knowledge_base["fraud_indicators"]

        indicators_text = "\n".join([f"⚠️ {item}" for item in indicators])

        return {
            "answer": f"""
🚨 مؤشرات كشف الاحتيال المالي:

{indicators_text}

💡 توصيات للوقاية:
1. تطبيق نظام المراجعة المستمرة
2. فصل المهام والصلاحيات
3. مراجعة القيود اليدوية
4. تحليل الأنماط غير العادية
5. إجراء جرد مفاجئ

يمكنك استخدام وكيل Fraud Detection Agent للكشف التلقائي.
            """.strip(),
            "confidence": 0.9,
            "sources": ["Association of Certified Fraud Examiners"],
            "related_topics": ["التحقيق الجنائي", "Forensic Accounting", "Internal Controls"]
        }

    def _answer_ratio_question(self, question: str) -> Dict:
        """الإجابة على أسئلة النسب المالية"""
        return {
            "answer": """
📊 النسب المالية الرئيسية:

🔹 نسب السيولة:
• النسبة الجارية = الأصول المتداولة / الخصوم المتداولة
• النسبة السريعة = (الأصول المتداولة - المخزون) / الخصوم المتداولة

🔹 نسب الربحية:
• هامش الربح الصافي = صافي الدخل / الإيرادات
• العائد على الأصول (ROA) = صافي الدخل / إجمالي الأصول
• العائد على حقوق الملكية (ROE) = صافي الدخل / حقوق الملكية

🔹 نسب المديونية:
• نسبة الدين إلى الأصول = إجمالي الديون / إجمالي الأصول
• تغطية الفائدة = الأرباح قبل الفوائد والضرائب / مصروفات الفائدة

🔹 نسب الكفاءة:
• دوران المخزون = تكلفة البضاعة المباعة / متوسط المخزون
• دوران المدينين = المبيعات الآجلة / متوسط المدينين

استخدم Financial Statements Agent لحساب هذه النسب تلقائياً.
            """.strip(),
            "confidence": 0.85,
            "sources": ["Financial Analysis Best Practices"],
            "related_topics": ["Beneish M-Score", "Altman Z-Score", "التحليل الرأسي والأفقي"]
        }

    def get_conversation_summary(self) -> str:
        """تلخيص المحادثة الحالية"""
        if not self.conversation_history:
            return "لا توجد محادثة حالياً"

        summary = "📝 ملخص المحادثة:\n\n"
        for i, msg in enumerate(self.conversation_history[-10:], 1):  # آخر 10 رسائل
            role = "👤 أنت" if msg['role'] == 'user' else "🤖 المساعد"
            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            summary += f"{i}. {role}: {content}\n"

        return summary

    def clear_history(self):
        """مسح سجل المحادثة"""
        self.conversation_history = []


# مثال للاستخدام
if __name__ == "__main__":
    copilot = AICopilotAgent()

    print("="*60)
    print("🤖 Finovate AI Copilot - المساعد المالي الذكي")
    print("="*60)

    questions = [
        "ما هي ضريبة القيمة المضافة في مصر؟",
        "كيف تحسب ضريبة الدخل لشريحة 50000 جنيه؟",
        "ما هو معيار IFRS 15؟",
        "ما هي مؤشرات كشف الاحتيال المالي؟",
        "كيف أحسب النسبة الجارية؟"
    ]

    for q in questions:
        print(f"\n❓ السؤال: {q}")
        print("-" * 60)
        response = copilot.ask(q)
        print(response['answer'])
        print(f"\n🎯 درجة الثقة: {response['confidence']*100:.0f}%")
        print("="*60)

    print("\n" + copilot.get_conversation_summary())
