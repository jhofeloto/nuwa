"""
Geospatial Pydantic Schemas

Data validation and serialization schemas for geospatial data and satellite imagery.
"""

from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.geospatial import DataSource, ProcessingStatus

# Enums for validation
class DataSourceSchema(str, Enum):
    SENTINEL_2 = "sentinel-2"
    LANDSAT_8 = "landsat-8"
    LANDSAT_9 = "landsat-9"
    MODIS = "modis"
    PLANET = "planet"
    AERIAL = "aerial"
    DRONE = "drone"
    OTHER = "other"

class ProcessingStatusSchema(str, Enum):
    RAW = "raw"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ANALYZED = "analyzed"
    FAILED = "failed"

# Base schemas
class GeospatialDataBase(BaseModel):
    """Base geospatial data schema."""
    name: str = Field(..., min_length=1, max_length=200, description="Data name")
    description: Optional[str] = Field(None, description="Data description")
    data_type: str = Field(..., description="Type of geospatial data (raster, vector, point_cloud)")
    source: DataSourceSchema = Field(..., description="Data source")
    source_id: Optional[str] = Field(None, max_length=200, description="Original ID from data source")
    
    # Temporal information
    acquisition_date: Optional[datetime] = Field(None, description="Data acquisition date")
    
    # Spatial information
    spatial_resolution_meters: Optional[float] = Field(None, gt=0, description="Spatial resolution in meters")
    coordinate_system: Optional[str] = Field("EPSG:4326", max_length=100, description="Coordinate reference system")
    
    # Quality metrics
    cloud_cover_percentage: Optional[float] = Field(None, ge=0, le=100, description="Cloud cover percentage")
    quality_score: Optional[float] = Field(None, ge=0, le=1, description="Overall quality score")
    
    # Spectral information
    spectral_bands: Optional[List[str]] = Field(None, description="Available spectral bands")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class GeospatialDataCreate(GeospatialDataBase):
    """Schema for creating geospatial data."""
    project_id: int = Field(..., description="Associated project ID")

class GeospatialDataResponse(GeospatialDataBase):
    """Complete geospatial data response schema."""
    id: int
    project_id: int
    
    # File information
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    file_format: Optional[str] = None
    
    # Processing information
    processing_status: ProcessingStatusSchema
    processing_date: Optional[datetime] = None
    
    # Storage information
    storage_location: Optional[str] = None
    access_url: Optional[str] = None
    
    # Analysis results
    analysis_results: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    is_processed: bool = Field(default=False, description="Whether data has been processed")
    has_good_quality: bool = Field(default=False, description="Whether data has good quality")
    
    model_config = ConfigDict(from_attributes=True)

class SatelliteImageResponse(BaseModel):
    """Response schema for satellite images."""
    id: int
    geospatial_data_id: int
    
    # Satellite information
    satellite_name: Optional[str] = None
    sensor_type: Optional[str] = None
    scene_id: Optional[str] = None
    orbit_number: Optional[int] = None
    
    # Acquisition details
    sun_elevation_angle: Optional[float] = None
    sun_azimuth_angle: Optional[float] = None
    view_angle: Optional[float] = None
    
    # Atmospheric conditions
    atmospheric_correction: bool = False
    atmospheric_parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Spectral indices
    ndvi: Optional[float] = None
    evi: Optional[float] = None
    ndwi: Optional[float] = None
    nbr: Optional[float] = None
    savi: Optional[float] = None
    
    # Land cover analysis
    land_cover_classes: Dict[str, float] = Field(default_factory=dict)
    dominant_land_cover: Optional[str] = None
    
    # Vegetation analysis
    vegetation_cover_percentage: Optional[float] = None
    biomass_estimate_tons_per_hectare: Optional[float] = None
    leaf_area_index: Optional[float] = None
    
    # Change detection
    change_detected: Optional[bool] = None
    change_type: Optional[str] = None
    change_magnitude: Optional[float] = None
    
    # Processing information
    processing_level: Optional[str] = None
    processing_date: Optional[datetime] = None
    processing_software: Optional[str] = None
    
    # Quality assessment
    overall_quality: Optional[str] = None
    quality_flags: List[str] = Field(default_factory=list)
    
    # Computed properties
    has_vegetation_indices: bool = Field(default=False, description="Whether vegetation indices are calculated")
    vegetation_health_score: Optional[float] = Field(None, description="Vegetation health score (0-1)")
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class VegetationAnalysisRequest(BaseModel):
    """Schema for vegetation analysis requests."""
    project_id: int = Field(..., description="Project ID to analyze")
    data_sources: List[DataSourceSchema] = Field(..., min_items=1, description="Satellite data sources")
    start_date: Optional[datetime] = Field(None, description="Analysis start date")
    end_date: Optional[datetime] = Field(None, description="Analysis end date")
    
    # Analysis parameters
    vegetation_indices: List[str] = Field(
        default=["NDVI", "EVI", "SAVI"], 
        description="Vegetation indices to calculate"
    )
    cloud_cover_threshold: float = Field(30, ge=0, le=100, description="Maximum cloud cover percentage")
    temporal_aggregation: str = Field("monthly", description="Temporal aggregation method")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            if v <= values['start_date']:
                raise ValueError('End date must be after start date')
        return v

class VegetationAnalysisResponse(BaseModel):
    """Schema for vegetation analysis results."""
    project_id: int
    analysis_date: datetime
    
    # Data sources used
    data_sources_used: List[str]
    scenes_analyzed: int
    
    # Vegetation indices
    vegetation_indices: Dict[str, float] = Field(default_factory=dict)
    
    # Vegetation metrics
    vegetation_metrics: Dict[str, float] = Field(default_factory=dict)
    
    # Temporal analysis
    temporal_analysis: Dict[str, Any] = Field(default_factory=dict)
    
    # Quality metrics
    quality_metrics: Dict[str, float] = Field(default_factory=dict)

class ChangeDetectionRequest(BaseModel):
    """Schema for change detection requests."""
    project_id: int = Field(..., description="Project ID")
    baseline_date: datetime = Field(..., description="Baseline date")
    comparison_date: datetime = Field(..., description="Comparison date")
    
    # Detection parameters
    change_threshold: float = Field(0.1, ge=0, le=1, description="Change detection threshold")
    minimum_area_hectares: float = Field(0.1, gt=0, description="Minimum change area to report")
    change_types: List[str] = Field(
        default=["deforestation", "reforestation", "degradation"],
        description="Types of changes to detect"
    )
    
    @validator('comparison_date')
    def validate_comparison_date(cls, v, values):
        if 'baseline_date' in values and v <= values['baseline_date']:
            raise ValueError('Comparison date must be after baseline date')
        return v

class ChangeDetectionResponse(BaseModel):
    """Schema for change detection results."""
    project_id: int
    analysis_date: datetime
    baseline_date: datetime
    comparison_date: datetime
    
    # Results
    changes_detected: bool
    change_areas: List[Dict[str, Any]] = Field(default_factory=list)
    total_changed_area_hectares: float = 0
    
    # Statistics
    statistics: Dict[str, Any] = Field(default_factory=dict)
    
    # Quality indicators
    detection_confidence: Optional[float] = None
    data_quality_baseline: Optional[float] = None
    data_quality_comparison: Optional[float] = None

class SpectralIndicesRequest(BaseModel):
    """Schema for spectral indices calculation requests."""
    data_id: int = Field(..., description="Geospatial data ID")
    indices: List[str] = Field(..., min_items=1, description="Spectral indices to calculate")
    
    # Processing options
    mask_clouds: bool = Field(True, description="Mask cloudy pixels")
    mask_water: bool = Field(False, description="Mask water pixels")
    output_format: str = Field("GeoTIFF", description="Output file format")
    
    @validator('indices')
    def validate_indices(cls, v):
        valid_indices = ["NDVI", "EVI", "SAVI", "NDWI", "NBR", "GNDVI", "ARVI", "MSAVI"]
        invalid_indices = [idx for idx in v if idx.upper() not in valid_indices]
        if invalid_indices:
            raise ValueError(f"Invalid spectral indices: {invalid_indices}. Valid indices: {valid_indices}")
        return [idx.upper() for idx in v]

class SpectralIndicesResponse(BaseModel):
    """Schema for spectral indices calculation results."""
    data_id: int
    calculation_date: datetime
    
    # Calculated indices
    calculated_indices: Dict[str, float] = Field(default_factory=dict)
    
    # Statistics
    statistics: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    
    # Processing information
    processing_time_seconds: float
    output_files: List[str] = Field(default_factory=list)
    
    # Quality metrics
    pixels_processed: Optional[int] = None
    pixels_masked: Optional[int] = None
    data_completeness: Optional[float] = None

class SatelliteDataAvailabilityRequest(BaseModel):
    """Schema for satellite data availability requests."""
    project_id: int = Field(..., description="Project ID")
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")
    satellites: List[DataSourceSchema] = Field(
        default=[DataSourceSchema.SENTINEL_2, DataSourceSchema.LANDSAT_8],
        description="Satellite sources to check"
    )
    max_cloud_cover: float = Field(50, ge=0, le=100, description="Maximum cloud cover")
    
class SatelliteDataAvailabilityResponse(BaseModel):
    """Schema for satellite data availability results."""
    project_id: int
    query_date: datetime
    
    # Date range
    date_range: Dict[str, Optional[str]]
    
    # Available data
    available_scenes: List[Dict[str, Any]] = Field(default_factory=list)
    total_scenes: int
    satellites: List[str] = Field(default_factory=list)
    
    # Coverage statistics
    coverage_statistics: Dict[str, Any] = Field(default_factory=dict)
    
    # Recommendations
    data_gaps: List[Dict[str, Any]] = Field(default_factory=list)
    recommended_downloads: List[str] = Field(default_factory=list)

class GeospatialProcessingJob(BaseModel):
    """Schema for geospatial processing jobs."""
    job_id: str
    job_type: str = Field(..., description="Type of processing job")
    project_id: int
    
    # Job status
    status: str = Field(..., description="Job status (queued, processing, completed, failed)")
    progress_percentage: float = Field(0, ge=0, le=100)
    
    # Timing
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    
    # Input/output
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Error information
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    
    # Processing parameters
    parameters: Dict[str, Any] = Field(default_factory=dict)