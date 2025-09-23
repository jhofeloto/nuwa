"""
Carbon Capture Projects API Endpoints

API endpoints for managing carbon capture projects and their evaluation.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from app.core.database import get_db
from app.schemas.projects import (
    ProjectCreate, ProjectUpdate, ProjectResponse, 
    ProjectListResponse, ProjectSummary
)
from app.services.projects import ProjectService
from app.core.logging_config import RequestLogger

router = APIRouter()
logger = logging.getLogger("app.api.projects")

@router.post("/", response_model=ProjectResponse, summary="Create New Project")
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new carbon capture project for evaluation.
    
    This endpoint accepts project information including:
    - Basic project details (name, description, location)
    - Geospatial boundaries (GeoJSON polygon)
    - Project type and methodology
    - Expected timeline and targets
    """
    with RequestLogger(logger, "create_project", project_name=project_data.name):
        try:
            project_service = ProjectService(db)
            project = await project_service.create_project(project_data)
            
            logger.info(f"Created project: {project.id} - {project.name}")
            
            return ProjectResponse.from_orm(project)
            
        except ValueError as e:
            logger.warning(f"Invalid project data: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to create project: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create project")

@router.get("/", response_model=ProjectListResponse, summary="List All Projects")
async def list_projects(
    skip: int = Query(0, ge=0, description="Number of projects to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of projects to return"),
    status: Optional[str] = Query(None, description="Filter by project status"),
    project_type: Optional[str] = Query(None, description="Filter by project type"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a paginated list of carbon capture projects.
    
    Supports filtering by status and project type.
    """
    with RequestLogger(logger, "list_projects", skip=skip, limit=limit):
        try:
            project_service = ProjectService(db)
            projects, total = await project_service.get_projects(
                skip=skip, 
                limit=limit, 
                status=status,
                project_type=project_type
            )
            
            project_summaries = [
                ProjectSummary.from_orm(project) for project in projects
            ]
            
            return ProjectListResponse(
                projects=project_summaries,
                total=total,
                skip=skip,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Failed to list projects: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve projects")

@router.get("/{project_id}", response_model=ProjectResponse, summary="Get Project Details")
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve detailed information about a specific project.
    """
    with RequestLogger(logger, "get_project", project_id=project_id):
        try:
            project_service = ProjectService(db)
            project = await project_service.get_project_by_id(project_id)
            
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            
            return ProjectResponse.from_orm(project)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get project {project_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve project")

@router.put("/{project_id}", response_model=ProjectResponse, summary="Update Project")
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing carbon capture project.
    """
    with RequestLogger(logger, "update_project", project_id=project_id):
        try:
            project_service = ProjectService(db)
            project = await project_service.update_project(project_id, project_data)
            
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            
            logger.info(f"Updated project: {project.id} - {project.name}")
            
            return ProjectResponse.from_orm(project)
            
        except HTTPException:
            raise
        except ValueError as e:
            logger.warning(f"Invalid update data for project {project_id}: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to update project {project_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update project")

@router.delete("/{project_id}", summary="Delete Project")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a carbon capture project and all associated data.
    
    **Warning:** This action is irreversible and will delete all evaluations,
    satellite data, and analysis results associated with the project.
    """
    with RequestLogger(logger, "delete_project", project_id=project_id):
        try:
            project_service = ProjectService(db)
            success = await project_service.delete_project(project_id)
            
            if not success:
                raise HTTPException(status_code=404, detail="Project not found")
            
            logger.info(f"Deleted project: {project_id}")
            
            return {"message": "Project deleted successfully", "project_id": project_id}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete project {project_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete project")

@router.get("/{project_id}/summary", summary="Get Project Summary")
async def get_project_summary(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a comprehensive summary of the project including:
    - Basic project information
    - Latest evaluation results
    - Geospatial statistics
    - Progress metrics
    """
    with RequestLogger(logger, "get_project_summary", project_id=project_id):
        try:
            project_service = ProjectService(db)
            summary = await project_service.get_project_summary(project_id)
            
            if not summary:
                raise HTTPException(status_code=404, detail="Project not found")
            
            return summary
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get project summary {project_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve project summary")

@router.post("/{project_id}/validate", summary="Validate Project Data")
async def validate_project_data(
    project_id: int,
    validation_params: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Validate project data against various criteria:
    - Geospatial boundary validation
    - Methodology compliance check
    - Data completeness assessment
    - Feasibility analysis
    """
    with RequestLogger(logger, "validate_project_data", project_id=project_id):
        try:
            project_service = ProjectService(db)
            validation_result = await project_service.validate_project_data(
                project_id, validation_params
            )
            
            if validation_result is None:
                raise HTTPException(status_code=404, detail="Project not found")
            
            return validation_result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to validate project {project_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to validate project data")

# Project statistics endpoints
@router.get("/{project_id}/stats", summary="Get Project Statistics")
async def get_project_stats(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed statistics for a project including:
    - Area calculations
    - Evaluation history
    - Performance metrics
    - Comparative analysis
    """
    with RequestLogger(logger, "get_project_stats", project_id=project_id):
        try:
            project_service = ProjectService(db)
            stats = await project_service.get_project_statistics(project_id)
            
            if stats is None:
                raise HTTPException(status_code=404, detail="Project not found")
            
            return stats
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get project stats {project_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve project statistics")