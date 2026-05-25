"""
Pytest Configuration and Fixtures
==================================
Shared fixtures and configuration for all tests.
"""

import pytest
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

import types


def _install_test_dependency_shims():
    """Install minimal shims for optional third-party deps unavailable in CI."""
    if 'loguru' not in sys.modules:
        m = types.ModuleType('loguru')
        class _Logger:
            def __getattr__(self, _):
                return lambda *a, **k: None
        m.logger = _Logger()
        sys.modules['loguru'] = m

    if 'numpy' not in sys.modules:
        m = types.ModuleType('numpy')
        m.mean = lambda values: (sum(values) / len(values)) if values else 0.0
        m.std = lambda values: 0.0
        m.array = lambda values: list(values)
        class _Random:
            @staticmethod
            def rand(*shape):
                total = 1
                for s in shape:
                    total *= s
                return [0.0] * total
        m.random = _Random
        sys.modules['numpy'] = m

    if 'pandas' not in sys.modules:
        m = types.ModuleType('pandas')
        class DataFrame(list):
            def __init__(self, data=None, *args, **kwargs):
                super().__init__(data or [])
        class Series(list):
            pass
        m.DataFrame = DataFrame
        m.Series = Series
        m.to_datetime = lambda value, *args, **kwargs: value
        sys.modules['pandas'] = m

    if 'requests' not in sys.modules:
        m = types.ModuleType('requests')
        class Response:
            def __init__(self, status_code=200, data=None):
                self.status_code = status_code
                self._data = data or {}
                self.text = str(self._data)
            def json(self):
                return self._data
        m.Response = Response
        m.get = m.post = m.put = m.delete = lambda *args, **kwargs: Response()
        sys.modules['requests'] = m

    if 'authlib' not in sys.modules:
        authlib = types.ModuleType('authlib')
        integrations = types.ModuleType('authlib.integrations')
        requests_client = types.ModuleType('authlib.integrations.requests_client')
        class OAuth2Session:
            def __init__(self, *args, **kwargs):
                pass
        requests_client.OAuth2Session = OAuth2Session
        sys.modules['authlib'] = authlib
        sys.modules['authlib.integrations'] = integrations
        sys.modules['authlib.integrations.requests_client'] = requests_client


def _should_install_test_shims() -> bool:
    """Allow disabling shims in strict environments via env var."""
    import os
    return os.getenv("FINOVATE_DISABLE_TEST_SHIMS", "0") != "1"


if _should_install_test_shims():
    _install_test_dependency_shims()

# Add project paths
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
for rel in ('', 'backend', 'connectors', 'agents'):
    candidate = str(REPO_ROOT / rel) if rel else str(REPO_ROOT)
    if candidate not in sys.path:
        sys.path.insert(0, candidate)


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
