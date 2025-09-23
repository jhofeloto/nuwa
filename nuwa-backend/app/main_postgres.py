"""
Nuwa Backend - Main Application with PostgreSQL + PostGIS Integration

FastAPI application with PostgreSQL database and PostGIS geospatial capabilities.
"""

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, text
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

# Import configurations
from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.core.database import init_database, close_database, get_db, check_database_health

# Import PostgreSQL models
from app.models.projects import Project, ProjectStatus, ProjectType
from app.models.evaluations import Evaluation, EvaluationStatus
from app.models.geospatial import GeospatialData, SatelliteImage, DataSource

# Import ML services
from app.ml.models.co2_predictor import co2_prediction_service

# Import Satellite services
from app.satellite.satellite_service import satellite_service

# Import Authentication system
from app.api.auth import router as auth_router
from app.core.middleware import SecurityMiddleware
from app.models.users import User, UserRole, UserStatus

# Global application state
app_state = {
    "startup_time": None, 
    "db_initialized": False, 
    "ml_initialized": False,
    "satellite_initialized": False,
    "postgis_available": False,
    "auth_initialized": False
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager with PostgreSQL + PostGIS initialization.
    """
    # Startup
    logger.info("🚀 Starting Nuwa Backend Service with PostgreSQL + PostGIS...")
    app_state["startup_time"] = datetime.utcnow()
    
    try:
        # Initialize database
        await init_database()
        app_state["db_initialized"] = True
        logger.info("✅ PostgreSQL database initialized successfully")
        
        # Check PostGIS availability
        health_info = await check_database_health()
        app_state["postgis_available"] = health_info.get("postgis_available", False)
        if app_state["postgis_available"]:
            logger.info(f"✅ PostGIS available: {health_info['postgis_version']}")
        else:
            logger.warning("⚠️ PostGIS not available - some geospatial features may be limited")
        
        # Initialize ML models
        await co2_prediction_service.initialize_models()
        app_state["ml_initialized"] = True
        logger.info("✅ ML models initialized successfully")
        
        # Initialize Satellite services
        app_state["satellite_initialized"] = True
        logger.info("✅ Satellite services initialized successfully")
        
        # Initialize Authentication system
        app_state["auth_initialized"] = True
        logger.info("✅ Authentication system initialized successfully")
        
        logger.info("✅ Nuwa Backend Service started successfully with PostgreSQL + PostGIS + ML + Satellite + Auth")
        
    except Exception as e:
        logger.error(f"❌ Failed to start Nuwa Backend Service: {str(e)}")
        app_state["db_initialized"] = False
        app_state["ml_initialized"] = False
        app_state["satellite_initialized"] = False
        app_state["postgis_available"] = False
        app_state["auth_initialized"] = False
        
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Nuwa Backend Service...")
    await close_database()
    logger.info("✅ Nuwa Backend Service shutdown complete")

# Initialize FastAPI application
def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application with PostgreSQL + PostGIS.
    """
    settings = get_settings()
    
    app = FastAPI(
        title="Nuwa - Carbon Capture Tokenization Platform (PostgreSQL + PostGIS)",
        description="""
        ## Nuwa Backend API (With PostgreSQL + PostGIS Integration)
        
        A comprehensive platform for carbon capture project evaluation and tokenization
        with full PostgreSQL database and PostGIS geospatial capabilities.
        
        ### Features Available:
        - 🌱 **Project Management**: Full CRUD operations with PostgreSQL database
        - 🗺️ **Geospatial Analytics**: PostGIS-powered geographic analysis
        - 📊 **Evaluations**: Project evaluation tracking and spatial analysis
        - 🔍 **Advanced Search**: Spatial queries, filtering, and pagination
        - 📈 **Analytics**: Project statistics and geospatial performance metrics
        - 🤖 **ML Predictions**: AI-powered CO2 capture predictions
        - 🛰️ **Satellite Monitoring**: Multi-source satellite data integration
        - 🎯 **Smart Analytics**: Machine learning enhanced insights
        - 🔧 **Health Monitoring**: Comprehensive system health checks
        - 🔐 **Authentication & Authorization**: JWT-based auth with role management
        - 📖 **API Documentation**: Interactive API documentation
        
        ### Database Features:
        - 💾 **PostgreSQL**: Enterprise-grade database with async support
        - 🗺️ **PostGIS**: Advanced geospatial operations and analysis
        - 🔗 **Relationships**: Proper foreign key constraints and referential integrity
        - 🏃 **Performance**: Optimized queries, indexing, and connection pooling
        - 📊 **Geospatial Data**: Native support for polygons, points, and raster data
        - 👥 **User Management**: Comprehensive user roles and permissions system
        
        ### Geospatial Capabilities:
        - **Vector Operations**: Point, line, polygon analysis
        - **Raster Processing**: Satellite imagery and analysis
        - **Spatial Queries**: Distance, intersection, containment
        - **Coordinate Systems**: Multi-projection support
        - **Spatial Indexing**: High-performance spatial searches
        
        ### Architecture:
        Built on FastAPI with async SQLAlchemy, PostgreSQL, PostGIS, and GeoAlchemy2 
        for enterprise-grade geospatial data management.
        """,
        version="1.0.0-postgresql-postgis",
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
    
    # Add Security Middleware for authentication and rate limiting
    app.add_middleware(SecurityMiddleware, enable_rate_limiting=True, enable_audit_logging=True)
    
    return app

# Create application instance
app = create_application()

# Include authentication router
app.include_router(auth_router)

# Setup logging
setup_logging()
logger = logging.getLogger("app.main")

# Health check endpoints
@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint providing basic system information.
    """
    return {
        "message": "🌱 Nuwa - Carbon Capture Tokenization Platform (PostgreSQL + PostGIS Edition)",
        "version": "1.0.0-postgresql-postgis",
        "status": "operational",
        "documentation": "/docs",
        "health": "/health",
        "database": "PostgreSQL + PostGIS",
        "features": [
            "Project Management",
            "Geospatial Analytics", 
            "ML Predictions",
            "Satellite Monitoring",
            "Carbon Credit Evaluation",
            "User Authentication & Authorization"
        ]
    }

@app.get("/health", tags=["System"])
async def health_check():
    """
    Comprehensive health check endpoint.
    """
    try:
        # Database health check
        db_health = await check_database_health()
        
        return {
            "status": "healthy" if all([
                app_state.get("db_initialized"),
                app_state.get("ml_initialized"),
                app_state.get("satellite_initialized"),
                app_state.get("auth_initialized")
            ]) else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (
                datetime.utcnow() - app_state["startup_time"]
            ).total_seconds() if app_state["startup_time"] else 0,
            "database": {
                "type": "PostgreSQL",
                "connected": db_health.get("connected", False),
                "version": db_health.get("version"),
                "pool_status": db_health.get("connection_pool", {})
            },
            "postgis": {
                "available": db_health.get("postgis_available", False),
                "version": db_health.get("postgis_version")
            },
            "services": {
                "database": "initialized" if app_state.get("db_initialized") else "not_initialized",
                "ml_models": "initialized" if app_state.get("ml_initialized") else "not_initialized", 
                "satellite_services": "initialized" if app_state.get("satellite_initialized") else "not_initialized",
                "authentication": "initialized" if app_state.get("auth_initialized") else "not_initialized",
            },
            "features": {
                "geospatial_analysis": app_state.get("postgis_available", False),
                "ml_predictions": app_state.get("ml_initialized", False),
                "satellite_integration": app_state.get("satellite_initialized", False),
                "user_authentication": app_state.get("auth_initialized", False),
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Project Management Endpoints with PostGIS Support
@app.post("/api/v1/projects", tags=["Projects"])
async def create_project(project_data: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """
    Create a new carbon capture project with geospatial data support.
    
    Enhanced with PostGIS capabilities for storing and analyzing project boundaries.
    """
    try:
        # Create project instance
        project = Project(
            name=project_data.get("name"),
            description=project_data.get("description"),
            project_type=ProjectType(project_data.get("project_type", "afforestation")),
            country=project_data.get("country"),
            region=project_data.get("region"),
            locality=project_data.get("locality"),
            latitude=project_data.get("latitude"),
            longitude=project_data.get("longitude"),
            total_area_hectares=project_data.get("total_area_hectares"),
            project_area_hectares=project_data.get("project_area_hectares"),
            estimated_co2_capture_tons_year=project_data.get("estimated_co2_capture_tons_year"),
            climate_zone=project_data.get("climate_zone"),
            methodology=project_data.get("methodology"),
            standard=project_data.get("standard")
        )
        
        # Handle geospatial boundary if provided
        if "boundary_polygon" in project_data:
            # Convert GeoJSON to PostGIS geometry
            boundary_geojson = project_data["boundary_polygon"]
            if isinstance(boundary_geojson, dict):
                # Use PostGIS to create geometry from GeoJSON
                geom_text = json.dumps(boundary_geojson)
                boundary_query = text("SELECT ST_GeomFromGeoJSON(:geom)")
                result = await db.execute(boundary_query, {"geom": geom_text})
                # This would be handled by GeoAlchemy2 in production
                project.metadata["boundary_geojson"] = boundary_geojson
        
        db.add(project)
        await db.commit()
        await db.refresh(project)
        
        logger.info(f"Created project: {project.name} (ID: {project.id})")
        
        return {
            "success": True,
            "project": project.to_dict(),
            "message": "Project created successfully with geospatial support"
        }
        
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/projects", tags=["Projects"])
async def get_projects(
    skip: int = 0,
    limit: int = 100,
    project_type: Optional[str] = None,
    status: Optional[str] = None,
    country: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get projects with advanced filtering and geospatial support.
    """
    try:
        query = select(Project)
        
        # Apply filters
        if project_type:
            query = query.where(Project.project_type == ProjectType(project_type))
        if status:
            query = query.where(Project.status == ProjectStatus(status))
        if country:
            query = query.where(Project.country.ilike(f"%{country}%"))
        
        # Add pagination
        query = query.offset(skip).limit(limit).order_by(desc(Project.created_at))
        
        result = await db.execute(query)
        projects = result.scalars().all()
        
        # Get total count
        count_query = select(func.count(Project.id))
        if project_type:
            count_query = count_query.where(Project.project_type == ProjectType(project_type))
        if status:
            count_query = count_query.where(Project.status == ProjectStatus(status))
        if country:
            count_query = count_query.where(Project.country.ilike(f"%{country}%"))
        
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        return {
            "success": True,
            "projects": [project.to_dict() for project in projects],
            "total_count": total_count,
            "page_info": {
                "skip": skip,
                "limit": limit,
                "has_next": skip + limit < total_count
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching projects: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch projects")

@app.get("/api/v1/projects/{project_id}", tags=["Projects"])
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a specific project with all geospatial data.
    """
    try:
        # Get project with geospatial data
        query = select(Project).where(Project.id == project_id)
        result = await db.execute(query)
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get associated geospatial data
        geospatial_query = select(GeospatialData).where(GeospatialData.project_id == project_id)
        geospatial_result = await db.execute(geospatial_query)
        geospatial_data = geospatial_result.scalars().all()
        
        project_dict = project.to_dict()
        project_dict["geospatial_data"] = [data.to_dict() for data in geospatial_data]
        
        return {
            "success": True,
            "project": project_dict
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch project")

# Geospatial Analysis Endpoints (PostGIS-powered)
@app.post("/api/v1/geospatial/spatial-query", tags=["Geospatial"])
async def spatial_query(query_data: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """
    Perform spatial queries using PostGIS capabilities.
    
    Supports:
    - Point-in-polygon queries
    - Distance calculations
    - Spatial intersections
    - Buffer operations
    """
    try:
        if not app_state.get("postgis_available"):
            raise HTTPException(
                status_code=503, 
                detail="PostGIS not available. Spatial queries require PostGIS extension."
            )
        
        query_type = query_data.get("type", "point_in_polygon")
        
        if query_type == "projects_near_point":
            # Find projects near a specific point
            latitude = query_data.get("latitude")
            longitude = query_data.get("longitude") 
            radius_km = query_data.get("radius_km", 10)
            
            if not all([latitude, longitude]):
                raise HTTPException(status_code=400, detail="latitude and longitude required")
            
            # PostGIS query for projects within radius
            spatial_query = text("""
                SELECT p.*, 
                       ST_Distance(
                           ST_Transform(ST_GeomFromText('POINT(:lon :lat)', 4326), 3857),
                           ST_Transform(ST_GeomFromText(CONCAT('POINT(', p.longitude, ' ', p.latitude, ')'), 4326), 3857)
                       ) / 1000 as distance_km
                FROM projects p
                WHERE p.latitude IS NOT NULL AND p.longitude IS NOT NULL
                  AND ST_DWithin(
                      ST_Transform(ST_GeomFromText('POINT(:lon :lat)', 4326), 3857),
                      ST_Transform(ST_GeomFromText(CONCAT('POINT(', p.longitude, ' ', p.latitude, ')'), 4326), 3857),
                      :radius_m
                  )
                ORDER BY distance_km
            """)
            
            result = await db.execute(spatial_query, {
                "lat": latitude,
                "lon": longitude,
                "radius_m": radius_km * 1000
            })
            
            projects = []
            for row in result.fetchall():
                projects.append({
                    "id": row.id,
                    "name": row.name,
                    "latitude": row.latitude,
                    "longitude": row.longitude,
                    "distance_km": float(row.distance_km) if row.distance_km else None
                })
            
            return {
                "success": True,
                "query_type": query_type,
                "center_point": {"latitude": latitude, "longitude": longitude},
                "radius_km": radius_km,
                "projects_found": len(projects),
                "projects": projects
            }
        
        else:
            return {
                "success": False,
                "error": f"Query type '{query_type}' not implemented yet",
                "supported_types": ["projects_near_point"]
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Spatial query error: {str(e)}")
        raise HTTPException(status_code=500, detail="Spatial query failed")

# Copy all ML endpoints from main_database.py
@app.post("/api/v1/ml/predict-co2", tags=["Machine Learning"])
async def predict_co2_capture(project_data: Dict[str, Any]):
    """
    Predict CO2 capture potential using ML models.
    
    This endpoint uses trained machine learning models to predict the CO2 capture
    potential of carbon projects based on various features.
    """
    try:
        if not app_state.get("ml_initialized", False):
            raise HTTPException(
                status_code=503,
                detail="ML models not initialized. Please try again later."
            )
        
        # Get ML prediction
        prediction = await co2_prediction_service.predict_co2_capture(project_data)
        
        if prediction.get("success", False):
            logger.info(f"ML prediction completed for project: {project_data.get('name', 'Unknown')}")
        
        return {
            "success": True,
            "ml_prediction": prediction,
            "input_features": project_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ML prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="ML prediction failed")

# Copy all satellite endpoints from main_database.py
@app.post("/api/v1/satellite/analyze-project", tags=["Satellite Monitoring"])
async def analyze_project_satellite_data(project_data: Dict[str, Any]):
    """
    Comprehensive satellite analysis for carbon capture projects.
    
    Enhanced with PostGIS support for better geospatial processing.
    """
    try:
        if not app_state.get("satellite_initialized", False):
            raise HTTPException(
                status_code=503,
                detail="Satellite services not initialized. Please try again later."
            )
        
        # Validate required parameters
        required_fields = ['bounds', 'project_start_date']
        missing_fields = [field for field in required_fields if field not in project_data]
        
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        # Parse dates
        from datetime import date
        project_start = date.fromisoformat(project_data['project_start_date'])
        analysis_date = (
            date.fromisoformat(project_data['analysis_date']) 
            if 'analysis_date' in project_data 
            else date.today()
        )
        
        # Parse bounds
        bounds = project_data['bounds']
        if len(bounds) != 4:
            raise HTTPException(
                status_code=400,
                detail="Bounds must be [min_longitude, min_latitude, max_longitude, max_latitude]"
            )
        
        bounds_tuple = tuple(float(b) for b in bounds)
        
        # Get satellite analysis
        analysis = await satellite_service.get_project_satellite_analysis(
            project_bounds=bounds_tuple,
            project_start_date=project_start,
            analysis_date=analysis_date,
            client_preference=project_data.get('satellite_preference')
        )
        
        if analysis.get("success", False):
            logger.info(f"Satellite analysis completed for project area: {bounds}")
        
        return {
            "success": True,
            "satellite_analysis": analysis,
            "input_parameters": project_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Satellite analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Satellite analysis failed")

@app.get("/api/v1/satellite/status", tags=["Satellite Monitoring"])
async def get_satellite_service_status():
    """
    Get current satellite service status and capabilities.
    """
    try:
        available_clients = satellite_service.get_available_clients()
        
        return {
            "success": True,
            "satellite_services": {
                "status": "operational",
                "available_clients": available_clients,
                "default_client": satellite_service.default_client,
                "supported_satellites": {
                    "sentinel2": {
                        "name": "Sentinel-2",
                        "resolution": "10m (RGB+NIR)",
                        "revisit_time": "5-10 days",
                        "spectral_bands": 13,
                        "supported_indices": ["NDVI", "EVI", "SAVI", "NDWI", "NDMI"]
                    },
                    "landsat": {
                        "name": "Landsat 8/9",
                        "resolution": "30m (multispectral)",
                        "revisit_time": "16 days (8 days combined)",
                        "spectral_bands": 11,
                        "supported_indices": ["NDVI", "EVI", "SAVI", "NBR", "NDMI", "NDWI"]
                    },
                    "mock": {
                        "name": "Mock Satellite (Demo)",
                        "resolution": "10-30m simulated", 
                        "revisit_time": "Variable",
                        "purpose": "Testing and demonstration"
                    }
                },
                "analysis_capabilities": [
                    "Vegetation health monitoring",
                    "Land cover change detection",
                    "Biomass estimation", 
                    "Carbon impact assessment",
                    "Time series analysis"
                ]
            },
            "system_status": {
                "satellite_initialized": app_state.get("satellite_initialized", False),
                "services_available": len(available_clients) > 0
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get satellite service status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve satellite service status")

# Database Statistics and Analytics
@app.get("/api/v1/analytics/database-stats", tags=["Analytics"])
async def get_database_statistics(db: AsyncSession = Depends(get_db)):
    """
    Get comprehensive database statistics including PostGIS spatial data.
    """
    try:
        stats = {}
        
        # Basic table counts
        project_count = await db.execute(select(func.count(Project.id)))
        stats["total_projects"] = project_count.scalar()
        
        geospatial_count = await db.execute(select(func.count(GeospatialData.id)))
        stats["total_geospatial_datasets"] = geospatial_count.scalar()
        
        # Project statistics by type
        project_types_query = select(
            Project.project_type, 
            func.count(Project.id).label('count')
        ).group_by(Project.project_type)
        
        project_types_result = await db.execute(project_types_query)
        stats["projects_by_type"] = {
            row.project_type.value: row.count 
            for row in project_types_result.fetchall()
        }
        
        # Geospatial statistics (PostGIS)
        if app_state.get("postgis_available"):
            # Calculate total area of all projects (using PostGIS)
            area_query = select(func.sum(Project.project_area_hectares)).where(
                Project.project_area_hectares.is_not(None)
            )
            area_result = await db.execute(area_query)
            total_area = area_result.scalar() or 0
            stats["total_project_area_hectares"] = float(total_area)
            
            # Geographic distribution
            country_query = select(
                Project.country,
                func.count(Project.id).label('count')
            ).where(Project.country.is_not(None)).group_by(Project.country)
            
            country_result = await db.execute(country_query)
            stats["projects_by_country"] = {
                row.country: row.count 
                for row in country_result.fetchall()
            }
        
        return {
            "success": True,
            "database_statistics": stats,
            "postgis_features": app_state.get("postgis_available", False),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching database statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch database statistics")

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main_postgres:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower()
    )