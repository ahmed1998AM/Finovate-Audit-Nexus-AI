# دليل بناء Finovate Audit Nexus AI لجميع المنصات

لقد تم تجهيز المستودع لدعم البناء التلقائي واليدوي لأنظمة **Windows** و **Linux** و **macOS**.

## 1. البناء التلقائي عبر GitHub Actions
لقد قمت بإعداد ملف `multi_platform_build.yml` في مجلد `.github/workflows`. هذا الملف يقوم بما يلي:
- بناء نسخة `.exe` للويندوز.
- بناء نسخة تنفيذية للينكس.
- بناء نسخة `.app` للماك.
- إنشاء **GitHub Release** تلقائياً عند إضافة Tag جديد (مثل `v1.0.0`) أو تشغيل البناء يدوياً.

> **ملاحظة هامة**: نظراً لقيود الأمان، يجب عليك رفع ملف `.github/workflows/multi_platform_build.yml` يدوياً إلى المستودع عبر موقع GitHub أو باستخدام صلاحيات الـ Workflow الخاصة بك.

## 2. البناء اليدوي (Local Build)
يمكنك استخدام السكربتات الموجودة في مجلد `scripts/` لبناء المشروع محلياً على جهازك:

### نظام Windows
قم بتشغيل الملف التالي في Terminal:
```cmd
scripts\build_windows.bat
```

### نظام Linux
قم بتشغيل الأوامر التالية:
```bash
chmod +x scripts/build_linux.sh
./scripts/build_linux.sh
```

### نظام macOS
قم بتشغيل الأوامر التالية:
```bash
chmod +x scripts/build_macos.sh
./scripts/build_macos.sh
```

## المتطلبات التقنية للبناء:
- **Python 3.11+**
- **PyInstaller** (يتم تثبيته تلقائياً عبر السكربتات)
- المكتبات الموجودة في `requirements.txt`

## المخرجات:
ستجد النسخ النهائية في مجلد `dist/` بعد اكتمال عملية البناء.
