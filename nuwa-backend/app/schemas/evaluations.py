"""
Evaluation Pydantic Schemas

Data validation and serialization schemas for project evaluations.
"""

from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.evaluations import EvaluationStatus, EvaluationType, ConfidenceLevel

# Enums for validation
class EvaluationStatusSchema(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class EvaluationTypeSchema(str, Enum):
    BASELINE = "baseline"
    MONITORING = "monitoring"
    VERIFICATION = "verification"
    IMPACT_ASSESSMENT = "impact_assessment"
    FEASIBILITY = "feasibility"
    RISK_ASSESSMENT = "risk_assessment"

class ConfidenceLevelSchema(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

# Base schemas
class EvaluationBase(BaseModel):
    """Base evaluation schema with common fields."""
    evaluation_type: EvaluationTypeSchema = Field(..., description="Type of evaluation")
    evaluation_date: datetime = Field(..., description="Date when evaluation was performed")
    period_start: Optional[datetime] = Field(None, description="Start of evaluation period")
    period_end: Optional[datetime] = Field(None, description="End of evaluation period")
    
    # Data sources
    satellite_data_sources: List[str] = Field(default_factory=list, description="Satellite data sources used")
    ground_truth_data: bool = Field(False, description="Ground truth data available")
    field_measurements: bool = Field(False, description="Field measurements included")
    
    # Analysis metadata
    analysis_method: Optional[str] = Field(None, max_length=200, description="Analysis method used")
    model_version: Optional[str] = Field(None, max_length=100, description="Model version")
    
    @validator('period_end')
    def validate_period_end(cls, v, values):
        if v and 'period_start' in values and values['period_start']:
            if v <= values['period_start']:
                raise ValueError('Period end must be after period start')
        return v

class EvaluationCreate(EvaluationBase):
    """Schema for creating a new evaluation."""
    project_id: int = Field(..., description="ID of the project being evaluated")
    
    # Optional initial results
    confidence_level: Optional[ConfidenceLevelSchema] = Field(None, description="Confidence level of results")
    notes: Optional[str] = Field(None, description="Additional notes or observations")

class EvaluationUpdate(BaseModel):
    """Schema for updating an existing evaluation."""
    status: Optional[EvaluationStatusSchema] = Field(None, description="Evaluation status")
    confidence_level: Optional[ConfidenceLevelSchema] = Field(None, description="Confidence level")
    
    # Carbon metrics
    estimated_co2_sequestered_tons: Optional[float] = Field(None, gt=0, description="Estimated CO2 sequestered (tons)")
    co2_sequestration_rate_tons_per_hectare: Optional[float] = Field(None, gt=0, description="CO2 sequestration rate per hectare")
    carbon_stock_change_tons: Optional[float] = Field(None, description="Change in carbon stock (tons)")
    
    # Vegetation metrics
    ndvi_average: Optional[float] = Field(None, ge=-1, le=1, description="Average NDVI value")
    ndvi_change: Optional[float] = Field(None, description="Change in NDVI")
    vegetation_cover_percentage: Optional[float] = Field(None, ge=0, le=100, description="Vegetation cover percentage")
    biomass_estimate_tons: Optional[float] = Field(None, gt=0, description="Biomass estimate (tons)")
    
    # Land use metrics
    deforestation_detected: Optional[bool] = Field(None, description="Deforestation detected")
    deforested_area_hectares: Optional[float] = Field(None, ge=0, description="Deforested area (hectares)")
    land_use_change_percentage: Optional[float] = Field(None, ge=0, le=100, description="Land use change percentage")
    
    # Environmental metrics
    soil_carbon_tons_per_hectare: Optional[float] = Field(None, gt=0, description="Soil carbon (tons per hectare)")
    water_stress_index: Optional[float] = Field(None, ge=0, le=1, description="Water stress index")
    biodiversity_index: Optional[float] = Field(None, ge=0, description="Biodiversity index")
    
    # Risk factors
    fire_risk_level: Optional[str] = Field(None, description="Fire risk level")
    drought_risk_level: Optional[str] = Field(None, description="Drought risk level")
    pest_disease_risk: Optional[str] = Field(None, description="Pest/disease risk level")
    
    # Quality metrics
    data_quality_score: Optional[float] = Field(None, ge=0, le=1, description="Data quality score")
    cloud_cover_percentage: Optional[float] = Field(None, ge=0, le=100, description="Cloud cover percentage")
    spatial_resolution_meters: Optional[float] = Field(None, gt=0, description="Spatial resolution (meters)")
    
    # Processing info
    processing_time_seconds: Optional[float] = Field(None, gt=0, description="Processing time (seconds)")
    
    # Verification
    verified: Optional[bool] = Field(None, description="Verification status")
    verification_notes: Optional[str] = Field(None, description="Verification notes")
    
    # Notes
    notes: Optional[str] = Field(None, description="Evaluation notes")

class EvaluationSummary(BaseModel):
    """Summary schema for evaluation list views."""
    id: int
    project_id: int
    evaluation_type: EvaluationTypeSchema
    status: EvaluationStatusSchema
    evaluation_date: datetime
    confidence_level: Optional[ConfidenceLevelSchema] = None
    
    # Key metrics
    estimated_co2_sequestered_tons: Optional[float] = None
    ndvi_average: Optional[float] = None
    vegetation_cover_percentage: Optional[float] = None
    data_quality_score: Optional[float] = None
    
    verified: bool = False
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class EvaluationResponse(BaseModel):
    """Complete evaluation response schema."""
    id: int
    project_id: int
    evaluation_type: EvaluationTypeSchema
    status: EvaluationStatusSchema
    
    # Timeline
    evaluation_date: datetime
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    
    # Data sources
    satellite_data_sources: List[str] = Field(default_factory=list)
    ground_truth_data: bool = False
    field_measurements: bool = False
    
    # Analysis info
    analysis_method: Optional[str] = None
    model_version: Optional[str] = None
    confidence_level: Optional[ConfidenceLevelSchema] = None
    
    # Carbon metrics
    estimated_co2_sequestered_tons: Optional[float] = None
    co2_sequestration_rate_tons_per_hectare: Optional[float] = None
    carbon_stock_change_tons: Optional[float] = None
    
    # Vegetation metrics
    ndvi_average: Optional[float] = None
    ndvi_change: Optional[float] = None
    vegetation_cover_percentage: Optional[float] = None
    biomass_estimate_tons: Optional[float] = None
    
    # Land use metrics
    deforestation_detected: Optional[bool] = None
    deforested_area_hectares: Optional[float] = None
    land_use_change_percentage: Optional[float] = None
    
    # Environmental metrics
    soil_carbon_tons_per_hectare: Optional[float] = None
    water_stress_index: Optional[float] = None
    biodiversity_index: Optional[float] = None
    
    # Risk factors
    fire_risk_level: Optional[str] = None
    drought_risk_level: Optional[str] = None
    pest_disease_risk: Optional[str] = None
    
    # Quality metrics
    data_quality_score: Optional[float] = None
    cloud_cover_percentage: Optional[float] = None
    spatial_resolution_meters: Optional[float] = None
    
    # Processing info
    processing_time_seconds: Optional[float] = None
    algorithm_parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Verification
    verified: bool = False
    verification_date: Optional[datetime] = None
    verification_notes: Optional[str] = None
    
    # Notes
    notes: Optional[str] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    co2_efficiency_rating: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class EvaluationListResponse(BaseModel):
    """Response schema for paginated evaluation lists."""
    evaluations: List[EvaluationSummary]
    total: int = Field(..., description="Total number of evaluations")
    skip: int = Field(..., description="Number of evaluations skipped")
    limit: int = Field(..., description="Maximum number of evaluations returned")
    has_more: bool = Field(..., description="Whether there are more evaluations available")
    
    @validator('has_more', always=True)
    def calculate_has_more(cls, v, values):
        if 'total' in values and 'skip' in values and 'limit' in values:
            return values['skip'] + values['limit'] < values['total']
        return False

class EvaluationMetricsCreate(BaseModel):
    """Schema for creating evaluation metrics."""
    metric_name: str = Field(..., max_length=200, description="Name of the metric")
    metric_category: Optional[str] = Field(None, max_length=100, description="Category of the metric")
    
    # Value (one of these should be provided)
    numeric_value: Optional[float] = Field(None, description="Numeric value")
    text_value: Optional[str] = Field(None, max_length=500, description="Text value")
    json_value: Optional[Dict[str, Any]] = Field(None, description="JSON value")
    
    # Metadata
    unit: Optional[str] = Field(None, max_length=50, description="Unit of measurement")
    measurement_method: Optional[str] = Field(None, max_length=200, description="Measurement method")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Confidence score")
    
    # Temporal info
    measurement_date: Optional[datetime] = Field(None, description="Measurement date")
    
    # Spatial info
    spatial_coverage: Optional[str] = Field(None, max_length=100, description="Spatial coverage")
    
    # Quality
    accuracy_percentage: Optional[float] = Field(None, ge=0, le=100, description="Accuracy percentage")
    precision_value: Optional[float] = Field(None, gt=0, description="Precision value")
    
    @validator('json_value')
    def validate_at_least_one_value(cls, v, values):
        numeric = values.get('numeric_value')
        text = values.get('text_value')
        if not any([numeric is not None, text is not None, v is not None]):
            raise ValueError('At least one value (numeric, text, or json) must be provided')
        return v

class EvaluationMetricsResponse(BaseModel):
    """Response schema for evaluation metrics."""
    id: int
    evaluation_id: int
    metric_name: str
    metric_category: Optional[str] = None
    
    # Values
    numeric_value: Optional[float] = None
    text_value: Optional[str] = None
    json_value: Optional[Dict[str, Any]] = None
    
    # Metadata
    unit: Optional[str] = None
    measurement_method: Optional[str] = None
    confidence_score: Optional[float] = None
    
    # Temporal info
    measurement_date: Optional[datetime] = None
    
    # Spatial info
    spatial_coverage: Optional[str] = None
    
    # Quality
    accuracy_percentage: Optional[float] = None
    precision_value: Optional[float] = None
    
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class EvaluationAnalysisRequest(BaseModel):
    """Schema for requesting evaluation analysis."""
    project_id: int = Field(..., description="Project ID to analyze")
    evaluation_type: EvaluationTypeSchema = Field(..., description="Type of evaluation to perform")
    
    # Time period
    period_start: Optional[datetime] = Field(None, description="Analysis period start")
    period_end: Optional[datetime] = Field(None, description="Analysis period end")
    
    # Data source preferences
    preferred_satellite_sources: List[str] = Field(default_factory=list, description="Preferred satellite data sources")
    include_ground_truth: bool = Field(False, description="Include ground truth data if available")
    
    # Analysis parameters
    spatial_resolution: Optional[float] = Field(None, gt=0, description="Desired spatial resolution (meters)")
    cloud_cover_threshold: float = Field(30, ge=0, le=100, description="Maximum acceptable cloud cover percentage")
    
    # Processing options
    force_reprocess: bool = Field(False, description="Force reprocessing even if recent results exist")
    save_intermediate_results: bool = Field(True, description="Save intermediate processing results")
    
    # Notification
    notify_on_completion: bool = Field(False, description="Send notification when analysis completes")

class EvaluationComparisonRequest(BaseModel):
    """Schema for comparing evaluations."""
    evaluation_ids: List[int] = Field(..., min_items=2, max_items=10, description="Evaluation IDs to compare")
    comparison_metrics: List[str] = Field(default_factory=list, description="Specific metrics to compare")
    normalize_values: bool = Field(True, description="Normalize values for comparison")
    
class EvaluationComparisonResponse(BaseModel):
    """Schema for evaluation comparison results."""
    evaluations: List[EvaluationSummary]
    
    # Comparison results
    metric_comparisons: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    statistical_summary: Dict[str, Any] = Field(default_factory=dict)
    
    # Insights
    best_performing: Optional[int] = Field(None, description="ID of best performing evaluation")
    performance_ranking: List[int] = Field(default_factory=list, description="Evaluation IDs ranked by performance")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations based on comparison")