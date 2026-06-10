# Finovate Audit Nexus AI - Desktop Application Guide
# دليل تطبيق سطح المكتب - Finovate Audit Nexus AI

## Introduction | مقدمة
The desktop application provides a robust, professional environment for financial auditors to perform AI-driven analysis directly on their workstations. It integrates the power of 22 AI agents with a modern web-integrated dashboard.

يوفر تطبيق سطح المكتب بيئة احترافية قوية للمراجعين الماليين لإجراء تحليلات مدعومة بالذكاء الاصطناعي مباشرة من أجهزتهم. يجمع التطبيق بين قوة 22 وكيل ذكاء اصطناعي ولوحة تحكم ويب متطورة مدمجة.

---

## Installation | التثبيت
### For Developers | للمطورين
1. Install Python 3.10+
2. Clone the repository
3. Run `pip install -r requirements.txt`
4. Launch with `python main.py --desktop`

### For End Users | للمستخدمين النهائيين
Download the latest release for your OS:
- **Windows:** `FinovateAuditNexus.exe`
- **macOS:** `FinovateAuditNexus.app`
- **Linux:** `FinovateAuditNexus`

---

## Key Features | الميزات الرئيسية
- **Native UI:** Built with PySide6 for high performance.
- **Web Dashboard:** Integrated HTML5/Chart.js dashboard for advanced visualizations.
- **Local DB:** SQLite-based local storage for offline access and security.
- **Background Sync:** Automatic data synchronization from ERP systems.
- **Multi-System Support:** Runs on Windows, macOS, and Linux.

---

## Troubleshooting | حل المشكلات
- **Web View not loading:** Ensure you have the latest graphics drivers and `PySide6-WebEngine` installed.
- **Database errors:** Check permissions for the `~/.finovate_audit` directory.
- **Connection issues:** Verify your firewall settings allow outbound connections to ERP endpoints.

---
**© 2025 Finovate – AHMED EG**
