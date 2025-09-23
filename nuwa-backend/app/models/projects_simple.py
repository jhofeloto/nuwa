"""
Simplified Project Database Models (without geospatial dependencies)

SQLAlchemy models for carbon capture projects without PostGIS dependencies.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, Enum, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from typing import Optional, Dict, Any

from app.core.database import Base

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
    Carbon Capture Project Model (Simplified)
    
    Represents a carbon capture/sequestration project with all associated
    metadata, location information, and evaluation parameters.
    """
    __tablename__ = "projects"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    
    # Project classification
    project_type = Column(Enum(ProjectType), nullable=False)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False)
    
    # Location details (simplified - no PostGIS geometry)
    country = Column(String(100))
    region = Column(String(100)) 
    locality = Column(String(100))
    
    # Coordinates for center point
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Store boundary as JSON (simplified approach)
    boundary_geojson = Column(JSON)
    
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
    
    # Technical specifications
    species_planted = Column(JSON)  # For forestry projects
    soil_types = Column(JSON)
    climate_zone = Column(String(100))
    average_rainfall_mm = Column(Float)
    average_temperature_c = Column(Float)
    
    # Project documentation
    feasibility_study_url = Column(String(500))
    environmental_impact_url = Column(String(500))
    community_engagement_url = Column(String(500))
    
    # Verification and monitoring
    monitoring_plan = Column(Text)
    verification_schedule = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Additional project metadata
    metadata = Column(JSON, default=dict)
    
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
        return self.status == ProjectStatus.ACTIVE
    
    @property
    def is_completed(self) -> bool:
        """Check if project is completed."""
        return self.status == ProjectStatus.COMPLETED
    
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
            "project_type": self.project_type.value if self.project_type else None,
            "status": self.status.value if self.status else None,
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
        }