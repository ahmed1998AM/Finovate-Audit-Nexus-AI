"""
Finovate Audit Nexus AI - Users & RBAC Management System
نظام إدارة المستخدمين والصلاحيات
"""
import hashlib
import secrets
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Role(Enum):
    """أدوار المستخدمين"""
    ADMIN = "Admin"
    AUDITOR = "Auditor"
    ACCOUNTANT = "Accountant"
    CFO = "CFO"
    TAX_REVIEWER = "Tax Reviewer"
    EXTERNAL_AUDITOR = "External Auditor"
    VIEWER = "Viewer"


class Permission(Enum):
    """الصلاحيات"""
    # صلاحيات عامة
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_REPORTS = "view_reports"
    EXPORT_REPORTS = "export_reports"
    
    # صلاحيات المراجعة
    RUN_AUDIT = "run_audit"
    VIEW_AUDIT_RESULTS = "view_audit_results"
    APPROVE_AUDIT = "approve_audit"
    
    # صلاحيات الذكاء الاصطناعي
    MANAGE_AGENTS = "manage_agents"
    CONFIGURE_AI = "configure_ai"
    VIEW_AI_LOGS = "view_ai_logs"
    
    # صلاحيات النظام
    MANAGE_USERS = "manage_users"
    MANAGE_SETTINGS = "manage_settings"
    VIEW_SYSTEM_LOGS = "view_system_logs"
    DELETE_DATA = "delete_data"
    
    # صلاحيات الضرائب
    REVIEW_TAX = "review_tax"
    SUBMIT_TAX = "submit_tax"
    
    # صلاحيات التحقيق
    FORENSIC_ACCESS = "forensic_access"
    FRAUD_INVESTIGATION = "fraud_investigation"


# خريطة الصلاحيات لكل دور
ROLE_PERMISSIONS = {
    Role.ADMIN: set(Permission),
    Role.AUDITOR: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_REPORTS,
        Permission.EXPORT_REPORTS,
        Permission.RUN_AUDIT,
        Permission.VIEW_AUDIT_RESULTS,
        Permission.VIEW_AI_LOGS
    },
    Role.ACCOUNTANT: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_REPORTS,
        Permission.EXPORT_REPORTS,
        Permission.VIEW_AUDIT_RESULTS
    },
    Role.CFO: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_REPORTS,
        Permission.EXPORT_REPORTS,
        Permission.VIEW_AUDIT_RESULTS,
        Permission.APPROVE_AUDIT,
        Permission.MANAGE_SETTINGS,
        Permission.VIEW_SYSTEM_LOGS
    },
    Role.TAX_REVIEWER: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_REPORTS,
        Permission.EXPORT_REPORTS,
        Permission.REVIEW_TAX,
        Permission.SUBMIT_TAX,
        Permission.VIEW_AUDIT_RESULTS
    },
    Role.EXTERNAL_AUDITOR: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_REPORTS,
        Permission.EXPORT_REPORTS,
        Permission.RUN_AUDIT,
        Permission.VIEW_AUDIT_RESULTS,
        Permission.FORENSIC_ACCESS
    },
    Role.VIEWER: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_REPORTS
    }
}


@dataclass
class User:
    """بيانات المستخدم"""
    user_id: str
    username: str
    email: str
    password_hash: str
    role: Role
    full_name: str
    department: str = ""
    is_active: bool = True
    is_locked: bool = False
    failed_login_attempts: int = 0
    last_login: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل المستخدم إلى قاموس"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "full_name": self.full_name,
            "department": self.department,
            "is_active": self.is_active,
            "is_locked": self.is_locked,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat(),
            "mfa_enabled": self.mfa_enabled
        }


class RBACManager:
    """
    مدير الصلاحيات والأدوار
    يدعم RBAC (Role-Based Access Control)
    """
    
    def __init__(self, users_file: str = "database/users.json"):
        self.users_file = Path(users_file)
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # تحميل المستخدمين من الملف
        self._load_users()
        
        # إنشاء مستخدم Admin افتراضي إذا لم يوجد
        if not self.users:
            self._create_default_admin()
    
    def _load_users(self) -> None:
        """تحميل المستخدمين من الملف"""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for user_data in data.get("users", []):
                    user = User(
                        user_id=user_data["user_id"],
                        username=user_data["username"],
                        email=user_data["email"],
                        password_hash=user_data["password_hash"],
                        role=Role(user_data["role"]),
                        full_name=user_data["full_name"],
                        department=user_data.get("department", ""),
                        is_active=user_data.get("is_active", True),
                        is_locked=user_data.get("is_locked", False),
                        failed_login_attempts=user_data.get("failed_login_attempts", 0),
                        last_login=datetime.fromisoformat(user_data["last_login"]) if user_data.get("last_login") else None,
                        created_at=datetime.fromisoformat(user_data["created_at"]),
                        updated_at=datetime.fromisoformat(user_data["updated_at"]),
                        mfa_enabled=user_data.get("mfa_enabled", False),
                        mfa_secret=user_data.get("mfa_secret")
                    )
                    self.users[user.user_id] = user
                    
                logger.info(f"Loaded {len(self.users)} users")
                
            except Exception as e:
                logger.error(f"Error loading users: {e}")
                self._create_default_admin()
        else:
            self._create_default_admin()
    
    def _save_users(self) -> None:
        """حفظ المستخدمين في الملف"""
        try:
            self.users_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "users": [user.to_dict() for user in self.users.values()],
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.info("Users saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving users: {e}")
    
    def _create_default_admin(self) -> None:
        """إنشاء مستخدم Admin افتراضي"""
        admin_password = self._hash_password("Admin@123")
        
        admin = User(
            user_id="admin_001",
            username="admin",
            email="admin@finovate.com",
            password_hash=admin_password,
            role=Role.ADMIN,
            full_name="System Administrator",
            department="IT"
        )
        
        self.users[admin.user_id] = admin
        self._save_users()
        
        logger.warning("Default admin user created - username: admin, password: Admin@123")
    
    def _hash_password(self, password: str) -> str:
        """تشفير كلمة المرور"""
        # استخدام SHA-256 مع salt
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """التحقق من كلمة المرور"""
        try:
            salt, stored_hash = password_hash.split(":")
            new_hash = hashlib.sha256((salt + password).encode()).hexdigest()
            return new_hash == stored_hash
        except:
            return False
    
    def create_user(self, username: str, email: str, password: str,
                   role: Role, full_name: str, department: str = "") -> User:
        """إنشاء مستخدم جديد"""
        # التحقق من عدم وجود المستخدم
        for user in self.users.values():
            if user.username == username or user.email == email:
                raise ValueError("Username or email already exists")
        
        # إنشاء user_id فريد
        user_id = f"user_{secrets.token_hex(4)}"
        
        # تشفير كلمة المرور
        password_hash = self._hash_password(password)
        
        # إنشاء المستخدم
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            full_name=full_name,
            department=department
        )
        
        self.users[user_id] = user
        self._save_users()
        
        logger.info(f"Created new user: {username} ({role.value})")
        return user
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """
        تسجيل الدخول
        يرجع session token إذا نجح
        """
        # البحث عن المستخدم
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break
        
        if not user:
            logger.warning(f"Login failed - user not found: {username}")
            return None
        
        # التحقق من حالة المستخدم
        if not user.is_active:
            logger.warning(f"Login failed - user inactive: {username}")
            return None
        
        if user.is_locked:
            logger.warning(f"Login failed - user locked: {username}")
            return None
        
        # التحقق من كلمة المرور
        if not self._verify_password(password, user.password_hash):
            user.failed_login_attempts += 1
            
            # قفل المستخدم بعد 5 محاولات فاشلة
            if user.failed_login_attempts >= 5:
                user.is_locked = True
                logger.warning(f"User locked due to failed attempts: {username}")
            
            self._save_users()
            logger.warning(f"Login failed - wrong password: {username}")
            return None
        
        # نجاح تسجيل الدخول
        user.failed_login_attempts = 0
        user.last_login = datetime.now()
        self._save_users()
        
        # إنشاء session
        session_token = secrets.token_urlsafe(32)
        self.sessions[session_token] = {
            "user_id": user.user_id,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=8)
        }
        
        logger.info(f"User logged in: {username}")
        return session_token
    
    def logout(self, session_token: str) -> bool:
        """تسجيل الخروج"""
        if session_token in self.sessions:
            del self.sessions[session_token]
            logger.info("User logged out")
            return True
        return False
    
    def validate_session(self, session_token: str) -> Optional[User]:
        """التحقق من الجلسة"""
        if session_token not in self.sessions:
            return None
        
        session = self.sessions[session_token]
        
        # التحقق من انتهاء الصلاحية
        if datetime.now() > session["expires_at"]:
            del self.sessions[session_token]
            return None
        
        # الحصول على المستخدم
        user = self.users.get(session["user_id"])
        return user
    
    def has_permission(self, user: User, permission: Permission) -> bool:
        """التحقق من صلاحية المستخدم"""
        user_permissions = ROLE_PERMISSIONS.get(user.role, set())
        return permission in user_permissions
    
    def get_user_permissions(self, user: User) -> List[str]:
        """الحصول على صلاحيات المستخدم"""
        user_permissions = ROLE_PERMISSIONS.get(user.role, set())
        return [p.value for p in user_permissions]
    
    def update_user_role(self, user_id: str, new_role: Role) -> bool:
        """تحديث دور المستخدم"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        user.role = new_role
        user.updated_at = datetime.now()
        self._save_users()
        
        logger.info(f"Updated user role: {user.username} -> {new_role.value}")
        return True
    
    def deactivate_user(self, user_id: str) -> bool:
        """تعطيل مستخدم"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        user.is_active = False
        user.updated_at = datetime.now()
        self._save_users()
        
        logger.info(f"Deactivated user: {user.username}")
        return True
    
    def reset_password(self, user_id: str, new_password: str) -> bool:
        """إعادة تعيين كلمة المرور"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        user.password_hash = self._hash_password(new_password)
        user.failed_login_attempts = 0
        user.is_locked = False
        user.updated_at = datetime.now()
        self._save_users()
        
        logger.info(f"Password reset for user: {user.username}")
        return True
    
    def list_users(self) -> List[Dict[str, Any]]:
        """سرد جميع المستخدمين"""
        return [user.to_dict() for user in self.users.values()]
    
    def get_user(self, user_id: str) -> Optional[User]:
        """الحصول على مستخدم"""
        return self.users.get(user_id)
    
    def delete_user(self, user_id: str) -> bool:
        """حذف مستخدم"""
        if user_id not in self.users:
            return False
        
        # لا يمكن حذف Admin
        if self.users[user_id].role == Role.ADMIN:
            logger.error("Cannot delete admin user")
            return False
        
        user = self.users.pop(user_id)
        self._save_users()
        
        logger.info(f"Deleted user: {user.username}")
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """إحصائيات المستخدمين"""
        stats = {
            "total_users": len(self.users),
            "active_users": sum(1 for u in self.users.values() if u.is_active),
            "locked_users": sum(1 for u in self.users.values() if u.is_locked),
            "by_role": {}
        }
        
        for role in Role:
            count = sum(1 for u in self.users.values() if u.role == role)
            stats["by_role"][role.value] = count
        
        return stats


# Factory function
def create_rbac_manager(users_file: str = "database/users.json") -> RBACManager:
    """إنشاء مدير RBAC"""
    return RBACManager(users_file)
