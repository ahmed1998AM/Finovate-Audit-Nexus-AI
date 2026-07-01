# هيكل المشروع — Finovate Audit Nexus AI

## نقطة الدخول
- `python main.py --desktop` — تطبيق سطح المكتب
- `python main.py --api` — خادم FastAPI
- `python main.py --all` — الخادم + التطبيق معاً

## المجلدات الرئيسية
| مجلد | الوظيفة |
|------|---------|
| `agents/` | 22 وكيل مراجعة ذكي |
| `backend/` | FastAPI، خدمات، orchestrator |
| `connectors/` | 15 موصل ERP |
| `frontend/` | PySide6 desktop UI |
| `frontend/services/` | جلسة، مصادقة |
| `frontend/executive/` | لوحة القيادة التنفيذية |
| `frontend/reports/` | عارض التقارير |
| `tests/` | 147 اختبار |
| `_archive/` | ملفات legacy (مثل `src/`) |

## API
جميع المسارات المحمية تحت `/api/v1/*` مع JWT.

## الإعدادات المحلية
`~/.finovate_audit/settings.json` — يتضمن `api_base_url`.
