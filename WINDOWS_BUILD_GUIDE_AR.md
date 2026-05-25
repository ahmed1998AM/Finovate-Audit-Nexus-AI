# 🪟 دليل بناء تطبيق الويندوز
# Windows Build Guide - Finovate Audit Nexus AI

## 📋 المحتويات

1. [نظرة عامة](#نظرة-عامة)
2. [المتطلبات](#المتطلبات)
3. [البناء التلقائي عبر GitHub Actions](#البناء-التلقائي)
4. [البناء اليدوي المحلي](#البناء-اليدوي-المحلي)
5. [استكشاف الأخطاء](#استكشاف-الأخطاء)
6. [الأسئلة الشائعة](#الأسئلة-الشائعة)

---

## نظرة عامة

يتم بناء تطبيق الويندوز باستخدام **GitHub Actions** تلقائياً عند كل push أو يمكن تشغيله يدوياً.

### الميزات:
- ✅ بناء تلقائي لـ Python 3.10, 3.11, 3.12
- ✅ استخدام PyInstaller و cx_Freeze
- ✅ إنشاء نسخة محمولة (Portable)
- ✅ تواقيع SHA256 للأمان
- ✅ إصدارات GitHub Releases تلقائية

---

## المتطلبات

### للبناء التلقائي (GitHub):
- حساب GitHub
- صلاحيات write على المستودع
- لا حاجة لأي إعدادات إضافية

### للبناء المحلي:
```bash
# Windows 10/11 (64-bit)
Python 3.10-3.12
pip install pyinstaller==6.3.0
pip install cx_Freeze==7.0.0
```

---

## البناء التلقائي

### التشغيل التلقائي:
```bash
git add .
git commit -m "feat: new feature"
git push origin main
```

سيبدأ البناء تلقائياً خلال دقائق.

### التشغيل اليدوي من GitHub:

1. اذهب إلى **Actions** tab
2. اختر **"Build Windows Executable"**
3. اضغط **"Run workflow"**
4. أدخل الإصدار (مثال: `1.0.0`)
5. حدد **"Create release"** إذا أردت
6. اضغط **"Run workflow"**

![Run Workflow](https://docs.github.com/assets/images/help/repository/workflow-dispatch.png)

---

## البناء اليدوي المحلي

### الخطوة 1: تثبيت المتطلبات
```powershell
# Windows PowerShell
python -m pip install --upgrade pip
pip install -r requirements-windows.txt
pip install pyinstaller==6.3.0
pip install cx_Freeze==7.0.0
```

### الخطوة 2: إنشاء ملف الإصدار
```powershell
$version = "1.0.0"
$buildDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$commitSha = git rev-parse HEAD

@"
__version__ = '$version'
__build_date__ = '$buildDate'
__commit_sha__ = '$commitSha'
__app_name__ = 'FinovateAuditNexus'
"@ | Out-File -FilePath "src/version.py" -Encoding UTF8
```

### الخطوة 3: البناء بـ PyInstaller
```powershell
pyinstaller --onefile --windowed --name FinovateAuditNexus src/main.py
```

### الخطوة 4: البناء البديل بـ cx_Freeze
```powershell
python setup_freeze.py build
```

### الخطوة 5: تجميع الملفات
```powershell
New-Item -ItemType Directory -Force -Path "dist_final"
Copy-Item "dist/*" -Destination "dist_final/" -Recurse
Copy-Item "README.md", "LICENSE", "CHANGELOG.md" -Destination "dist_final/"
Compress-Archive -Path "dist_final/*" -DestinationPath "FinovateAuditNexus_portable.zip"
```

---

## استكشاف الأخطاء

### ❌ خطأ: `sap-hana-client` غير متوفر

**السبب:** الحزمة غير متوفرة لـ Windows/Python 3.10+

**الحل:**
```yaml
# تم استبعادها تلقائياً في requirements-windows.txt
#或使用 متغيرات البيئة:
SET SKIP_SAP=true
pip install -r requirements-windows.txt
```

### ❌ خطأ: `cx-Oracle` يتطلب Oracle Client

**السبب:** يحتاج إلى تثبيت Oracle Client منفصلاً

**الحل:**
```powershell
# تجاوز الحزمة للبناء الأساسي
pip install -r requirements-windows.txt
# Oracle connector اختياري للاستخدام الإنتاجي
```

### ❌ خطأ: الذاكرة غير كافية أثناء البناء

**السبب:** PyInstaller يحتاج ذاكرة كبيرة

**الحل:**
```powershell
# زيادة صفحة الملف
[System.Environment]::SetEnvironmentVariable("PYTHONMALLOC", "malloc", "User")
# أو استخدام cx_Freeze بدلاً من ذلك
python setup_freeze.py build
```

### ❌ خطأ: timeout أثناء تثبيت vcredist

**الحل:** تم إزالة تثبيت vcredist من workflow
- التطبيق لا يحتاج Visual C++ redistributables
- Pure Python build لا يتطلب هذه المكتبات

---

## الأسئلة الشائعة

### س: كم يستغرق البناء؟
**ج:** 10-25 دقيقة حسب حجم التغييرات

### س: أين أجد الملفات المبنية؟
**ج:** 
- في GitHub: **Actions** → اختر الـ workflow → **Artifacts**
- محلياً: مجلد `dist/` أو `build/`

### س: ما الفرق بين النسخة المحمولة والعادية؟
**ج:**
- **المحمولة (Portable):** ZIP واحد، لا يحتاج تثبيت
- **العادية:** مثبت كامل مع اختصارات وسجل

### س: كيف أضيف connectors إضافية؟
**ج:** عدّل `requirements-windows.txt` وأعد البناء

### س: هل يدعم Windows 7/8؟
**ج:** لا، فقط Windows 10/11 (64-bit)

---

## 📞 الدعم

للأسئلة والمشاكل:
- 📧 support@finovate-audit.com
- 💬 GitHub Issues
- 📚 [التوثيق الكامل](./docs/)

---

**🎉 جاهز للاستخدام!**

Finovate Audit Nexus AI v1.0.0
Enterprise AI Financial Audit Platform
