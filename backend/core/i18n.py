"""
Finovate Audit Nexus AI - Internationalization (i18n) System
نظام التدويل والدعم الثنائي (العربية / English)
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

TRANSLATIONS_DIR = Path(__file__).parent.parent.parent / "translations"


class I18n:
    def __init__(self, default_lang: str = "en"):
        self._default_lang = default_lang
        self._translations: Dict[str, Dict[str, str]] = {"en": {}, "ar": {}}
        self._load_translations()

    def _load_translations(self):
        if not TRANSLATIONS_DIR.exists():
            TRANSLATIONS_DIR.mkdir(parents=True, exist_ok=True)
            self._create_default_translations()

        for lang in ["en", "ar"]:
            path = TRANSLATIONS_DIR / f"{lang}.json"
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        self._translations[lang] = json.load(f)
                except Exception as e:
                    logger.error(f"Failed to load translations for {lang}: {e}")

        logger.info(f"Loaded {sum(len(v) for v in self._translations.values())} translation keys")

    def _create_default_translations(self):
        en = {
            "app.name": "Finovate Audit Nexus AI",
            "app.tagline": "Enterprise AI Financial Audit & Intelligence Platform",
            "dashboard.title": "Dashboard",
            "dashboard.welcome": "Welcome to Finovate Audit Nexus AI",
            "audit.title": "Audit",
            "audit.start": "Start Audit",
            "audit.in_progress": "Audit in progress",
            "audit.completed": "Audit completed",
            "audit.failed": "Audit failed",
            "connector.title": "Connectors",
            "connector.connected": "Connected",
            "connector.disconnected": "Disconnected",
            "connector.error": "Connection error",
            "agent.title": "AI Agents",
            "agent.active": "Active",
            "agent.idle": "Idle",
            "agent.error": "Error",
            "report.title": "Reports",
            "report.generating": "Generating report",
            "report.ready": "Report ready",
            "settings.title": "Settings",
            "settings.saved": "Settings saved",
            "user.login": "Login",
            "user.logout": "Logout",
            "user.profile": "Profile",
            "notifications.title": "Notifications",
            "notifications.empty": "No notifications",
            "error.generic": "An error occurred",
            "error.not_found": "Not found",
            "error.unauthorized": "Unauthorized",
            "loading": "Loading...",
            "save": "Save",
            "cancel": "Cancel",
            "delete": "Delete",
            "edit": "Edit",
            "create": "Create",
            "search": "Search",
            "filter": "Filter",
            "export": "Export",
            "import": "Import",
            "yes": "Yes",
            "no": "No",
            "confirm": "Confirm",
            "success": "Success",
        }
        ar = {
            "app.name": "Finovate – تدقيق مالي ذكي",
            "app.tagline": "منصة مؤسسية للتدقيق المالي بالذكاء الاصطناعي",
            "dashboard.title": "لوحة التحكم",
            "dashboard.welcome": "مرحباً بك في منصة Finovate للتدقيق المالي الذكي",
            "audit.title": "التدقيق",
            "audit.start": "بدء التدقيق",
            "audit.in_progress": "التدقيق قيد التنفيذ",
            "audit.completed": "اكتمل التدقيق",
            "audit.failed": "فشل التدقيق",
            "connector.title": "الموصلات",
            "connector.connected": "متصل",
            "connector.disconnected": "غير متصل",
            "connector.error": "خطأ في الاتصال",
            "agent.title": "وكلاء الذكاء الاصطناعي",
            "agent.active": "نشط",
            "agent.idle": "خامل",
            "agent.error": "خطأ",
            "report.title": "التقارير",
            "report.generating": "جارٍ إنشاء التقرير",
            "report.ready": "التقرير جاهز",
            "settings.title": "الإعدادات",
            "settings.saved": "تم حفظ الإعدادات",
            "user.login": "تسجيل الدخول",
            "user.logout": "تسجيل الخروج",
            "user.profile": "الملف الشخصي",
            "notifications.title": "الإشعارات",
            "notifications.empty": "لا توجد إشعارات",
            "error.generic": "حدث خطأ",
            "error.not_found": "غير موجود",
            "error.unauthorized": "غير مصرح",
            "loading": "جارٍ التحميل...",
            "save": "حفظ",
            "cancel": "إلغاء",
            "delete": "حذف",
            "edit": "تعديل",
            "create": "إنشاء",
            "search": "بحث",
            "filter": "تصفية",
            "export": "تصدير",
            "import": "استيراد",
            "yes": "نعم",
            "no": "لا",
            "confirm": "تأكيد",
            "success": "تم بنجاح",
        }
        with open(TRANSLATIONS_DIR / "en.json", "w", encoding="utf-8") as f:
            json.dump(en, f, ensure_ascii=False, indent=2)
        with open(TRANSLATIONS_DIR / "ar.json", "w", encoding="utf-8") as f:
            json.dump(ar, f, ensure_ascii=False, indent=2)
        self._translations["en"] = en
        self._translations["ar"] = ar
        logger.info(f"Created default translations ({len(en)} EN + {len(ar)} AR keys)")

    def t(self, key: str, lang: Optional[str] = None, **kwargs) -> str:
        lang = lang or self._default_lang
        text = self._translations.get(lang, {}).get(key)
        if text is None:
            text = self._translations.get("en", {}).get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        return text

    def direction(self, lang: str) -> str:
        return "rtl" if lang == "ar" else "ltr"

    def available_languages(self) -> list:
        return [{"code": "en", "name": "English", "direction": "ltr"},
                {"code": "ar", "name": "العربية", "direction": "rtl"}]


_i18n_instance: Optional[I18n] = None


def get_i18n(lang: str = "ar") -> I18n:
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18n(default_lang=lang)
    return _i18n_instance
