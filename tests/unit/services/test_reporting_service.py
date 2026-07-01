"""
Tests for ReportingService - اختبارات خدمة توليد التقارير الاحترافية
"""

import json
import time
from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

import pytest

from backend.services.reporting_service import ReportingService

SAMPLE_FINDINGS = [
    {'severity': 'critical', 'finding_type': 'fraud', 'description': 'Material misstatement found', 'recommendation': 'Restate financials'},
    {'severity': 'high', 'finding_type': 'error', 'description': 'Revenue recognition error', 'recommendation': 'Adjust entries'},
    {'severity': 'medium', 'finding_type': 'compliance', 'description': 'Missing disclosure', 'recommendation': 'Add note'},
    {'severity': 'low', 'finding_type': 'risk', 'description': 'Minor control weakness', 'recommendation': 'Update policy'},
]


@pytest.fixture
def reporting_service():
    """إنشاء خدمة تقارير جديدة لكل اختبار"""
    return ReportingService()


@pytest.fixture
def sample_report(reporting_service):
    """إنشاء تقرير مراجعة نموذجي للاختبارات"""
    return reporting_service.create_audit_report('PROJ-001', 'financial', SAMPLE_FINDINGS)


class TestCreateAuditReport:
    """اختبارات إنشاء تقارير المراجعة"""

    def test_create_report_success(self, reporting_service):
        """إنشاء تقرير مراجعة بنجاح"""
        report = reporting_service.create_audit_report('PROJ-001', 'financial', SAMPLE_FINDINGS)

        assert report['report_id'].startswith('RPT-PROJ-001-')
        assert report['project_id'] == 'PROJ-001'
        assert report['report_type'] == 'financial'
        assert report['status'] == 'draft'
        assert report['total_findings'] == 4

    def test_create_report_empty_findings(self, reporting_service):
        """إنشاء تقرير بدون نتائج"""
        report = reporting_service.create_audit_report('PROJ-001', 'compliance', [])

        assert report['total_findings'] == 0
        assert report['findings_summary'] == {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}

    def test_create_report_without_recommendations(self, reporting_service):
        """إنشاء تقرير بدون توصيات"""
        report = reporting_service.create_audit_report('PROJ-001', 'financial', SAMPLE_FINDINGS, include_recommendations=False)

        assert report['include_recommendations'] is False

    def test_create_report_stores_internal(self, reporting_service):
        """التحقق من تخزين التقرير داخلياً"""
        report = reporting_service.create_audit_report('PROJ-001', 'tax', [])

        assert report['report_id'] in reporting_service.reports

    def test_create_report_findings_summary(self, reporting_service):
        """التحقق من ملخص النتائج في التقرير"""
        findings = [
            {'severity': 'critical'},
            {'severity': 'high'},
            {'severity': 'high'},
        ]
        report = reporting_service.create_audit_report('PROJ-001', 'financial', findings)

        assert report['findings_summary']['critical'] == 1
        assert report['findings_summary']['high'] == 2
        assert report['findings_summary']['medium'] == 0


class TestGenerateExecutiveSummary:
    """اختبارات توليد الملخص التنفيذي"""

    def test_generate_summary_success(self, reporting_service, sample_report):
        """توليد ملخص تنفيذي بنجاح"""
        summary = reporting_service.generate_executive_summary(sample_report['report_id'])

        assert summary['report_id'] == sample_report['report_id']
        assert 'executive_summary' in summary
        assert summary['executive_summary']['overview'] is not None

    def test_generate_summary_risk_level(self, reporting_service, sample_report):
        """التحقق من مستوى المخاطر في الملخص"""
        summary = reporting_service.generate_executive_summary(sample_report['report_id'])

        assert summary['executive_summary']['risk_level'] == 'high'

    def test_generate_summary_risk_level_low(self, reporting_service):
        """مستوى مخاطر منخفض عندما لا توجد نتائج critical"""
        report = reporting_service.create_audit_report('PROJ-002', 'financial', [
            {'severity': 'low'}
        ])
        summary = reporting_service.generate_executive_summary(report['report_id'])

        assert summary['executive_summary']['risk_level'] == 'medium'

    def test_generate_summary_overall_opinion(self, reporting_service, sample_report):
        """التحقق من الرأي العام في الملخص"""
        summary = reporting_service.generate_executive_summary(sample_report['report_id'])

        assert summary['executive_summary']['overall_opinion'] == 'qualified'

    def test_generate_summary_opinion_unqualified(self, reporting_service):
        """رأي غير متحفظ عندما لا توجد نتائج critical"""
        report = reporting_service.create_audit_report('PROJ-003', 'financial', [
            {'severity': 'low'}
        ])
        summary = reporting_service.generate_executive_summary(report['report_id'])

        assert summary['executive_summary']['overall_opinion'] == 'unqualified'

    def test_generate_summary_report_not_found(self, reporting_service):
        """ملخص لتقرير غير موجود"""
        summary = reporting_service.generate_executive_summary('NONEXISTENT')

        assert summary == {}

    def test_generate_summary_recommendations_count(self, reporting_service, sample_report):
        """التحقق من عدد التوصيات في الملخص"""
        summary = reporting_service.generate_executive_summary(sample_report['report_id'])

        assert summary['executive_summary']['recommendations_count'] == 4


class TestExportReport:
    """اختبارات تصدير التقارير"""

    @pytest.fixture
    def mock_pdf(self):
        """محاكاة توليد PDF"""
        with patch.object(ReportingService, '_generate_pdf', return_value=b'x' * 2048) as m:
            yield m

    @pytest.fixture
    def mock_excel(self):
        """محاكاة توليد Excel"""
        with patch.object(ReportingService, '_generate_excel', return_value=b'x' * 2048) as m:
            yield m

    def test_export_pdf(self, reporting_service, sample_report, mock_pdf):
        """تصدير التقرير بصيغة PDF"""
        with patch('builtins.open', mock_open()), \
                patch('os.makedirs') as mock_mkdir:
            result = reporting_service.export_report(sample_report['report_id'], 'pdf')

        assert result['success'] is True
        assert result['format'] == 'pdf'
        assert result['file_path'].endswith('.pdf')
        mock_pdf.assert_called_once()

    def test_export_html(self, reporting_service, sample_report):
        """تصدير التقرير بصيغة HTML"""
        with patch('builtins.open', mock_open()) as mock_file, \
                patch('os.makedirs') as mock_mkdir:
            result = reporting_service.export_report(sample_report['report_id'], 'html')

        assert result['success'] is True
        assert result['format'] == 'html'
        assert result['file_path'].endswith('.html')
        mock_file.assert_called_once()

    def test_export_json(self, reporting_service, sample_report):
        """تصدير التقرير بصيغة JSON"""
        with patch('builtins.open', mock_open()) as mock_file, \
                patch('os.makedirs') as mock_mkdir:
            result = reporting_service.export_report(sample_report['report_id'], 'json')

        assert result['success'] is True
        assert result['format'] == 'json'
        assert result['file_path'].endswith('.json')

    def test_export_excel(self, reporting_service, sample_report, mock_excel):
        """تصدير التقرير بصيغة Excel"""
        with patch('builtins.open', mock_open()), \
                patch('os.makedirs') as mock_mkdir:
            result = reporting_service.export_report(sample_report['report_id'], 'excel')

        assert result['success'] is True
        assert result['format'] == 'excel'
        mock_excel.assert_called_once()

    def test_export_xlsx(self, reporting_service, sample_report, mock_excel):
        """تصدير التقرير بصيغة xlsx"""
        with patch('builtins.open', mock_open()), \
                patch('os.makedirs') as mock_mkdir:
            result = reporting_service.export_report(sample_report['report_id'], 'xlsx')

        assert result['success'] is True
        assert result['format'] == 'xlsx'

    def test_export_report_not_found(self, reporting_service):
        """تصدير تقرير غير موجود"""
        result = reporting_service.export_report('NONEXISTENT', 'pdf')

        assert result['success'] is False
        assert 'Report not found' in result['error']

    def test_export_unsupported_format(self, reporting_service, sample_report):
        """تصدير بصيغة غير مدعومة"""
        result = reporting_service.export_report(sample_report['report_id'], 'docx')

        assert result['success'] is False
        assert 'Unsupported format: docx' in result['error']

    def test_export_updates_status(self, reporting_service, sample_report, mock_pdf):
        """التحقق من تحديث حالة التقرير بعد التصدير"""
        with patch('builtins.open', mock_open()), \
                patch('os.makedirs'):
            reporting_service.export_report(sample_report['report_id'], 'pdf')

        report = reporting_service.reports[sample_report['report_id']]
        assert report['status'] == 'finalized'
        assert report['generated_at'] is not None

    def test_export_creates_directory(self, reporting_service, sample_report, mock_pdf):
        """التحقق من إنشاء دليل التصدير"""
        with patch('builtins.open', mock_open()), \
                patch('os.makedirs') as mock_mkdir:
            reporting_service.export_report(sample_report['report_id'], 'pdf')

        mock_mkdir.assert_called_once()

    def test_export_html_content(self, reporting_service, sample_report):
        """التحقق من محتوى HTML المصدر"""
        with patch('os.makedirs'):
            with patch('builtins.open', mock_open()) as mock_file:
                reporting_service.export_report(sample_report['report_id'], 'html')

        handle = mock_file()
        written_content = ''.join(c.args[0] for c in handle.write.call_args_list)
        assert '<!DOCTYPE html>' in written_content
        assert 'Audit Report' in written_content
        assert 'Material misstatement found' in written_content

    def test_export_json_content(self, reporting_service, sample_report):
        """التحقق من محتوى JSON المصدر"""
        with patch('os.makedirs'):
            with patch('builtins.open', mock_open()) as mock_file:
                reporting_service.export_report(sample_report['report_id'], 'json')

        handle = mock_file()
        written_content = ''.join(c.args[0] for c in handle.write.call_args_list)
        parsed = json.loads(written_content)
        assert parsed['header']['report_id'] == sample_report['report_id']
        assert parsed['risk_assessment']['risk_level'] == 'high'

    def test_export_returns_file_size(self, reporting_service, sample_report, mock_pdf):
        """التحقق من إرجاع حجم الملف بعد التصدير"""
        with patch('builtins.open', mock_open()), \
                patch('os.makedirs'):
            result = reporting_service.export_report(sample_report['report_id'], 'pdf')

        assert 'file_size_kb' in result
        assert result['file_size_kb'] > 0


class TestListReports:
    """اختبارات قائمة التقارير"""

    def test_list_reports_empty(self, reporting_service):
        """قائمة فارغة عند عدم وجود تقارير"""
        assert reporting_service.list_reports() == []

    def test_list_reports_all(self, reporting_service):
        """قائمة بجميع التقارير"""
        reporting_service.create_audit_report('PROJ-001', 'financial', [])
        reporting_service.create_audit_report('PROJ-002', 'compliance', [])

        reports = reporting_service.list_reports()
        assert len(reports) == 2

    def test_list_reports_filter_by_project(self, reporting_service):
        """تصفية التقارير حسب المشروع"""
        r1 = reporting_service.create_audit_report('PROJ-001', 'financial', [])
        time.sleep(1.01)
        r2 = reporting_service.create_audit_report('PROJ-001', 'tax', [])
        r3 = reporting_service.create_audit_report('PROJ-002', 'compliance', [])

        reports = reporting_service.list_reports(project_id='PROJ-001')
        assert len(reports) == 2

    def test_list_reports_filter_no_match(self, reporting_service):
        """تصفية لا تتطابق مع أي تقرير"""
        reporting_service.create_audit_report('PROJ-001', 'financial', [])
        reports = reporting_service.list_reports(project_id='NONEXISTENT')

        assert reports == []
