# دليل النشر على GitHub Actions
# GitHub Actions Deployment Guide

## نظرة عامة | Overview

تم إعداد المشروع للنشر التلقائي على GitHub Actions مع اختبارات شاملة وبناء Docker.

The project is configured for automatic deployment on GitHub Actions with comprehensive testing and Docker build.

## الملفات المهيأة | Configured Files

### 1. CI/CD Workflow (`.github/workflows/ci_cd.yml`)

يحتوي على الخطوات التالية:
- اختبار على Python 3.10, 3.11, 3.12
- فحص الكود بـ flake8
- تشغيل الاختبارات بـ pytest
- رفع تغطية الكود إلى Codecov
- بناء صورة Docker
- فحص أمني بـ safety و bandit

Contains:
- Testing on Python 3.10, 3.11, 3.12
- Code linting with flake8
- Running tests with pytest
- Uploading code coverage to Codecov
- Building Docker image
- Security scanning with safety and bandit

### 2. متطلبات البناء | Build Requirements

**requirements.txt** - محدّث للعمل مع GitHub Actions:
- إصدارات متوافقة مع numpy >= 1.26.0, < 2.0.0
- openpyxl >= 3.1.2, < 3.2.0
- PySide6 معطّل في CI/CD (اختياري)

### 3. Dockerfile

مُحسّن للبناء في GitHub Actions:
- مرحلة بناء منفصلة
- مستخدم غير جذر للأمان
- فحص صحي مدمج

## الإعداد | Setup

### 1. إضافة الأسرار | Add Secrets

في GitHub Repository → Settings → Secrets and variables → Actions:

```bash
DOCKER_USERNAME=your_docker_username
DOCKER_PASSWORD=your_docker_access_token
```

### 2. تشغيل يدوي | Manual Trigger

يمكن تشغيل الـ workflow يدوياً من خلال:
```yaml
workflow_dispatch:
```

## الأوامر | Commands

### بناء محلي | Local Build

```bash
# Linux/macOS
./scripts/build.sh all

# أو يدوياً | Or manually
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/ -v
python setup.py sdist bdist_wheel
```

### بناء Docker محلي | Local Docker Build

```bash
docker build -t finovate-audit-nexus:latest .
docker-compose up -d
```

## التحقق | Verification

بعد الدفع إلى GitHub:

1. ✅ تحقق من تبويب "Actions"
2. ✅ انتظر اكتمال الـ workflow
3. ✅ تحقق من نجاح جميع الاختبارات
4. ✅ تحقق من بناء Docker
5. ✅ تحقق من تقارير الأمان

## استكشاف الأخطاء | Troubleshooting

### فشل الاختبارات
```bash
python -m pytest tests/ -v --tb=short
```

### مشاكل التبعيات
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --force-reinstall
```

### فشل بناء Docker
```bash
docker build --no-cache -t finovate-audit-nexus:latest .
```

## الحالة | Status

| المكون | الحالة |
|--------|--------|
| CI/CD Workflow | ✅ جاهز |
| requirements.txt | ✅ محدّث |
| Dockerfile | ✅ مُحسّن |
| scripts/build.sh | ✅ جاهز |
| .gitignore | ✅ محدّث |
| setup.py | ✅ جاهز |
| MANIFEST.in | ✅ جاهز |

##下一步 | Next Steps

1. اربط المستودع بـ GitHub
2. أضف الأسرار المطلوبة
3. ادفع التغييرات
4. راقب عملية البناء في Actions

---

**Finovate Audit Nexus AI v1.0.0**
جاهز للنشر! 🚀
Ready for deployment! 🚀
