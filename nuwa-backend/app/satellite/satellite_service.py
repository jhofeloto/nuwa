"""
Main satellite data service for the Nuwa platform.
Coordinates multiple satellite data sources and provides unified API.
"""

import asyncio
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional, Union
import logging

from .clients.base_client import SatelliteDataClient, MockSatelliteClient
from .clients.sentinel2_client import Sentinel2Client
from .clients.landsat_client import LandsatClient

logger = logging.getLogger(__name__)


class SatelliteDataService:
    """
    Main service for satellite data integration in Nuwa platform.
    Provides unified access to multiple satellite data sources.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.clients: Dict[str, SatelliteDataClient] = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize available clients
        self._initialize_clients()
        
        # Service configuration
        self.default_client = "mock"  # Default to mock for demo
        self.max_concurrent_requests = 3
        self.cache_enabled = False  # Could be enabled for production
    
    def _initialize_clients(self):
        """Initialize all available satellite data clients."""
        # Mock client (always available for testing/demo)
        self.clients["mock"] = MockSatelliteClient()
        
        # Sentinel-2 client
        sentinel_config = self.config.get("sentinel2", {})
        self.clients["sentinel2"] = Sentinel2Client(
            username=sentinel_config.get("username"),
            password=sentinel_config.get("password")
        )
        
        # Landsat client  
        landsat_config = self.config.get("landsat", {})
        self.clients["landsat"] = LandsatClient(
            username=landsat_config.get("username"),
            password=landsat_config.get("password")
        )
        
        self.logger.info(f"Initialized {len(self.clients)} satellite clients: {list(self.clients.keys())}")
    
    def get_available_clients(self) -> List[str]:
        """Get list of available satellite data clients."""
        return list(self.clients.keys())
    
    def set_default_client(self, client_name: str):
        """Set the default satellite client."""
        if client_name not in self.clients:
            raise ValueError(f"Client '{client_name}' not available. Available: {list(self.clients.keys())}")
        self.default_client = client_name
        self.logger.info(f"Default client set to: {client_name}")
    
    async def get_project_satellite_analysis(
        self,
        project_bounds: Tuple[float, float, float, float],
        project_start_date: date,
        analysis_date: Optional[date] = None,
        client_preference: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive satellite analysis for a carbon capture project.
        
        Args:
            project_bounds: Geographic bounds (min_lon, min_lat, max_lon, max_lat)
            project_start_date: When the project started
            analysis_date: Current date for analysis (defaults to today)
            client_preference: Preferred satellite clients in order
            
        Returns:
            Comprehensive satellite analysis results
        """
        if analysis_date is None:
            analysis_date = date.today()
        
        if project_start_date >= analysis_date:
            raise ValueError("Project start date must be before analysis date")
        
        # Determine which clients to use
        clients_to_use = self._select_clients(client_preference)
        
        # Perform analysis with multiple clients
        results = {}
        
        try:
            # Run analysis with each client
            for client_name in clients_to_use:
                client = self.clients[client_name]
                
                client_result = await self._analyze_project_with_client(
                    client, project_bounds, project_start_date, analysis_date
                )
                
                results[client_name] = client_result
                
                # If we have good results from primary client, we might skip others
                if client_name == clients_to_use[0] and client_result.get("success", False):
                    break
            
            # Combine and synthesize results
            analysis = await self._synthesize_project_analysis(results, project_bounds)
            
            return {
                "success": True,
                "project_bounds": project_bounds,
                "analysis_period": {
                    "project_start": project_start_date.isoformat(),
                    "analysis_date": analysis_date.isoformat(),
                    "monitoring_duration_days": (analysis_date - project_start_date).days
                },
                "satellite_analysis": analysis,
                "data_sources": list(results.keys()),
                "processing_info": {
                    "processed_at": datetime.now().isoformat(),
                    "clients_used": list(results.keys()),
                    "analysis_quality": self._assess_analysis_quality(results)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in satellite analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "project_bounds": project_bounds,
                "analysis_period": {
                    "project_start": project_start_date.isoformat(),
                    "analysis_date": analysis_date.isoformat()
                }
            }
    
    def _select_clients(self, client_preference: Optional[List[str]] = None) -> List[str]:
        """Select which satellite clients to use for analysis."""
        if client_preference:
            # Use specified preferences, filter for available clients
            available_preferred = [c for c in client_preference if c in self.clients]
            if available_preferred:
                return available_preferred
        
        # Default selection strategy
        if "sentinel2" in self.clients:
            return ["sentinel2", "mock"]  # Prefer Sentinel-2 with mock backup
        elif "landsat" in self.clients:
            return ["landsat", "mock"]    # Prefer Landsat with mock backup
        else:
            return ["mock"]               # Fallback to mock only
    
    async def _analyze_project_with_client(
        self,
        client: SatelliteDataClient,
        bounds: Tuple[float, float, float, float],
        start_date: date,
        analysis_date: date
    ) -> Dict[str, Any]:
        """Perform project analysis with a specific satellite client."""
        try:
            # Get baseline (project start) data
            baseline_period = (start_date, min(start_date + timedelta(days=30), analysis_date))
            
            # Get current data
            current_period = (max(analysis_date - timedelta(days=30), start_date), analysis_date)
            
            # Parallel execution of different analyses
            tasks = [
                client.get_vegetation_index(bounds, baseline_period, "NDVI"),
                client.get_vegetation_index(bounds, current_period, "NDVI"),
                client.detect_land_cover_change(bounds, start_date, analysis_date),
                client.get_imagery_metadata(bounds, start_date, analysis_date)
            ]
            
            baseline_ndvi, current_ndvi, change_detection, imagery_metadata = await asyncio.gather(
                *tasks, return_exceptions=True
            )
            
            # Handle any exceptions
            results = {
                "success": True,
                "client_name": client.name,
                "baseline_vegetation": baseline_ndvi if not isinstance(baseline_ndvi, Exception) else None,
                "current_vegetation": current_ndvi if not isinstance(current_ndvi, Exception) else None,
                "change_analysis": change_detection if not isinstance(change_detection, Exception) else None,
                "imagery_metadata": imagery_metadata if not isinstance(imagery_metadata, Exception) else None,
                "errors": []
            }
            
            # Log any errors but don't fail completely
            for i, (name, result) in enumerate([
                ("baseline_vegetation", baseline_ndvi),
                ("current_vegetation", current_ndvi), 
                ("change_analysis", change_detection),
                ("imagery_metadata", imagery_metadata)
            ]):
                if isinstance(result, Exception):
                    error_msg = f"Error in {name}: {str(result)}"
                    results["errors"].append(error_msg)
                    self.logger.warning(error_msg)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Client analysis failed for {client.name}: {e}")
            return {
                "success": False,
                "client_name": client.name,
                "error": str(e)
            }
    
    async def _synthesize_project_analysis(
        self, 
        client_results: Dict[str, Dict[str, Any]], 
        bounds: Tuple[float, float, float, float]
    ) -> Dict[str, Any]:
        """Synthesize results from multiple satellite clients into unified analysis."""
        
        # Find the best result (successful with most complete data)
        best_result = None
        for client_name, result in client_results.items():
            if result.get("success", False):
                # Count non-null analysis components
                completeness = sum([
                    1 for key in ["baseline_vegetation", "current_vegetation", "change_analysis"]
                    if result.get(key) is not None
                ])
                
                if best_result is None or completeness > best_result[1]:
                    best_result = (result, completeness)
        
        if best_result is None:
            return {"error": "No successful satellite analysis available"}
        
        primary_result = best_result[0]
        
        # Extract key metrics
        analysis = {
            "data_source": primary_result["client_name"],
            "area_analysis": self._extract_area_metrics(primary_result, bounds),
            "vegetation_monitoring": self._extract_vegetation_metrics(primary_result),
            "change_detection": self._extract_change_metrics(primary_result),
            "carbon_impact_assessment": self._assess_carbon_impact(primary_result),
            "monitoring_recommendations": self._generate_monitoring_recommendations(primary_result)
        }
        
        return analysis
    
    def _extract_area_metrics(self, result: Dict[str, Any], bounds: Tuple[float, float, float, float]) -> Dict[str, Any]:
        """Extract area-related metrics from satellite analysis."""
        # Use mock client to calculate area
        mock_client = self.clients["mock"]
        area_hectares = mock_client.calculate_area_hectares(bounds)
        
        area_metrics = {
            "total_area_hectares": area_hectares,
            "bounds": bounds
        }
        
        # Add change detection area metrics if available
        if result.get("change_analysis"):
            change_data = result["change_analysis"]
            if "area_analysis" in change_data:
                area_metrics.update({
                    "changed_area_hectares": change_data["area_analysis"].get("changed_area_hectares", 0),
                    "change_percentage": change_data["area_analysis"].get("change_percentage", 0),
                    "stable_area_hectares": change_data["area_analysis"].get("stable_area_hectares", area_hectares)
                })
        
        return area_metrics
    
    def _extract_vegetation_metrics(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract vegetation monitoring metrics."""
        vegetation_metrics = {
            "monitoring_available": False
        }
        
        baseline = result.get("baseline_vegetation")
        current = result.get("current_vegetation")
        
        if baseline and current:
            vegetation_metrics.update({
                "monitoring_available": True,
                "baseline_ndvi": baseline["statistics"]["mean"],
                "current_ndvi": current["statistics"]["mean"],
                "ndvi_change": current["statistics"]["mean"] - baseline["statistics"]["mean"],
                "vegetation_trend": self._interpret_vegetation_trend(
                    baseline["statistics"]["mean"], 
                    current["statistics"]["mean"]
                ),
                "baseline_health": baseline["interpretation"].get("vegetation_health", "unknown"),
                "current_health": current["interpretation"].get("vegetation_health", "unknown"),
                "confidence": "high" if baseline.get("imagery_used") and current.get("imagery_used") else "medium"
            })
        elif current:
            # Only current data available
            vegetation_metrics.update({
                "monitoring_available": True,
                "current_ndvi": current["statistics"]["mean"],
                "current_health": current["interpretation"].get("vegetation_health", "unknown"),
                "confidence": "medium"
            })
        
        return vegetation_metrics
    
    def _extract_change_metrics(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract land cover change metrics."""
        change_metrics = {
            "change_detection_available": False
        }
        
        change_data = result.get("change_analysis")
        if change_data:
            detection = change_data.get("change_detection", {})
            
            change_metrics.update({
                "change_detection_available": True,
                "primary_change_type": detection.get("primary_change_type", "unknown"),
                "confidence_score": detection.get("confidence_score", 0),
                "change_significance": detection.get("change_significance", "unknown"),
                "environmental_impact": change_data.get("environmental_impact", {}),
                "analysis_quality": change_data.get("processing_info", {}).get("quality_assessment", {})
            })
        
        return change_metrics
    
    def _assess_carbon_impact(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess carbon sequestration impact based on satellite data."""
        carbon_assessment = {
            "assessment_available": False
        }
        
        # From vegetation monitoring
        vegetation = result.get("current_vegetation")
        if vegetation:
            interpretation = vegetation.get("interpretation", {})
            
            carbon_assessment.update({
                "assessment_available": True,
                "estimated_biomass_tons_ha": interpretation.get("estimated_biomass_tons_ha", 0),
                "forest_coverage_percent": interpretation.get("forest_coverage_percent", 0),
                "carbon_sequestration_potential": self._assess_sequestration_potential(
                    interpretation.get("vegetation_health", "unknown"),
                    interpretation.get("estimated_biomass_tons_ha", 0)
                )
            })
        
        # From change detection
        change_data = result.get("change_analysis")
        if change_data and "environmental_impact" in change_data:
            impact = change_data["environmental_impact"]
            carbon_assessment.update({
                "carbon_impact_tons": impact.get("carbon_impact_tons", 0),
                "ecosystem_health_change": impact.get("ecosystem_health_change", 0)
            })
        
        return carbon_assessment
    
    def _assess_sequestration_potential(self, health: str, biomass: float) -> str:
        """Assess carbon sequestration potential based on vegetation health and biomass."""
        if health in ["excellent", "good"] and biomass > 100:
            return "high"
        elif health in ["good", "moderate"] and biomass > 50:
            return "medium"
        elif health != "very_poor" and biomass > 10:
            return "low"
        else:
            return "very_low"
    
    def _interpret_vegetation_trend(self, baseline_ndvi: float, current_ndvi: float) -> str:
        """Interpret vegetation trend from NDVI comparison."""
        change = current_ndvi - baseline_ndvi
        
        if change > 0.1:
            return "significantly_improving"
        elif change > 0.05:
            return "improving"  
        elif change > -0.05:
            return "stable"
        elif change > -0.1:
            return "declining"
        else:
            return "significantly_declining"
    
    def _generate_monitoring_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """Generate monitoring recommendations based on analysis."""
        recommendations = []
        
        # Based on vegetation health
        vegetation = result.get("current_vegetation")
        if vegetation:
            health = vegetation.get("interpretation", {}).get("vegetation_health", "unknown")
            
            if health in ["poor", "very_poor"]:
                recommendations.append("Increase monitoring frequency due to poor vegetation health")
                recommendations.append("Consider intervention measures to improve ecosystem health")
            elif health == "moderate":
                recommendations.append("Regular monthly monitoring recommended")
            else:
                recommendations.append("Continue standard quarterly monitoring")
        
        # Based on change detection
        change_data = result.get("change_analysis")
        if change_data:
            change_type = change_data.get("change_detection", {}).get("primary_change_type", "")
            
            if "deforestation" in change_type or "decline" in change_type:
                recommendations.append("Urgent: Investigate causes of vegetation loss")
                recommendations.append("Implement protective measures immediately")
            elif "disturbance" in change_type:
                recommendations.append("Monitor recovery progress closely")
                recommendations.append("Consider restoration activities if natural recovery is slow")
        
        # Data quality recommendations
        if result.get("errors"):
            recommendations.append("Improve satellite data quality by reducing cloud cover constraints")
        
        # Default recommendation if no specific issues
        if not recommendations:
            recommendations.append("Continue regular satellite monitoring to track project progress")
        
        return recommendations
    
    def _assess_analysis_quality(self, results: Dict[str, Dict[str, Any]]) -> str:
        """Assess overall quality of satellite analysis."""
        successful_analyses = sum(1 for r in results.values() if r.get("success", False))
        total_analyses = len(results)
        
        if successful_analyses == 0:
            return "poor"
        elif successful_analyses / total_analyses >= 0.8:
            return "excellent"
        elif successful_analyses / total_analyses >= 0.6:
            return "good"
        else:
            return "fair"
    
    async def get_satellite_imagery_for_project(
        self,
        project_bounds: Tuple[float, float, float, float],
        start_date: date,
        end_date: date,
        client_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get available satellite imagery metadata for a project area and time range.
        """
        client = self.clients.get(client_name, self.clients[self.default_client])
        
        try:
            imagery = await client.get_imagery_metadata(project_bounds, start_date, end_date)
            
            return {
                "success": True,
                "client_used": client.name,
                "imagery_count": len(imagery),
                "imagery_metadata": imagery,
                "date_range": [start_date.isoformat(), end_date.isoformat()],
                "area_bounds": project_bounds
            }
            
        except Exception as e:
            self.logger.error(f"Error getting imagery metadata: {e}")
            return {
                "success": False,
                "error": str(e),
                "client_used": client.name
            }
    
    async def calculate_vegetation_index_for_project(
        self,
        project_bounds: Tuple[float, float, float, float],
        date_range: Tuple[date, date],
        index_type: str = "NDVI",
        client_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate vegetation index for a specific project area and time range.
        """
        client = self.clients.get(client_name, self.clients[self.default_client])
        
        try:
            vegetation_data = await client.get_vegetation_index(
                project_bounds, date_range, index_type
            )
            
            return {
                "success": True,
                "client_used": client.name,
                "vegetation_index": vegetation_data
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating vegetation index: {e}")
            return {
                "success": False,
                "error": str(e),
                "client_used": client.name
            }


# Global satellite service instance
satellite_service = SatelliteDataService()