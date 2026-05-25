# 🪟 دليل بناء تطبيق ويندوز

## Finovate Audit Nexus AI - Windows Build Guide

### 📋 نظرة عامة

يتم بناء تطبيق الويندوز تلقائياً باستخدام GitHub Actions عند كل push أو pull request. يمكن أيضاً تشغيل البناء يدوياً وإنشاء إصدارات رسمية.

---

## 🚀 التشغيل التلقائي

### محفزات البناء التلقائي:

1. **عند الدفع (Push)** إلى الفروع:
   - `main`
   - `master`
   - `develop`

2. **عند طلب السحب (Pull Request)** إلى:
   - `main`
   - `master`

3. **المسارات التي تُ触发 البناء**:
   ```
   src/**
   requirements.txt
   pyproject.toml
   .github/workflows/build_windows.yml
   ```

---

## 🔧 التشغيل اليدوي

### من خلال GitHub UI:

1. اذهب إلى **Actions** في مستودع GitHub
2. اختر **"Build Windows Executable"** من القائمة
3. اضغط على **"Run workflow"**
4. اختر الفرع المناسب
5. أدخل الإصدار (اختياري)، مثال: `1.0.0`
6. حدد **"Create release"** إذا أردت إنشاء إصدار رسمي
7. اضغط **"Run workflow"**

### مثال على إدخال اليدوي:

```yaml
Version number: 1.0.0
Create release: ✓ (محدد)
```

---

## 📦 مخرجات البناء

### الملفات التي يتم إنشاؤها:

| الملف | الوصف |
|-------|-------|
| `FinovateAuditNexus.exe` | التطبيق الرئيسي قابل للتنفيذ |
| `FinovateAuditNexus_portable.zip` | نسخة محمولة مضغوطة |
| `BUILD_INFO.txt` | معلومات البناء والإصدار |
| `SHA256SUMS.txt` | تجزئات SHA256 للتحقق من السلامة |
| `README.md` | دليل المستخدم |
| `LICENSE` | رخصة الاستخدام |
| `CHANGELOG.md` | سجل التغييرات |

### بيئات Python المدعومة:

- ✅ Python 3.10
- ✅ Python 3.11 (الافتراضي)
- ✅ Python 3.12

---

## 🛠️ تقنيات البناء

### الأدوات المستخدمة:

1. **PyInstaller** (الأساسي)
   - يحول تطبيق Python إلى exe مستقل
   - يتضمن جميع المكتبات المطلوبة
   - يدعم واجهة الرسومية (GUI)

2. **cx_Freeze** (بديل)
   - يُستخدم إذا فشل PyInstaller
   - بديل موثوق للبناء

3. **Chocolatey**
   - لتثبيت تبعيات النظام
   - vcredist-all
   - .NET 6.0 SDK

---

## 📊 خطوات البناء

### 1. إعداد البيئة
```bash
- تثبيت Python 3.10/3.11/3.12
- ترقية pip و setuptools
- تثبيت PyInstaller و cx_Freeze
```

### 2. تثبيت التبعيات
```bash
pip install -r requirements.txt
pip install -e .
```

### 3. تشغيل الاختبارات
```bash
pytest tests/ -v --cov=src
```

### 4. إنشاء ملف الإصدار
```python
__version__ = '1.0.0'
__build_date__ = '2024-01-25 10:30:00'
__commit_sha__ = 'abc123...'
```

### 5. البناء مع PyInstaller
```bash
pyinstaller --clean FinovateAuditNexus.spec
```

### 6. تنظيم الملفات
```
build_windows/
├── FinovateAuditNexus.exe
├── FinovateAuditNexus_portable.zip
├── BUILD_INFO.txt
├── SHA256SUMS.txt
├── README.md
├── LICENSE
└── CHANGELOG.md
```

### 7. رفع الملفات
- يتم رفع الملفات كـ artifacts
- متاحة للتحميل لمدة 30 يوم

---

## 🎯 إنشاء إصدار رسمي

### عند تحديد "Create release":

1. **تنزيل جميع الملفات** من artifacts
2. **إنشاء ملاحظات الإصدار** تلقائياً
3. **رفع الملفات** إلى GitHub Releases
4. **إنشاء tag** بالإصدار المحدد
5. **نشر الإعلان** عن الإصدار الجديد

### مثال على إصدار:

```
Tag: v1.0.0
Name: Finovate Audit Nexus AI v1.0.0
Files:
  - FinovateAuditNexus.exe (250 MB)
  - FinovateAuditNexus_portable.zip (200 MB)
  - SHA256SUMS.txt
  - BUILD_INFO.txt
```

---

## 🔐 التحقق من السلامة

### التحقق من التجزئات:

```powershell
# في PowerShell
Get-FileHash FinovateAuditNexus.exe -Algorithm SHA256

# مقارنة مع SHA256SUMS.txt
certutil -hashfile FinovateAuditNexus.exe SHA256
```

### التأكد من التوقيع:

إذا تم توقيع التطبيق رقمياً:
```powershell
sigcheck.exe FinovateAuditNexus.exe
```

---

## ⚙️ متطلبات النظام

### الحد الأدنى:

- **نظام التشغيل**: Windows 10/11 (64-bit)
- **المعالج**: Intel i5 أو ما يعادله
- **الذاكرة**: 8 GB RAM
- **التخزين**: 2 GB مساحة حرة
- **.NET Framework**: 6.0 (مضمن)

### الموصى به:

- **نظام التشغيل**: Windows 11 (64-bit)
- **المعالج**: Intel i7 أو AMD Ryzen 7
- **الذاكرة**: 16 GB RAM
- **التخزين**: 5 GB SSD
- **كرت شاشة**: DirectX 11 compatible

---

## 🐛 استكشاف الأخطاء

### مشاكل شائعة وحلولها:

#### 1. فشل البناء مع PyInstaller
```yaml
الحل: سيتم استخدام cx_Freeze تلقائياً كبديل
```

#### 2. نقص في الذاكرة
```yaml
الحل: زيادة موارد runner في GitHub Actions
أو البناء المحلي باستخدام نفس الإعدادات
```

#### 3. مكتبات مفقودة
```yaml
الحل: إضافة المكتبة إلى hiddenimports في spec file
```

#### 4. خطأ في التبعيات
```bash
# إعادة تثبيت التبعيات
pip uninstall -y -r requirements.txt
pip install -r requirements.txt
```

---

## 🏗️ البناء المحلي

### للمطورين الذين يريدون البناء محلياً:

```bash
# 1. تثبيت الأدوات
pip install pyinstaller==6.3.0
pip install cx_Freeze==7.0.0

# 2. إنشاء ملف spec
python -m PyInstaller.utils.make_main_module_spec src/main.py

# 3. تعديل الملف وإضافة الإعدادات

# 4. البناء
pyinstaller --clean FinovateAuditNexus.spec

# 5. اختبار التطبيق
./dist/FinovateAuditNexus.exe
```

---

## 📈 التحسينات المستقبلية

### مخطط لها:

- [ ] إضافة توقيع رقمي للكود
- [ ] دعم MSI Installer
- [ ] تحديث تلقائي للتطبيق
- [ ] بناء لنسخة 32-bit
- [ ] دعم Windows Server
- [ ] تحسين حجم الملف النهائي
- [ ] إضافة اختبارات أداء للبناء

---

## 📞 الدعم

للحصول على المساعدة:

- **GitHub Issues**: https://github.com/your-repo/issues
- **الوثائق**: https://github.com/your-repo/wiki
- **البريد**: support@finovate-audit.com

---

## 📝 الترخيص

MIT License - راجع ملف LICENSE للتفاصيل.

---

**🎉 Finovate Audit Nexus AI - جاهز للاستخدام على ويندوز!**
