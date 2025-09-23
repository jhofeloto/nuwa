"""
Evaluation Database Models

SQLAlchemy models for project evaluations and assessment metrics.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from typing import Optional, Dict, Any

from app.core.database import Base

class EvaluationStatus(enum.Enum):
    """Evaluation status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class EvaluationType(enum.Enum):
    """Evaluation type enumeration."""
    BASELINE = "baseline"
    MONITORING = "monitoring"
    VERIFICATION = "verification"
    IMPACT_ASSESSMENT = "impact_assessment"
    FEASIBILITY = "feasibility"
    RISK_ASSESSMENT = "risk_assessment"

class ConfidenceLevel(enum.Enum):
    """Confidence level for evaluation results."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class Evaluation(Base):
    """
    Project Evaluation Model
    
    Represents an evaluation/assessment of a carbon capture project
    including satellite analysis, ML predictions, and various metrics.
    """
    __tablename__ = "evaluations"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    
    # Project relationship
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    # Evaluation metadata
    evaluation_type = Column(Enum(EvaluationType), nullable=False)
    status = Column(Enum(EvaluationStatus), default=EvaluationStatus.PENDING, nullable=False)
    
    # Timeline
    evaluation_date = Column(DateTime, nullable=False)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    
    # Data sources used
    satellite_data_sources = Column(JSON, default=list)  # ["sentinel-2", "landsat-8", etc.]
    ground_truth_data = Column(Boolean, default=False)
    field_measurements = Column(Boolean, default=False)
    
    # Analysis parameters
    analysis_method = Column(String(200))
    model_version = Column(String(100))
    
    # Results and metrics
    confidence_level = Column(Enum(ConfidenceLevel))
    
    # Carbon metrics
    estimated_co2_sequestered_tons = Column(Float)
    co2_sequestration_rate_tons_per_hectare = Column(Float)
    carbon_stock_change_tons = Column(Float)
    
    # Vegetation metrics
    ndvi_average = Column(Float)
    ndvi_change = Column(Float)
    vegetation_cover_percentage = Column(Float)
    biomass_estimate_tons = Column(Float)
    
    # Land use metrics
    deforestation_detected = Column(Boolean)
    deforested_area_hectares = Column(Float)
    land_use_change_percentage = Column(Float)
    
    # Environmental metrics
    soil_carbon_tons_per_hectare = Column(Float)
    water_stress_index = Column(Float)
    biodiversity_index = Column(Float)
    
    # Risk factors
    fire_risk_level = Column(String(50))
    drought_risk_level = Column(String(50))
    pest_disease_risk = Column(String(50))
    
    # Quality metrics
    data_quality_score = Column(Float)  # 0-1 scale
    cloud_cover_percentage = Column(Float)
    spatial_resolution_meters = Column(Float)
    
    # Detailed results (JSON storage for flexible metrics)
    detailed_results = Column(JSON, default=dict)
    
    # Processing information
    processing_time_seconds = Column(Float)
    algorithm_parameters = Column(JSON, default=dict)
    
    # Validation and verification
    verified = Column(Boolean, default=False)
    verification_date = Column(DateTime)
    verification_notes = Column(Text)
    
    # Notes and comments
    notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="evaluations")
    metrics = relationship("EvaluationMetrics", back_populates="evaluation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Evaluation(id={self.id}, project_id={self.project_id}, type={self.evaluation_type}, status={self.status})>"
    
    @property
    def is_completed(self) -> bool:
        """Check if evaluation is completed."""
        return self.status == EvaluationStatus.COMPLETED
    
    @property
    def has_high_confidence(self) -> bool:
        """Check if evaluation has high confidence level."""
        return self.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH]
    
    @property
    def co2_efficiency_rating(self) -> Optional[str]:
        """Calculate CO2 efficiency rating based on sequestration rate."""
        if not self.co2_sequestration_rate_tons_per_hectare:
            return None
        
        rate = self.co2_sequestration_rate_tons_per_hectare
        if rate >= 10:
            return "excellent"
        elif rate >= 7:
            return "good"
        elif rate >= 4:
            return "average"
        elif rate >= 2:
            return "below_average"
        else:
            return "poor"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert evaluation to dictionary representation."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "evaluation_type": self.evaluation_type.value if self.evaluation_type else None,
            "status": self.status.value if self.status else None,
            "evaluation_date": self.evaluation_date.isoformat() if self.evaluation_date else None,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "confidence_level": self.confidence_level.value if self.confidence_level else None,
            "estimated_co2_sequestered_tons": self.estimated_co2_sequestered_tons,
            "co2_sequestration_rate_tons_per_hectare": self.co2_sequestration_rate_tons_per_hectare,
            "ndvi_average": self.ndvi_average,
            "vegetation_cover_percentage": self.vegetation_cover_percentage,
            "biomass_estimate_tons": self.biomass_estimate_tons,
            "deforestation_detected": self.deforestation_detected,
            "data_quality_score": self.data_quality_score,
            "verified": self.verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "co2_efficiency_rating": self.co2_efficiency_rating,
        }

class EvaluationMetrics(Base):
    """
    Extended Evaluation Metrics Model
    
    Stores additional detailed metrics that may vary by evaluation type
    and methodology. Provides flexibility for different measurement approaches.
    """
    __tablename__ = "evaluation_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey('evaluations.id'), nullable=False)
    
    # Metric identification
    metric_name = Column(String(200), nullable=False)
    metric_category = Column(String(100))  # e.g., "carbon", "vegetation", "soil", "risk"
    
    # Metric values
    numeric_value = Column(Float)
    text_value = Column(String(500))
    json_value = Column(JSON)
    
    # Metric metadata
    unit = Column(String(50))
    measurement_method = Column(String(200))
    confidence_score = Column(Float)  # 0-1 scale
    
    # Temporal information
    measurement_date = Column(DateTime)
    
    # Spatial information (if applicable)
    spatial_coverage = Column(String(100))  # e.g., "full_area", "sample_points", "boundary"
    
    # Quality indicators
    accuracy_percentage = Column(Float)
    precision_value = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    evaluation = relationship("Evaluation", back_populates="metrics")
    
    def __repr__(self):
        return f"<EvaluationMetrics(id={self.id}, evaluation_id={self.evaluation_id}, metric='{self.metric_name}', value={self.numeric_value})>"