"""
Base satellite data client for standardized satellite API interactions
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


class SatelliteDataClient(ABC):
    """
    Abstract base class for satellite data clients.
    Provides a standardized interface for different satellite data sources.
    """
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    async def get_imagery_metadata(
        self, 
        bounds: Tuple[float, float, float, float],  # (min_lon, min_lat, max_lon, max_lat)
        start_date: date,
        end_date: date,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Get metadata for available imagery in the specified area and time range.
        
        Args:
            bounds: Geographic bounds (min_lon, min_lat, max_lon, max_lat)
            start_date: Start date for imagery search
            end_date: End date for imagery search
            **kwargs: Additional provider-specific parameters
            
        Returns:
            List of imagery metadata dictionaries
        """
        pass
    
    @abstractmethod
    async def get_vegetation_index(
        self,
        bounds: Tuple[float, float, float, float],
        date_range: Tuple[date, date],
        index_type: str = "NDVI",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate vegetation indices for the specified area and time.
        
        Args:
            bounds: Geographic bounds
            date_range: (start_date, end_date) tuple
            index_type: Type of vegetation index (NDVI, EVI, SAVI, etc.)
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing vegetation index data and statistics
        """
        pass
    
    @abstractmethod
    async def detect_land_cover_change(
        self,
        bounds: Tuple[float, float, float, float],
        before_date: date,
        after_date: date,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Detect land cover changes between two time periods.
        
        Args:
            bounds: Geographic bounds
            before_date: Date for "before" imagery
            after_date: Date for "after" imagery
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing change detection results
        """
        pass
    
    def validate_bounds(self, bounds: Tuple[float, float, float, float]) -> bool:
        """Validate geographic bounds format and values."""
        min_lon, min_lat, max_lon, max_lat = bounds
        
        if not (-180 <= min_lon <= 180 and -180 <= max_lon <= 180):
            return False
        if not (-90 <= min_lat <= 90 and -90 <= max_lat <= 90):
            return False
        if min_lon >= max_lon or min_lat >= max_lat:
            return False
            
        return True
    
    def calculate_area_hectares(self, bounds: Tuple[float, float, float, float]) -> float:
        """
        Calculate approximate area in hectares for the given bounds.
        Simple calculation assuming rectangular area.
        """
        min_lon, min_lat, max_lon, max_lat = bounds
        
        # Approximate conversion (varies by latitude)
        lat_avg = (min_lat + max_lat) / 2
        
        # Degrees to meters conversion (approximate)
        lon_deg_to_m = 111320 * abs(lat_avg * 0.017453292519943295)  # cos(lat in radians)
        lat_deg_to_m = 110540  # Approximately constant
        
        width_m = (max_lon - min_lon) * lon_deg_to_m
        height_m = (max_lat - min_lat) * lat_deg_to_m
        
        area_m2 = width_m * height_m
        area_hectares = area_m2 / 10000  # Convert to hectares
        
        return area_hectares


class MockSatelliteClient(SatelliteDataClient):
    """
    Mock satellite client for testing and demonstration purposes.
    Generates realistic but synthetic satellite data.
    """
    
    def __init__(self):
        super().__init__("MockSatellite")
    
    async def get_imagery_metadata(
        self, 
        bounds: Tuple[float, float, float, float],
        start_date: date,
        end_date: date,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Generate mock imagery metadata."""
        if not self.validate_bounds(bounds):
            raise ValueError("Invalid geographic bounds")
        
        # Generate mock imagery entries
        import random
        from datetime import timedelta
        
        imagery_list = []
        current_date = start_date
        
        while current_date <= end_date:
            # Skip some dates randomly to simulate data availability
            if random.random() > 0.3:  # 70% chance of data availability
                imagery_list.append({
                    "id": f"MOCK_{current_date.strftime('%Y%m%d')}",
                    "date": current_date.isoformat(),
                    "sensor": "MockSat-1",
                    "resolution": 10,  # meters
                    "cloud_cover": random.uniform(0, 30),
                    "bounds": bounds,
                    "url": f"https://mock-satellite.example.com/data/{current_date.strftime('%Y%m%d')}",
                    "bands": ["B02", "B03", "B04", "B08"],  # Blue, Green, Red, NIR
                    "processing_level": "L2A"
                })
            
            current_date += timedelta(days=random.randint(3, 16))  # Irregular intervals
        
        self.logger.info(f"Generated {len(imagery_list)} mock imagery entries for {bounds}")
        return imagery_list
    
    async def get_vegetation_index(
        self,
        bounds: Tuple[float, float, float, float],
        date_range: Tuple[date, date],
        index_type: str = "NDVI",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate mock vegetation index data."""
        if not self.validate_bounds(bounds):
            raise ValueError("Invalid geographic bounds")
        
        import random
        import numpy as np
        
        start_date, end_date = date_range
        area_hectares = self.calculate_area_hectares(bounds)
        
        # Generate realistic NDVI values based on area characteristics
        base_ndvi = 0.6 if area_hectares > 1000 else 0.4  # Assume larger areas are more forested
        
        # Simulate seasonal variation
        days_from_start = (end_date - start_date).days
        seasonal_factor = 0.1 * np.sin(days_from_start / 365.0 * 2 * np.pi)
        
        mean_ndvi = base_ndvi + seasonal_factor + random.uniform(-0.1, 0.1)
        mean_ndvi = max(0.0, min(1.0, mean_ndvi))  # Clamp to valid range
        
        # Generate statistics
        std_ndvi = random.uniform(0.05, 0.15)
        min_ndvi = max(0.0, mean_ndvi - 2 * std_ndvi)
        max_ndvi = min(1.0, mean_ndvi + 2 * std_ndvi)
        
        result = {
            "index_type": index_type,
            "bounds": bounds,
            "date_range": [start_date.isoformat(), end_date.isoformat()],
            "area_hectares": area_hectares,
            "statistics": {
                "mean": round(mean_ndvi, 4),
                "std": round(std_ndvi, 4),
                "min": round(min_ndvi, 4),
                "max": round(max_ndvi, 4),
                "median": round(mean_ndvi + random.uniform(-0.02, 0.02), 4),
                "pixel_count": int(area_hectares * 100),  # Assume 1 pixel per 100m²
                "valid_pixels": int(area_hectares * 85)   # 85% valid data
            },
            "interpretation": {
                "vegetation_health": "good" if mean_ndvi > 0.5 else "moderate" if mean_ndvi > 0.3 else "poor",
                "estimated_biomass_tons_ha": round(mean_ndvi * 150, 2),  # Rough biomass estimate
                "forest_coverage_percent": round(min(100, mean_ndvi * 120), 1),
                "change_trend": "stable"
            },
            "imagery_used": await self.get_imagery_metadata(bounds, start_date, end_date),
            "processing_info": {
                "processed_at": datetime.now().isoformat(),
                "algorithm": f"Mock {index_type} Calculator v1.0",
                "quality_flags": {
                    "cloud_contamination": random.uniform(0, 15),
                    "shadow_contamination": random.uniform(0, 10),
                    "data_quality_score": random.uniform(0.8, 1.0)
                }
            }
        }
        
        self.logger.info(f"Generated {index_type} data for {area_hectares:.1f} hectares")
        return result
    
    async def detect_land_cover_change(
        self,
        bounds: Tuple[float, float, float, float],
        before_date: date,
        after_date: date,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate mock land cover change detection."""
        if not self.validate_bounds(bounds):
            raise ValueError("Invalid geographic bounds")
        
        import random
        
        area_hectares = self.calculate_area_hectares(bounds)
        days_between = (after_date - before_date).days
        
        # Simulate different change types based on area size and time span
        change_probability = min(0.5, days_between / 365.0 * 0.2)  # More change over longer periods
        
        if random.random() < change_probability:
            # Simulate some change
            change_area = area_hectares * random.uniform(0.01, 0.15)  # 1-15% of area changed
            change_type = random.choice([
                "deforestation", "afforestation", "urbanization", 
                "agriculture_expansion", "natural_disturbance"
            ])
        else:
            # No significant change
            change_area = area_hectares * random.uniform(0.001, 0.005)  # <0.5% change
            change_type = "stable"
        
        # Calculate change metrics
        before_ndvi = await self.get_vegetation_index(bounds, (before_date, before_date))
        after_ndvi = await self.get_vegetation_index(bounds, (after_date, after_date))
        
        ndvi_change = after_ndvi["statistics"]["mean"] - before_ndvi["statistics"]["mean"]
        
        result = {
            "bounds": bounds,
            "analysis_period": {
                "before_date": before_date.isoformat(),
                "after_date": after_date.isoformat(),
                "days_between": days_between
            },
            "area_analysis": {
                "total_area_hectares": area_hectares,
                "changed_area_hectares": round(change_area, 2),
                "change_percentage": round(change_area / area_hectares * 100, 2),
                "stable_area_hectares": round(area_hectares - change_area, 2)
            },
            "change_detection": {
                "primary_change_type": change_type,
                "confidence_score": random.uniform(0.75, 0.95),
                "ndvi_change": round(ndvi_change, 4),
                "change_significance": "significant" if abs(ndvi_change) > 0.1 else "minor"
            },
            "environmental_impact": {
                "estimated_co2_impact_tons": round(change_area * random.uniform(-5, 15), 2),
                "biodiversity_impact": "negative" if change_type == "deforestation" else "positive" if change_type == "afforestation" else "neutral",
                "ecosystem_health_change": round(ndvi_change * 100, 1)
            },
            "imagery_analysis": {
                "before_imagery": before_ndvi["imagery_used"][:1],  # Take first image
                "after_imagery": after_ndvi["imagery_used"][:1]
            },
            "processing_info": {
                "processed_at": datetime.now().isoformat(),
                "algorithm": "Mock Change Detection v1.0",
                "quality_assessment": {
                    "temporal_consistency": random.uniform(0.8, 1.0),
                    "spatial_accuracy": random.uniform(0.85, 0.98),
                    "overall_confidence": random.uniform(0.8, 0.95)
                }
            }
        }
        
        self.logger.info(f"Detected {change_type} affecting {change_area:.1f} hectares")
        return result