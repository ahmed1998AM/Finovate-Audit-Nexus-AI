"""
Finovate Audit Nexus AI - Continuous Audit Agent
المراجعة المستمرة والمراقبة اللحظية
"""
import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AuditEvent:
    timestamp: datetime
    event_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    data: Dict[str, Any]
    rule_id: str

class ContinuousAuditAgent:
    """
    وكيل المراجعة المستمرة
    يراقب البيانات لحظياً ويكشف الانحرافات فوراً
    """

    def __init__(self):
        self.rules: List[Dict] = []
        self.alerts: List[AuditEvent] = []
        self.is_running = False
        self.monitoring_thread = None
        self.callbacks: List[Callable] = []

        # قواعد افتراضية للكشف
        self._load_default_rules()

    def _load_default_rules(self):
        """تحميل قواعد الكشف الافتراضية"""
        self.rules = [
            {
                "id": "RULE_001",
                "name": "حركة بنكية كبيرة مفاجئة",
                "type": "threshold",
                "field": "amount",
                "operator": ">",
                "value": 100000,
                "severity": "HIGH"
            },
            {
                "id": "RULE_002",
                "name": "تعديل قيد بعد الإغلاق",
                "type": "time_check",
                "condition": "post_close_edit",
                "severity": "CRITICAL"
            },
            {
                "id": "RULE_003",
                "name": "مستخدم واحد قام بأكثر من 50 قيد في ساعة",
                "type": "frequency",
                "field": "user_id",
                "count": 50,
                "window": 3600,  # seconds
                "severity": "MEDIUM"
            },
            {
                "id": "RULE_004",
                "name": "حذف عملية مالية",
                "type": "action_check",
                "action": "delete",
                "severity": "CRITICAL"
            }
        ]

    def add_rule(self, rule: Dict):
        """إضافة قاعدة جديدة"""
        self.rules.append(rule)
        logger.info(f"Rule added: {rule['name']}")

    def register_alert_callback(self, callback: Callable):
        """تسجيل دالة لاستقبال التنبيهات"""
        self.callbacks.append(callback)

    def process_transaction(self, transaction: Dict[str, Any]) -> List[AuditEvent]:
        """
        معالجة معاملة وفحصها ضد جميع القواعد
        """
        triggered_alerts = []

        for rule in self.rules:
            if self._check_rule(rule, transaction):
                alert = AuditEvent(
                    timestamp=datetime.now(),
                    event_type=rule['name'],
                    severity=rule['severity'],
                    description=f"تم كشف انتهاك للقاعدة: {rule['name']}",
                    data=transaction,
                    rule_id=rule['id']
                )
                triggered_alerts.append(alert)
                self._send_alert(alert)

        return triggered_alerts

    def _check_rule(self, rule: Dict, data: Dict) -> bool:
        """فحص قاعدة معينة ضد البيانات"""
        try:
            if rule['type'] == 'threshold':
                value = data.get(rule['field'], 0)
                if rule['operator'] == '>' and value > rule['value']:
                    return True
                elif rule['operator'] == '<' and value < rule['value']:
                    return True

            elif rule['type'] == 'action_check':
                if data.get('action') == rule['action']:
                    return True

            # يمكن إضافة منطق أكثر تعقيداً هنا
            return False
        except Exception as e:
            logger.error(f"Error checking rule {rule['id']}: {e}")
            return False

    def _send_alert(self, alert: AuditEvent):
        """إرسال تنبيه"""
        self.alerts.append(alert)
        logger.warning(f"🚨 ALERT [{alert.severity}]: {alert.description}")

        for callback in self.callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Callback error: {e}")

    def start_monitoring(self, data_stream: Callable):
        """بدء المراقبة المستمرة"""
        self.is_running = True

        def monitor_loop():
            while self.is_running:
                try:
                    # جلب بيانات جديدة من المصدر
                    new_data = data_stream()
                    if new_data:
                        if isinstance(new_data, list):
                            for item in new_data:
                                self.process_transaction(item)
                        else:
                            self.process_transaction(new_data)

                    time.sleep(1)  # فحص كل ثانية
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    time.sleep(5)

        self.monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("✅ Continuous Audit Monitoring Started")

    def stop_monitoring(self):
        """إيقاف المراقبة"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logger.info("⏹️ Continuous Audit Monitoring Stopped")

    def get_alerts(self, last_n: int = 10) -> List[AuditEvent]:
        """الحصول على آخر التنبيهات"""
        return self.alerts[-last_n:]

    def generate_report(self) -> Dict:
        """توليد تقرير المراجعة المستمرة"""
        return {
            "total_alerts": len(self.alerts),
            "critical": len([a for a in self.alerts if a.severity == 'CRITICAL']),
            "high": len([a for a in self.alerts if a.severity == 'HIGH']),
            "medium": len([a for a in self.alerts if a.severity == 'MEDIUM']),
            "low": len([a for a in self.alerts if a.severity == 'LOW']),
            "rules_active": len(self.rules),
            "status": "running" if self.is_running else "stopped"
        }

# مثال للاستخدام
if __name__ == "__main__":
    agent = ContinuousAuditAgent()

    def on_alert(alert: AuditEvent):
        print(f"🔔 تنبيه فوري: {alert.description} - الخطورة: {alert.severity}")

    agent.register_alert_callback(on_alert)

    # محاكاة بيانات
    test_data = [
        {"id": 1, "amount": 5000, "user": "ahmed", "action": "create"},
        {"id": 2, "amount": 150000, "user": "mona", "action": "create"},  # تنبيه!
        {"id": 3, "amount": 2000, "user": "ali", "action": "delete"},     # تنبيه!
    ]

    print("🚀 بدء اختبار المراجعة المستمرة...")
    for data in test_data:
        agent.process_transaction(data)

    print("\n📊 تقرير المراجعة:")
    report = agent.generate_report()
    for k, v in report.items():
        print(f"{k}: {v}")
