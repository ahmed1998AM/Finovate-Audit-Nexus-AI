"""
Finovate Audit Nexus AI - FastAPI Application
Main application entry point
Enterprise AI Financial Audit & Intelligence Platform
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from loguru import logger

# Import routes
from backend.api.routes import audits, ai_providers

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

    # Initialize AI Engine
    from backend.ai_engine.engine_v2 import get_ai_engine_v2
    ai_engine = get_ai_engine_v2()
    logger.info(f"AI Engine initialized with {len(ai_engine.get_available_providers())} providers")

    yield

    # Shutdown
    logger.info("Shutting down Finovate Audit Nexus AI application...")


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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Finovate Audit Nexus AI",
        "version": "2.0.0"
    }


@app.get("/api/health")
async def api_health_check():
    """API health check endpoint"""
    try:
        from backend.ai_engine.engine_v2 import get_ai_engine_v2
        ai_engine = get_ai_engine_v2()

        return {
            "status": "healthy",
            "service": "Finovate Audit Nexus AI API",
            "version": "2.0.0",
            "ai_engine": {
                "status": ai_engine.status,
                "providers_available": len(ai_engine.get_available_providers()),
                "active_provider": ai_engine.active_provider
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# ==================== API Routes ====================

# Include audit routes
app.include_router(audits.router)

# Include AI provider routes
app.include_router(ai_providers.router)


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
            "ai_providers": "/api/ai",
            "health": "/api/health",
            "docs": "/api/docs"
        }
    }


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


# ==================== Startup/Shutdown Events ====================

@app.on_event("startup")
async def startup_event():
    """Called when the application starts"""
    logger.info("Application startup event triggered")


@app.on_event("shutdown")
async def shutdown_event():
    """Called when the application shuts down"""
    logger.info("Application shutdown event triggered")


# ==================== Application Entry Point ====================

if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    workers = int(os.getenv("API_WORKERS", "4"))

    logger.info(f"Starting API server on {host}:{port}")

    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=debug,
        workers=workers if not debug else 1,
        log_level="info"
    )
