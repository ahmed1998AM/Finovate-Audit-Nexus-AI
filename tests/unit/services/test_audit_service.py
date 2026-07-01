"""
Tests for AuditService - اختبارات خدمة إدارة مشاريع المراجعة والتدقيق
"""

from datetime import datetime
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest

from backend.services.audit_service import AuditService


@pytest.fixture
def audit_service():
    """إنشاء خدمة مراجعة مع مكونات وهمية"""
    with patch('backend.services.audit_service._get_db_manager') as mock_db_cls, \
            patch('backend.services.audit_service._get_chief_agent') as mock_chief_cls:
        mock_db_cls.return_value = MagicMock()
        mock_chief_cls.return_value = MagicMock()
        service = AuditService()
        yield service


class TestCreateAuditProject:
    """اختبارات إنشاء مشاريع المراجعة"""

    def test_create_project_success(self, audit_service, sample_project_params):
        """إنشاء مشروع مراجعة بنجاح"""
        project = audit_service.create_audit_project(**sample_project_params)

        assert project['project_name'] == 'Test Audit Project'
        assert project['company_id'] == 1
        assert project['audit_type'] == 'financial'
        assert project['status'] == 'planning'
        assert project['progress'] == 0
        assert project['project_id'].startswith('AUD-')

    def test_create_project_generates_unique_ids(self, audit_service, sample_project_params):
        """إنشاء مشروعين بمعرفين مختلفين"""
        p1 = audit_service.create_audit_project(**sample_project_params)
        p2 = audit_service.create_audit_project(**sample_project_params)

        assert p1['project_id'] != p2['project_id']

    def test_create_project_various_audit_types(self, audit_service, sample_project_params):
        """إنشاء مشاريع بأنواع مراجعة مختلفة"""
        for audit_type in ['financial', 'tax', 'fraud', 'compliance']:
            params = {**sample_project_params, 'audit_type': audit_type}
            project = audit_service.create_audit_project(**params)
            assert project['audit_type'] == audit_type

    def test_create_project_stores_in_active(self, audit_service, sample_project_params):
        """تخزين المشروع في active_projects بعد الإنشاء"""
        project = audit_service.create_audit_project(**sample_project_params)
        assert project['project_id'] in audit_service.active_projects

    def test_create_project_with_empty_team(self, audit_service, sample_project_params):
        """إنشاء مشروع بفريق فارغ"""
        params = {**sample_project_params, 'team_members': []}
        project = audit_service.create_audit_project(**params)
        assert project['team_members'] == []


class TestUpdateProjectStatus:
    """اختبارات تحديث حالة المشروع"""

    def test_update_status_success(self, audit_service, sample_project_params):
        """تحديث حالة المشروع بنجاح"""
        project = audit_service.create_audit_project(**sample_project_params)
        result = audit_service.update_project_status(project['project_id'], 'in_progress')

        assert result is True
        assert audit_service.active_projects[project['project_id']]['status'] == 'in_progress'

    def test_update_status_with_progress(self, audit_service, sample_project_params):
        """تحديث حالة المشروع مع نسبة تقدم"""
        project = audit_service.create_audit_project(**sample_project_params)
        audit_service.update_project_status(project['project_id'], 'in_progress', 50.0)

        assert audit_service.active_projects[project['project_id']]['progress'] == 50.0

    def test_update_status_clamps_progress_above_100(self, audit_service, sample_project_params):
        """تثبيت نسبة التقدم عند 100 إذا تجاوزت"""
        project = audit_service.create_audit_project(**sample_project_params)
        audit_service.update_project_status(project['project_id'], 'completed', 150.0)

        assert audit_service.active_projects[project['project_id']]['progress'] == 100

    def test_update_status_clamps_progress_below_0(self, audit_service, sample_project_params):
        """تثبيت نسبة التقدم عند 0 إذا كانت سالبة"""
        project = audit_service.create_audit_project(**sample_project_params)
        audit_service.update_project_status(project['project_id'], 'planning', -10.0)

        assert audit_service.active_projects[project['project_id']]['progress'] == 0

    def test_update_status_invalid_project(self, audit_service):
        """تحديث حالة مشروع غير موجود"""
        result = audit_service.update_project_status('NONEXISTENT', 'completed')

        assert result is False

    def test_update_status_transitions(self, audit_service, sample_project_params):
        """التحقق من انتقالات الحالة المختلفة"""
        project = audit_service.create_audit_project(**sample_project_params)
        transitions = ['planning', 'in_progress', 'review', 'completed']
        for status in transitions:
            audit_service.update_project_status(project['project_id'], status)
            assert audit_service.active_projects[project['project_id']]['status'] == status


class TestAddFinding:
    """اختبارات إضافة نتائج المراجعة"""

    def test_add_finding_success(self, audit_service, sample_project_params, sample_finding_params):
        """إضافة نتيجة مراجعة بنجاح"""
        project = audit_service.create_audit_project(**sample_project_params)
        finding = audit_service.add_finding(project['project_id'], **sample_finding_params)

        assert finding['finding_id'].startswith('FND-')
        assert finding['finding_type'] == 'error'
        assert finding['severity'] == 'medium'
        assert finding['status'] == 'open'
        assert finding['reviewed_by'] is None

    def test_add_finding_various_severities(self, audit_service, sample_project_params, sample_finding_params):
        """إضافة نتائج بدرجات خطورة مختلفة"""
        project = audit_service.create_audit_project(**sample_project_params)
        for severity in ['low', 'medium', 'high', 'critical']:
            params = {**sample_finding_params, 'severity': severity}
            finding = audit_service.add_finding(project['project_id'], **params)
            assert finding['severity'] == severity

    def test_add_finding_various_types(self, audit_service, sample_project_params, sample_finding_params):
        """إضافة نتائج بأنواع مختلفة"""
        project = audit_service.create_audit_project(**sample_project_params)
        for ftype in ['error', 'fraud', 'compliance', 'risk']:
            params = {**sample_finding_params, 'finding_type': ftype}
            finding = audit_service.add_finding(project['project_id'], **params)
            assert finding['finding_type'] == ftype

    def test_add_finding_no_affected_accounts(self, audit_service, sample_project_params, sample_finding_params):
        """إضافة نتيجة بدون حسابات متأثرة"""
        project = audit_service.create_audit_project(**sample_project_params)
        params = {**sample_finding_params, 'affected_accounts': None}
        finding = audit_service.add_finding(project['project_id'], **params)

        assert finding['affected_accounts'] == []

    def test_add_finding_invalid_project(self, audit_service, sample_finding_params):
        """إضافة نتيجة لمشروع غير موجود"""
        finding = audit_service.add_finding('NONEXISTENT', **sample_finding_params)

        assert finding == {}

    def test_add_finding_multiple_findings(self, audit_service, sample_project_params, sample_finding_params):
        """إضافة نتائج متعددة لنفس المشروع"""
        project = audit_service.create_audit_project(**sample_project_params)
        for i in range(3):
            finding = audit_service.add_finding(project['project_id'], **sample_finding_params)
            assert finding['finding_id'] != ''

        assert len(audit_service.active_projects[project['project_id']]['findings']) == 3


class TestGetProjectSummary:
    """اختبارات الحصول على ملخص المشروع"""

    def test_get_summary_success(self, audit_service, sample_project_params):
        """الحصول على ملخص مشروع بدون نتائج"""
        project = audit_service.create_audit_project(**sample_project_params)
        summary = audit_service.get_project_summary(project['project_id'])

        assert summary['project_id'] == project['project_id']
        assert summary['project_name'] == 'Test Audit Project'
        assert summary['total_findings'] == 0
        assert summary['findings_by_severity'] == {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}

    def test_get_summary_with_findings(self, audit_service, sample_project_params, sample_finding_params):
        """الحصول على ملخص مشروع مع نتائج"""
        project = audit_service.create_audit_project(**sample_project_params)
        for severity in ['critical', 'high', 'medium', 'low']:
            params = {**sample_finding_params, 'severity': severity}
            audit_service.add_finding(project['project_id'], **params)

        summary = audit_service.get_project_summary(project['project_id'])

        assert summary['total_findings'] == 4
        assert summary['findings_by_severity'] == {'critical': 1, 'high': 1, 'medium': 1, 'low': 1}

    def test_get_summary_invalid_project(self, audit_service):
        """الحصول على ملخص مشروع غير موجود"""
        summary = audit_service.get_project_summary('NONEXISTENT')

        assert summary == {}

    def test_get_summary_findings_by_type(self, audit_service, sample_project_params, sample_finding_params):
        """التحقق من تصنيف النتائج حسب النوع"""
        project = audit_service.create_audit_project(**sample_project_params)
        for ftype in ['error', 'fraud', 'compliance', 'risk']:
            params = {**sample_finding_params, 'finding_type': ftype}
            audit_service.add_finding(project['project_id'], **params)

        summary = audit_service.get_project_summary(project['project_id'])

        assert summary['findings_by_type'] == {'error': 1, 'fraud': 1, 'compliance': 1, 'risk': 1}


class TestListProjects:
    """اختبارات قائمة مشاريع المراجعة"""

    def test_list_projects_empty(self, audit_service):
        """قائمة فارغة عند عدم وجود مشاريع"""
        assert audit_service.list_projects() == []

    def test_list_projects_all(self, audit_service, sample_project_params):
        """قائمة بجميع المشاريع"""
        audit_service.create_audit_project(**sample_project_params)
        audit_service.create_audit_project(**{**sample_project_params, 'company_id': 2})

        projects = audit_service.list_projects()
        assert len(projects) == 2

    def test_list_projects_filter_by_company(self, audit_service, sample_project_params):
        """تصفية المشاريع حسب الشركة"""
        audit_service.create_audit_project(**sample_project_params)
        audit_service.create_audit_project(**{**sample_project_params, 'company_id': 2})

        projects = audit_service.list_projects(company_id=1)
        assert len(projects) == 1
        assert projects[0]['company_id'] == 1

    def test_list_projects_filter_by_status(self, audit_service, sample_project_params):
        """تصفية المشاريع حسب الحالة"""
        p1 = audit_service.create_audit_project(**sample_project_params)
        p2 = audit_service.create_audit_project(**{**sample_project_params, 'project_name': 'Second'})
        audit_service.update_project_status(p2['project_id'], 'in_progress')

        projects = audit_service.list_projects(status='planning')
        assert len(projects) == 1
        assert projects[0]['project_id'] == p1['project_id']

    def test_list_projects_filter_by_both(self, audit_service, sample_project_params):
        """تصفية المشاريع حسب الشركة والحالة معاً"""
        p1 = audit_service.create_audit_project(**sample_project_params)
        audit_service.update_project_status(p1['project_id'], 'in_progress')
        audit_service.create_audit_project(**{**sample_project_params, 'company_id': 2})

        projects = audit_service.list_projects(company_id=1, status='in_progress')
        assert len(projects) == 1


class TestCloseProject:
    """اختبارات إغلاق المشاريع"""

    def test_close_project_success(self, audit_service, sample_project_params):
        """إغلاق مشروع بنجاح"""
        project = audit_service.create_audit_project(**sample_project_params)
        result = audit_service.close_project(project['project_id'], 'Final report content')

        assert result is True
        closed = audit_service.active_projects[project['project_id']]
        assert closed['status'] == 'closed'
        assert closed['progress'] == 100
        assert closed['final_report'] == 'Final report content'
        assert 'closed_at' in closed

    def test_close_project_invalid_project(self, audit_service):
        """إغلاق مشروع غير موجود"""
        result = audit_service.close_project('NONEXISTENT', 'report')
        assert result is False

    def test_close_project_updates_timestamps(self, audit_service, sample_project_params):
        """التحقق من تحديث الطوابع الزمنية عند الإغلاق"""
        project = audit_service.create_audit_project(**sample_project_params)
        original_updated = project['updated_at']
        audit_service.close_project(project['project_id'], 'report')

        closed = audit_service.active_projects[project['project_id']]
        assert closed['updated_at'] >= original_updated


class TestRunFullAIAudit:
    """اختبارات تشغيل التدقيق الكامل بالذكاء الاصطناعي"""

    @pytest.fixture
    def mock_sap_connector(self):
        """إنشاء موصل SAP وهمي"""
        with patch('connectors.sap_connector.connector.SAPErpConnector') as mock_cls, \
                patch('connectors.sap_connector.connector.SAPConnectionConfig') as mock_cfg:
            instance = MagicMock()
            instance.connect.return_value = True
            instance.get_journal_entries.return_value = [{'id': 1, 'amount': 5000}]
            instance.get_financial_statements.return_value = {'total_revenue': 100000}
            mock_cls.return_value = instance
            mock_cfg.return_value = MagicMock()
            yield instance

    @pytest.fixture
    def mock_db(self):
        """مدير قاعدة بيانات وهمي مع session"""
        db = MagicMock()
        session = MagicMock()
        db.get_session.return_value = session
        return db, session

    @pytest.fixture
    def mock_chief(self):
        """وكيل رئيسي وهمي"""
        agent = MagicMock()
        agent.run_audit_workflow = AsyncMock()
        agent.run_audit_workflow.return_value = {
            'core_results': {
                'fraud_agent': {
                    'fraud_indicators': [{'type': 'anomaly', 'score': 0.85}]
                }
            },
            'risk_assessment': {
                'overall_risk': 'medium',
                'score': 65
            }
        }
        return agent

    @pytest.fixture
    def service_with_mocks(self, mock_db, mock_chief):
        """خدمة مراجعة مع مكونات وهمية للتدقيق الكامل"""
        db, _ = mock_db
        with patch('backend.services.audit_service._get_db_manager') as mock_get_db, \
                patch('backend.services.audit_service._get_chief_agent') as mock_get_chief:
            mock_get_db.return_value = db
            mock_get_chief.return_value = mock_chief
            service = AuditService()
        service.db_manager = db
        service.chief_agent = mock_chief
        return service

    @pytest.mark.asyncio
    async def test_run_full_audit_success(self, service_with_mocks, mock_sap_connector):
        """تشغيل التدقيق الكامل بنجاح"""
        with patch.dict('os.environ', {
            'SAP_HOST': 'test.sap.com',
            'SAP_SYSTEM_NUMBER': '01',
            'SAP_CLIENT': '200',
            'SAP_USERNAME': 'test_user',
            'SAP_PASSWORD': 'test_pass'
        }):
            result = await service_with_mocks.run_full_ai_audit('1000', '2024', 1)

        assert result is not None
        assert 'risk_assessment' in result
        assert result['risk_assessment']['overall_risk'] == 'medium'
        mock_sap_connector.connect.assert_called_once()
        mock_sap_connector.get_journal_entries.assert_called_once_with('1000', '2024')

    @pytest.mark.asyncio
    async def test_run_full_audit_calls_db_save(self, service_with_mocks, mock_sap_connector, mock_db):
        """التحقق من حفظ البيانات في قاعدة البيانات"""
        db, session = mock_db

        with patch.dict('os.environ', {}, clear=True):
            await service_with_mocks.run_full_ai_audit('1000', '2024', 1)

        db.save_financial_data.assert_called_once_with(session, ANY, 'SAP')
        db.save_anomalies.assert_called_once()
        db.save_risk_assessment.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_full_audit_closes_session(self, service_with_mocks, mock_sap_connector, mock_db):
        """التحقق من إغلاق جلسة قاعدة البيانات بعد التشغيل"""
        _, session = mock_db

        with patch.dict('os.environ', {}, clear=True):
            await service_with_mocks.run_full_ai_audit('1000', '2024', 1)

        session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_full_audit_closes_session_on_error(self, service_with_mocks, mock_sap_connector, mock_db):
        """التحقق من إغلاق الجلسة حتى عند حدوث خطأ"""
        _, session = mock_db
        mock_sap_connector.get_journal_entries.side_effect = Exception('Connection failed')

        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(Exception, match='Connection failed'):
                await service_with_mocks.run_full_ai_audit('1000', '2024', 1)

        session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_full_audit_without_fraud_results(self, service_with_mocks, mock_sap_connector, mock_db):
        """تشغيل التدقيق بدون نتائج احتيال"""
        service_with_mocks.chief_agent.run_audit_workflow.return_value = {
            'core_results': {},
            'risk_assessment': {'overall_risk': 'low'}
        }

        with patch.dict('os.environ', {}, clear=True):
            result = await service_with_mocks.run_full_ai_audit('1000', '2024', 1)

        assert result['core_results'] == {}

    @pytest.mark.asyncio
    async def test_run_full_audit_uses_env_vars(self, service_with_mocks, mock_sap_connector):
        """التحقق من استخدام متغيرات البيئة في تكوين الاتصال"""
        with patch.dict('os.environ', {
            'SAP_HOST': 'prod.sap.com',
            'SAP_SYSTEM_NUMBER': '10',
        }, clear=True):
            await service_with_mocks.run_full_ai_audit('2000', '2025', 2)

        mock_sap_connector.get_journal_entries.assert_called_once_with('2000', '2025')
