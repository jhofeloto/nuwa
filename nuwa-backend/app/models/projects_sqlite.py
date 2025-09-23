"""
SQLite Project Database Models

SQLAlchemy models for carbon capture projects using SQLite.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, Enum, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from typing import Optional, Dict, Any

from app.core.database_sqlite import Base

class ProjectStatus(enum.Enum):
    """Project status enumeration."""
    DRAFT = "draft"
    SUBMITTED = "submitted" 
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ProjectType(enum.Enum):
    """Project type enumeration."""
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

class Project(Base):
    """
    Carbon Capture Project Model for SQLite
    
    Represents a carbon capture/sequestration project with all associated
    metadata, location information, and evaluation parameters.
    """
    __tablename__ = "projects"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    
    # Project classification
    project_type = Column(String(50), nullable=False)  # Store as string for SQLite
    status = Column(String(50), default="draft", nullable=False)  # Store as string for SQLite
    
    # Location details
    country = Column(String(100))
    region = Column(String(100)) 
    locality = Column(String(100))
    
    # Coordinates for center point
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Store boundary as JSON (simplified approach)
    boundary_geojson = Column(Text)  # Store as TEXT in SQLite
    
    # Area and scale
    total_area_hectares = Column(Float)
    project_area_hectares = Column(Float)  # Actual project implementation area
    
    # Timeline
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    project_duration_years = Column(Integer)
    
    # Carbon targets and projections
    estimated_co2_capture_tons_year = Column(Float)
    total_estimated_co2_tons = Column(Float)
    
    # Methodology and standards
    methodology = Column(String(200))
    standard = Column(String(100))  # e.g., VCS, CDM, Gold Standard
    baseline_scenario = Column(Text)
    
    # Economic information
    estimated_cost_usd = Column(Float)
    revenue_model = Column(Text)
    
    # Technical specifications (stored as JSON text)
    species_planted = Column(Text)  # JSON as TEXT for SQLite
    soil_types = Column(Text)       # JSON as TEXT for SQLite
    climate_zone = Column(String(100))
    average_rainfall_mm = Column(Float)
    average_temperature_c = Column(Float)
    
    # Project documentation
    feasibility_study_url = Column(String(500))
    environmental_impact_url = Column(String(500))
    community_engagement_url = Column(String(500))
    
    # Verification and monitoring
    monitoring_plan = Column(Text)
    verification_schedule = Column(Text)  # JSON as TEXT for SQLite
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Additional project metadata
    project_metadata = Column(Text)  # JSON as TEXT for SQLite (renamed to avoid conflict)
    
    # Validation flags
    is_validated = Column(Boolean, default=False)
    validation_notes = Column(Text)
    
    # Relationships will be defined when evaluation models are created
    # evaluations = relationship("Evaluation", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', type={self.project_type}, status={self.status})>"
    
    @property
    def area_sqkm(self) -> Optional[float]:
        """Calculate project area in square kilometers."""
        if self.project_area_hectares:
            return self.project_area_hectares / 100
        return None
    
    @property
    def is_active(self) -> bool:
        """Check if project is currently active."""
        return self.status == "active"
    
    @property
    def is_completed(self) -> bool:
        """Check if project is completed."""
        return self.status == "completed"
    
    @property
    def co2_capture_rate_per_hectare(self) -> Optional[float]:
        """Calculate CO2 capture rate per hectare per year."""
        if self.estimated_co2_capture_tons_year and self.project_area_hectares:
            return self.estimated_co2_capture_tons_year / self.project_area_hectares
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "project_type": self.project_type,
            "status": self.status,
            "country": self.country,
            "region": self.region,
            "locality": self.locality,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "total_area_hectares": self.total_area_hectares,
            "project_area_hectares": self.project_area_hectares,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "estimated_co2_capture_tons_year": self.estimated_co2_capture_tons_year,
            "total_estimated_co2_tons": self.total_estimated_co2_tons,
            "methodology": self.methodology,
            "standard": self.standard,
            "estimated_cost_usd": self.estimated_cost_usd,
            "climate_zone": self.climate_zone,
            "is_validated": self.is_validated,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "area_sqkm": self.area_sqkm,
            "co2_capture_rate_per_hectare": self.co2_capture_rate_per_hectare,
        }

class Evaluation(Base):
    """
    Project Evaluation Model for SQLite
    
    Represents an evaluation/assessment of a carbon capture project.
    """
    __tablename__ = "evaluations"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    
    # Project relationship
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    # Evaluation metadata
    evaluation_type = Column(String(50), nullable=False)  # baseline, monitoring, verification, etc.
    status = Column(String(50), default="pending", nullable=False)
    
    # Timeline
    evaluation_date = Column(DateTime, nullable=False)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    
    # Data sources used (stored as JSON text)
    satellite_data_sources = Column(Text)  # JSON array as TEXT
    ground_truth_data = Column(Boolean, default=False)
    field_measurements = Column(Boolean, default=False)
    
    # Analysis parameters
    analysis_method = Column(String(200))
    model_version = Column(String(100))
    
    # Results and metrics
    confidence_level = Column(String(20))  # low, medium, high, very_high
    
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
    detailed_results = Column(Text)  # JSON as TEXT
    
    # Processing information
    processing_time_seconds = Column(Float)
    algorithm_parameters = Column(Text)  # JSON as TEXT
    
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
    project = relationship("Project", foreign_keys=[project_id])
    
    def __repr__(self):
        return f"<Evaluation(id={self.id}, project_id={self.project_id}, type={self.evaluation_type}, status={self.status})>"
    
    @property
    def is_completed(self) -> bool:
        """Check if evaluation is completed."""
        return self.status == "completed"
    
    @property
    def has_high_confidence(self) -> bool:
        """Check if evaluation has high confidence level."""
        return self.confidence_level in ["high", "very_high"]
    
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
            "evaluation_type": self.evaluation_type,
            "status": self.status,
            "evaluation_date": self.evaluation_date.isoformat() if self.evaluation_date else None,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "confidence_level": self.confidence_level,
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