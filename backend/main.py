"""
Finovate Audit Nexus AI - FastAPI Application
Main application entry point
Enterprise AI Financial Audit & Intelligence Platform
"""

import os
from contextlib import asynccontextmanager

import sqlalchemy as sa
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from backend.api.auth_middleware import get_current_user
from backend.api.endpoints import agents as endpoints_agents
from backend.api.endpoints import (
    audit_projects,
    auth,
    backups,
    companies,
    connectors,
    dashboard,
    documents,
    findings,
    notifications,
    predictive,
    reports,
    ws,
)
from backend.api.endpoints import tasks as task_endpoints
from backend.api.endpoints import webhooks_api as webhook_endpoints
from backend.api.logging_middleware import RequestLogMiddleware
from backend.api.rate_limit import RateLimitMiddleware
from backend.api.routes import ai_providers, audits
from backend.database import get_db_session, init_db
from backend.database.bootstrap import seed_default_data

# Configure logging
logger.add(
    "logs/finovate_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="7 days",
    level="INFO"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    logger.info("Starting Finovate Audit Nexus AI application...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")

    # Initialize database (cached singleton)
    init_db()
    logger.info("Database initialized")

    # Seed default data (admin user, default company)
    try:
        with get_db_session() as session:
            seed_default_data(session)
        logger.info("Default data seeded")
    except Exception as e:
        logger.warning(f"Could not seed default data: {e}")

    # Initialize AI Engine
    from backend.ai_engine.engine_v2 import get_ai_engine_v2
    ai_engine = get_ai_engine_v2()
    logger.info(f"AI Engine initialized with {len(ai_engine.get_available_providers())} providers")

    # Initialize Event Bus
    from backend.core.events import get_event_bus
    _event_bus = get_event_bus()
    logger.info("Event bus initialized")

    # Initialize WebSocket event bridge
    from backend.api.websocket import init_ws_event_bridge
    init_ws_event_bridge()
    logger.info("WebSocket event bridge initialized")

    # Initialize Task Queue
    from backend.core.tasks import get_task_queue
    task_queue = get_task_queue()
    logger.info("Task queue initialized")

    # Initialize Cache
    from backend.core.cache import get_cache
    cache = get_cache()
    logger.info(f"Cache initialized: {cache.get_stats()}")

    yield

    # Shutdown
    task_queue.shutdown(wait=True)
    logger.info("Task queue shut down")

    # Shutdown
    logger.info("Shutting down Finovate Audit Nexus AI application...")

    # Database backup on shutdown
    try:
        from backend.database.backup import create_backup
        backup_path = create_backup()
        if backup_path:
            logger.info("Automatic backup created on shutdown: %s", backup_path)
    except Exception as e:
        logger.warning("Could not create backup on shutdown: %s", e)


# Create FastAPI application
app = FastAPI(
    title="Finovate Audit Nexus AI",
    description="Enterprise AI Financial Audit & Intelligence Platform",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Request logging
app.add_middleware(RequestLogMiddleware)

# Rate limiting
app.add_middleware(RateLimitMiddleware, max_requests=200, window_seconds=60)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With", "Accept"],
)


# ==================== Health Check ====================

@app.get("/api/health")
async def api_health_check():
    """API health check endpoint"""
    db_status = "unchecked"
    try:
        with get_db_session() as session:
            session.execute(sa.text("SELECT 1"))
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"
    try:
        from backend.ai_engine.engine_v2 import get_ai_engine_v2
        ai_engine = get_ai_engine_v2()
        ai_info = {
            "status": ai_engine.status,
            "providers_available": len(ai_engine.get_available_providers()),
            "active_provider": ai_engine.active_provider,
        }
    except Exception as e:
        ai_info = {"status": f"error: {e}"}
    return {
        "status": "healthy",
        "service": "Finovate Audit Nexus AI API",
        "version": "2.0.0",
        "database": db_status,
        "ai_engine": ai_info,
    }


# ==================== API Routes ====================

# Public routes (no auth required)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

# Protected routes (JWT required)
protected = APIRouter(dependencies=[Depends(get_current_user)])
protected.include_router(audits.router)
protected.include_router(ai_providers.router)
protected.include_router(endpoints_agents.router, prefix="/api/v1/agents")
protected.include_router(reports.router, prefix="/api/v1")
protected.include_router(predictive.router, prefix="/api/v1")
protected.include_router(companies.router, prefix="/api/v1/companies")
protected.include_router(audit_projects.router, prefix="/api/v1/audit-projects")
protected.include_router(findings.router, prefix="/api/v1/findings")
protected.include_router(documents.router, prefix="/api/v1/documents")
protected.include_router(dashboard.router, prefix="/api/v1/audit")
protected.include_router(notifications.router, prefix="/api/v1/notifications")
protected.include_router(connectors.router, prefix="/api/v1")
protected.include_router(webhook_endpoints.router, prefix="/api/v1/webhooks")
protected.include_router(task_endpoints.router, prefix="/api/v1/tasks")
protected.include_router(backups.router)
app.include_router(protected)

# WebSocket endpoint (auth via token query param, not via header)
app.include_router(ws.router)


# ==================== Root Endpoints ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Finovate Audit Nexus AI",
        "version": "2.0.0",
        "description": "Enterprise AI Financial Audit & Intelligence Platform",
        "documentation": "/api/docs",
        "status": "running"
    }


@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {
        "service": "Finovate Audit Nexus AI API",
        "version": "2.0.0",
        "endpoints": {
            "audits": "/api/audits",
            "agents": "/api/agents",
            "ai_providers": "/api/ai",
            "health": "/api/health",
            "docs": "/api/docs"
        }
    }


# ==================== Frontend Static Files (PySide6 Desktop only) ====================
logger.info("Desktop UI runs via PySide6 (not served from backend)")

# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled Exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc)
        }
    )

# ==================== Application Entry Point ====================

if __name__ == "__main__":
    import uvicorn

    from backend.core.tls import tls_config

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    workers = int(os.getenv("API_WORKERS", "4"))

    ssl_kwargs = tls_config.get_uvicorn_kwargs()
    protocol = "https" if ssl_kwargs else "http"
    logger.info(f"Starting API server on {protocol}://{host}:{port}")

    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=debug,
        workers=workers if not debug else 1,
        log_level="info",
        **ssl_kwargs
    )
