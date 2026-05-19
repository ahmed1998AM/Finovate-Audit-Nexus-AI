"""
Notification Service - خدمة الإشعارات والتنبيهات
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """
    خدمة الإشعارات والتنبيهات
    
    المسؤولة عن:
    - إرسال إشعارات للمستخدمين
    - تنبيهات الاحتيال
    - تنبيهات المراجعة
    - إدارة تفضيلات الإشعارات
    """
    
    def __init__(self):
        """تهيئة خدمة الإشعارات"""
        self.notifications = {}
        self.user_preferences = {}
        logger.info("NotificationService initialized")
    
    def send_notification(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        priority: str = 'normal',
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        إرسال إشعار
        
        Args:
            user_id: معرف المستخدم
            notification_type: نوع الإشعار
            title: العنوان
            message: الرسالة
            priority: الأولوية (low, normal, high, urgent)
            data: بيانات إضافية
            
        Returns:
            معلومات الإشعار
        """
        notif_id = f"NOTIF-{datetime.now().strftime('%Y%m%d%H%M%S')}-{user_id}"
        
        notification = {
            'notification_id': notif_id,
            'user_id': user_id,
            'notification_type': notification_type,
            'title': title,
            'message': message,
            'priority': priority,
            'data': data or {},
            'status': 'sent',
            'read': False,
            'created_at': datetime.now(),
            'read_at': None
        }
        
        self.notifications[notif_id] = notification
        logger.info(f"Sent notification {notif_id} to user {user_id}")
        
        return notification
    
    def send_fraud_alert(
        self,
        user_id: int,
        alert_type: str,
        severity: str,
        description: str,
        evidence: List[str],
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        إرسال تنبيه احتيال
        
        Args:
            user_id: معرف المستخدم
            alert_type: نوع التنبيه
            severity: الخطورة
            description: الوصف
            evidence: الأدلة
            project_id: معرف المشروع
            
        Returns:
            معلومات التنبيه
        """
        return self.send_notification(
            user_id=user_id,
            notification_type='fraud_alert',
            title=f"تنبيه احتيال - {severity}",
            message=description,
            priority='urgent' if severity == 'critical' else 'high',
            data={
                'alert_type': alert_type,
                'severity': severity,
                'evidence': evidence,
                'project_id': project_id
            }
        )
    
    def send_audit_reminder(
        self,
        user_id: int,
        task_name: str,
        due_date: datetime,
        project_id: str
    ) -> Dict[str, Any]:
        """
        إرسال تذكير بمهمة مراجعة
        
        Args:
            user_id: معرف المستخدم
            task_name: اسم المهمة
            due_date: تاريخ الاستحقاق
            project_id: معرف المشروع
            
        Returns:
            معلومات التذكير
        """
        return self.send_notification(
            user_id=user_id,
            notification_type='audit_reminder',
            title=f"تذكير: {task_name}",
            message=f"المهمة '{task_name}' مستحقة في {due_date.strftime('%Y-%m-%d')}",
            priority='normal',
            data={
                'task_name': task_name,
                'due_date': due_date.isoformat(),
                'project_id': project_id
            }
        )
    
    def mark_as_read(self, notification_id: str) -> bool:
        """
        تحديد الإشعار كمقروء
        
        Args:
            notification_id: معرف الإشعار
            
        Returns:
            True إذا نجح التحديث
        """
        if notification_id not in self.notifications:
            logger.error(f"Notification {notification_id} not found")
            return False
        
        self.notifications[notification_id]['read'] = True
        self.notifications[notification_id]['read_at'] = datetime.now()
        
        logger.info(f"Marked notification {notification_id} as read")
        return True
    
    def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        الحصول على إشعارات المستخدم
        
        Args:
            user_id: معرف المستخدم
            unread_only: الإشعارات غير المقروءة فقط
            limit: الحد الأقصى
            
        Returns:
            قائمة الإشعارات
        """
        notifications = [n for n in self.notifications.values() if n['user_id'] == user_id]
        
        if unread_only:
            notifications = [n for n in notifications if not n['read']]
        
        # ترتيب حسب الأحدث
        notifications.sort(key=lambda x: x['created_at'], reverse=True)
        
        return notifications[:limit]
    
    def get_unread_count(self, user_id: int) -> int:
        """
        الحصول على عدد الإشعارات غير المقروءة
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            العدد
        """
        return len([n for n in self.notifications.values() if n['user_id'] == user_id and not n['read']])
    
    def set_user_preferences(
        self,
        user_id: int,
        preferences: Dict[str, Any]
    ) -> bool:
        """
        تعيين تفضيلات الإشعارات للمستخدم
        
        Args:
            user_id: معرف المستخدم
            preferences: التفضيلات
            
        Returns:
            True إذا نجح الحفظ
        """
        self.user_preferences[user_id] = preferences
        logger.info(f"Set notification preferences for user {user_id}")
        return True
    
    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """
        الحصول على تفضيلات المستخدم
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            التفضيلات
        """
        return self.user_preferences.get(user_id, {
            'email_notifications': True,
            'push_notifications': True,
            'fraud_alerts': True,
            'audit_reminders': True,
            'daily_digest': False
        })
