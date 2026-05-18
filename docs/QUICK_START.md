# Finovate Audit Nexus AI - دليل البدء السريع

## 🚀 التثبيت السريع

### 1. تثبيت المتطلبات الأساسية

```bash
# إنشاء بيئة افتراضية (مستحسن)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate  # Windows

# تثبيت المكتبات
pip install -r requirements.txt
```

### 2. إعداد البيئة

```bash
# نسخ ملف الإعدادات
cp .env.example .env

# تحرير ملف .env وإضافة مفاتيح API الخاصة بك
# على الأقل أضف مفتاح واحد للذكاء الاصطناعي
```

### 3. تشغيل التطبيق

```bash
# تشغيل واجهة سطح المكتب
python main.py

# أو تشغيل الخلفية فقط
python -m backend.core.config
```

## 📋 المكونات الرئيسية

### الوكلاء الذكية المتاحة

| الوكيل | الوظيفة | الحالة |
|--------|---------|--------|
| Chief Agent | رئيس الوكلاء | ✅ جاهز |
| Journal Agent | مراجعة قيود اليومية | ✅ جاهز |
| Ledger Agent | مراجعة دفتر الأستاذ | ✅ جاهز |
| TB Agent | مراجعة ميزان المراجعة | ✅ جاهز |
| Tax Agent | المراجعة الضريبية | ✅ جاهز |
| Fraud Agent | كشف الاحتيال | ✅ جاهز |
| OCR Agent | معالجة المستندات | ⏳ قيد التطوير |
| Bank Agent | مراجعة البنوك | ⏳ قيد التطوير |

### خطوات التشغيل الأولى

1. **تحميل البيانات**
   - ملفات Excel: `uploads/journal_entries.xlsx`
   - ملفات PDF: `uploads/invoices.pdf`

2. **تشغيل المراجعة**
   ```python
   from agents.journal_agent.agent import JournalEntryAuditAgent
   import pandas as pd
   
   agent = JournalEntryAuditAgent()
   data = pd.read_excel("uploads/journal_entries.xlsx")
   results = await agent.analyze_journal_entries(data)
   ```

3. **عرض النتائج**
   ```python
   print(agent.generate_findings_report(results))
   ```

## 🔧 التكوين المتقدم

### إضافة مزود ذكاء اصطناعي

في ملف `.env`:

```env
# OpenAI
OPENAI_API_KEY="sk-..."

# أو Ollama محلي
OLLAMA_HOST="http://localhost:11434"
OLLAMA_MODEL="llama3"
```

### تفعيل وصلات ERP

```env
SAP_ENABLED=true
ORACLE_ENABLED=false
ODOO_ENABLED=true
```

## 📊 هيكل الملفات

```
Finovate_Audit_Nexus_AI/
├── agents/              # الوكلاء الذكية
│   ├── journal_agent/   # مراجعة القيود
│   ├── ledger_agent/    # مراجعة الأستاذ
│   ├── tax_agent/       # الضرائب
│   └── ...
├── backend/             # الخلفية
│   ├── core/           # النواة
│   ├── orchestrator/   # التنسيق
│   └── ...
├── connectors/          # وصلات ERP
├── frontend/            # الواجهة
├── uploads/            # الملفات المرفوعة
├── exports/            # التقارير المُصدرة
└── docs/               # الوثائق
```

## 🆘 حل المشاكل

### مشكلة: خطأ في استيراد PySide6
```bash
pip uninstall PySide6
pip install PySide6==6.6.0
```

### مشكلة: خطأ في قاعدة البيانات
```bash
mkdir -p database
touch database/finovate.db
```

### مشكلة: وكيل لا يعمل
تحقق من تسجيل الوكيل في Orchestrator:
```python
from backend.orchestrator.agent_orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()
print(orchestrator.get_registered_agents())
```

## 📞 الدعم

- **المطور**: Ahmed Mostafa Ibrahim
- **البريد**: gogom8870@gmail.com
- **الهاتف**: 01225155329

## 🔗 روابط مفيدة

- [دليل التثبيت الكامل](SETUP_GUIDE.md)
- [وثائق API](api_docs.md)
- [أمثلة الاستخدام](examples/)

---

**Finovate – AHMED EG** © 2025
