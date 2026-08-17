# Finovate Audit Nexus AI 🚀

## Enterprise AI Financial Audit & Intelligence Platform

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![Tests](https://img.shields.io/badge/tests-724/724%20passing-brightgreen.svg)
![Desktop](https://img.shields.io/badge/desktop-PySide6-blueviolet.svg)
![Backend](https://img.shields.io/badge/backend-FastAPI-success.svg)
![Agents](https://img.shields.io/badge/agents-22%20AI-orange.svg)

---

## نظرة عامة

منصة سطح مكتب احترافية تعمل بالذكاء الاصطناعي متعدد الوكلاء (Multi-Agent AI System) متخصصة في المراجعة المالية والتدقيق وكشف الاحتيال والامتثال الضريبي، مع 22 وكيل ذكي و 15 موصل لأنظمة ERP.

### المميزات الأساسية
- تطبيق سطح مكتب PySide6 مع 11 صفحة واجهة
- خادم FastAPI مع نقاط نهاية `/api/v1/*`
- 22 وكيل AI (مراجعة، احتيال، امتثال، مخاطر، ...)
- 15 موصل ERP (SAP, Oracle, QuickBooks, Xero, ...)
- JWT Authentication + RBAC (6 أدوار، 25 صلاحية)
- WebSocket للاتصال المباشر مع البث الجماعي
- Webhook system للتكامل الخارجي
- Event Bus داخلي للتواصل بين الخدمات
- Caching layer (Redis + in-memory fallback)
- Task Queue للمهام غير المتزامنة
- Email/SMTP مع قوالب Jinja2 (عربي/إنجليزي)
- i18n تدويل ثنائي اللغة (عربي / English)
- TLS/HTTPS للإنتاج
- تقارير PDF/HTML/Excel
- **724 اختبار (0 fail)** — وحدات، تكامل، أداء، E2E
- **Ruff linting: 0 خطأ**

---

## المتطلبات

- Python 3.11+
- PySide6 (لواجهة سطح المكتب)
- FastAPI + Uvicorn (للخادم)
- SQLite (قاعدة بيانات افتراضية)

---

## التثبيت والتشغيل

```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل الخادم وسطح المكتب معاً
python main.py --all

# تشغيل سطح المكتب فقط
python main.py --desktop

# تشغيل الخادم فقط
python main.py --api

# تشغيل الاختبارات
python main.py --test
# أو
pytest tests/ -v
```

### Docker (Production)
```bash
# تشغيل النظام بالكامل (خلفية + قاعدة بيانات + Redis + واجهة)
docker-compose up -d

# أو بناء وتشغيل الخلفية فقط
docker build -t finovate-backend .
docker run -p 8000:8000 --env-file .env finovate-backend
```

### Quick Start (تطوير)
```bash
# 1. إعداد المفاتيح السرية
python -c "import secrets; open('.env','a').write(f'JWT_SECRET_KEY={secrets.token_hex(32)}\nENCRYPTION_KEY={secrets.token_hex(16)}\n')"

# 2. تثبيت المتطلبات
pip install -r requirements.txt

# 3. تشغيل الخادم
uvicorn backend.main:app --reload --port 8000

# 4. تشغيل الاختبارات
pytest -q
```

### API Documentation
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

---

## هيكل المشروع

```
Finovate-Audit-Nexus-AI/
├── main.py                    # نقطة دخول وحيدة
├── agents/                    # 22 وكيل ذكي
├── backend/
│   ├── main.py                # FastAPI app
│   ├── api/endpoints/         # نقاط نهاية API
│   ├── api/routes/            # مسارات إضافية
│   ├── services/              # منطق الأعمال
│   ├── orchestrator/          # تنسيق الوكلاء
│   ├── ai_engine/             # محرك LLM
│   ├── agents/                # فئات أساس الوكلاء
│   ├── database/              # إعداد DB + نماذج
│   └── security/              # الأمان والتشفير
├── connectors/                # 15 موصل ERP
├── frontend/
│   ├── main_window.py         # النافذة الرئيسية
│   ├── api_client.py          # عميل API موحد
│   ├── components/            # مكونات واجهة مشتركة
│   ├── dashboard/             # لوحة القيادة
│   ├── executive/             # لوحة تنفيذية
│   ├── reports/               # عارض التقارير
│   ├── audit_projects/        # مشاريع التدقيق
│   ├── agents/                # إدارة الوكلاء
│   ├── fraud/                 # كشف الاحتيال
│   ├── compliance/            # الامتثال
│   ├── connectors/            # إدارة الموصلات
│   ├── analytics/             # تحليلات
│   ├── settings/              # الإعدادات
│   ├── services/              # جلسة + مصادقة
│   └── styles/                # نظام التصميم
├── tests/                     # 159 اختبار
│   ├── unit/                  # 88 اختبار وحدة
│   ├── integration/           # 52 اختبار تكامل
│   ├── e2e/                   # 5 اختبار E2E
│   └── performance/           # 14 اختبار أداء
├── scripts/                   # بناء وتوزيع
├── docs/                      # وثائق
└── _archive/                  # ملفات قديمة (مؤرشفة)
```

---

## API Endpoints

| Method | Endpoint | الوصف |
|--------|----------|-------|
| POST | `/api/v1/auth/login` | تسجيل الدخول |
| POST | `/api/v1/auth/register` | تسجيل مستخدم جديد |
| GET | `/api/v1/auth/me` | معلومات المستخدم الحالي |
| POST | `/api/v1/auth/change-password` | تغيير كلمة المرور |
| GET | `/api/v1/audit/dashboard` | بيانات لوحة القيادة |
| GET | `/api/v1/audit/dashboard/summary-report` | تقرير ملخص |
| GET | `/api/v1/audit/dashboard/recommendations` | توصيات |
| GET | `/api/v1/audit-projects/` | قائمة مشاريع التدقيق |
| POST | `/api/v1/audit-projects/` | إنشاء مشروع |
| GET | `/api/v1/findings/` | نتائج المراجعة |
| GET/POST | `/api/v1/agents/` | إدارة الوكلاء |
| POST | `/api/v1/agents/execute` | تنفيذ وكيل |
| GET/POST | `/api/v1/reports` | إدارة التقارير |
| POST | `/api/v1/reports/create` | إنشاء تقرير |
| POST | `/api/v1/reports/{id}/summary` | ملخص تقرير |
| POST | `/api/v1/reports/{id}/export` | تصدير تقرير |
| GET/POST | `/api/v1/connectors` | إدارة الموصلات |
| DELETE | `/api/v1/connectors/{id}` | حذف موصل |
| POST | `/api/v1/documents/upload` | رفع مستند |
| POST | `/api/v1/audits/start` | بدء مراجعة |
| GET | `/api/v1/ai/providers` | مزودي AI |
| GET | `/api/v1/ai/status` | حالة AI |

---

## صفحات الواجهة (11 صفحة)

| الصفحة | المعرف | الوظيفة |
|--------|--------|---------|
| لوحة القيادة | `dashboard` | مؤشرات الأداء الرئيسية |
| القيادة التنفيذية | `executive` | KPIs + توصيات الإدارة العليا |
| التحليلات | `analytics` | تحليلات مالية سريعة |
| وكلاء AI | `agents` | إدارة وتشغيل الوكلاء |
| التقارير | `reports` | عرض وإنشاء وتصدير التقارير |
| إدارة AI | `ai_management` | إعداد مزودي LLM |
| الموصلات | `connectors` | إدارة موصلات ERP |
| مشاريع التدقيق | `audit_projects` | CRUD كامل للمشاريع |
| كشف الاحتيال | `fraud_detection` | تنبيهات وتحقيقات الاحتيال |
| الامتثال | `compliance` | معايير وتقارير الامتثال |
| الإعدادات | `settings` | إعدادات التطبيق والمظهر |

---

## الإحصائيات الحالية

| المقياس | القيمة |
|---------|--------|
| ملفات Python النشطة | ~180 ملف |
| أسطر الكود | ~35,000 سطر |
| وكلاء ذكية | 22/22 |
| موصلات ERP | 15/15 |
| صفحات الواجهة | 11/11 |
| اختبارات | **724/724 ناجحة** |
| API Endpoints | 25+ نقطة نهاية |
| خدمات Backend | 9 خدمات |

---

## المطور

**Ahmed Mostafa Ibrahim**
- Brand: **Finovate – AHMED EG**
- Email: gogom8870@gmail.com

---

© 2025 Ahmed Mostafa Ibrahim — All Rights Reserved

---
**ملاحظة للمطور:** لضمان نجاح بناء نسخة ويندوز، يرجى التأكد من تحديث ملف `.github/workflows/build.yml` لاستخدام **Python 3.10** كما هو موضح في تعليمات Manus.
 
Final Trigger
