"""
Pytest Configuration and Fixtures
==================================
Shared fixtures and configuration for all tests.
"""

import pytest
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

# Add project paths
sys.path.insert(0, '/workspace')
sys.path.insert(0, '/workspace/backend')
sys.path.insert(0, '/workspace/connectors')
sys.path.insert(0, '/workspace/agents')


@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture."""
    return {
        'database_url': 'sqlite:///test.db',
        'api_key': 'test_api_key_12345',
        'environment': 'testing',
        'debug': True
    }


@pytest.fixture
def sample_financial_data():
    """Sample financial data for testing."""
    return {
        'balance_sheet': {
            'assets': {'current': 100000, 'non_current': 400000},
            'liabilities': {'current': 50000, 'non_current': 150000},
            'equity': 300000
        },
        'income_statement': {
            'revenue': 500000,
            'expenses': 350000,
            'net_income': 150000
        },
        'cash_flow': {
            'operating': 180000,
            'investing': -50000,
            'financing': -30000
        }
    }


@pytest.fixture
def sample_audit_engagement():
    """Sample audit engagement data."""
    return {
        'engagement_id': 'ENG-2024-001',
        'client_name': 'Test Corporation',
        'period_start': '2024-01-01',
        'period_end': '2024-12-31',
        'status': 'in_progress',
        'team': [
            {'role': 'partner', 'name': 'John Smith'},
            {'role': 'manager', 'name': 'Jane Doe'},
            {'role': 'senior', 'name': 'Bob Johnson'}
        ]
    }


@pytest.fixture
def mock_api_client():
    """Mock API client for testing."""
    client = Mock()
    client.get.return_value = {'status': 'success', 'data': {}}
    client.post.return_value = {'status': 'created', 'id': '12345'}
    client.delete.return_value = {'status': 'deleted'}
    return client


@pytest.fixture
def mock_database_connection():
    """Mock database connection for testing."""
    conn = Mock()
    conn.execute.return_value = []
    conn.commit.return_value = None
    conn.close.return_value = None
    return conn


@pytest.fixture
def sample_users():
    """Sample user data for testing."""
    return [
        {'id': 1, 'username': 'admin', 'role': 'administrator', 'active': True},
        {'id': 2, 'username': 'auditor1', 'role': 'auditor', 'active': True},
        {'id': 3, 'username': 'viewer1', 'role': 'viewer', 'active': False}
    ]


@pytest.fixture
def sample_transactions():
    """Sample transaction data for testing."""
    return [
        {'id': 'TXN001', 'date': '2024-01-15', 'amount': 5000, 'type': 'revenue'},
        {'id': 'TXN002', 'date': '2024-01-16', 'amount': 2500, 'type': 'expense'},
        {'id': 'TXN003', 'date': '2024-01-17', 'amount': 7500, 'type': 'revenue'},
        {'id': 'TXN004', 'date': '2024-01-18', 'amount': 1000, 'type': 'expense'}
    ]


@pytest.fixture
def sample_compliance_requirements():
    """Sample compliance requirements for testing."""
    return {
        'ifrs': [
            {'standard': 'IFRS 15', 'description': 'Revenue from Contracts', 'applicable': True},
            {'standard': 'IFRS 16', 'description': 'Leases', 'applicable': True},
            {'standard': 'IAS 36', 'description': 'Impairment of Assets', 'applicable': False}
        ],
        'gaap': [
            {'standard': 'ASC 606', 'description': 'Revenue Recognition', 'applicable': True},
            {'standard': 'ASC 842', 'description': 'Leases', 'applicable': True}
        ],
        'sox': [
            {'section': '302', 'description': 'Corporate Responsibility', 'applicable': True},
            {'section': '404', 'description': 'Internal Controls', 'applicable': True}
        ]
    }


@pytest.fixture(autouse=True)
def reset_test_state():
    """Reset test state before each test."""
    # Setup code (runs before each test)
    yield
    # Teardown code (runs after each test)
    pass


# Custom markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "smoke: Smoke tests")
