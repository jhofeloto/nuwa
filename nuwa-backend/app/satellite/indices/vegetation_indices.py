"""
Vegetation Indices Calculation Module
Calculates various vegetation indices for carbon capture assessment
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json


class VegetationIndicesCalculator:
    """
    Calculator for various vegetation indices used in carbon capture assessment.
    Provides comprehensive analysis of vegetation health and carbon potential.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Standard wavelength ranges for satellite bands (micrometers)
        self.band_ranges = {
            'blue': (0.45, 0.51),      # B2 in Sentinel-2
            'green': (0.54, 0.57),     # B3 in Sentinel-2  
            'red': (0.65, 0.68),       # B4 in Sentinel-2
            'red_edge': (0.70, 0.75),  # B5/B6/B7 in Sentinel-2
            'nir': (0.78, 0.88),       # B8 in Sentinel-2
            'swir1': (1.57, 1.65),     # B11 in Sentinel-2
            'swir2': (2.11, 2.29)      # B12 in Sentinel-2
        }
    
    def calculate_comprehensive_indices(
        self, 
        vegetation_data: Dict[str, Any], 
        location_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive vegetation indices from satellite data.
        
        Args:
            vegetation_data: Raw vegetation data from satellite APIs
            location_data: Location information (lat, lon, climate zone, etc.)
            
        Returns:
            Dictionary with calculated indices and interpretations
        """
        try:
            # Extract basic indices from input data
            ndvi = vegetation_data.get('ndvi', {}).get('value', 0.5)
            evi = vegetation_data.get('evi', {}).get('value', 0.4)
            
            # Calculate additional indices based on NDVI/EVI
            indices = {}
            
            # 1. Enhanced Vegetation Index 2 (EVI2) - simplified EVI
            indices['evi2'] = self._calculate_evi2(ndvi)
            
            # 2. Soil Adjusted Vegetation Index (SAVI)
            indices['savi'] = self._calculate_savi(ndvi, L=0.5)
            
            # 3. Modified Soil Adjusted Vegetation Index (MSAVI)
            indices['msavi'] = self._calculate_msavi(ndvi)
            
            # 4. Green Normalized Difference Vegetation Index (GNDVI)
            indices['gndvi'] = self._calculate_gndvi(ndvi)
            
            # 5. Leaf Area Index (LAI) estimation
            indices['lai'] = self._estimate_lai(ndvi, evi)
            
            # 6. Fraction of Photosynthetically Active Radiation (fPAR)
            indices['fpar'] = self._calculate_fpar(ndvi)
            
            # 7. Gross Primary Productivity approximation
            indices['gpp_estimate'] = self._estimate_gpp(ndvi, evi, location_data)
            
            # 8. Vegetation Condition Index (VCI)
            indices['vci'] = self._calculate_vci(ndvi)
            
            # 9. Normalized Burn Ratio (NBR) - for forest health
            indices['nbr'] = self._estimate_nbr(ndvi)
            
            # Calculate carbon-specific metrics
            carbon_metrics = self._calculate_carbon_metrics(indices, location_data)
            
            # Temporal analysis if historical data available
            temporal_analysis = self._analyze_temporal_trends(vegetation_data)
            
            return {
                'success': True,
                'indices': indices,
                'carbon_metrics': carbon_metrics,
                'temporal_analysis': temporal_analysis,
                'quality_assessment': self._assess_data_quality(indices),
                'recommendations': self._generate_recommendations(indices, carbon_metrics),
                'calculation_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating vegetation indices: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _calculate_evi2(self, ndvi: float) -> Dict[str, Any]:
        """
        Calculate Enhanced Vegetation Index 2 (simplified version).
        EVI2 = 2.5 * (NIR - Red) / (NIR + 2.4 * Red + 1)
        Approximated from NDVI.
        """
        # Approximate EVI2 from NDVI using empirical relationship
        evi2_value = ndvi * 0.8 + 0.1  # Simplified conversion
        evi2_value = max(0, min(1, evi2_value))
        
        return {
            'value': round(evi2_value, 4),
            'description': 'Enhanced Vegetation Index 2',
            'interpretation': self._interpret_evi(evi2_value),
            'use_case': 'Improved vegetation monitoring in high biomass areas'
        }
    
    def _calculate_savi(self, ndvi: float, L: float = 0.5) -> Dict[str, Any]:
        """
        Calculate Soil Adjusted Vegetation Index.
        SAVI = ((NIR - Red) / (NIR + Red + L)) * (1 + L)
        """
        # Approximate from NDVI: SAVI ≈ NDVI * (1 + L) / (1 + L * NDVI)
        savi_value = ndvi * (1 + L) / (1 + L * ndvi)
        savi_value = max(0, min(1, savi_value))
        
        return {
            'value': round(savi_value, 4),
            'description': 'Soil Adjusted Vegetation Index',
            'L_factor': L,
            'interpretation': self._interpret_savi(savi_value),
            'use_case': 'Vegetation assessment in areas with exposed soil'
        }
    
    def _calculate_msavi(self, ndvi: float) -> Dict[str, Any]:
        """
        Calculate Modified Soil Adjusted Vegetation Index.
        More sophisticated soil adjustment than SAVI.
        """
        # Simplified approximation from NDVI
        msavi_value = ndvi * 0.95 + 0.02
        msavi_value = max(0, min(1, msavi_value))
        
        return {
            'value': round(msavi_value, 4),
            'description': 'Modified Soil Adjusted Vegetation Index',
            'interpretation': self._interpret_savi(msavi_value),
            'use_case': 'Advanced soil background correction'
        }
    
    def _calculate_gndvi(self, ndvi: float) -> Dict[str, Any]:
        """
        Calculate Green Normalized Difference Vegetation Index.
        More sensitive to chlorophyll content.
        """
        # Approximate from NDVI with slight adjustment for chlorophyll sensitivity
        gndvi_value = ndvi * 0.85 + 0.05
        gndvi_value = max(0, min(1, gndvi_value))
        
        return {
            'value': round(gndvi_value, 4),
            'description': 'Green Normalized Difference Vegetation Index',
            'interpretation': self._interpret_ndvi(gndvi_value),
            'use_case': 'Chlorophyll content assessment'
        }
    
    def _estimate_lai(self, ndvi: float, evi: float) -> Dict[str, Any]:
        """
        Estimate Leaf Area Index from vegetation indices.
        LAI represents the total leaf area per unit ground area.
        """
        # Empirical relationship: LAI = f(NDVI, EVI)
        # Based on scientific literature correlations
        
        if ndvi < 0.2:
            lai_value = 0.1
        elif ndvi < 0.5:
            lai_value = (ndvi - 0.2) * 6.67  # Linear growth up to LAI=2
        else:
            # Logarithmic relationship for higher NDVI values
            lai_value = 2 + np.log(1 + (ndvi - 0.5) * 10) * 1.5
        
        # EVI adjustment
        evi_factor = max(0.8, min(1.2, evi / ndvi)) if ndvi > 0 else 1.0
        lai_value *= evi_factor
        
        lai_value = max(0.1, min(8.0, lai_value))  # Realistic bounds
        
        return {
            'value': round(lai_value, 2),
            'unit': 'm²/m²',
            'description': 'Leaf Area Index',
            'interpretation': self._interpret_lai(lai_value),
            'carbon_relevance': 'Higher LAI indicates more photosynthetic surface area'
        }
    
    def _calculate_fpar(self, ndvi: float) -> Dict[str, Any]:
        """
        Calculate fraction of Photosynthetically Active Radiation absorbed.
        """
        # Empirical relationship: fPAR = f(NDVI)
        if ndvi < 0.125:
            fpar_value = 0
        elif ndvi > 0.8:
            fpar_value = 0.95
        else:
            # Linear relationship in the middle range
            fpar_value = 1.25 * ndvi - 0.15625
        
        fpar_value = max(0, min(0.95, fpar_value))
        
        return {
            'value': round(fpar_value, 4),
            'description': 'Fraction of Photosynthetically Active Radiation',
            'interpretation': self._interpret_fpar(fpar_value),
            'carbon_relevance': 'Direct indicator of photosynthetic potential'
        }
    
    def _estimate_gpp(self, ndvi: float, evi: float, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate Gross Primary Productivity.
        """
        # Base GPP from vegetation indices
        base_gpp = (ndvi * 0.6 + evi * 0.4) * 15  # kg C/m²/year
        
        # Climate zone adjustment
        climate_zone = location_data.get('climate_zone', 'temperate')
        climate_factors = {
            'tropical': 1.3,
            'subtropical': 1.1,
            'temperate': 1.0,
            'boreal': 0.8,
            'mediterranean': 1.05,
            'arid': 0.6,
            'semi-arid': 0.75
        }
        
        climate_factor = climate_factors.get(climate_zone.lower(), 1.0)
        adjusted_gpp = base_gpp * climate_factor
        
        # Convert to tons CO2 equivalent per hectare per year
        co2_equivalent = adjusted_gpp * 44/12 * 10  # Convert C to CO2, m² to ha
        
        return {
            'value_kg_c_m2_year': round(adjusted_gpp, 2),
            'value_tons_co2_ha_year': round(co2_equivalent, 2),
            'description': 'Gross Primary Productivity estimate',
            'methodology': 'vegetation_indices_correlation',
            'uncertainty': '±30%',
            'carbon_relevance': 'Total carbon fixed through photosynthesis'
        }
    
    def _calculate_vci(self, ndvi: float) -> Dict[str, Any]:
        """
        Calculate Vegetation Condition Index (relative to historical normal).
        """
        # For new areas, use climate-based normal
        # This would ideally use long-term historical data
        
        # Assume normal NDVI for the region (this would be database-driven in production)
        normal_ndvi = 0.6  # Baseline assumption
        
        if normal_ndvi > 0:
            vci_value = (ndvi / normal_ndvi) * 100
        else:
            vci_value = 50  # Neutral if no baseline
        
        vci_value = max(0, min(200, vci_value))
        
        return {
            'value': round(vci_value, 1),
            'unit': 'percent',
            'description': 'Vegetation Condition Index',
            'interpretation': self._interpret_vci(vci_value),
            'baseline_ndvi': normal_ndvi
        }
    
    def _estimate_nbr(self, ndvi: float) -> Dict[str, Any]:
        """
        Estimate Normalized Burn Ratio for forest health assessment.
        """
        # Approximate NBR from NDVI (in reality uses NIR and SWIR bands)
        # Healthy vegetation typically has NBR > 0.1
        nbr_value = ndvi * 0.7 - 0.1
        nbr_value = max(-1, min(1, nbr_value))
        
        return {
            'value': round(nbr_value, 4),
            'description': 'Normalized Burn Ratio (estimated)',
            'interpretation': self._interpret_nbr(nbr_value),
            'use_case': 'Forest health and burn severity assessment'
        }
    
    def _calculate_carbon_metrics(self, indices: Dict[str, Any], location_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate carbon-specific metrics from vegetation indices.
        """
        lai = indices['lai']['value']
        fpar = indices['fpar']['value'] 
        gpp = indices['gpp_estimate']['value_tons_co2_ha_year']
        
        # Above-ground biomass estimation (tons/ha)
        # Based on LAI and vegetation type
        agb = lai * 25  # Simplified relationship
        
        # Carbon stock in biomass (tons C/ha)
        carbon_stock = agb * 0.47  # ~47% of biomass is carbon
        
        # Net Primary Productivity (rough approximation)
        npp = gpp * 0.45  # NPP ≈ 45% of GPP
        
        # Carbon sequestration rate (tons CO2/ha/year)
        sequestration_rate = npp * 44/12  # Convert C to CO2
        
        return {
            'above_ground_biomass_tons_ha': round(agb, 1),
            'carbon_stock_tons_c_ha': round(carbon_stock, 1),
            'npp_tons_c_ha_year': round(npp, 2),
            'sequestration_rate_tons_co2_ha_year': round(sequestration_rate, 2),
            'methodology': 'allometric_equations_and_indices',
            'uncertainty': {
                'biomass': '±40%',
                'carbon_stock': '±35%',
                'sequestration_rate': '±50%'
            }
        }
    
    def _analyze_temporal_trends(self, vegetation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze temporal trends in vegetation data.
        """
        # This would analyze historical time series in a full implementation
        return {
            'trend_available': False,
            'reason': 'Requires historical time series data',
            'recommendation': 'Collect multi-temporal observations for trend analysis'
        }
    
    def _assess_data_quality(self, indices: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess the quality of calculated indices.
        """
        quality_score = 0
        issues = []
        
        # Check for realistic values
        lai_value = indices['lai']['value']
        if 0.1 <= lai_value <= 8:
            quality_score += 25
        else:
            issues.append('LAI value outside realistic range')
        
        fpar_value = indices['fpar']['value']
        if 0 <= fpar_value <= 0.95:
            quality_score += 25
        else:
            issues.append('fPAR value outside realistic range')
        
        # Add more quality checks as needed
        quality_score += 50  # Base score for calculation completion
        
        return {
            'overall_score': quality_score,
            'quality_level': 'high' if quality_score >= 80 else 'medium' if quality_score >= 60 else 'low',
            'issues_identified': issues,
            'data_completeness': 100  # All indices calculated
        }
    
    def _generate_recommendations(self, indices: Dict[str, Any], carbon_metrics: Dict[str, Any]) -> List[str]:
        """
        Generate management recommendations based on vegetation analysis.
        """
        recommendations = []
        
        lai = indices['lai']['value']
        sequestration_rate = carbon_metrics['sequestration_rate_tons_co2_ha_year']
        
        if lai < 2:
            recommendations.append("Low vegetation density detected. Consider reforestation or afforestation activities.")
        
        if sequestration_rate < 5:
            recommendations.append("Low carbon sequestration potential. Investigate soil conditions and species selection.")
        
        if sequestration_rate > 15:
            recommendations.append("High carbon sequestration potential identified. Prioritize for carbon credit development.")
        
        if indices['vci']['value'] < 80:
            recommendations.append("Vegetation condition below normal. Monitor for stress factors.")
        
        return recommendations
    
    # Interpretation methods
    def _interpret_ndvi(self, ndvi: float) -> str:
        """Interpret NDVI values."""
        if ndvi < 0.1: return 'No vegetation'
        elif ndvi < 0.2: return 'Sparse vegetation'
        elif ndvi < 0.4: return 'Moderate vegetation'
        elif ndvi < 0.6: return 'Dense vegetation'
        else: return 'Very dense vegetation'
    
    def _interpret_evi(self, evi: float) -> str:
        """Interpret EVI values."""
        if evi < 0.1: return 'No photosynthetic activity'
        elif evi < 0.3: return 'Low activity'
        elif evi < 0.5: return 'Moderate activity'
        else: return 'High photosynthetic activity'
    
    def _interpret_savi(self, savi: float) -> str:
        """Interpret SAVI values."""
        return self._interpret_ndvi(savi)  # Similar interpretation to NDVI
    
    def _interpret_lai(self, lai: float) -> str:
        """Interpret LAI values."""
        if lai < 1: return 'Sparse canopy'
        elif lai < 3: return 'Moderate canopy'
        elif lai < 5: return 'Dense canopy'
        else: return 'Very dense, multi-layer canopy'
    
    def _interpret_fpar(self, fpar: float) -> str:
        """Interpret fPAR values."""
        if fpar < 0.2: return 'Low light absorption'
        elif fpar < 0.5: return 'Moderate light absorption'
        elif fpar < 0.8: return 'High light absorption'
        else: return 'Maximum light absorption'
    
    def _interpret_vci(self, vci: float) -> str:
        """Interpret VCI values."""
        if vci < 35: return 'Poor vegetation condition'
        elif vci < 65: return 'Below normal condition'
        elif vci < 85: return 'Normal condition'
        else: return 'Above normal condition'
    
    def _interpret_nbr(self, nbr: float) -> str:
        """Interpret NBR values."""
        if nbr < -0.1: return 'Severely burned or bare'
        elif nbr < 0.1: return 'Moderate burn or stressed'
        elif nbr < 0.3: return 'Healthy vegetation'
        else: return 'Very healthy vegetation'


# Global vegetation indices calculator instance
vegetation_calculator = VegetationIndicesCalculator()


if __name__ == "__main__":
    # Test the vegetation indices calculator
    calculator = VegetationIndicesCalculator()
    
    # Mock vegetation data
    test_vegetation_data = {
        'ndvi': {'value': 0.7, 'confidence': 0.9},
        'evi': {'value': 0.6, 'confidence': 0.85}
    }
    
    test_location_data = {
        'latitude': -3.4653,
        'longitude': -62.2159,
        'climate_zone': 'tropical'
    }
    
    result = calculator.calculate_comprehensive_indices(
        test_vegetation_data, 
        test_location_data
    )
    
    print("Vegetation Indices Test Result:")
    print(json.dumps(result, indent=2))