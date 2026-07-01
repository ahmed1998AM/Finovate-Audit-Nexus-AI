"""
Shared fixtures and configuration for service-level unit tests.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def sample_project_params():
    """معلمات مشروع مراجعة نموذجية للاختبارات"""
    return {
        'company_id': 1,
        'project_name': 'Test Audit Project',
        'audit_type': 'financial',
        'start_date': datetime(2024, 1, 1),
        'end_date': datetime(2024, 12, 31),
        'team_members': [1, 2, 3],
        'scope': {'departments': ['finance', 'it']}
    }


@pytest.fixture
def sample_finding_params():
    """معلمات نتيجة مراجعة نموذجية للاختبارات"""
    return {
        'finding_type': 'error',
        'severity': 'medium',
        'description': 'Misstatement in revenue recognition',
        'evidence': ['journal_entry_123', 'invoice_456'],
        'recommendation': 'Adjust revenue recognition policy',
        'affected_accounts': ['4000- Revenue', '1200- AR']
    }


@pytest.fixture
def mock_connector_instance():
    """instance موصل وهمي يتم إرجاعه من _instantiate_connector"""
    inst = MagicMock()
    inst.connect.return_value = True
    inst.disconnect.return_value = True
    inst.is_connected = True
    inst.test_connection.return_value = {'success': True, 'connected': True}
    inst.get_health_status.return_value = {'connector_id': 'test', 'status': 'healthy'}
    inst.get_journal_entries.return_value = [{'id': 1, 'amount': 1000}]
    inst.get_trial_balance.return_value = [{'account': '1000', 'balance': 5000}]
    inst.get_financial_statements.return_value = {'total_assets': 100000}
    inst.get_accounts.return_value = [{'code': '1000', 'name': 'Cash'}]
    return inst
