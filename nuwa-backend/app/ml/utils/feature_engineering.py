"""
Feature Engineering for Carbon Capture Projects
Transforms project data into ML-ready features
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json


class CarbonFeatureEngineer:
    """
    Feature engineering class for carbon capture projects.
    Converts project metadata into numerical features for ML models.
    """
    
    def __init__(self):
        # Climate zone mappings (normalized 0-1)
        self.climate_zones = {
            "tropical": 1.0,
            "subtropical": 0.8,
            "temperate": 0.6,
            "boreal": 0.4,
            "arctic": 0.2,
            "mediterranean": 0.7,
            "arid": 0.3,
            "semi-arid": 0.4
        }
        
        # Vegetation type carbon sequestration potential (normalized 0-1)
        self.vegetation_types = {
            "forest": 1.0,
            "grassland": 0.4,
            "wetland": 0.8,
            "agricultural": 0.3,
            "agroforestry": 0.7,
            "mangrove": 0.9,
            "bamboo": 0.8,
            "shrubland": 0.5,
            "mixed": 0.6
        }
        
        # Project methodology efficiency factors
        self.methodologies = {
            "afforestation": 0.9,
            "reforestation": 0.8,
            "agroforestry": 0.7,
            "soil_carbon": 0.6,
            "wetland_restoration": 0.8,
            "grassland_management": 0.5,
            "biochar": 0.7,
            "direct_air_capture": 0.9,
            "other": 0.4
        }
        
        # Soil type carbon storage capacity
        self.soil_types = {
            "clay": 0.9,
            "loam": 0.8,
            "sandy": 0.4,
            "peat": 1.0,
            "silt": 0.7,
            "rocky": 0.2,
            "mixed": 0.6
        }
    
    def extract_features(self, project_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract numerical features from project data.
        
        Args:
            project_data: Project dictionary with metadata
            
        Returns:
            Dictionary of numerical features ready for ML
        """
        features = {}
        
        # Basic project features
        features['area_hectares'] = float(project_data.get('area_hectares', 0))
        features['duration_years'] = float(project_data.get('duration_years', 1))
        features['budget_usd'] = float(project_data.get('budget_usd', 0))
        
        # Climate and environmental features
        climate_zone = project_data.get('climate_zone', 'temperate')
        features['climate_factor'] = self.climate_zones.get(climate_zone.lower(), 0.6)
        
        vegetation_type = project_data.get('vegetation_type', 'mixed')
        features['vegetation_factor'] = self.vegetation_types.get(vegetation_type.lower(), 0.6)
        
        methodology = project_data.get('methodology', 'other')
        features['methodology_factor'] = self.methodologies.get(methodology.lower(), 0.4)
        
        # Soil and geological features
        soil_type = project_data.get('soil_type', 'mixed')
        features['soil_factor'] = self.soil_types.get(soil_type.lower(), 0.6)
        
        # Environmental conditions
        features['annual_rainfall_mm'] = float(project_data.get('annual_rainfall_mm', 1000))
        features['avg_temperature_c'] = float(project_data.get('avg_temperature_c', 20))
        features['elevation_m'] = float(project_data.get('elevation_m', 0))
        
        # Derived features
        features['area_budget_ratio'] = (
            features['area_hectares'] / max(features['budget_usd'], 1) * 1000
        )
        features['rainfall_temperature_index'] = (
            features['annual_rainfall_mm'] / max(features['avg_temperature_c'], 1)
        )
        
        # Geographic and location features
        latitude = project_data.get('latitude', 0)
        longitude = project_data.get('longitude', 0)
        features['latitude_abs'] = abs(float(latitude))  # Distance from equator
        features['longitude'] = float(longitude)
        
        # Temporal features
        start_date = project_data.get('start_date')
        if start_date:
            if isinstance(start_date, str):
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            features['start_month'] = start_date.month
            features['start_season'] = self._get_season(start_date.month)
        else:
            features['start_month'] = 6  # Default to mid-year
            features['start_season'] = 2  # Default to summer
        
        # Technology and management features
        technology_level = project_data.get('technology_level', 'medium')
        features['technology_factor'] = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.9,
            'advanced': 1.0
        }.get(technology_level.lower(), 0.6)
        
        # Scale and efficiency features
        features['project_scale'] = min(features['area_hectares'] / 1000, 1.0)  # Normalized to 1000ha
        features['intensity_factor'] = (
            features['methodology_factor'] * 
            features['vegetation_factor'] * 
            features['climate_factor']
        )
        
        return features
    
    def _get_season(self, month: int) -> float:
        """Convert month to seasonal factor (Northern Hemisphere)"""
        if month in [12, 1, 2]:  # Winter
            return 0.25
        elif month in [3, 4, 5]:  # Spring
            return 0.75
        elif month in [6, 7, 8]:  # Summer
            return 1.0
        else:  # Fall
            return 0.5
    
    def create_feature_dataframe(self, projects: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert list of projects to feature DataFrame.
        
        Args:
            projects: List of project dictionaries
            
        Returns:
            Pandas DataFrame with extracted features
        """
        feature_list = []
        for project in projects:
            features = self.extract_features(project)
            features['project_id'] = project.get('id', 0)
            feature_list.append(features)
        
        return pd.DataFrame(feature_list)
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names for model training."""
        return [
            'area_hectares', 'duration_years', 'budget_usd',
            'climate_factor', 'vegetation_factor', 'methodology_factor', 'soil_factor',
            'annual_rainfall_mm', 'avg_temperature_c', 'elevation_m',
            'area_budget_ratio', 'rainfall_temperature_index',
            'latitude_abs', 'longitude', 'start_month', 'start_season',
            'technology_factor', 'project_scale', 'intensity_factor'
        ]


def generate_synthetic_training_data(n_samples: int = 1000) -> pd.DataFrame:
    """
    Generate synthetic training data for carbon capture prediction.
    
    Args:
        n_samples: Number of synthetic samples to generate
        
    Returns:
        DataFrame with features and target CO2 capture values
    """
    np.random.seed(42)  # For reproducible results
    
    feature_engineer = CarbonFeatureEngineer()
    projects = []
    
    for i in range(n_samples):
        # Generate realistic project parameters
        area = np.random.lognormal(mean=5, sigma=1.5)  # Log-normal distribution for area
        area = max(10, min(area, 50000))  # Clamp between 10 and 50,000 hectares
        
        duration = np.random.uniform(5, 30)  # 5-30 years
        
        # Budget correlates with area but with some noise
        budget = area * np.random.uniform(500, 5000) + np.random.normal(0, area * 100)
        budget = max(10000, budget)
        
        # Random climate and ecosystem parameters
        climate_zones = list(feature_engineer.climate_zones.keys())
        vegetation_types = list(feature_engineer.vegetation_types.keys())
        methodologies = list(feature_engineer.methodologies.keys())
        soil_types = list(feature_engineer.soil_types.keys())
        
        project = {
            'id': i,
            'area_hectares': area,
            'duration_years': duration,
            'budget_usd': budget,
            'climate_zone': np.random.choice(climate_zones),
            'vegetation_type': np.random.choice(vegetation_types),
            'methodology': np.random.choice(methodologies),
            'soil_type': np.random.choice(soil_types),
            'annual_rainfall_mm': np.random.uniform(200, 4000),
            'avg_temperature_c': np.random.uniform(-10, 35),
            'elevation_m': np.random.uniform(0, 4000),
            'latitude': np.random.uniform(-60, 60),
            'longitude': np.random.uniform(-180, 180),
            'start_date': datetime(2020, np.random.randint(1, 13), 1).isoformat(),
            'technology_level': np.random.choice(['low', 'medium', 'high', 'advanced'])
        }
        
        projects.append(project)
    
    # Create feature DataFrame
    df = feature_engineer.create_feature_dataframe(projects)
    
    # Generate realistic CO2 capture targets based on features
    # This uses a combination of area, intensity factors, and some noise
    base_co2_per_hectare = 10  # Base tons CO2/hectare/year
    
    df['co2_capture_tons_year'] = (
        df['area_hectares'] * 
        df['intensity_factor'] * 
        base_co2_per_hectare * 
        (1 + df['technology_factor'] * 0.5) *  # Technology boost
        (1 + np.random.normal(0, 0.2, len(df)))  # Random variation
    )
    
    # Ensure positive values and reasonable bounds
    df['co2_capture_tons_year'] = np.clip(df['co2_capture_tons_year'], 1, None)
    
    return df


if __name__ == "__main__":
    # Test the feature engineering
    engineer = CarbonFeatureEngineer()
    
    # Test single project feature extraction
    test_project = {
        'area_hectares': 1000,
        'duration_years': 10,
        'budget_usd': 500000,
        'climate_zone': 'tropical',
        'vegetation_type': 'forest',
        'methodology': 'afforestation',
        'soil_type': 'clay',
        'annual_rainfall_mm': 2000,
        'avg_temperature_c': 25,
        'elevation_m': 500,
        'latitude': -5.5,
        'longitude': -55.0,
        'start_date': '2024-06-01',
        'technology_level': 'high'
    }
    
    features = engineer.extract_features(test_project)
    print("Extracted features:", features)
    
    # Generate synthetic training data
    synthetic_data = generate_synthetic_training_data(100)
    print(f"\nGenerated {len(synthetic_data)} synthetic training samples")
    print("Feature columns:", synthetic_data.columns.tolist())
    print("\nSample data:")
    print(synthetic_data.head())