"""
Nuwa Backend API v1 Router

Main API router that includes all endpoint groups.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import projects, evaluations, health, geospatial

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health Check"]
)

api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["Carbon Capture Projects"]
)

api_router.include_router(
    evaluations.router,
    prefix="/evaluations",
    tags=["Project Evaluations"]
)

api_router.include_router(
    geospatial.router,
    prefix="/geospatial",
    tags=["Geospatial Analysis"]
)