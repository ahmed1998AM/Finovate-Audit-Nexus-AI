"""
User Service - خدمة إدارة المستخدمين والصلاحيات
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.security import hash_password, verify_password

logger = logging.getLogger(__name__)


class UserService:
    """
    خدمة إدارة المستخدمين والصلاحيات

    المسؤولة عن:
    - إدارة حسابات المستخدمين
    - المصادقة والتفويض
    - إدارة الصلاحيات (RBAC)
    - تتبع نشاط المستخدمين
    """

    def __init__(self):
        """تهيئة خدمة المستخدمين"""
        self.users = {}
        self.sessions = {}
        self.roles = {
            'admin': ['all'],
            'auditor': ['audit.read', 'audit.write', 'reports.read', 'reports.write'],
            'accountant': ['audit.read', 'reports.read'],
            'cfo': ['audit.read', 'reports.read', 'analytics.read', 'executive.read'],
            'external_auditor': ['audit.read', 'reports.read'],
            'tax_reviewer': ['tax.read', 'tax.write', 'reports.read']
        }
        logger.info("UserService initialized")

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str,
        full_name: str,
        company_id: int
    ) -> Dict[str, Any]:
        """
        إنشاء مستخدم جديد

        Args:
            username: اسم المستخدم
            email: البريد الإلكتروني
            password: كلمة المرور
            role: الدور
            full_name: الاسم الكامل
            company_id: معرف الشركة

        Returns:
            معلومات المستخدم
        """
        user_id = f"USR-{company_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # التحقق من عدم وجود المستخدم
        for u in self.users.values():
            if u['username'] == username or u['email'] == email:
                return {'success': False, 'error': 'Username or email already exists'}

        # التحقق من صحة الدور
        if role not in self.roles:
            return {'success': False, 'error': 'Invalid role'}

        # تشفير كلمة المرور
        hashed_password = hash_password(password)

        user = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'password_hash': hashed_password,
            'role': role,
            'full_name': full_name,
            'company_id': company_id,
            'status': 'active',
            'permissions': self.roles[role],
            'created_at': datetime.now(),
            'last_login': None,
            'failed_login_attempts': 0,
            'locked_until': None
        }

        self.users[user_id] = user
        logger.info(f"Created user: {user_id} ({username})")

        return {'success': True, 'user': {k: v for k, v in user.items() if k != 'password_hash'}}

    def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """
        مصادقة المستخدم

        Args:
            username: اسم المستخدم
            password: كلمة المرور

        Returns:
            نتيجة المصادقة
        """
        # البحث عن المستخدم
        user = None
        for u in self.users.values():
            if u['username'] == username:
                user = u
                break

        if not user:
            logger.warning(f"Authentication failed: User {username} not found")
            return {'success': False, 'error': 'Invalid credentials'}

        # التحقق من حالة الحساب
        if user['status'] != 'active':
            return {'success': False, 'error': 'Account is inactive'}

        if user['locked_until'] and datetime.now() < user['locked_until']:
            return {'success': False, 'error': 'Account is locked'}

        # التحقق من كلمة المرور
        if not verify_password(password, user['password_hash']):
            user['failed_login_attempts'] += 1

            # قفل الحساب بعد 5 محاولات فاشلة
            if user['failed_login_attempts'] >= 5:
                from datetime import timedelta
                user['locked_until'] = datetime.now() + timedelta(minutes=15)
                logger.warning(f"Account locked: {username}")

            return {'success': False, 'error': 'Invalid credentials'}

        # نجاح المصادقة
        user['failed_login_attempts'] = 0
        user['locked_until'] = None
        user['last_login'] = datetime.now()

        # إنشاء جلسة
        session_id = f"SES-{user['user_id']}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.sessions[session_id] = {
            'session_id': session_id,
            'user_id': user['user_id'],
            'created_at': datetime.now(),
            'expires_at': datetime.now().replace(hour=23, minute=59, second=59),
            'ip_address': '127.0.0.1'  # يمكن تمريره كمعامل
        }

        logger.info(f"User authenticated: {username}")

        return {
            'success': True,
            'user': {k: v for k, v in user.items() if k != 'password_hash'},
            'session': self.sessions[session_id]
        }

    def logout(self, session_id: str) -> bool:
        """
        تسجيل الخروج

        Args:
            session_id: معرف الجلسة

        Returns:
            True إذا نجح تسجيل الخروج
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Session terminated: {session_id}")
            return True

        return False

    def get_user(self, user_id: str) -> Dict[str, Any]:
        """
        الحصول على معلومات المستخدم

        Args:
            user_id: معرف المستخدم

        Returns:
            معلومات المستخدم
        """
        if user_id not in self.users:
            return {'exists': False}

        user = self.users[user_id]
        return {
            'exists': True,
            **{k: v for k, v in user.items() if k != 'password_hash'}
        }

    def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """
        تحديث معلومات المستخدم

        Args:
            user_id: معرف المستخدم
            updates: البيانات المحدثة

        Returns:
            True إذا نجح التحديث
        """
        if user_id not in self.users:
            logger.error(f"User {user_id} not found")
            return False

        user = self.users[user_id]

        # تحديث الحقول المسموحة
        allowed_fields = ['email', 'full_name', 'role', 'status']

        for field, value in updates.items():
            if field in allowed_fields:
                if field == 'role' and value in self.roles:
                    user['role'] = value
                    user['permissions'] = self.roles[value]
                elif field != 'role':
                    user[field] = value

        logger.info(f"Updated user: {user_id}")
        return True

    def delete_user(self, user_id: str) -> bool:
        """
        حذف مستخدم

        Args:
            user_id: معرف المستخدم

        Returns:
            True إذا نجح الحذف
        """
        if user_id not in self.users:
            logger.error(f"User {user_id} not found")
            return False

        del self.users[user_id]

        # حذف الجلسات النشطة
        sessions_to_delete = [sid for sid, sess in self.sessions.items() if sess['user_id'] == user_id]
        for sid in sessions_to_delete:
            del self.sessions[sid]

        logger.info(f"Deleted user: {user_id}")
        return True

    def has_permission(self, user_id: str, permission: str) -> bool:
        """
        التحقق من صلاحية المستخدم

        Args:
            user_id: معرف المستخدم
            permission: الصلاحية المطلوبة

        Returns:
            True إذا كان لديه الصلاحية
        """
        if user_id not in self.users:
            return False

        user = self.users[user_id]

        # المسؤول لديه جميع الصلاحيات
        if 'all' in user['permissions']:
            return True

        return permission in user['permissions']

    def list_users(self, company_id: Optional[int] = None, role: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        قائمة المستخدمين

        Args:
            company_id: تصفية حسب الشركة
            role: تصفية حسب الدور

        Returns:
            قائمة المستخدمين
        """
        users = list(self.users.values())

        if company_id is not None:
            users = [u for u in users if u['company_id'] == company_id]

        if role is not None:
            users = [u for u in users if u['role'] == role]

        return [{k: v for k, v in u.items() if k != 'password_hash'} for u in users]

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        الحصول على معلومات الجلسة

        Args:
            session_id: معرف الجلسة

        Returns:
            معلومات الجلسة
        """
        if session_id not in self.sessions:
            return {'valid': False}

        session = self.sessions[session_id]

        # التحقق من انتهاء الصلاحية
        if datetime.now() > session['expires_at']:
            del self.sessions[session_id]
            return {'valid': False, 'error': 'Session expired'}

        return {
            'valid': True,
            **session
        }

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """
        تغيير كلمة المرور

        Args:
            user_id: معرف المستخدم
            old_password: كلمة المرور القديمة
            new_password: كلمة المرور الجديدة

        Returns:
            True إذا نجح التغيير
        """
        if user_id not in self.users:
            return False

        user = self.users[user_id]

        # التحقق من كلمة المرور القديمة
        if not verify_password(old_password, user['password_hash']):
            return False

        # تحديث كلمة المرور
        user['password_hash'] = hash_password(new_password)

        logger.info(f"Password changed for user: {user_id}")
        return True
