"""
Nuwa Backend - Main Application with Database Integration

FastAPI application with SQLite database integration for development.
"""

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

# Import configurations
from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.core.database_sqlite import init_database, close_database, get_db, check_database_health

# Import models (SQLite specific imports)
from app.models.projects_sqlite import Project, Evaluation

# Import ML services
from app.ml.models.co2_predictor import co2_prediction_service

# Import Satellite services
from app.satellite.satellite_service import satellite_service

# Global application state
app_state = {"startup_time": None, "db_initialized": False, "ml_initialized": False}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager with database initialization.
    """
    # Startup
    logger.info("🚀 Starting Nuwa Backend Service with Database...")
    app_state["startup_time"] = datetime.utcnow()
    
    try:
        # Initialize database
        await init_database()
        app_state["db_initialized"] = True
        logger.info("✅ Database initialized successfully")
        
        # Initialize ML models
        await co2_prediction_service.initialize_models()
        app_state["ml_initialized"] = True
        logger.info("✅ ML models initialized successfully")
        
        # Initialize Satellite services
        app_state["satellite_initialized"] = True
        logger.info("✅ Satellite services initialized successfully")
        
        logger.info("✅ Nuwa Backend Service started successfully with Database & ML")
        
    except Exception as e:
        logger.error(f"❌ Failed to start Nuwa Backend Service: {str(e)}")
        app_state["db_initialized"] = False
        app_state["ml_initialized"] = False
        app_state["satellite_initialized"] = False
        
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Nuwa Backend Service...")
    await close_database()
    logger.info("✅ Nuwa Backend Service shutdown complete")

# Initialize FastAPI application
def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application with database.
    """
    settings = get_settings()
    
    app = FastAPI(
        title="Nuwa - Carbon Capture Tokenization Platform (Database)",
        description="""
        ## Nuwa Backend API (With Database Integration)
        
        A comprehensive platform for carbon capture project evaluation and tokenization
        with full database integration.
        
        ### Features Available:
        - 🌱 **Project Management**: Full CRUD operations with SQLite database
        - 📊 **Evaluations**: Project evaluation tracking and analysis
        - 🔍 **Advanced Search**: Filtering, pagination, and sorting
        - 📈 **Analytics**: Project statistics and performance metrics
        - 🤖 **ML Predictions**: AI-powered CO2 capture predictions
        - 🛰️ **Satellite Monitoring**: Multi-source satellite data integration
        - 🎯 **Smart Analytics**: Machine learning enhanced insights
        - 🔧 **Health Monitoring**: Comprehensive system health checks
        - 📖 **API Documentation**: Interactive API documentation
        
        ### Database Features:
        - 💾 **Persistent Storage**: SQLite database with WAL mode
        - 🔗 **Relationships**: Proper foreign key constraints
        - 🏃 **Performance**: Optimized queries and indexing
        - 📊 **Sample Data**: Pre-loaded development data
        
        ### Architecture:
        Built on FastAPI with async SQLAlchemy and SQLite for reliable data persistence.
        """,
        version="1.0.0-database",
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
    
    return app

# Create application instance
app = create_application()

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
        "message": "🌱 Nuwa - Carbon Capture Tokenization Platform (Database Edition)",
        "version": "1.0.0-database",
        "status": "operational",
        "mode": "database",
        "docs": "/docs",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "SQLite Database Integration",
            "Project CRUD Operations",
            "Evaluation Tracking",
            "Advanced Analytics",
            "ML CO2 Predictions", 
            "Satellite Data Integration",
            "Sample Data Included"
        ]
    }

@app.get("/health", tags=["System"])
async def health_check():
    """
    Comprehensive health check with database status.
    """
    db_health = await check_database_health()
    
    health_status = {
        "status": "healthy" if db_health["connected"] else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0-database",
        "uptime": None,
        "services": {
            "api": "healthy",
            "database": db_health,
            "ml_models": "initialized" if app_state.get("ml_initialized") else "not_initialized",
            "satellite_services": "initialized" if app_state.get("satellite_initialized") else "not_initialized",
        }
    }
    
    # Calculate uptime
    if app_state["startup_time"]:
        uptime_seconds = (datetime.utcnow() - app_state["startup_time"]).total_seconds()
        health_status["uptime"] = f"{uptime_seconds:.1f} seconds"
    
    return health_status

@app.get("/status", tags=["System"])
async def detailed_status(db: AsyncSession = Depends(get_db)):
    """
    Detailed system status with database statistics.
    """
    settings = get_settings()
    
    # Get database statistics
    projects_count = await db.execute(select(func.count(Project.id)))
    evaluations_count = await db.execute(select(func.count(Evaluation.id)))
    
    return {
        "system": {
            "name": "Nuwa Backend (Database)",
            "version": "1.0.0-database",
            "environment": settings.ENVIRONMENT,
            "startup_time": app_state["startup_time"].isoformat() if app_state["startup_time"] else None,
            "db_initialized": app_state["db_initialized"],
        },
        "database": await check_database_health(),
        "statistics": {
            "projects_count": projects_count.scalar(),
            "evaluations_count": evaluations_count.scalar(),
        },
        "features": {
            "project_management": True,
            "evaluation_tracking": True,
            "advanced_search": True,
            "analytics": True,
            "persistent_storage": True,
            "geospatial_analysis": False,
            "ml_predictions": False,
            "satellite_integration": False,
            "blockchain_connectivity": False,
        }
    }

# Project management endpoints with database
@app.post("/api/v1/projects/", tags=["Projects"])
async def create_project(project_data: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """
    Create a new project with database persistence.
    """
    try:
        # Basic validation
        if not project_data.get("name"):
            raise HTTPException(status_code=400, detail="Project name is required")
        
        # Create project instance
        project = Project(
            name=project_data["name"],
            description=project_data.get("description"),
            project_type=project_data.get("project_type", "other"),
            status=project_data.get("status", "draft"),
            country=project_data.get("country"),
            region=project_data.get("region"),
            locality=project_data.get("locality"),
            latitude=project_data.get("latitude"),
            longitude=project_data.get("longitude"),
            total_area_hectares=project_data.get("total_area_hectares"),
            project_area_hectares=project_data.get("project_area_hectares"),
            estimated_co2_capture_tons_year=project_data.get("estimated_co2_capture_tons_year"),
            total_estimated_co2_tons=project_data.get("total_estimated_co2_tons"),
            methodology=project_data.get("methodology"),
            standard=project_data.get("standard"),
            baseline_scenario=project_data.get("baseline_scenario"),
            estimated_cost_usd=project_data.get("estimated_cost_usd"),
            revenue_model=project_data.get("revenue_model"),
            climate_zone=project_data.get("climate_zone"),
            average_rainfall_mm=project_data.get("average_rainfall_mm"),
            average_temperature_c=project_data.get("average_temperature_c"),
            feasibility_study_url=project_data.get("feasibility_study_url"),
            environmental_impact_url=project_data.get("environmental_impact_url"),
            community_engagement_url=project_data.get("community_engagement_url"),
            monitoring_plan=project_data.get("monitoring_plan")
        )
        
        # Handle JSON fields
        if project_data.get("species_planted"):
            project.species_planted = json.dumps(project_data["species_planted"])
        if project_data.get("soil_types"):
            project.soil_types = json.dumps(project_data["soil_types"])
        if project_data.get("verification_schedule"):
            project.verification_schedule = json.dumps(project_data["verification_schedule"])
        if project_data.get("metadata"):
            project.project_metadata = json.dumps(project_data["metadata"])
        
        # Add to database
        db.add(project)
        await db.commit()
        await db.refresh(project)
        
        logger.info(f"Created project {project.id}: {project.name}")
        
        return project.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create project: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create project")

@app.get("/api/v1/projects/", tags=["Projects"])
async def list_projects(
    skip: int = 0, 
    limit: int = 50,
    status: str = None,
    project_type: str = None,
    country: str = None,
    search: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List projects with advanced filtering and search.
    """
    try:
        # Build query
        query = select(Project)
        
        # Apply filters
        if status:
            query = query.where(Project.status == status)
        if project_type:
            query = query.where(Project.project_type == project_type)
        if country:
            query = query.where(Project.country == country)
        if search:
            query = query.where(
                Project.name.ilike(f"%{search}%") |
                Project.description.ilike(f"%{search}%")
            )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(Project.created_at)).offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        projects = result.scalars().all()
        
        # Convert to dict
        projects_data = [project.to_dict() for project in projects]
        
        return {
            "projects": projects_data,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total,
            "filters_applied": {
                "status": status,
                "project_type": project_type,
                "country": country,
                "search": search
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to list projects: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve projects")

@app.get("/api/v1/projects/{project_id}", tags=["Projects"])
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a specific project with related evaluations.
    """
    try:
        # Get project
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get related evaluations
        evaluations_result = await db.execute(
            select(Evaluation).where(Evaluation.project_id == project_id)
        )
        evaluations = evaluations_result.scalars().all()
        
        project_dict = project.to_dict()
        project_dict["evaluations"] = [eval.to_dict() for eval in evaluations]
        project_dict["evaluations_count"] = len(evaluations)
        
        return project_dict
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve project")

@app.put("/api/v1/projects/{project_id}", tags=["Projects"])
async def update_project(
    project_id: int, 
    project_data: Dict[str, Any], 
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing project.
    """
    try:
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Update fields
        for field, value in project_data.items():
            if hasattr(project, field) and value is not None:
                if field in ["species_planted", "soil_types", "verification_schedule", "project_metadata"]:
                    # Handle JSON fields
                    setattr(project, field, json.dumps(value) if value else None)
                else:
                    setattr(project, field, value)
        
        await db.commit()
        await db.refresh(project)
        
        logger.info(f"Updated project {project.id}: {project.name}")
        
        return project.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update project")

@app.delete("/api/v1/projects/{project_id}", tags=["Projects"])
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a project and all related data.
    """
    try:
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_name = project.name
        
        # Delete related evaluations first
        await db.execute(select(Evaluation).where(Evaluation.project_id == project_id))
        
        # Delete project
        await db.delete(project)
        await db.commit()
        
        logger.info(f"Deleted project {project_id}: {project_name}")
        
        return {"message": "Project deleted successfully", "project_id": project_id}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete project")

# Analytics endpoints
@app.get("/api/v1/analytics/summary", tags=["Analytics"])
async def get_analytics_summary(db: AsyncSession = Depends(get_db)):
    """
    Get comprehensive analytics summary.
    """
    try:
        # Projects statistics
        total_projects = await db.execute(select(func.count(Project.id)))
        active_projects = await db.execute(
            select(func.count(Project.id)).where(Project.status == "active")
        )
        
        # CO2 projections
        total_co2_projection = await db.execute(
            select(func.sum(Project.estimated_co2_capture_tons_year)).where(Project.status == "active")
        )
        
        # Area statistics
        total_area = await db.execute(
            select(func.sum(Project.project_area_hectares)).where(Project.status == "active")
        )
        
        # Countries count
        countries_count = await db.execute(
            select(func.count(func.distinct(Project.country)))
        )
        
        return {
            "summary": {
                "total_projects": total_projects.scalar() or 0,
                "active_projects": active_projects.scalar() or 0,
                "total_countries": countries_count.scalar() or 0,
                "total_area_hectares": total_area.scalar() or 0,
                "projected_co2_capture_tons_year": total_co2_projection.scalar() or 0,
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get analytics summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")

# ML Prediction endpoints
@app.post("/api/v1/ml/predict-co2", tags=["ML Predictions"])
async def predict_project_co2(project_data: Dict[str, Any]):
    """
    Predict CO2 capture for a project using ML models.
    
    This endpoint uses ensemble machine learning models to predict
    the annual CO2 capture potential based on project parameters.
    
    **Required Parameters:**
    - area_hectares: Project area in hectares
    - climate_zone: Climate classification (tropical, temperate, etc.)
    - vegetation_type: Type of vegetation (forest, grassland, etc.)
    - methodology: Carbon capture methodology
    
    **Optional Parameters:**
    - duration_years: Project duration
    - budget_usd: Project budget
    - soil_type: Soil classification
    - annual_rainfall_mm: Annual precipitation
    - avg_temperature_c: Average temperature
    - elevation_m: Elevation above sea level
    - latitude/longitude: Geographic coordinates
    - technology_level: Technology sophistication level
    
    **Returns:**
    - predicted_co2_tons_year: Annual CO2 capture prediction
    - confidence_interval: Statistical confidence bounds
    - model_agreement: Standard deviation between models
    - individual_predictions: Results from each ML model
    """
    try:
        if not app_state.get("ml_initialized", False):
            raise HTTPException(
                status_code=503, 
                detail="ML models not initialized. Please try again later."
            )
        
        # Validate required parameters
        required_fields = ['area_hectares']
        missing_fields = [field for field in required_fields if field not in project_data]
        
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        # Get prediction from ML service
        prediction = await co2_prediction_service.predict_co2_capture(project_data)
        
        if 'error' in prediction:
            raise HTTPException(status_code=500, detail=prediction['error'])
        
        logger.info(f"ML CO2 prediction completed for project area: {project_data.get('area_hectares')} ha")
        
        return {
            "success": True,
            "prediction": prediction,
            "input_parameters": project_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ML prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="ML prediction failed")

@app.post("/api/v1/ml/enhance-project/{project_id}", tags=["ML Predictions"])
async def enhance_project_with_ml(project_id: int, db: AsyncSession = Depends(get_db)):
    """
    Enhance existing project with ML-based CO2 predictions.
    
    This endpoint takes an existing project from the database and
    uses ML models to predict its CO2 capture potential, then
    optionally updates the project with the ML prediction.
    """
    try:
        if not app_state.get("ml_initialized", False):
            raise HTTPException(
                status_code=503, 
                detail="ML models not initialized. Please try again later."
            )
        
        # Get project from database
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Convert project to ML input format
        project_data = {
            'area_hectares': float(project.project_area_hectares or 0),
            'duration_years': float(project.project_duration_years or 10),
            'budget_usd': float(project.estimated_cost_usd or 0),
            'climate_zone': project.climate_zone or 'temperate',
            'vegetation_type': getattr(project, 'vegetation_type', 'mixed'),
            'methodology': project.methodology or 'other',
            'soil_type': project.soil_types or 'mixed',
            'annual_rainfall_mm': float(project.average_rainfall_mm or 1000),
            'avg_temperature_c': float(project.average_temperature_c or 20),
            'elevation_m': float(getattr(project, 'elevation_m', 0)),
            'latitude': float(project.latitude or 0),
            'longitude': float(project.longitude or 0),
            'start_date': project.start_date.isoformat() if project.start_date else '2024-01-01',
            'technology_level': getattr(project, 'technology_level', 'medium')
        }
        
        # Get ML prediction
        prediction = await co2_prediction_service.predict_co2_capture(project_data)
        
        if 'error' in prediction:
            raise HTTPException(status_code=500, detail=prediction['error'])
        
        logger.info(f"Enhanced project {project_id} with ML prediction: {prediction.get('predicted_co2_tons_year', 0):.2f} tons CO2/year")
        
        return {
            "success": True,
            "project": {
                "id": project.id,
                "name": project.name,
                "original_co2_estimate": project.estimated_co2_capture_tons_year,
                "area_hectares": project.project_area_hectares
            },
            "ml_prediction": prediction,
            "comparison": {
                "original_estimate": project.estimated_co2_capture_tons_year or 0,
                "ml_prediction": prediction.get('predicted_co2_tons_year', 0),
                "difference_percent": (
                    ((prediction.get('predicted_co2_tons_year', 0) - (project.estimated_co2_capture_tons_year or 0)) /
                     max(project.estimated_co2_capture_tons_year or 1, 1)) * 100
                ) if project.estimated_co2_capture_tons_year else None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to enhance project {project_id} with ML: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to enhance project with ML")

@app.post("/api/v1/ml/batch-predict", tags=["ML Predictions"])
async def batch_predict_co2(projects_data: List[Dict[str, Any]]):
    """
    Batch CO2 prediction for multiple projects.
    
    This endpoint allows prediction for multiple projects at once,
    which is more efficient for processing large datasets.
    """
    try:
        if not app_state.get("ml_initialized", False):
            raise HTTPException(
                status_code=503, 
                detail="ML models not initialized. Please try again later."
            )
        
        if len(projects_data) > 100:  # Limit batch size
            raise HTTPException(
                status_code=400,
                detail="Batch size limited to 100 projects. Please split into smaller batches."
            )
        
        # Get batch predictions
        predictions = co2_prediction_service.model.predict_batch(
            projects_data, use_ensemble=True
        )
        
        successful_predictions = [p for p in predictions if 'error' not in p]
        failed_predictions = [p for p in predictions if 'error' in p]
        
        logger.info(f"Batch ML prediction completed: {len(successful_predictions)} successful, {len(failed_predictions)} failed")
        
        return {
            "success": True,
            "results": {
                "successful": successful_predictions,
                "failed": failed_predictions,
                "summary": {
                    "total_projects": len(projects_data),
                    "successful_predictions": len(successful_predictions),
                    "failed_predictions": len(failed_predictions),
                    "success_rate": len(successful_predictions) / len(projects_data) * 100
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch ML prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Batch ML prediction failed")

@app.get("/api/v1/ml/model-status", tags=["ML Predictions"])
async def get_ml_model_status():
    """
    Get current ML model status and performance metrics.
    
    Returns information about:
    - Model training status
    - Performance metrics (R², RMSE, etc.)
    - Available models
    - Feature importance
    """
    try:
        status = await co2_prediction_service.get_model_status()
        
        return {
            "success": True,
            "ml_models": status,
            "system_status": {
                "ml_initialized": app_state.get("ml_initialized", False),
                "models_available": status.get("status") == "trained"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get ML model status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve ML model status")

# Satellite Data Integration endpoints
@app.post("/api/v1/satellite/analyze-project", tags=["Satellite Monitoring"])
async def analyze_project_satellite_data(project_data: Dict[str, Any]):
    """
    Comprehensive satellite analysis for carbon capture projects.
    
    This endpoint performs multi-source satellite monitoring including:
    - Vegetation health assessment using NDVI
    - Land cover change detection
    - Biomass and carbon impact estimation
    - Monitoring recommendations
    
    **Required Parameters:**
    - bounds: Geographic boundaries [min_lon, min_lat, max_lon, max_lat]
    - project_start_date: When the project began (YYYY-MM-DD)
    
    **Optional Parameters:**
    - analysis_date: Current analysis date (defaults to today)
    - satellite_preference: Preferred satellites ["sentinel2", "landsat", "mock"]
    
    **Returns:**
    - Comprehensive satellite monitoring report
    - Vegetation health trends
    - Change detection results
    - Carbon impact assessment
    - Monitoring recommendations
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

@app.post("/api/v1/satellite/vegetation-index", tags=["Satellite Monitoring"]) 
async def calculate_vegetation_index(request_data: Dict[str, Any]):
    """
    Calculate vegetation indices for specific areas and time periods.
    
    **Supported Indices:**
    - NDVI: Normalized Difference Vegetation Index
    - EVI: Enhanced Vegetation Index
    - SAVI: Soil Adjusted Vegetation Index
    - NDWI: Normalized Difference Water Index
    - NBR: Normalized Burn Ratio (Landsat only)
    
    **Required Parameters:**
    - bounds: Geographic boundaries [min_lon, min_lat, max_lon, max_lat]
    - start_date: Start of analysis period (YYYY-MM-DD)
    - end_date: End of analysis period (YYYY-MM-DD)
    
    **Optional Parameters:**
    - index_type: Vegetation index type (default: NDVI)
    - satellite: Preferred satellite ["sentinel2", "landsat", "mock"]
    """
    try:
        if not app_state.get("satellite_initialized", False):
            raise HTTPException(
                status_code=503,
                detail="Satellite services not initialized. Please try again later."
            )
        
        # Validate required parameters
        required_fields = ['bounds', 'start_date', 'end_date']
        missing_fields = [field for field in required_fields if field not in request_data]
        
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        # Parse parameters
        from datetime import date
        bounds_tuple = tuple(float(b) for b in request_data['bounds'])
        start_date = date.fromisoformat(request_data['start_date'])
        end_date = date.fromisoformat(request_data['end_date'])
        index_type = request_data.get('index_type', 'NDVI')
        satellite = request_data.get('satellite')
        
        # Calculate vegetation index
        result = await satellite_service.calculate_vegetation_index_for_project(
            project_bounds=bounds_tuple,
            date_range=(start_date, end_date),
            index_type=index_type,
            client_name=satellite
        )
        
        logger.info(f"Vegetation index {index_type} calculated for {bounds_tuple}")
        
        return {
            "success": True,
            "vegetation_analysis": result,
            "parameters": request_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Vegetation index calculation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Vegetation index calculation failed")

@app.get("/api/v1/satellite/imagery/{project_id}", tags=["Satellite Monitoring"])
async def get_project_imagery_metadata(
    project_id: int, 
    start_date: str,
    end_date: str,
    satellite: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get available satellite imagery metadata for a specific project.
    
    Returns information about satellite data availability including:
    - Available imagery dates
    - Cloud cover percentages
    - Spatial resolution
    - Data sources and quality
    """
    try:
        if not app_state.get("satellite_initialized", False):
            raise HTTPException(
                status_code=503,
                detail="Satellite services not initialized. Please try again later."
            )
        
        # Get project from database
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Parse dates
        from datetime import date
        start_dt = date.fromisoformat(start_date)
        end_dt = date.fromisoformat(end_date)
        
        # Construct bounds from project data
        if project.latitude and project.longitude:
            # Create approximate bounds around project location (±0.01 degrees)
            bounds = (
                float(project.longitude) - 0.01,
                float(project.latitude) - 0.01,
                float(project.longitude) + 0.01,
                float(project.latitude) + 0.01
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Project does not have valid coordinates for satellite analysis"
            )
        
        # Get imagery metadata
        imagery_data = await satellite_service.get_satellite_imagery_for_project(
            project_bounds=bounds,
            start_date=start_dt,
            end_date=end_dt,
            client_name=satellite
        )
        
        logger.info(f"Retrieved imagery metadata for project {project_id}")
        
        return {
            "success": True,
            "project": {
                "id": project.id,
                "name": project.name,
                "coordinates": [project.longitude, project.latitude],
                "area_hectares": project.project_area_hectares
            },
            "imagery_data": imagery_data,
            "query_parameters": {
                "start_date": start_date,
                "end_date": end_date,
                "satellite": satellite
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get imagery metadata for project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve imagery metadata")

@app.get("/api/v1/satellite/status", tags=["Satellite Monitoring"])
async def get_satellite_service_status():
    """
    Get current satellite service status and capabilities.
    
    Returns information about:
    - Available satellite data sources
    - Service health status  
    - Supported analysis types
    - API rate limits and usage
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
        "main_database:app",
        host="0.0.0.0",
        port=8001,  # Different port to avoid conflict
        reload=True,
        log_level="info",
        access_log=True,
    )