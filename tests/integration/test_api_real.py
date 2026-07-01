"""
Finovate Audit Nexus AI - API Integration Tests
اختبارات API حقيقية مع httpx AsyncClient
"""

import os

os.environ["DATABASE_URL"] = "sqlite:///./test_finovate.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["ENVIRONMENT"] = "test"

import httpx
import pytest
from backend.main import app
from backend.api.endpoints.auth import create_access_token
from backend.database import get_db
from backend.database.models import Base
from datetime import timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class MockUser:
    def __init__(self):
        self.id = 1
        self.username = "test_admin"
        self.email = "admin@test.com"
        self.role = "admin"
        self.is_active = True


mock_user = MockUser()
transport = httpx.ASGITransport(app=app)

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_finovate.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
def auth_token():
    """Create a test JWT token."""
    return create_access_token(data={"sub": "test_admin", "role": "admin"}, expires_delta=timedelta(hours=1))


class TestHealthEndpoints:
    def test_health_check(self):
        app.dependency_overrides.clear()
        async def _test():
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
                r = await c.get("/api/health")
                assert r.status_code == 200
                assert r.json()["status"] == "healthy"
        import asyncio
        asyncio.run(_test())

    def test_root(self):
        async def _test():
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
                r = await c.get("/")
                assert r.status_code == 200
        import asyncio
        asyncio.run(_test())

    def test_api_root(self):
        async def _test():
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
                r = await c.get("/api")
                assert r.status_code == 200
        import asyncio
        asyncio.run(_test())


class TestConnectorAPI:
    def setup_method(self):
        from backend.api.auth_middleware import get_current_user
        app.dependency_overrides[get_current_user] = lambda: mock_user

    def teardown_method(self):
        app.dependency_overrides.clear()

    def _headers(self):
        return {"Authorization": f"Bearer test-token"}

    def test_list_connectors_authorized(self):
        async def _test():
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
                r = await c.get("/api/v1/connectors", headers=self._headers())
                assert r.status_code == 200
        import asyncio
        asyncio.run(_test())

    def test_notification_channels(self):
        async def _test():
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
                r = await c.get("/api/v1/notifications/channels", headers=self._headers())
                assert r.status_code == 200
        import asyncio
        asyncio.run(_test())

    def test_notification_history(self):
        async def _test():
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
                r = await c.get("/api/v1/notifications/history", headers=self._headers())
                assert r.status_code == 200
        import asyncio
        asyncio.run(_test())

    def test_task_list(self):
        async def _test():
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
                r = await c.get("/api/v1/tasks", headers=self._headers())
                assert r.status_code == 200
        import asyncio
        asyncio.run(_test())

    def test_webhooks_list(self):
        async def _test():
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
                r = await c.get("/api/v1/webhooks", headers=self._headers())
                assert r.status_code == 200
        import asyncio
        asyncio.run(_test())


class TestSwaggerDocs:
    def test_swagger_ui(self):
        async def _test():
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
                r = await c.get("/api/docs")
                assert r.status_code == 200
                assert "swagger" in r.text.lower()
        import asyncio
        asyncio.run(_test())

    def test_redoc_ui(self):
        async def _test():
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
                r = await c.get("/api/redoc")
                assert r.status_code == 200
                assert "redoc" in r.text.lower()
        import asyncio
        asyncio.run(_test())

    def test_openapi_spec(self):
        async def _test():
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
                r = await c.get("/api/openapi.json")
                assert r.status_code == 200
                spec = r.json()
                assert spec["info"]["title"] == "Finovate Audit Nexus AI"
                assert spec["info"]["version"] == "2.0.0"
        import asyncio
        asyncio.run(_test())


class TestAuthAPI:
    """Test authentication endpoints with test database."""
    
    def test_register_user(self, test_db):
        """Test user registration."""
        async def _test():
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
                r = await c.post("/api/v1/auth/register", json={
                    "username": "newuser",
                    "email": "newuser@test.com",
                    "password": "SecurePass123!",
                    "role": "auditor"
                })
                assert r.status_code in [200, 201]
        import asyncio
        asyncio.run(_test())
    
    def test_login_success(self, test_db):
        """Test successful login."""
        async def _test():
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
                # First register
                await c.post("/api/v1/auth/register", json={
                    "username": "loginuser",
                    "email": "login@test.com",
                    "password": "LoginPass123!",
                    "role": "auditor"
                })
                # Then login
                r = await c.post("/api/v1/auth/login", json={
                    "username": "loginuser",
                    "password": "LoginPass123!"
                })
                assert r.status_code == 200
                data = r.json()
                assert "access_token" in data
                assert data["user_info"]["username"] == "loginuser"
        import asyncio
        asyncio.run(_test())
    
    def test_login_invalid_credentials(self, test_db):
        """Test login with invalid credentials."""
        async def _test():
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
                r = await c.post("/api/v1/auth/login", json={
                    "username": "nonexistent",
                    "password": "wrongpass"
                })
                assert r.status_code == 401
        import asyncio
        asyncio.run(_test())


class TestAuditProjectsAPI:
    """Test audit projects endpoints with test database."""
    
    def setup_method(self):
        from backend.api.auth_middleware import get_current_user
        app.dependency_overrides[get_current_user] = lambda: mock_user
    
    def teardown_method(self):
        app.dependency_overrides.clear()
    
    def _headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_create_audit_project(self, test_db, auth_token):
        """Test creating an audit project."""
        async def _test():
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
                r = await c.post("/api/v1/audit-projects/", 
                    headers=self._headers(auth_token),
                    json={
                        "project_name": "Test Audit Project",
                        "company_id": 1,
                        "audit_type": "financial",
                        "start_date": "2024-01-01",
                        "end_date": "2024-12-31"
                    })
                assert r.status_code in [200, 201]
        import asyncio
        asyncio.run(_test())
    
    def test_list_audit_projects(self, test_db, auth_token):
        """Test listing audit projects."""
        async def _test():
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
                r = await c.get("/api/v1/audit-projects/", 
                    headers=self._headers(auth_token))
                assert r.status_code == 200
                data = r.json()
                assert isinstance(data, list) or isinstance(data.get("data"), list)
        import asyncio
        asyncio.run(_test())


class TestFindingsAPI:
    """Test findings endpoints with test database."""
    
    def setup_method(self):
        from backend.api.auth_middleware import get_current_user
        app.dependency_overrides[get_current_user] = lambda: mock_user
    
    def teardown_method(self):
        app.dependency_overrides.clear()
    
    def _headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_list_findings(self, test_db, auth_token):
        """Test listing audit findings."""
        async def _test():
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
                r = await c.get("/api/v1/findings/", 
                    headers=self._headers(auth_token))
                assert r.status_code == 200
                data = r.json()
                assert isinstance(data, list)
        import asyncio
        asyncio.run(_test())
