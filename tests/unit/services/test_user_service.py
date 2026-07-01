"""
Unit Tests for UserService - اختبارات وحدة خدمة المستخدمين
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from backend.services.user_service import UserService


class TestUserService:
    """اختبارات خدمة إدارة المستخدمين والصلاحيات"""

    @pytest.fixture
    def service(self):
        """إنشاء نسخة جديدة من الخدمة مع محاكاة دوال التشفير"""
        with patch('backend.services.user_service.hash_password') as mock_hash, \
                patch('backend.services.user_service.verify_password') as mock_verify:
            mock_hash.side_effect = lambda p: f"hashed_{p}"
            mock_verify.side_effect = lambda p, h: h == f"hashed_{p}"
            yield UserService()

    def test_init(self, service):
        """اختبار تهيئة الخدمة والتأكد من القيم الافتراضية"""
        assert service.users == {}
        assert service.sessions == {}
        assert 'admin' in service.roles
        assert 'auditor' in service.roles
        assert 'accountant' in service.roles
        assert 'cfo' in service.roles
        assert 'external_auditor' in service.roles
        assert 'tax_reviewer' in service.roles
        assert 'all' in service.roles['admin']

    def test_create_user_success(self, service):
        """اختبار إنشاء مستخدم جديد بنجاح"""
        result = service.create_user("ahmed", "ahmed@example.com", "pass123", "admin", "Ahmed Ali", 1)
        assert result['success'] is True
        user = result['user']
        assert user['username'] == "ahmed"
        assert user['email'] == "ahmed@example.com"
        assert user['role'] == "admin"
        assert user['full_name'] == "Ahmed Ali"
        assert user['company_id'] == 1
        assert user['status'] == 'active'
        assert user['permissions'] == ['all']
        assert user['failed_login_attempts'] == 0
        assert user['locked_until'] is None
        assert 'password_hash' not in user
        assert 'user_id' in user

    def test_create_user_duplicate_username(self, service):
        """اختبار رفض إنشاء مستخدم باسم مستخدم مكرر"""
        service.create_user("ahmed", "ahmed@example.com", "pass123", "admin", "Ahmed", 1)
        result = service.create_user("ahmed", "other@example.com", "pass456", "auditor", "Other", 1)
        assert result['success'] is False
        assert 'already exists' in result['error']

    def test_create_user_duplicate_email(self, service):
        """اختبار رفض إنشاء مستخدم ببريد إلكتروني مكرر"""
        service.create_user("ahmed", "ahmed@example.com", "pass123", "admin", "Ahmed", 1)
        result = service.create_user("other", "ahmed@example.com", "pass456", "auditor", "Other", 1)
        assert result['success'] is False
        assert 'already exists' in result['error']

    def test_create_user_invalid_role(self, service):
        """اختبار رفض إنشاء مستخدم بدور غير معروف"""
        result = service.create_user("ahmed", "ahmed@example.com", "pass123", "superadmin", "Ahmed", 1)
        assert result['success'] is False
        assert result['error'] == 'Invalid role'

    def test_create_user_various_roles(self, service):
        """اختبار إنشاء مستخدمين بجميع الأدوار المدعومة"""
        roles = ['admin', 'auditor', 'accountant', 'cfo', 'external_auditor', 'tax_reviewer']
        for i, role in enumerate(roles):
            result = service.create_user(f"user{i}", f"user{i}@test.com", "pass", role, f"User{i}", i)
            assert result['success'] is True
            assert result['user']['role'] == role

    def test_authenticate_success(self, service):
        """اختبار مصادقة ناجحة مع إنشاء جلسة"""
        service.create_user("ahmed", "ahmed@example.com", "correctpass", "admin", "Ahmed", 1)
        result = service.authenticate("ahmed", "correctpass")
        assert result['success'] is True
        assert result['user']['username'] == "ahmed"
        assert 'session' in result
        session = result['session']
        assert session['session_id'].startswith('SES-')
        assert session['user_id'] == result['user']['user_id']
        assert 'created_at' in session
        assert 'expires_at' in session

    def test_authenticate_wrong_password(self, service):
        """اختبار مصادقة فاشلة بسبب كلمة مرور خاطئة"""
        service.create_user("ahmed", "ahmed@example.com", "correctpass", "admin", "Ahmed", 1)
        result = service.authenticate("ahmed", "wrongpass")
        assert result['success'] is False
        assert result['error'] == 'Invalid credentials'

    def test_authenticate_inactive_user(self, service):
        """اختبار مصادقة مستخدم غير نشط"""
        service.create_user("ahmed", "ahmed@example.com", "pass", "admin", "Ahmed", 1)
        user_id = list(service.users.keys())[0]
        service.update_user(user_id, {'status': 'inactive'})
        result = service.authenticate("ahmed", "pass")
        assert result['success'] is False
        assert result['error'] == 'Account is inactive'

    def test_authenticate_locked_account(self, service):
        """اختبار مصادقة حساب مقفول"""
        service.create_user("ahmed", "ahmed@example.com", "pass", "admin", "Ahmed", 1)
        user_id = list(service.users.keys())[0]
        service.users[user_id]['locked_until'] = datetime.now() + timedelta(minutes=15)
        result = service.authenticate("ahmed", "pass")
        assert result['success'] is False
        assert result['error'] == 'Account is locked'

    def test_authenticate_account_locking_after_5_failures(self, service):
        """اختبار قفل الحساب تلقائياً بعد 5 محاولات فاشلة"""
        service.create_user("ahmed", "ahmed@example.com", "correctpass", "admin", "Ahmed", 1)
        for i in range(5):
            result = service.authenticate("ahmed", "wrongpass")
            assert result['success'] is False
        user_id = list(service.users.keys())[0]
        assert service.users[user_id]['failed_login_attempts'] == 5
        assert service.users[user_id]['locked_until'] is not None
        result = service.authenticate("ahmed", "correctpass")
        assert result['success'] is False
        assert result['error'] == 'Account is locked'

    def test_authenticate_unlocks_after_lockout_expires(self, service):
        """اختبار فتح الحساب بعد انتهاء مدة القفل"""
        import backend.services.user_service as us_module
        original_dt = us_module.datetime
        fixed_now = datetime(2025, 6, 1, 12, 0, 0)
        with patch.object(us_module, 'datetime') as mock_dt:
            mock_dt.now.return_value = fixed_now
            mock_dt.side_effect = lambda *a, **kw: original_dt(*a, **kw) if a else fixed_now
            service.create_user("ahmed", "ahmed@example.com", "correctpass", "admin", "Ahmed", 1)
            for i in range(5):
                service.authenticate("ahmed", "wrongpass")
            result = service.authenticate("ahmed", "correctpass")
            assert result['success'] is False
        future_now = datetime(2025, 6, 1, 12, 16, 0)
        with patch.object(us_module, 'datetime') as mock_dt:
            mock_dt.now.return_value = future_now
            mock_dt.side_effect = lambda *a, **kw: original_dt(*a, **kw) if a else future_now
            result = service.authenticate("ahmed", "correctpass")
            assert result['success'] is True

    def test_authenticate_nonexistent_user(self, service):
        """اختبار مصادقة مستخدم غير موجود"""
        result = service.authenticate("nonexistent", "pass")
        assert result['success'] is False
        assert result['error'] == 'Invalid credentials'

    def test_logout_success(self, service):
        """اختبار تسجيل خروج ناجح"""
        service.create_user("ahmed", "ahmed@example.com", "pass", "admin", "Ahmed", 1)
        auth = service.authenticate("ahmed", "pass")
        session_id = auth['session']['session_id']
        assert service.logout(session_id) is True
        assert session_id not in service.sessions

    def test_logout_invalid_session(self, service):
        """اختبار تسجيل خروج بجلسة غير موجودة"""
        assert service.logout("INVALID-SESSION") is False

    def test_get_user_success(self, service):
        """اختبار الحصول على معلومات مستخدم موجود"""
        create_result = service.create_user("ahmed", "ahmed@example.com", "pass", "admin", "Ahmed", 1)
        user_id = create_result['user']['user_id']
        result = service.get_user(user_id)
        assert result['exists'] is True
        assert result['username'] == "ahmed"
        assert result['email'] == "ahmed@example.com"
        assert 'password_hash' not in result

    def test_get_user_not_found(self, service):
        """اختبار الحصول على مستخدم غير موجود"""
        result = service.get_user("NONEXISTENT")
        assert result['exists'] is False

    def test_update_user_success(self, service):
        """اختبار تحديث بيانات مستخدم بنجاح"""
        create_result = service.create_user("ahmed", "ahmed@example.com", "pass", "admin", "Ahmed", 1)
        user_id = create_result['user']['user_id']
        assert service.update_user(user_id, {'email': 'new@example.com', 'full_name': 'Ahmed Updated'}) is True
        updated = service.get_user(user_id)
        assert updated['email'] == 'new@example.com'
        assert updated['full_name'] == 'Ahmed Updated'
        assert updated['role'] == 'admin'

    def test_update_user_not_found(self, service):
        """اختبار تحديث مستخدم غير موجود"""
        assert service.update_user("NONEXISTENT", {'email': 'test@test.com'}) is False

    def test_update_user_role(self, service):
        """اختبار تحديث دور المستخدم وتحديث الصلاحيات"""
        create_result = service.create_user("ahmed", "ahmed@example.com", "pass", "accountant", "Ahmed", 1)
        user_id = create_result['user']['user_id']
        assert service.update_user(user_id, {'role': 'auditor'}) is True
        updated = service.get_user(user_id)
        assert updated['role'] == 'auditor'
        assert 'audit.write' in updated['permissions']
        assert 'audit.read' in updated['permissions']

    def test_update_user_disallowed_field(self, service):
        """اختبار عدم تحديث حقل غير مسموح به"""
        create_result = service.create_user("ahmed", "ahmed@example.com", "pass", "admin", "Ahmed", 1)
        user_id = create_result['user']['user_id']
        service.update_user(user_id, {'username': 'hacker'})
        result = service.get_user(user_id)
        assert result['username'] == 'ahmed'

    def test_update_user_invalid_role_ignored(self, service):
        """اختبار تجاهل تحديث بدور غير صحيح"""
        create_result = service.create_user("ahmed", "ahmed@example.com", "pass", "accountant", "Ahmed", 1)
        user_id = create_result['user']['user_id']
        service.update_user(user_id, {'role': 'superadmin'})
        updated = service.get_user(user_id)
        assert updated['role'] == 'accountant'

    def test_delete_user_success(self, service):
        """اختبار حذف مستخدم بنجاح"""
        create_result = service.create_user("ahmed", "ahmed@example.com", "pass", "admin", "Ahmed", 1)
        user_id = create_result['user']['user_id']
        assert service.delete_user(user_id) is True
        assert service.get_user(user_id)['exists'] is False

    def test_delete_user_not_found(self, service):
        """اختبار حذف مستخدم غير موجود"""
        assert service.delete_user("NONEXISTENT") is False

    def test_delete_user_removes_sessions(self, service):
        """اختبار حذف جميع جلسات المستخدم عند حذفه"""
        create_result = service.create_user("ahmed", "ahmed@example.com", "pass", "admin", "Ahmed", 1)
        user_id = create_result['user']['user_id']
        auth = service.authenticate("ahmed", "pass")
        session_id = auth['session']['session_id']
        assert session_id in service.sessions
        service.delete_user(user_id)
        assert session_id not in service.sessions

    def test_has_permission_admin_all(self, service):
        """اختبار أن المسؤول لديه جميع الصلاحيات"""
        create_result = service.create_user("ahmed", "ahmed@example.com", "pass", "admin", "Ahmed", 1)
        user_id = create_result['user']['user_id']
        assert service.has_permission(user_id, 'anything.any') is True
        assert service.has_permission(user_id, '') is True

    def test_has_permission_granted(self, service):
        """اختبار وجود صلاحية محددة للمستخدم"""
        create_result = service.create_user("ahmed", "ahmed@example.com", "pass", "auditor", "Ahmed", 1)
        user_id = create_result['user']['user_id']
        assert service.has_permission(user_id, 'audit.read') is True
        assert service.has_permission(user_id, 'reports.write') is True

    def test_has_permission_denied(self, service):
        """اختبار عدم وجود صلاحية للمستخدم"""
        create_result = service.create_user("ahmed", "ahmed@example.com", "pass", "accountant", "Ahmed", 1)
        user_id = create_result['user']['user_id']
        assert service.has_permission(user_id, 'audit.write') is False
        assert service.has_permission(user_id, 'executive.read') is False

    def test_has_permission_user_not_found(self, service):
        """اختبار صلاحية لمستخدم غير موجود"""
        assert service.has_permission("NONEXISTENT", "audit.read") is False

    def test_list_users_all(self, service):
        """اختبار قائمة جميع المستخدمين"""
        service.create_user("user1", "user1@test.com", "pass", "admin", "User1", 1)
        service.create_user("user2", "user2@test.com", "pass", "auditor", "User2", 2)
        users = service.list_users()
        assert len(users) == 2

    def test_list_users_by_company(self, service):
        """اختبار تصفية المستخدمين حسب معرف الشركة"""
        service.create_user("user1", "user1@test.com", "pass", "admin", "User1", 1)
        service.create_user("user2", "user2@test.com", "pass", "auditor", "User2", 2)
        users = service.list_users(company_id=1)
        assert len(users) == 1
        assert users[0]['company_id'] == 1

    def test_list_users_by_role(self, service):
        """اختبار تصفية المستخدمين حسب الدور"""
        service.create_user("user1", "user1@test.com", "pass", "admin", "User1", 1)
        service.create_user("user2", "user2@test.com", "pass", "auditor", "User2", 2)
        users = service.list_users(role='auditor')
        assert len(users) == 1
        assert users[0]['role'] == 'auditor'

    def test_list_users_no_password_hash(self, service):
        """اختبار عدم ظهور كلمة المرور المشفرة في قائمة المستخدمين"""
        service.create_user("user1", "user1@test.com", "pass", "admin", "User1", 1)
        service.create_user("user2", "user2@test.com", "pass", "auditor", "User2", 2)
        users = service.list_users()
        assert 'password_hash' not in users[0]
        assert 'password_hash' not in users[1]

    def test_list_users_empty(self, service):
        """اختبار قائمة المستخدمين عندما لا يوجد مستخدمين"""
        users = service.list_users()
        assert users == []

    def test_list_users_filter_no_match(self, service):
        """اختبار تصفية لا تطابق أي مستخدم"""
        service.create_user("user1", "user1@test.com", "pass", "admin", "User1", 1)
        users = service.list_users(company_id=999)
        assert users == []

    def test_get_session_valid(self, service):
        """اختبار الحصول على جلسة صالحة"""
        service.create_user("ahmed", "ahmed@example.com", "pass", "admin", "Ahmed", 1)
        auth = service.authenticate("ahmed", "pass")
        session_id = auth['session']['session_id']
        result = service.get_session(session_id)
        assert result['valid'] is True
        assert result['user_id'] == auth['user']['user_id']
        assert 'created_at' in result
        assert 'expires_at' in result

    def test_get_session_not_found(self, service):
        """اختبار الحصول على جلسة غير موجودة"""
        result = service.get_session("INVALID-SESSION")
        assert result['valid'] is False

    def test_get_session_expired(self, service):
        """اختبار جلسة منتهية الصلاحية"""
        import backend.services.user_service as us_module
        original_dt = us_module.datetime
        fixed_now = datetime(2025, 6, 1, 12, 0, 0)
        with patch.object(us_module, 'datetime') as mock_dt:
            mock_dt.now.return_value = fixed_now
            mock_dt.side_effect = lambda *a, **kw: original_dt(*a, **kw) if a else fixed_now
            service.create_user("ahmed", "ahmed@example.com", "pass", "admin", "Ahmed", 1)
            auth = service.authenticate("ahmed", "pass")
            session_id = auth['session']['session_id']
            result = service.get_session(session_id)
            assert result['valid'] is True
        future_now = datetime(2025, 6, 2, 0, 0, 0)
        with patch.object(us_module, 'datetime') as mock_dt:
            mock_dt.now.return_value = future_now
            mock_dt.side_effect = lambda *a, **kw: original_dt(*a, **kw) if a else future_now
            result = service.get_session(session_id)
            assert result['valid'] is False
            assert result.get('error') == 'Session expired'

    def test_change_password_success(self, service):
        """اختبار تغيير كلمة المرور بنجاح"""
        create_result = service.create_user("ahmed", "ahmed@example.com", "oldpass", "admin", "Ahmed", 1)
        user_id = create_result['user']['user_id']
        assert service.change_password(user_id, "oldpass", "newpass") is True
        assert service.users[user_id]['password_hash'] == "hashed_newpass"

    def test_change_password_wrong_old_password(self, service):
        """اختبار رفض تغيير كلمة المرور بسبب خطأ في كلمة المرور القديمة"""
        create_result = service.create_user("ahmed", "ahmed@example.com", "oldpass", "admin", "Ahmed", 1)
        user_id = create_result['user']['user_id']
        assert service.change_password(user_id, "wrongold", "newpass") is False
        assert service.users[user_id]['password_hash'] == "hashed_oldpass"

    def test_change_password_user_not_found(self, service):
        """اختبار تغيير كلمة المرور لمستخدم غير موجود"""
        assert service.change_password("NONEXISTENT", "old", "new") is False

    def test_authenticate_resets_failed_attempts_on_success(self, service):
        """اختبار إعادة تعيين عداد المحاولات الفاشلة بعد مصادقة ناجحة"""
        service.create_user("ahmed", "ahmed@example.com", "correctpass", "admin", "Ahmed", 1)
        for i in range(3):
            service.authenticate("ahmed", "wrongpass")
        user_id = list(service.users.keys())[0]
        assert service.users[user_id]['failed_login_attempts'] == 3
        service.authenticate("ahmed", "correctpass")
        assert service.users[user_id]['failed_login_attempts'] == 0
        assert service.users[user_id]['locked_until'] is None

    def test_create_user_empty_username(self, service):
        """اختبار إنشاء مستخدم باسم فارغ"""
        result = service.create_user("", "empty@test.com", "pass", "admin", "Empty", 1)
        assert result['success'] is True
        assert result['user']['username'] == ""

    def test_authenticate_empty_username(self, service):
        """اختبار مصادقة باسم مستخدم فارغ"""
        result = service.authenticate("", "pass")
        assert result['success'] is False

    def test_list_users_none_filters(self, service):
        """اختبار list_users مع تمرير None كمعاملات تصفية"""
        service.create_user("user1", "user1@test.com", "pass", "admin", "User1", 1)
        users = service.list_users(company_id=None, role=None)
        assert len(users) == 1
