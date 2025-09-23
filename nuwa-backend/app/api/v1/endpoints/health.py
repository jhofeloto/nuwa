"""
Health Check API Endpoints

Comprehensive health monitoring endpoints for the Nuwa backend.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import logging
from datetime import datetime

from app.core.database import get_db, check_database_health
from app.core.config import get_settings

router = APIRouter()
logger = logging.getLogger("app.api.health")

@router.get("/", summary="Basic Health Check")
async def basic_health():
    """
    Basic health check endpoint.
    Returns simple status information.
    """
    return {
        "status": "healthy",
        "service": "nuwa-backend",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }

@router.get("/detailed", summary="Detailed Health Check")
async def detailed_health():
    """
    Detailed health check including database and services status.
    """
    settings = get_settings()
    
    # Check database health
    db_health = await check_database_health()
    
    health_data = {
        "status": "healthy" if db_health["connected"] else "unhealthy",
        "service": "nuwa-backend",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "services": {
            "database": {
                "status": "healthy" if db_health["connected"] else "unhealthy",
                "connected": db_health["connected"],
                "version": db_health.get("version"),
                "postgis_available": db_health.get("postgis_available", False),
                "postgis_version": db_health.get("postgis_version"),
                "connection_pool": db_health.get("connection_pool", {})
            },
            "geospatial_processing": {
                "status": "ready",
                "description": "Geospatial analysis capabilities"
            },
            "ml_models": {
                "status": "not_implemented",
                "description": "Machine learning models for CO2 prediction"
            },
            "satellite_integration": {
                "status": "not_implemented", 
                "description": "Sentinel-2 and Landsat data integration"
            },
            "blockchain": {
                "status": "not_implemented",
                "description": "Cardano blockchain connectivity"
            }
        },
        "features": {
            "project_evaluation": True,
            "geospatial_analysis": True,
            "ml_predictions": False,
            "satellite_data": False,
            "tokenization": False
        }
    }
    
    # Update overall status based on critical services
    critical_services = ["database"]
    unhealthy_critical = [
        service for service in critical_services 
        if health_data["services"][service]["status"] != "healthy"
    ]
    
    if unhealthy_critical:
        health_data["status"] = "unhealthy"
        health_data["unhealthy_services"] = unhealthy_critical
    
    return health_data

@router.get("/database", summary="Database Health Check")
async def database_health():
    """
    Specific database health check endpoint.
    """
    try:
        db_health = await check_database_health()
        
        return {
            "status": "healthy" if db_health["connected"] else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            **db_health
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@router.get("/readiness", summary="Readiness Check")
async def readiness_check():
    """
    Kubernetes-style readiness check.
    Returns 200 if service is ready to accept traffic.
    """
    try:
        # Check if database is accessible
        db_health = await check_database_health()
        
        if not db_health["connected"]:
            raise HTTPException(
                status_code=503,
                detail="Database not accessible"
            )
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service not ready: {str(e)}"
        )

@router.get("/liveness", summary="Liveness Check")
async def liveness_check():
    """
    Kubernetes-style liveness check.
    Returns 200 if service is alive (basic functionality).
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }