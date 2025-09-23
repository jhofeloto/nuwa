"""
Nuwa Backend - Simplified Main Application (without geospatial dependencies)

This is a simplified version of the FastAPI application for testing
basic functionality without requiring PostGIS or GDAL.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime
from typing import Dict, Any
import asyncio

# Import configurations (with fallbacks for missing dependencies)
from app.core.config import get_settings
from app.core.logging_config import setup_logging

# Global application state
app_state = {"startup_time": None}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    Simplified version without database initialization.
    """
    # Startup
    logger.info("🚀 Starting Nuwa Backend Service (Simplified Mode)...")
    app_state["startup_time"] = datetime.utcnow()
    
    try:
        # Skip database initialization for simplified version
        logger.info("✅ Nuwa Backend Service started successfully (Database skipped)")
        
    except Exception as e:
        logger.error(f"❌ Failed to start Nuwa Backend Service: {str(e)}")
        
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Nuwa Backend Service...")
    logger.info("✅ Nuwa Backend Service shutdown complete")

# Initialize FastAPI application
def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application (simplified version).
    """
    settings = get_settings()
    
    app = FastAPI(
        title="Nuwa - Carbon Capture Tokenization Platform (Simplified)",
        description="""
        ## Nuwa Backend API (Test Version)
        
        A simplified version of the comprehensive platform for carbon capture project evaluation and tokenization.
        
        ### Features Available in Test Mode:
        - 🌱 **Basic Project Management**: CRUD operations for carbon capture projects
        - 📊 **Health Monitoring**: System health and status endpoints
        - 🔧 **API Documentation**: Interactive API documentation
        
        ### Features Not Available (Require Full Setup):
        - 🛰️ **Satellite Integration**: Satellite data processing (requires GDAL/PostGIS)
        - 🤖 **ML Predictions**: Machine learning models (requires additional setup)
        - ⛓️ **Blockchain Integration**: Smart contracts (requires Cardano node)
        - 🗺️ **Geospatial Analysis**: PostGIS-powered geographic processing
        
        ### Architecture:
        Built on FastAPI with in-memory storage for testing purposes.
        """,
        version="1.0.0-simplified",
        contact={
            "name": "Nuwa Development Team",
            "email": "dev@nuwa.earth",
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
        lifespan=lifespan,
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
    
    # We'll add simplified API routes here instead of including complex routers
    
    return app

# Create application instance
app = create_application()

# Setup logging
setup_logging()
logger = logging.getLogger("app.main")

# In-memory storage for testing (replace with database in full version)
projects_store = {}
next_project_id = 1

# Basic health check endpoints
@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint providing basic system information.
    """
    return {
        "message": "🌱 Nuwa - Carbon Capture Tokenization Platform (Simplified Test Version)",
        "version": "1.0.0-simplified",
        "status": "operational",
        "mode": "testing",
        "docs": "/docs",
        "timestamp": datetime.utcnow().isoformat(),
        "note": "This is a simplified version for testing basic functionality"
    }

@app.get("/health", tags=["System"])
async def health_check():
    """
    Basic health check endpoint for simplified version.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0-simplified",
        "uptime": None,
        "mode": "simplified_testing",
        "services": {
            "api": "healthy",
            "storage": "in_memory",
            "database": "not_configured",
            "ml_models": "not_implemented",
            "satellite_api": "not_implemented",
            "blockchain": "not_implemented",
        }
    }
    
    # Calculate uptime
    if app_state["startup_time"]:
        uptime_seconds = (datetime.utcnow() - app_state["startup_time"]).total_seconds()
        health_status["uptime"] = f"{uptime_seconds:.1f} seconds"
    
    return health_status

@app.get("/status", tags=["System"])
async def detailed_status():
    """
    Detailed system status for simplified version.
    """
    settings = get_settings()
    
    return {
        "system": {
            "name": "Nuwa Backend (Simplified)",
            "version": "1.0.0-simplified",
            "environment": settings.ENVIRONMENT,
            "startup_time": app_state["startup_time"].isoformat() if app_state["startup_time"] else None,
            "mode": "testing",
        },
        "storage": {
            "type": "in_memory",
            "projects_count": len(projects_store),
            "persistent": False,
        },
        "features": {
            "basic_api": True,
            "project_management": True,
            "health_monitoring": True,
            "geospatial_analysis": False,
            "ml_predictions": False,
            "satellite_integration": False,
            "blockchain_connectivity": False,
        },
        "api": {
            "docs_enabled": True,
            "cors_origins": len(settings.ALLOWED_ORIGINS),
        },
        "limitations": [
            "Using in-memory storage (data will be lost on restart)",
            "Geospatial features disabled (requires PostGIS)",
            "Machine learning features disabled",
            "Satellite data integration disabled (requires GDAL)",
            "Blockchain features disabled"
        ]
    }

# Simplified project management endpoints (in-memory)
@app.post("/api/v1/projects/", tags=["Projects"])
async def create_project(project_data: Dict[str, Any]):
    """
    Create a new project (simplified version using in-memory storage).
    """
    global next_project_id
    
    try:
        # Basic validation
        if not project_data.get("name"):
            raise HTTPException(status_code=400, detail="Project name is required")
        
        # Create project
        project = {
            "id": next_project_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            **project_data
        }
        
        projects_store[next_project_id] = project
        next_project_id += 1
        
        logger.info(f"Created project {project['id']}: {project['name']}")
        
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create project: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create project")

@app.get("/api/v1/projects/", tags=["Projects"])
async def list_projects(skip: int = 0, limit: int = 50):
    """
    List projects (simplified version).
    """
    try:
        all_projects = list(projects_store.values())
        
        # Apply pagination
        paginated_projects = all_projects[skip:skip + limit]
        
        return {
            "projects": paginated_projects,
            "total": len(all_projects),
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < len(all_projects)
        }
        
    except Exception as e:
        logger.error(f"Failed to list projects: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve projects")

@app.get("/api/v1/projects/{project_id}", tags=["Projects"])
async def get_project(project_id: int):
    """
    Get a specific project.
    """
    try:
        if project_id not in projects_store:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return projects_store[project_id]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve project")

@app.delete("/api/v1/projects/{project_id}", tags=["Projects"])
async def delete_project(project_id: int):
    """
    Delete a project.
    """
    try:
        if project_id not in projects_store:
            raise HTTPException(status_code=404, detail="Project not found")
        
        deleted_project = projects_store.pop(project_id)
        logger.info(f"Deleted project {project_id}: {deleted_project['name']}")
        
        return {"message": "Project deleted successfully", "project_id": project_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete project")

# API Health endpoints
@app.get("/api/v1/health/", tags=["Health"])
async def api_health():
    """Basic API health check."""
    return {
        "status": "healthy",
        "api_version": "v1",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/health/detailed", tags=["Health"])
async def api_detailed_health():
    """Detailed API health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0-simplified",
        "environment": get_settings().ENVIRONMENT,
        "services": {
            "api": {"status": "healthy"},
            "storage": {"status": "healthy", "type": "in_memory"},
            "database": {"status": "not_configured"},
        },
        "features": {
            "project_management": True,
            "geospatial_analysis": False,
            "ml_predictions": False,
            "satellite_data": False,
            "blockchain": False
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
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True,
    )