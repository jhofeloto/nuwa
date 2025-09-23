"""
Geospatial Database Models

SQLAlchemy models for geospatial data, satellite images, and geographic analysis.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry, Raster
import enum
from datetime import datetime
from typing import Optional, Dict, Any, List

from app.core.database import Base

class DataSource(enum.Enum):
    """Satellite data source enumeration."""
    SENTINEL_2 = "sentinel-2"
    LANDSAT_8 = "landsat-8"
    LANDSAT_9 = "landsat-9"
    MODIS = "modis"
    PLANET = "planet"
    AERIAL = "aerial"
    DRONE = "drone"
    OTHER = "other"

class ProcessingStatus(enum.Enum):
    """Processing status for geospatial data."""
    RAW = "raw"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ANALYZED = "analyzed"
    FAILED = "failed"

class GeospatialData(Base):
    """
    Geospatial Data Model
    
    Stores geospatial datasets associated with carbon capture projects
    including satellite imagery, vector data, and analysis results.
    """
    __tablename__ = "geospatial_data"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    
    # Project relationship
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    # Data identification
    name = Column(String(200), nullable=False)
    description = Column(Text)
    data_type = Column(String(100))  # e.g., "raster", "vector", "point_cloud"
    
    # Data source information
    source = Column(Enum(DataSource), nullable=False)
    source_id = Column(String(200))  # Original ID from data source
    
    # Temporal information
    acquisition_date = Column(DateTime)
    processing_date = Column(DateTime)
    
    # Spatial information
    geometry = Column(Geometry('GEOMETRY', srid=4326))  # Footprint or boundary
    spatial_resolution_meters = Column(Float)
    coordinate_system = Column(String(100), default="EPSG:4326")
    
    # Raster data (for satellite imagery)
    raster_data = Column(Raster)  # PostGIS raster support
    
    # File information
    file_path = Column(String(500))
    file_size_bytes = Column(Integer)
    file_format = Column(String(50))  # e.g., "GeoTIFF", "NetCDF", "Shapefile"
    
    # Processing status and metadata
    processing_status = Column(Enum(ProcessingStatus), default=ProcessingStatus.RAW)
    processing_parameters = Column(JSON, default=dict)
    
    # Quality metrics
    cloud_cover_percentage = Column(Float)
    quality_score = Column(Float)  # 0-1 scale
    
    # Band/spectral information (for multispectral data)
    spectral_bands = Column(JSON, default=list)  # List of band names/wavelengths
    
    # Analysis results
    analysis_results = Column(JSON, default=dict)
    
    # Storage and access information
    storage_location = Column(String(500))  # URL or path to stored data
    access_url = Column(String(500))  # Public access URL if available
    
    # Metadata
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="geospatial_data")
    satellite_images = relationship("SatelliteImage", back_populates="geospatial_data", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<GeospatialData(id={self.id}, name='{self.name}', source={self.source}, project_id={self.project_id})>"
    
    @property
    def is_processed(self) -> bool:
        """Check if data has been processed."""
        return self.processing_status in [ProcessingStatus.PROCESSED, ProcessingStatus.ANALYZED]
    
    @property
    def has_good_quality(self) -> bool:
        """Check if data has good quality (low cloud cover, high quality score)."""
        cloud_ok = not self.cloud_cover_percentage or self.cloud_cover_percentage < 20
        quality_ok = not self.quality_score or self.quality_score > 0.7
        return cloud_ok and quality_ok
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert geospatial data to dictionary representation."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "data_type": self.data_type,
            "source": self.source.value if self.source else None,
            "acquisition_date": self.acquisition_date.isoformat() if self.acquisition_date else None,
            "processing_date": self.processing_date.isoformat() if self.processing_date else None,
            "spatial_resolution_meters": self.spatial_resolution_meters,
            "processing_status": self.processing_status.value if self.processing_status else None,
            "cloud_cover_percentage": self.cloud_cover_percentage,
            "quality_score": self.quality_score,
            "file_format": self.file_format,
            "file_size_bytes": self.file_size_bytes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class SatelliteImage(Base):
    """
    Satellite Image Model
    
    Specific model for satellite imagery with detailed spectral and
    processing information for vegetation and carbon analysis.
    """
    __tablename__ = "satellite_images"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    
    # Parent geospatial data
    geospatial_data_id = Column(Integer, ForeignKey('geospatial_data.id'), nullable=False)
    
    # Satellite-specific information
    satellite_name = Column(String(100))  # e.g., "Sentinel-2A", "Landsat-8"
    sensor_type = Column(String(100))     # e.g., "MSI", "OLI"
    
    # Orbit and scene information
    orbit_number = Column(Integer)
    scene_id = Column(String(200))
    product_id = Column(String(200))
    
    # Acquisition details
    sun_elevation_angle = Column(Float)
    sun_azimuth_angle = Column(Float)
    view_angle = Column(Float)
    
    # Atmospheric conditions
    atmospheric_correction = Column(Boolean, default=False)
    atmospheric_parameters = Column(JSON, default=dict)
    
    # Spectral indices (calculated from bands)
    ndvi = Column(Float)          # Normalized Difference Vegetation Index
    evi = Column(Float)           # Enhanced Vegetation Index  
    ndwi = Column(Float)          # Normalized Difference Water Index
    nbr = Column(Float)           # Normalized Burn Ratio
    savi = Column(Float)          # Soil-Adjusted Vegetation Index
    
    # Land cover classification results
    land_cover_classes = Column(JSON, default=dict)  # Percentage of each class
    dominant_land_cover = Column(String(100))
    
    # Vegetation analysis results
    vegetation_cover_percentage = Column(Float)
    biomass_estimate_tons_per_hectare = Column(Float)
    leaf_area_index = Column(Float)
    
    # Change detection (compared to previous images)
    change_detected = Column(Boolean)
    change_type = Column(String(100))  # e.g., "deforestation", "growth", "degradation"
    change_magnitude = Column(Float)
    
    # Processing information
    processing_level = Column(String(20))  # e.g., "L1C", "L2A", "L3"
    processing_date = Column(DateTime)
    processing_software = Column(String(100))
    
    # Analysis parameters
    analysis_algorithms = Column(JSON, default=list)
    algorithm_versions = Column(JSON, default=dict)
    
    # Quality assessment
    overall_quality = Column(String(50))  # e.g., "excellent", "good", "fair", "poor"
    quality_flags = Column(JSON, default=list)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    geospatial_data = relationship("GeospatialData", back_populates="satellite_images")
    
    def __repr__(self):
        return f"<SatelliteImage(id={self.id}, satellite='{self.satellite_name}', scene_id='{self.scene_id}')>"
    
    @property
    def has_vegetation_indices(self) -> bool:
        """Check if vegetation indices are calculated."""
        return any([self.ndvi, self.evi, self.savi])
    
    @property
    def vegetation_health_score(self) -> Optional[float]:
        """Calculate vegetation health score based on indices (0-1 scale)."""
        if not self.ndvi:
            return None
        
        # Simple health score based on NDVI
        # NDVI ranges from -1 to 1, healthy vegetation typically > 0.3
        if self.ndvi >= 0.7:
            return 1.0
        elif self.ndvi >= 0.5:
            return 0.8
        elif self.ndvi >= 0.3:
            return 0.6
        elif self.ndvi >= 0.1:
            return 0.4
        else:
            return 0.2
    
    def calculate_spectral_indices(self, red: float, nir: float, blue: float = None, swir: float = None) -> Dict[str, float]:
        """
        Calculate spectral indices from band values.
        
        Args:
            red: Red band reflectance (0-1)
            nir: Near-infrared band reflectance (0-1) 
            blue: Blue band reflectance (0-1), optional
            swir: Short-wave infrared reflectance (0-1), optional
            
        Returns:
            Dictionary of calculated indices
        """
        indices = {}
        
        # NDVI: (NIR - Red) / (NIR + Red)
        if nir is not None and red is not None:
            denominator = nir + red
            if denominator != 0:
                indices['ndvi'] = (nir - red) / denominator
        
        # EVI: 2.5 * ((NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1))
        if nir is not None and red is not None and blue is not None:
            denominator = nir + 6*red - 7.5*blue + 1
            if denominator != 0:
                indices['evi'] = 2.5 * ((nir - red) / denominator)
        
        # SAVI: ((NIR - Red) / (NIR + Red + 0.5)) * 1.5
        if nir is not None and red is not None:
            denominator = nir + red + 0.5
            if denominator != 0:
                indices['savi'] = ((nir - red) / denominator) * 1.5
        
        # NBR: (NIR - SWIR) / (NIR + SWIR)
        if nir is not None and swir is not None:
            denominator = nir + swir
            if denominator != 0:
                indices['nbr'] = (nir - swir) / denominator
        
        return indices
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert satellite image to dictionary representation."""
        return {
            "id": self.id,
            "geospatial_data_id": self.geospatial_data_id,
            "satellite_name": self.satellite_name,
            "sensor_type": self.sensor_type,
            "scene_id": self.scene_id,
            "orbit_number": self.orbit_number,
            "sun_elevation_angle": self.sun_elevation_angle,
            "atmospheric_correction": self.atmospheric_correction,
            "ndvi": self.ndvi,
            "evi": self.evi,
            "ndwi": self.ndwi,
            "vegetation_cover_percentage": self.vegetation_cover_percentage,
            "biomass_estimate_tons_per_hectare": self.biomass_estimate_tons_per_hectare,
            "change_detected": self.change_detected,
            "change_type": self.change_type,
            "processing_level": self.processing_level,
            "overall_quality": self.overall_quality,
            "vegetation_health_score": self.vegetation_health_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }