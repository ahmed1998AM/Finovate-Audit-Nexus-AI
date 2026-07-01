"""
Behavioral Intelligence Agent
وكيل تحليل السلوك المالي والإداري

المهام:
- تحليل سلوك المستخدمين في النظام
- كشف السلوك غير الطبيعي
- كشف التحايل الإداري
- تحليل الأنماط المشبوهة
- مراقبة أوقات الدخول والخروج
- تتبع تغييرات الصلاحيات
"""

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class BehaviorRiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AnomalyType(Enum):
    UNUSUAL_TIME = "UNUSUAL_TIME"
    FREQUENT_CHANGES = "FREQUENT_CHANGES"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"
    BULK_OPERATIONS = "BULK_OPERATIONS"
    AFTER_HOURS_ACCESS = "AFTER_HOURS_ACCESS"
    REPEATED_FAILURES = "REPEATED_FAILURES"
    BYPASS_ATTEMPTS = "BYPASS_ATTEMPTS"
    DATA_EXFILTRATION = "DATA_EXFILTRATION"


@dataclass
class UserBehaviorProfile:
    user_id: str
    username: str
    role: str
    department: str
    avg_login_time: str
    avg_logout_time: str
    typical_actions_per_day: int
    typical_modules: List[str]
    risk_score: float = 0.0
    anomaly_count: int = 0
    last_activity: Optional[str] = None
    behavior_flags: List[str] = None

    def __post_init__(self):
        if self.behavior_flags is None:
            self.behavior_flags = []


@dataclass
class BehavioralAnomaly:
    anomaly_id: str
    user_id: str
    anomaly_type: str
    description: str
    risk_level: str
    timestamp: str
    evidence: Dict[str, Any]
    recommended_action: str


class BehavioralIntelligenceAgent:
    """
    وكيل الذكاء السلوكي لتحليل أنماط المستخدمين وكشف التحايل
    """

    def __init__(self):
        self.user_profiles: Dict[str, UserBehaviorProfile] = {}
        self.anomalies: List[BehavioralAnomaly] = []
        self.activity_logs: List[Dict[str, Any]] = []
        self.work_hours_start = 8  # 8 AM
        self.work_hours_end = 17   # 5 PM

    def add_user_profile(self, profile: UserBehaviorProfile):
        """إضافة ملف سلوكي لمستخدم"""
        self.user_profiles[profile.user_id] = profile

    def log_activity(self, activity: Dict[str, Any]):
        """تسجيل نشاط مستخدم"""
        activity['timestamp'] = activity.get('timestamp', datetime.now().isoformat())
        self.activity_logs.append(activity)

        # تحليل النشاط فورًا
        self._analyze_activity(activity)

    def _analyze_activity(self, activity: Dict[str, Any]):
        """تحليل نشاط فردي"""
        user_id = activity.get('user_id')
        if not user_id or user_id not in self.user_profiles:
            return

        profile = self.user_profiles[user_id]
        timestamp = datetime.fromisoformat(activity['timestamp'])

        # فحص الوصول خارج أوقات العمل
        if self._is_after_hours(timestamp):
            self._create_anomaly(
                user_id=user_id,
                anomaly_type=AnomalyType.AFTER_HOURS_ACCESS.value,
                description=f"وصول خارج أوقات العمل في {timestamp.strftime('%H:%M')}",
                risk_level=BehaviorRiskLevel.MEDIUM.value,
                evidence={"timestamp": activity['timestamp'], "action": activity.get('action')},
                recommended_action="مراجعة سبب الوصول خارج أوقات العمل"
            )

        # فحص العمليات الضخمة
        if activity.get('record_count', 0) > 1000:
            self._create_anomaly(
                user_id=user_id,
                anomaly_type=AnomalyType.BULK_OPERATIONS.value,
                description=f"عملية ضخمة: {activity.get('record_count')} سجل",
                risk_level=BehaviorRiskLevel.HIGH.value,
                evidence={"record_count": activity.get('record_count'), "action": activity.get('action')},
                recommended_action="مراجعة ضرورة العملية الضخمة والتأكد من الصلاحية"
            )

        # تحديث الملف السلوكي
        profile.last_activity = activity['timestamp']
        profile.anomaly_count = len([a for a in self.anomalies if a.user_id == user_id])

    def _is_after_hours(self, timestamp: datetime) -> bool:
        """التحقق مما إذا كان الوقت خارج ساعات العمل"""
        hour = timestamp.hour
        is_weekend = timestamp.weekday() >= 5  # Saturday = 5, Sunday = 6
        return hour < self.work_hours_start or hour > self.work_hours_end or is_weekend

    def _create_anomaly(self, user_id: str, anomaly_type: str, description: str,
                       risk_level: str, evidence: Dict, recommended_action: str):
        """إنشاء سجل شذوذ سلوكي"""
        anomaly_id = f"ANOM-{hashlib.md5(f'{user_id}{datetime.now()}'.encode()).hexdigest()[:8].upper()}"

        anomaly = BehavioralAnomaly(
            anomaly_id=anomaly_id,
            user_id=user_id,
            anomaly_type=anomaly_type,
            description=description,
            risk_level=risk_level,
            timestamp=datetime.now().isoformat(),
            evidence=evidence,
            recommended_action=recommended_action
        )

        self.anomalies.append(anomaly)

        # تحديث ملف المستخدم
        if user_id in self.user_profiles:
            self.user_profiles[user_id].risk_score = self._calculate_user_risk(user_id)
            self.user_profiles[user_id].behavior_flags.append(anomaly_type)

    def _calculate_user_risk(self, user_id: str) -> float:
        """حساب درجة الخطر للمستخدم"""
        user_anomalies = [a for a in self.anomalies if a.user_id == user_id]

        if not user_anomalies:
            return 0.0

        risk_weights = {
            BehaviorRiskLevel.LOW.value: 1.0,
            BehaviorRiskLevel.MEDIUM.value: 2.5,
            BehaviorRiskLevel.HIGH.value: 5.0,
            BehaviorRiskLevel.CRITICAL.value: 10.0
        }

        total_weight = sum(risk_weights.get(a.risk_level, 1.0) for a in user_anomalies)
        max_possible = len(user_anomalies) * 10.0

        return min(100.0, (total_weight / max_possible) * 100) if max_possible > 0 else 0.0

    def detect_privilege_escalation(self, user_id: str, old_role: str, new_role: str) -> Optional[BehavioralAnomaly]:
        """كشف تصعيد الصلاحيات"""
        admin_roles = ['admin', 'super_admin', 'root', 'manager']

        if old_role not in admin_roles and new_role in admin_roles:
            anomaly = BehavioralAnomaly(
                anomaly_id=f"PRIV-{hashlib.md5(f'{user_id}{datetime.now()}'.encode()).hexdigest()[:8].upper()}",
                user_id=user_id,
                anomaly_type=AnomalyType.PRIVILEGE_ESCALATION.value,
                description=f"تصعيد صلاحيات من {old_role} إلى {new_role}",
                risk_level=BehaviorRiskLevel.CRITICAL.value,
                timestamp=datetime.now().isoformat(),
                evidence={"old_role": old_role, "new_role": new_role},
                recommended_action="مراجعة فورية لتصعيد الصلاحيات والتأكد من الموافقات"
            )
            self.anomalies.append(anomaly)
            return anomaly
        return None

    def analyze_login_patterns(self, user_id: str, login_times: List[str]) -> Dict[str, Any]:
        """تحليل أنماط تسجيل الدخول"""
        if not login_times:
            return {"status": "no_data"}

        timestamps = [datetime.fromisoformat(t) for t in login_times]

        # حساب متوسط وقت تسجيل الدخول
        hours = [t.hour for t in timestamps]
        avg_hour = sum(hours) / len(hours)

        anomalies_detected = []

        # فحص تسجيل الدخول في أوقات غير معتادة
        for ts in timestamps:
            if self._is_after_hours(ts):
                anomalies_detected.append({
                    "type": "after_hours_login",
                    "timestamp": ts.isoformat(),
                    "risk": "MEDIUM"
                })

        return {
            "user_id": user_id,
            "total_logins": len(login_times),
            "avg_login_hour": round(avg_hour, 2),
            "anomalies_count": len(anomalies_detected),
            "anomalies": anomalies_detected,
            "risk_assessment": "HIGH" if len(anomalies_detected) > 3 else "MEDIUM" if len(anomalies_detected) > 0 else "LOW"
        }

    def get_behavioral_report(self) -> Dict[str, Any]:
        """الحصول على تقرير سلوكي شامل"""
        high_risk_users = [
            uid for uid, profile in self.user_profiles.items()
            if profile.risk_score > 50
        ]

        critical_anomalies = [
            a for a in self.anomalies
            if a.risk_level == BehaviorRiskLevel.CRITICAL.value
        ]

        anomaly_types = {}
        for anomaly in self.anomalies:
            anomaly_types[anomaly.anomaly_type] = anomaly_types.get(anomaly.anomaly_type, 0) + 1

        return {
            "report_timestamp": datetime.now().isoformat(),
            "total_users_monitored": len(self.user_profiles),
            "total_activities_logged": len(self.activity_logs),
            "total_anomalies_detected": len(self.anomalies),
            "high_risk_users": high_risk_users,
            "critical_anomalies_count": len(critical_anomalies),
            "anomaly_types_distribution": anomaly_types,
            "top_risk_users": sorted(
                [(uid, p.risk_score) for uid, p in self.user_profiles.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "recommendations": self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """توليد توصيات بناءً على التحليل"""
        recommendations = []

        critical_count = len([a for a in self.anomalies if a.risk_level == BehaviorRiskLevel.CRITICAL.value])
        if critical_count > 0:
            recommendations.append(f"مراجعة فورية لـ {critical_count} حالات حرجة")

        after_hours = len([a for a in self.anomalies if a.anomaly_type == AnomalyType.AFTER_HOURS_ACCESS.value])
        if after_hours > 5:
            recommendations.append("مراجعة سياسة الوصول خارج أوقات العمل وتفعيل مصادقة إضافية")

        privilege_escalations = len([a for a in self.anomalies if a.anomaly_type == AnomalyType.PRIVILEGE_ESCALATION.value])
        if privilege_escalations > 0:
            recommendations.append("مراجعة جميع عمليات تصعيد الصلاحيات الأخيرة")

        if not recommendations:
            recommendations.append("لا توجد توصيات عاجلة - الاستمرار في المراقبة الروتينية")

        return recommendations

    def export_anomalies(self, format: str = "json") -> str:
        """تصدير الشذوذات المكتشفة"""
        if format == "json":
            return json.dumps([asdict(a) for a in self.anomalies], indent=2, ensure_ascii=False)
        elif format == "csv":
            import csv
            import io
            output = io.StringIO()
            if self.anomalies:
                writer = csv.DictWriter(output, fieldnames=asdict(self.anomalies[0]).keys())
                writer.writeheader()
                for anomaly in self.anomalies:
                    writer.writerow(asdict(anomaly))
            return output.getvalue()
        return ""


# مثال استخدام
if __name__ == "__main__":
    print("=" * 80)
    print("Behavioral Intelligence Agent - وكيل الذكاء السلوكي")
    print("=" * 80)

    agent = BehavioralIntelligenceAgent()

    # إضافة ملفات مستخدمين
    agent.add_user_profile(UserBehaviorProfile(
        user_id="USR001",
        username="ahmed.mostafa",
        role="accountant",
        department="finance",
        avg_login_time="08:30",
        avg_logout_time="17:00",
        typical_actions_per_day=150,
        typical_modules=["journal_entries", "reports", "trial_balance"]
    ))

    agent.add_user_profile(UserBehaviorProfile(
        user_id="USR002",
        username="mohamed.hassan",
        role="admin",
        department="IT",
        avg_login_time="09:00",
        avg_logout_time="18:00",
        typical_actions_per_day=200,
        typical_modules=["user_management", "system_config", "audit_logs"]
    ))

    # محاكاة أنشطة
    print("\n📊 تسجيل الأنشطة...")

    # نشاط طبيعي
    agent.log_activity({
        "user_id": "USR001",
        "action": "create_journal_entry",
        "module": "journal_entries",
        "record_count": 5,
        "timestamp": "2025-01-15T10:30:00"
    })

    # نشاط مشبوه - وصول خارج أوقات العمل
    agent.log_activity({
        "user_id": "USR001",
        "action": "bulk_export",
        "module": "reports",
        "record_count": 15000,
        "timestamp": "2025-01-15T23:45:00"
    })

    # نشاط خطير - عملية ضخمة
    agent.log_activity({
        "user_id": "USR002",
        "action": "delete_audit_logs",
        "module": "system_config",
        "record_count": 5000,
        "timestamp": "2025-01-15T02:15:00"
    })

    # تصعيد صلاحيات
    agent.detect_privilege_escalation("USR001", "accountant", "admin")

    # تحليل أنماط تسجيل الدخول
    login_times = [
        "2025-01-10T08:30:00",
        "2025-01-11T09:15:00",
        "2025-01-12T23:45:00",  # مشبوه
        "2025-01-13T02:30:00",  # مشبوه جداً
        "2025-01-14T08:45:00"
    ]

    print("\n🔍 تحليل أنماط تسجيل الدخول:")
    login_analysis = agent.analyze_login_patterns("USR001", login_times)
    print(json.dumps(login_analysis, indent=2, ensure_ascii=False))

    # التقرير السلوكي الشامل
    print("\n" + "=" * 80)
    print("📋 التقرير السلوكي الشامل")
    print("=" * 80)

    report = agent.get_behavioral_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))

    # عرض الشذوذات المكتشفة
    print("\n" + "=" * 80)
    print("⚠️ الشذوذات المكتشفة")
    print("=" * 80)

    for anomaly in agent.anomalies:
        print(f"\n[{anomaly.risk_level}] {anomaly.anomaly_id}")
        print(f"  المستخدم: {anomaly.user_id}")
        print(f"  النوع: {anomaly.anomaly_type}")
        print(f"  الوصف: {anomaly.description}")
        print(f"  التوصية: {anomaly.recommended_action}")

    print("\n✅ تم تحليل السلوك بنجاح!")
    print(f"   إجمالي الشذوذات: {len(agent.anomalies)}")
    print(f"   المستخدمين تحت المراقبة: {len(agent.user_profiles)}")
