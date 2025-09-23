"""
Project Pydantic Schemas

Data validation and serialization schemas for carbon capture projects.
"""

from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.projects import ProjectStatus, ProjectType

# Enums for validation
class ProjectStatusSchema(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ProjectTypeSchema(str, Enum):
    AFFORESTATION = "afforestation"
    REFORESTATION = "reforestation"
    FOREST_MANAGEMENT = "forest_management"
    AGROFORESTRY = "agroforestry"
    GRASSLAND_MANAGEMENT = "grassland_management"
    WETLAND_RESTORATION = "wetland_restoration"
    SOIL_CARBON = "soil_carbon"
    BIOCHAR = "biochar"
    DIRECT_AIR_CAPTURE = "direct_air_capture"
    BIOMASS_ENERGY = "biomass_energy"
    OTHER = "other"

# Base schemas
class ProjectBase(BaseModel):
    """Base project schema with common fields."""
    name: str = Field(..., min_length=1, max_length=200, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    project_type: ProjectTypeSchema = Field(..., description="Type of carbon capture project")
    
    # Location information
    country: Optional[str] = Field(None, max_length=100, description="Country")
    region: Optional[str] = Field(None, max_length=100, description="Region/state")
    locality: Optional[str] = Field(None, max_length=100, description="Local area/city")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude (WGS84)")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude (WGS84)")
    
    # Area information
    total_area_hectares: Optional[float] = Field(None, gt=0, description="Total area in hectares")
    project_area_hectares: Optional[float] = Field(None, gt=0, description="Project implementation area in hectares")
    
    # Timeline
    start_date: Optional[datetime] = Field(None, description="Project start date")
    end_date: Optional[datetime] = Field(None, description="Project end date")
    project_duration_years: Optional[int] = Field(None, gt=0, le=100, description="Project duration in years")
    
    # Carbon projections
    estimated_co2_capture_tons_year: Optional[float] = Field(None, gt=0, description="Estimated CO2 capture per year (tons)")
    total_estimated_co2_tons: Optional[float] = Field(None, gt=0, description="Total estimated CO2 capture (tons)")
    
    # Methodology
    methodology: Optional[str] = Field(None, max_length=200, description="Carbon accounting methodology")
    standard: Optional[str] = Field(None, max_length=100, description="Certification standard")
    baseline_scenario: Optional[str] = Field(None, description="Baseline scenario description")
    
    # Economic information
    estimated_cost_usd: Optional[float] = Field(None, gt=0, description="Estimated project cost in USD")
    revenue_model: Optional[str] = Field(None, description="Revenue model description")
    
    # Environmental conditions
    species_planted: Optional[List[str]] = Field(None, description="Species to be planted (for forestry projects)")
    soil_types: Optional[List[str]] = Field(None, description="Soil types present")
    climate_zone: Optional[str] = Field(None, max_length=100, description="Climate zone")
    average_rainfall_mm: Optional[float] = Field(None, gt=0, description="Average annual rainfall (mm)")
    average_temperature_c: Optional[float] = Field(None, description="Average temperature (Celsius)")
    
    # Documentation URLs
    feasibility_study_url: Optional[str] = Field(None, max_length=500, description="Feasibility study document URL")
    environmental_impact_url: Optional[str] = Field(None, max_length=500, description="Environmental impact assessment URL")
    community_engagement_url: Optional[str] = Field(None, max_length=500, description="Community engagement documentation URL")
    
    # Monitoring
    monitoring_plan: Optional[str] = Field(None, description="Monitoring and verification plan")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            if v <= values['start_date']:
                raise ValueError('End date must be after start date')
        return v
    
    @validator('project_area_hectares')
    def validate_project_area(cls, v, values):
        if v and 'total_area_hectares' in values and values['total_area_hectares']:
            if v > values['total_area_hectares']:
                raise ValueError('Project area cannot be larger than total area')
        return v

class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    # Boundary geometry as GeoJSON
    boundary_geojson: Optional[Dict[str, Any]] = Field(None, description="Project boundary as GeoJSON polygon")
    
    @validator('boundary_geojson')
    def validate_boundary_geojson(cls, v):
        if v:
            # Basic GeoJSON validation
            if not isinstance(v, dict):
                raise ValueError('Boundary must be a valid GeoJSON object')
            if v.get('type') != 'Polygon':
                raise ValueError('Boundary must be a Polygon GeoJSON')
            if 'coordinates' not in v:
                raise ValueError('GeoJSON must contain coordinates')
        return v

class ProjectUpdate(BaseModel):
    """Schema for updating an existing project."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None)
    status: Optional[ProjectStatusSchema] = Field(None)
    project_type: Optional[ProjectTypeSchema] = Field(None)
    
    # Location updates
    country: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    locality: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    
    # Area updates
    total_area_hectares: Optional[float] = Field(None, gt=0)
    project_area_hectares: Optional[float] = Field(None, gt=0)
    
    # Timeline updates
    start_date: Optional[datetime] = Field(None)
    end_date: Optional[datetime] = Field(None)
    project_duration_years: Optional[int] = Field(None, gt=0, le=100)
    
    # Carbon projection updates
    estimated_co2_capture_tons_year: Optional[float] = Field(None, gt=0)
    total_estimated_co2_tons: Optional[float] = Field(None, gt=0)
    
    # Methodology updates
    methodology: Optional[str] = Field(None, max_length=200)
    standard: Optional[str] = Field(None, max_length=100)
    baseline_scenario: Optional[str] = Field(None)
    
    # Economic updates
    estimated_cost_usd: Optional[float] = Field(None, gt=0)
    revenue_model: Optional[str] = Field(None)
    
    # Validation updates
    is_validated: Optional[bool] = Field(None)
    validation_notes: Optional[str] = Field(None)
    
    # Boundary update
    boundary_geojson: Optional[Dict[str, Any]] = Field(None, description="Updated project boundary as GeoJSON")

class ProjectSummary(BaseModel):
    """Summary schema for project list views."""
    id: int
    name: str
    project_type: ProjectTypeSchema
    status: ProjectStatusSchema
    country: Optional[str] = None
    region: Optional[str] = None
    project_area_hectares: Optional[float] = None
    estimated_co2_capture_tons_year: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    is_validated: bool = False
    
    model_config = ConfigDict(from_attributes=True)

class ProjectResponse(BaseModel):
    """Complete project response schema."""
    id: int
    name: str
    description: Optional[str] = None
    project_type: ProjectTypeSchema
    status: ProjectStatusSchema
    
    # Location information
    country: Optional[str] = None
    region: Optional[str] = None
    locality: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Area information
    total_area_hectares: Optional[float] = None
    project_area_hectares: Optional[float] = None
    
    # Timeline
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    project_duration_years: Optional[int] = None
    
    # Carbon projections
    estimated_co2_capture_tons_year: Optional[float] = None
    total_estimated_co2_tons: Optional[float] = None
    
    # Methodology
    methodology: Optional[str] = None
    standard: Optional[str] = None
    baseline_scenario: Optional[str] = None
    
    # Economic information
    estimated_cost_usd: Optional[float] = None
    revenue_model: Optional[str] = None
    
    # Environmental conditions
    species_planted: Optional[List[str]] = None
    soil_types: Optional[List[str]] = None
    climate_zone: Optional[str] = None
    average_rainfall_mm: Optional[float] = None
    average_temperature_c: Optional[float] = None
    
    # Documentation
    feasibility_study_url: Optional[str] = None
    environmental_impact_url: Optional[str] = None
    community_engagement_url: Optional[str] = None
    monitoring_plan: Optional[str] = None
    
    # Validation
    is_validated: bool = False
    validation_notes: Optional[str] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    area_sqkm: Optional[float] = None
    co2_capture_rate_per_hectare: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)

class ProjectListResponse(BaseModel):
    """Response schema for paginated project lists."""
    projects: List[ProjectSummary]
    total: int = Field(..., description="Total number of projects matching criteria")
    skip: int = Field(..., description="Number of projects skipped")
    limit: int = Field(..., description="Maximum number of projects returned")
    has_more: bool = Field(..., description="Whether there are more projects available")
    
    @validator('has_more', always=True)
    def calculate_has_more(cls, v, values):
        if 'total' in values and 'skip' in values and 'limit' in values:
            return values['skip'] + values['limit'] < values['total']
        return False

class ProjectValidationRequest(BaseModel):
    """Schema for project validation requests."""
    check_geometry: bool = Field(True, description="Validate project boundary geometry")
    check_feasibility: bool = Field(True, description="Perform feasibility analysis")
    check_methodology: bool = Field(True, description="Validate methodology compliance")
    check_data_completeness: bool = Field(True, description="Check data completeness")
    additional_checks: Optional[List[str]] = Field(None, description="Additional validation checks to perform")

class ProjectValidationResponse(BaseModel):
    """Schema for project validation results."""
    project_id: int
    validation_date: datetime
    overall_status: str = Field(..., description="Overall validation status")
    
    # Individual validation results
    geometry_valid: bool
    geometry_issues: Optional[List[str]] = None
    
    feasibility_score: Optional[float] = Field(None, ge=0, le=1)
    feasibility_issues: Optional[List[str]] = None
    
    methodology_compliant: bool
    methodology_issues: Optional[List[str]] = None
    
    data_completeness_score: float = Field(..., ge=0, le=1)
    missing_data_fields: Optional[List[str]] = None
    
    recommendations: List[str] = Field(default_factory=list)
    
class ProjectStatistics(BaseModel):
    """Schema for project statistics and analytics."""
    project_id: int
    
    # Basic statistics
    total_evaluations: int = 0
    last_evaluation_date: Optional[datetime] = None
    
    # Performance metrics
    average_co2_sequestration_rate: Optional[float] = None
    total_co2_sequestered: Optional[float] = None
    performance_trend: Optional[str] = None  # "improving", "stable", "declining"
    
    # Geospatial statistics
    monitored_area_percentage: Optional[float] = None
    vegetation_cover_trend: Optional[str] = None
    deforestation_incidents: int = 0
    
    # Quality metrics
    data_quality_average: Optional[float] = None
    confidence_level_distribution: Dict[str, int] = Field(default_factory=dict)
    
    # Comparative analysis
    performance_vs_target: Optional[float] = None  # Percentage of target achieved
    ranking_percentile: Optional[float] = None  # Performance ranking among similar projects