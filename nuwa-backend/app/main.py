"""
Nuwa Backend - Carbon Capture Project Tokenization Platform
FastAPI Main Application

This is the core FastAPI application for the Nuwa platform, providing:
- RESTful API for carbon capture project evaluation
- Geospatial data processing capabilities
- Machine learning model integration
- Blockchain connectivity for tokenization
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import asyncio
import os
from datetime import datetime
from typing import Dict, Any

# Import configurations and database
from app.core.config import get_settings
from app.core.database import get_db_connection, init_database
from app.core.logging_config import setup_logging

# Import API routers
from app.api.v1.api import api_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global application state
app_state = {"db_connected": False, "startup_time": None}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    Handles database initialization and cleanup.
    """
    # Startup
    logger.info("🚀 Starting Nuwa Backend Service...")
    app_state["startup_time"] = datetime.utcnow()
    
    try:
        # Initialize database connection
        await init_database()
        app_state["db_connected"] = True
        logger.info("✅ Database connection established")
        
        # Additional startup tasks can be added here
        # - Initialize ML models
        # - Setup satellite data connections
        # - Validate blockchain connectivity
        
        logger.info("✅ Nuwa Backend Service started successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to start Nuwa Backend Service: {str(e)}")
        app_state["db_connected"] = False
        
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Nuwa Backend Service...")
    # Cleanup tasks here
    logger.info("✅ Nuwa Backend Service shutdown complete")

# Initialize FastAPI application
def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    settings = get_settings()
    
    app = FastAPI(
        title="Nuwa - Carbon Capture Tokenization Platform",
        description="""
        ## Nuwa Backend API
        
        A comprehensive platform for carbon capture project evaluation and tokenization.
        
        ### Features:
        - 🌱 **Project Evaluation**: Advanced geospatial analysis of carbon capture projects
        - 🛰️ **Satellite Integration**: Real-time satellite data processing (Sentinel-2, Landsat)
        - 🤖 **ML Predictions**: Machine learning models for CO2 capture forecasting
        - ⛓️ **Blockchain Ready**: Smart contract integration with Cardano blockchain
        - 🗺️ **Geospatial Analysis**: PostGIS-powered geographic data processing
        - 📊 **Real-time Analytics**: Live monitoring and reporting capabilities
        
        ### Architecture:
        Built on FastAPI with PostgreSQL+PostGIS for enterprise-grade performance.
        """,
        version="1.0.0",
        contact={
            "name": "Nuwa Development Team",
            "email": "dev@nuwa.earth",
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
        lifespan=lifespan,
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
        openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    return app

# Create application instance
app = create_application()

# Health check endpoints
@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint providing basic system information.
    """
    return {
        "message": "🌱 Nuwa - Carbon Capture Tokenization Platform",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "timestamp": datetime.utcnow().isoformat(),
    }

@app.get("/health", tags=["System"])
async def health_check():
    """
    Comprehensive health check endpoint.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "uptime": None,
        "services": {
            "database": "unknown",
            "ml_models": "not_implemented",
            "satellite_api": "not_implemented",
            "blockchain": "not_implemented",
        }
    }
    
    # Calculate uptime
    if app_state["startup_time"]:
        uptime_seconds = (datetime.utcnow() - app_state["startup_time"]).total_seconds()
        health_status["uptime"] = f"{uptime_seconds:.1f} seconds"
    
    # Check database connection
    try:
        db_connection = await get_db_connection()
        if db_connection and app_state["db_connected"]:
            health_status["services"]["database"] = "healthy"
        else:
            health_status["services"]["database"] = "unhealthy"
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Health check database error: {str(e)}")
        health_status["services"]["database"] = "error"
        health_status["status"] = "unhealthy"
    
    return health_status

@app.get("/status", tags=["System"])
async def detailed_status():
    """
    Detailed system status and configuration information.
    """
    settings = get_settings()
    
    return {
        "system": {
            "name": "Nuwa Backend",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "startup_time": app_state["startup_time"].isoformat() if app_state["startup_time"] else None,
        },
        "database": {
            "connected": app_state["db_connected"],
            "host": settings.DATABASE_HOST,
            "database": settings.DATABASE_NAME,
            "postgis_enabled": True,  # Will be validated later
        },
        "features": {
            "geospatial_analysis": True,
            "ml_predictions": False,  # Will be implemented
            "satellite_integration": False,  # Will be implemented
            "blockchain_connectivity": False,  # Will be implemented
        },
        "api": {
            "docs_enabled": settings.ENVIRONMENT != "production",
            "cors_origins": len(settings.ALLOWED_ORIGINS),
        }
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom HTTP exception handler with detailed logging.
    """
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path),
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    General exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception: {str(exc)} - {request.url}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path),
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Development server configuration
    settings = get_settings()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True,
    )