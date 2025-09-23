"""
Project Service Layer

Business logic for carbon capture project management.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional, Dict, Any, Tuple
import logging
from datetime import datetime
from geoalchemy2 import functions as geo_func

from app.models.projects import Project, ProjectStatus, ProjectType
from app.models.evaluations import Evaluation
from app.schemas.projects import (
    ProjectCreate, ProjectUpdate, ProjectValidationRequest,
    ProjectValidationResponse, ProjectStatistics
)
from app.core.logging_config import RequestLogger

logger = logging.getLogger("app.services.projects")

class ProjectService:
    """
    Service class for project management operations.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_project(self, project_data: ProjectCreate) -> Project:
        """
        Create a new carbon capture project.
        
        Args:
            project_data: Project creation data
            
        Returns:
            Created project instance
        """
        with RequestLogger(logger, "create_project", project_name=project_data.name):
            try:
                # Create project instance
                project = Project(
                    name=project_data.name,
                    description=project_data.description,
                    project_type=ProjectType(project_data.project_type.value),
                    status=ProjectStatus.DRAFT,
                    country=project_data.country,
                    region=project_data.region,
                    locality=project_data.locality,
                    latitude=project_data.latitude,
                    longitude=project_data.longitude,
                    total_area_hectares=project_data.total_area_hectares,
                    project_area_hectares=project_data.project_area_hectares,
                    start_date=project_data.start_date,
                    end_date=project_data.end_date,
                    project_duration_years=project_data.project_duration_years,
                    estimated_co2_capture_tons_year=project_data.estimated_co2_capture_tons_year,
                    total_estimated_co2_tons=project_data.total_estimated_co2_tons,
                    methodology=project_data.methodology,
                    standard=project_data.standard,
                    baseline_scenario=project_data.baseline_scenario,
                    estimated_cost_usd=project_data.estimated_cost_usd,
                    revenue_model=project_data.revenue_model,
                    species_planted=project_data.species_planted,
                    soil_types=project_data.soil_types,
                    climate_zone=project_data.climate_zone,
                    average_rainfall_mm=project_data.average_rainfall_mm,
                    average_temperature_c=project_data.average_temperature_c,
                    feasibility_study_url=project_data.feasibility_study_url,
                    environmental_impact_url=project_data.environmental_impact_url,
                    community_engagement_url=project_data.community_engagement_url,
                    monitoring_plan=project_data.monitoring_plan,
                )
                
                # Handle boundary geometry if provided
                if project_data.boundary_geojson:
                    await self._set_project_boundary(project, project_data.boundary_geojson)
                
                # Add to database
                self.db.add(project)
                await self.db.commit()
                await self.db.refresh(project)
                
                logger.info(f"Created project {project.id}: {project.name}")
                return project
                
            except Exception as e:
                await self.db.rollback()
                logger.error(f"Failed to create project: {str(e)}")
                raise
    
    async def get_projects(
        self, 
        skip: int = 0, 
        limit: int = 50,
        status: Optional[str] = None,
        project_type: Optional[str] = None
    ) -> Tuple[List[Project], int]:
        """
        Get paginated list of projects with optional filtering.
        
        Args:
            skip: Number of projects to skip
            limit: Maximum number of projects to return
            status: Filter by project status
            project_type: Filter by project type
            
        Returns:
            Tuple of (projects list, total count)
        """
        with RequestLogger(logger, "get_projects", skip=skip, limit=limit):
            try:
                # Build query with filters
                query = select(Project)
                count_query = select(func.count(Project.id))
                
                # Apply filters
                filters = []
                if status:
                    filters.append(Project.status == ProjectStatus(status))
                if project_type:
                    filters.append(Project.project_type == ProjectType(project_type))
                
                if filters:
                    query = query.where(and_(*filters))
                    count_query = count_query.where(and_(*filters))
                
                # Get total count
                total_result = await self.db.execute(count_query)
                total = total_result.scalar()
                
                # Get paginated results
                query = query.offset(skip).limit(limit).order_by(Project.updated_at.desc())
                result = await self.db.execute(query)
                projects = result.scalars().all()
                
                return projects, total
                
            except Exception as e:
                logger.error(f"Failed to get projects: {str(e)}")
                raise
    
    async def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """
        Get a project by its ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project instance or None if not found
        """
        try:
            query = select(Project).where(Project.id == project_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get project {project_id}: {str(e)}")
            raise
    
    async def update_project(self, project_id: int, project_data: ProjectUpdate) -> Optional[Project]:
        """
        Update an existing project.
        
        Args:
            project_id: Project ID to update
            project_data: Updated project data
            
        Returns:
            Updated project instance or None if not found
        """
        with RequestLogger(logger, "update_project", project_id=project_id):
            try:
                project = await self.get_project_by_id(project_id)
                if not project:
                    return None
                
                # Update fields that are provided
                update_data = project_data.dict(exclude_unset=True)
                
                for field, value in update_data.items():
                    if field == "status" and value:
                        setattr(project, field, ProjectStatus(value))
                    elif field == "project_type" and value:
                        setattr(project, field, ProjectType(value))
                    elif field == "boundary_geojson":
                        if value:
                            await self._set_project_boundary(project, value)
                    else:
                        setattr(project, field, value)
                
                await self.db.commit()
                await self.db.refresh(project)
                
                logger.info(f"Updated project {project.id}: {project.name}")
                return project
                
            except Exception as e:
                await self.db.rollback()
                logger.error(f"Failed to update project {project_id}: {str(e)}")
                raise
    
    async def delete_project(self, project_id: int) -> bool:
        """
        Delete a project and all associated data.
        
        Args:
            project_id: Project ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        with RequestLogger(logger, "delete_project", project_id=project_id):
            try:
                project = await self.get_project_by_id(project_id)
                if not project:
                    return False
                
                await self.db.delete(project)
                await self.db.commit()
                
                logger.info(f"Deleted project {project_id}")
                return True
                
            except Exception as e:
                await self.db.rollback()
                logger.error(f"Failed to delete project {project_id}: {str(e)}")
                raise
    
    async def get_project_summary(self, project_id: int) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive project summary with statistics.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project summary dictionary or None if not found
        """
        with RequestLogger(logger, "get_project_summary", project_id=project_id):
            try:
                project = await self.get_project_by_id(project_id)
                if not project:
                    return None
                
                # Get evaluation statistics
                eval_query = select(
                    func.count(Evaluation.id).label('total_evaluations'),
                    func.max(Evaluation.evaluation_date).label('last_evaluation'),
                    func.avg(Evaluation.estimated_co2_sequestered_tons).label('avg_co2'),
                    func.avg(Evaluation.data_quality_score).label('avg_quality')
                ).where(Evaluation.project_id == project_id)
                
                eval_result = await self.db.execute(eval_query)
                eval_stats = eval_result.first()
                
                summary = {
                    "project": project.to_dict(),
                    "statistics": {
                        "total_evaluations": eval_stats.total_evaluations or 0,
                        "last_evaluation_date": eval_stats.last_evaluation.isoformat() if eval_stats.last_evaluation else None,
                        "average_co2_sequestered": eval_stats.avg_co2,
                        "average_data_quality": eval_stats.avg_quality,
                    },
                    "calculated_metrics": {
                        "area_sqkm": project.area_sqkm,
                        "co2_rate_per_hectare": project.co2_capture_rate_per_hectare,
                        "is_active": project.is_active,
                        "is_completed": project.is_completed,
                    }
                }
                
                return summary
                
            except Exception as e:
                logger.error(f"Failed to get project summary {project_id}: {str(e)}")
                raise
    
    async def validate_project_data(
        self, 
        project_id: int, 
        validation_params: Dict[str, Any]
    ) -> Optional[ProjectValidationResponse]:
        """
        Validate project data against various criteria.
        
        Args:
            project_id: Project ID to validate
            validation_params: Validation parameters
            
        Returns:
            Validation results or None if project not found
        """
        with RequestLogger(logger, "validate_project_data", project_id=project_id):
            try:
                project = await self.get_project_by_id(project_id)
                if not project:
                    return None
                
                # Initialize validation results
                validation_result = ProjectValidationResponse(
                    project_id=project_id,
                    validation_date=datetime.utcnow(),
                    overall_status="pending",
                    geometry_valid=True,
                    methodology_compliant=True,
                    data_completeness_score=0.0
                )
                
                issues = []
                recommendations = []
                
                # Validate geometry if requested
                if validation_params.get("check_geometry", True):
                    geometry_issues = await self._validate_geometry(project)
                    if geometry_issues:
                        validation_result.geometry_valid = False
                        validation_result.geometry_issues = geometry_issues
                        issues.extend(geometry_issues)
                
                # Check data completeness
                completeness_score, missing_fields = self._check_data_completeness(project)
                validation_result.data_completeness_score = completeness_score
                validation_result.missing_data_fields = missing_fields
                
                if completeness_score < 0.8:
                    recommendations.append("Complete missing required fields to improve project quality")
                
                # Check methodology compliance
                if validation_params.get("check_methodology", True):
                    methodology_issues = self._validate_methodology(project)
                    if methodology_issues:
                        validation_result.methodology_compliant = False
                        validation_result.methodology_issues = methodology_issues
                        issues.extend(methodology_issues)
                
                # Determine overall status
                if not issues:
                    validation_result.overall_status = "valid"
                elif len(issues) <= 2:
                    validation_result.overall_status = "valid_with_warnings"
                else:
                    validation_result.overall_status = "invalid"
                
                validation_result.recommendations = recommendations
                
                return validation_result
                
            except Exception as e:
                logger.error(f"Failed to validate project {project_id}: {str(e)}")
                raise
    
    async def get_project_statistics(self, project_id: int) -> Optional[ProjectStatistics]:
        """
        Get detailed statistics for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project statistics or None if not found
        """
        with RequestLogger(logger, "get_project_statistics", project_id=project_id):
            try:
                project = await self.get_project_by_id(project_id)
                if not project:
                    return None
                
                # Get evaluation statistics
                eval_stats_query = select(
                    func.count(Evaluation.id).label('total_evaluations'),
                    func.max(Evaluation.evaluation_date).label('last_evaluation'),
                    func.avg(Evaluation.estimated_co2_sequestered_tons).label('avg_co2'),
                    func.sum(Evaluation.estimated_co2_sequestered_tons).label('total_co2'),
                    func.avg(Evaluation.data_quality_score).label('avg_quality'),
                    func.count().filter(Evaluation.deforestation_detected == True).label('deforestation_count')
                ).where(Evaluation.project_id == project_id)
                
                eval_result = await self.db.execute(eval_stats_query)
                eval_data = eval_result.first()
                
                # Calculate performance metrics
                target_co2 = project.estimated_co2_capture_tons_year or 0
                actual_co2 = eval_data.avg_co2 or 0
                performance_vs_target = (actual_co2 / target_co2 * 100) if target_co2 > 0 else None
                
                statistics = ProjectStatistics(
                    project_id=project_id,
                    total_evaluations=eval_data.total_evaluations or 0,
                    last_evaluation_date=eval_data.last_evaluation,
                    average_co2_sequestration_rate=eval_data.avg_co2,
                    total_co2_sequestered=eval_data.total_co2,
                    data_quality_average=eval_data.avg_quality,
                    deforestation_incidents=eval_data.deforestation_count or 0,
                    performance_vs_target=performance_vs_target
                )
                
                return statistics
                
            except Exception as e:
                logger.error(f"Failed to get project statistics {project_id}: {str(e)}")
                raise
    
    async def _set_project_boundary(self, project: Project, geojson: Dict[str, Any]) -> None:
        """
        Set project boundary from GeoJSON.
        
        Args:
            project: Project instance
            geojson: GeoJSON polygon
        """
        try:
            # Convert GeoJSON to PostGIS geometry
            # This would typically use ST_GeomFromGeoJSON function
            # For now, we'll store the raw coordinates
            if geojson.get("type") == "Polygon" and "coordinates" in geojson:
                coordinates = geojson["coordinates"]
                if coordinates and len(coordinates[0]) >= 4:
                    # Calculate centroid for latitude/longitude
                    points = coordinates[0]
                    lat_sum = sum(point[1] for point in points[:-1])
                    lon_sum = sum(point[0] for point in points[:-1])
                    count = len(points) - 1
                    
                    project.latitude = lat_sum / count
                    project.longitude = lon_sum / count
                    
                    # TODO: Set actual PostGIS geometry
                    # project.boundary_geom = func.ST_GeomFromGeoJSON(geojson)
            
        except Exception as e:
            logger.warning(f"Failed to set project boundary: {str(e)}")
    
    async def _validate_geometry(self, project: Project) -> List[str]:
        """
        Validate project geometry.
        
        Args:
            project: Project instance
            
        Returns:
            List of geometry validation issues
        """
        issues = []
        
        # Check if coordinates are provided
        if not project.latitude or not project.longitude:
            issues.append("Project coordinates (latitude/longitude) are required")
        
        # Validate coordinate ranges
        if project.latitude and (project.latitude < -90 or project.latitude > 90):
            issues.append("Invalid latitude value (must be between -90 and 90)")
        
        if project.longitude and (project.longitude < -180 or project.longitude > 180):
            issues.append("Invalid longitude value (must be between -180 and 180)")
        
        # Check area consistency
        if project.project_area_hectares and project.total_area_hectares:
            if project.project_area_hectares > project.total_area_hectares:
                issues.append("Project area cannot be larger than total area")
        
        return issues
    
    def _check_data_completeness(self, project: Project) -> Tuple[float, List[str]]:
        """
        Check project data completeness.
        
        Args:
            project: Project instance
            
        Returns:
            Tuple of (completeness score 0-1, list of missing fields)
        """
        required_fields = [
            'name', 'project_type', 'country', 'latitude', 'longitude',
            'project_area_hectares', 'start_date', 'methodology'
        ]
        
        important_fields = [
            'description', 'estimated_co2_capture_tons_year', 'standard',
            'baseline_scenario', 'monitoring_plan'
        ]
        
        missing_required = []
        missing_important = []
        
        # Check required fields
        for field in required_fields:
            if not getattr(project, field, None):
                missing_required.append(field)
        
        # Check important fields
        for field in important_fields:
            if not getattr(project, field, None):
                missing_important.append(field)
        
        # Calculate completeness score
        total_fields = len(required_fields) + len(important_fields)
        missing_count = len(missing_required) + (len(missing_important) * 0.5)
        completeness_score = max(0, (total_fields - missing_count) / total_fields)
        
        missing_fields = missing_required + missing_important
        
        return completeness_score, missing_fields
    
    def _validate_methodology(self, project: Project) -> List[str]:
        """
        Validate project methodology compliance.
        
        Args:
            project: Project instance
            
        Returns:
            List of methodology validation issues
        """
        issues = []
        
        if not project.methodology:
            issues.append("Project methodology must be specified")
        
        if not project.standard:
            issues.append("Certification standard should be specified")
        
        if not project.baseline_scenario:
            issues.append("Baseline scenario description is required for most methodologies")
        
        if not project.monitoring_plan:
            issues.append("Monitoring and verification plan should be documented")
        
        # Check project type specific requirements
        if project.project_type in [ProjectType.AFFORESTATION, ProjectType.REFORESTATION]:
            if not project.species_planted:
                issues.append("Species information is required for forestry projects")
        
        return issues