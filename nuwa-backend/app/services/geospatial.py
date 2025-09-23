"""
Geospatial Service Layer

Business logic for geospatial data management and satellite imagery analysis.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional, Dict, Any, Tuple
import logging
from datetime import datetime, timedelta
from fastapi import UploadFile

from app.models.geospatial import GeospatialData, SatelliteImage, DataSource, ProcessingStatus
from app.models.projects import Project
from app.schemas.geospatial import GeospatialDataCreate
from app.core.logging_config import RequestLogger

logger = logging.getLogger("app.services.geospatial")

class GeospatialService:
    """
    Service class for geospatial data management operations.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def upload_data(self, data_info: GeospatialDataCreate, file: Optional[UploadFile] = None) -> GeospatialData:
        """
        Upload geospatial data for a project.
        
        Args:
            data_info: Geospatial data information
            file: Optional uploaded file
            
        Returns:
            Created geospatial data instance
        """
        with RequestLogger(logger, "upload_data", project_id=data_info.project_id):
            try:
                # Verify project exists
                project_query = select(Project).where(Project.id == data_info.project_id)
                project_result = await self.db.execute(project_query)
                project = project_result.scalar_one_or_none()
                
                if not project:
                    raise ValueError(f"Project {data_info.project_id} not found")
                
                # Handle file upload if provided
                file_path = None
                file_size = None
                file_format = None
                
                if file:
                    # In a real implementation, this would save the file to storage
                    file_path = f"uploads/{data_info.project_id}/{file.filename}"
                    file_size = file.size
                    file_format = file.filename.split('.')[-1] if '.' in file.filename else None
                    
                    # TODO: Implement actual file storage logic
                    logger.info(f"Would save file {file.filename} to {file_path}")
                
                # Create geospatial data instance
                geospatial_data = GeospatialData(
                    project_id=data_info.project_id,
                    name=data_info.name,
                    description=data_info.description,
                    data_type=data_info.data_type,
                    source=DataSource(data_info.source.value),
                    source_id=data_info.source_id,
                    acquisition_date=data_info.acquisition_date,
                    spatial_resolution_meters=data_info.spatial_resolution_meters,
                    coordinate_system=data_info.coordinate_system or "EPSG:4326",
                    file_path=file_path,
                    file_size_bytes=file_size,
                    file_format=file_format,
                    processing_status=ProcessingStatus.RAW,
                    cloud_cover_percentage=data_info.cloud_cover_percentage,
                    quality_score=data_info.quality_score,
                    spectral_bands=data_info.spectral_bands or [],
                    storage_location=file_path,
                    metadata=data_info.metadata or {}
                )
                
                # Add to database
                self.db.add(geospatial_data)
                await self.db.commit()
                await self.db.refresh(geospatial_data)
                
                logger.info(f"Uploaded geospatial data {geospatial_data.id} for project {data_info.project_id}")
                return geospatial_data
                
            except Exception as e:
                await self.db.rollback()
                logger.error(f"Failed to upload geospatial data: {str(e)}")
                raise
    
    async def get_project_data(
        self,
        project_id: int,
        data_type: Optional[str] = None,
        source: Optional[str] = None,
        processed_only: bool = False
    ) -> List[GeospatialData]:
        """
        Get geospatial data for a project.
        
        Args:
            project_id: Project ID
            data_type: Filter by data type
            source: Filter by data source
            processed_only: Show only processed data
            
        Returns:
            List of geospatial data
        """
        with RequestLogger(logger, "get_project_data", project_id=project_id):
            try:
                # Build query with filters
                query = select(GeospatialData).where(GeospatialData.project_id == project_id)
                
                if data_type:
                    query = query.where(GeospatialData.data_type == data_type)
                
                if source:
                    query = query.where(GeospatialData.source == DataSource(source))
                
                if processed_only:
                    query = query.where(
                        GeospatialData.processing_status.in_([
                            ProcessingStatus.PROCESSED, 
                            ProcessingStatus.ANALYZED
                        ])
                    )
                
                # Order by acquisition date
                query = query.order_by(GeospatialData.acquisition_date.desc())
                
                result = await self.db.execute(query)
                data_list = result.scalars().all()
                
                return data_list
                
            except Exception as e:
                logger.error(f"Failed to get project data for {project_id}: {str(e)}")
                raise
    
    async def get_data_by_id(self, data_id: int) -> Optional[GeospatialData]:
        """
        Get geospatial data by ID.
        
        Args:
            data_id: Data ID
            
        Returns:
            Geospatial data instance or None if not found
        """
        try:
            query = select(GeospatialData).where(GeospatialData.id == data_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get geospatial data {data_id}: {str(e)}")
            raise
    
    async def analyze_vegetation(
        self,
        project_id: int,
        data_sources: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Analyze vegetation using available satellite data.
        
        Args:
            project_id: Project ID to analyze
            data_sources: Satellite data sources to use
            start_date: Analysis start date
            end_date: Analysis end date
            
        Returns:
            Vegetation analysis results
        """
        with RequestLogger(logger, "analyze_vegetation", project_id=project_id):
            try:
                # Get available satellite data for the project
                query = select(GeospatialData).where(
                    and_(
                        GeospatialData.project_id == project_id,
                        GeospatialData.source.in_([DataSource(src) for src in data_sources])
                    )
                )
                
                if start_date:
                    query = query.where(GeospatialData.acquisition_date >= start_date)
                if end_date:
                    query = query.where(GeospatialData.acquisition_date <= end_date)
                
                result = await self.db.execute(query)
                satellite_data = result.scalars().all()
                
                if not satellite_data:
                    raise ValueError("No suitable satellite data found for analysis")
                
                # Simulate vegetation analysis (in real implementation, this would process actual imagery)
                analysis_result = {
                    "project_id": project_id,
                    "data_sources_used": data_sources,
                    "scenes_analyzed": len(satellite_data),
                    "vegetation_indices": {
                        "average_ndvi": 0.65,  # Simulated values
                        "ndvi_change": 0.02,
                        "evi": 0.58,
                        "savi": 0.61
                    },
                    "vegetation_metrics": {
                        "vegetation_cover_percentage": 75.3,
                        "biomass_estimate_tons_per_hectare": 45.2,
                        "leaf_area_index": 3.8
                    },
                    "temporal_analysis": {
                        "trend": "increasing",
                        "seasonal_variation": 0.15,
                        "anomalies_detected": []
                    },
                    "quality_metrics": {
                        "average_cloud_cover": 12.5,
                        "data_quality_score": 0.89
                    }
                }
                
                logger.info(f"Completed vegetation analysis for project {project_id}")
                return analysis_result
                
            except Exception as e:
                logger.error(f"Failed vegetation analysis for project {project_id}: {str(e)}")
                raise
    
    async def detect_changes(
        self,
        project_id: int,
        baseline_date: datetime,
        comparison_date: datetime,
        threshold: float = 0.1
    ) -> Dict[str, Any]:
        """
        Perform change detection analysis.
        
        Args:
            project_id: Project ID
            baseline_date: Baseline date for comparison
            comparison_date: Comparison date
            threshold: Change detection threshold
            
        Returns:
            Change detection results
        """
        with RequestLogger(logger, "detect_changes", project_id=project_id):
            try:
                # Find satellite data near the specified dates
                baseline_query = select(GeospatialData).where(
                    and_(
                        GeospatialData.project_id == project_id,
                        GeospatialData.acquisition_date >= baseline_date - timedelta(days=7),
                        GeospatialData.acquisition_date <= baseline_date + timedelta(days=7)
                    )
                ).order_by(func.abs(GeospatialData.acquisition_date - baseline_date)).limit(1)
                
                comparison_query = select(GeospatialData).where(
                    and_(
                        GeospatialData.project_id == project_id,
                        GeospatialData.acquisition_date >= comparison_date - timedelta(days=7),
                        GeospatialData.acquisition_date <= comparison_date + timedelta(days=7)
                    )
                ).order_by(func.abs(GeospatialData.acquisition_date - comparison_date)).limit(1)
                
                baseline_result = await self.db.execute(baseline_query)
                baseline_data = baseline_result.scalar_one_or_none()
                
                comparison_result = await self.db.execute(comparison_query)
                comparison_data = comparison_result.scalar_one_or_none()
                
                if not baseline_data or not comparison_data:
                    raise ValueError("Insufficient satellite data for change detection")
                
                # Simulate change detection analysis
                changes_detected = True  # Simulated result
                
                change_result = {
                    "changes_detected": changes_detected,
                    "change_areas": [
                        {
                            "area_id": 1,
                            "change_type": "deforestation",
                            "area_hectares": 2.3,
                            "confidence": 0.87,
                            "location": {"latitude": -10.5, "longitude": -55.2}
                        }
                    ] if changes_detected else [],
                    "total_changed_area": 2.3 if changes_detected else 0,
                    "statistics": {
                        "baseline_date": baseline_data.acquisition_date.isoformat(),
                        "comparison_date": comparison_data.acquisition_date.isoformat(),
                        "threshold_used": threshold,
                        "detection_confidence": 0.87,
                        "change_magnitude": 0.23
                    }
                }
                
                logger.info(f"Completed change detection for project {project_id}")
                return change_result
                
            except Exception as e:
                logger.error(f"Failed change detection for project {project_id}: {str(e)}")
                raise
    
    async def get_available_satellite_data(
        self,
        project_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        satellite: Optional[str] = None,
        max_cloud_cover: float = 50
    ) -> Dict[str, Any]:
        """
        Get available satellite data for a project.
        
        Args:
            project_id: Project ID
            start_date: Start date filter
            end_date: End date filter
            satellite: Satellite filter
            max_cloud_cover: Maximum cloud cover
            
        Returns:
            Available satellite data information
        """
        try:
            # Build query
            query = select(GeospatialData).where(GeospatialData.project_id == project_id)
            
            if start_date:
                query = query.where(GeospatialData.acquisition_date >= start_date)
            if end_date:
                query = query.where(GeospatialData.acquisition_date <= end_date)
            if satellite:
                query = query.where(GeospatialData.source == DataSource(satellite))
            if max_cloud_cover < 100:
                query = query.where(GeospatialData.cloud_cover_percentage <= max_cloud_cover)
            
            result = await self.db.execute(query)
            available_data = result.scalars().all()
            
            # Process results
            scenes = []
            satellites = set()
            
            for data in available_data:
                scenes.append({
                    "id": data.id,
                    "source": data.source.value,
                    "acquisition_date": data.acquisition_date.isoformat() if data.acquisition_date else None,
                    "cloud_cover": data.cloud_cover_percentage,
                    "quality_score": data.quality_score,
                    "processing_status": data.processing_status.value
                })
                satellites.add(data.source.value)
            
            return {
                "scenes": scenes,
                "satellites": list(satellites),
                "coverage_stats": {
                    "total_scenes": len(scenes),
                    "date_range_days": (end_date - start_date).days if start_date and end_date else None,
                    "average_cloud_cover": sum(s["cloud_cover"] or 0 for s in scenes) / len(scenes) if scenes else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get available satellite data for project {project_id}: {str(e)}")
            raise
    
    async def request_satellite_download(
        self,
        project_id: int,
        scenes: List[str],
        processing_level: str = "L2A",
        bands: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Request satellite data download.
        
        Args:
            project_id: Project ID
            scenes: Scene IDs to download
            processing_level: Processing level
            bands: Specific bands to download
            
        Returns:
            Download request results
        """
        with RequestLogger(logger, "request_satellite_download", project_id=project_id):
            try:
                # In a real implementation, this would interface with satellite data APIs
                download_id = f"dl_{project_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                estimated_completion = datetime.utcnow() + timedelta(hours=2)
                
                logger.info(f"Requested satellite download for project {project_id}: {len(scenes)} scenes")
                
                return {
                    "download_id": download_id,
                    "estimated_completion": estimated_completion.isoformat(),
                    "scenes_requested": len(scenes),
                    "processing_level": processing_level,
                    "bands": bands or ["all"]
                }
                
            except Exception as e:
                logger.error(f"Failed to request satellite download: {str(e)}")
                raise
    
    async def get_area_statistics(
        self,
        project_id: int,
        analysis_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive area statistics for a project.
        
        Args:
            project_id: Project ID
            analysis_date: Specific analysis date
            
        Returns:
            Area statistics
        """
        try:
            # Get project information
            project_query = select(Project).where(Project.id == project_id)
            project_result = await self.db.execute(project_query)
            project = project_result.scalar_one_or_none()
            
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            # Simulate comprehensive statistics
            statistics = {
                "area_stats": {
                    "total_project_area_hectares": project.project_area_hectares or 0,
                    "monitored_area_hectares": (project.project_area_hectares or 0) * 0.95,  # 95% coverage
                    "area_sq_km": project.area_sqkm or 0
                },
                "vegetation_stats": {
                    "forest_cover_percentage": 68.5,
                    "grassland_percentage": 22.3,
                    "agricultural_percentage": 7.2,
                    "water_bodies_percentage": 2.0,
                    "average_ndvi": 0.65,
                    "vegetation_trend": "stable"
                },
                "land_use": {
                    "primary_forest": 45.2,
                    "secondary_forest": 23.3,
                    "grassland": 22.3,
                    "agriculture": 7.2,
                    "water": 2.0
                },
                "trends": {
                    "deforestation_rate_per_year": 0.2,  # percentage
                    "reforestation_rate_per_year": 1.8,
                    "net_forest_change": 1.6,
                    "carbon_sequestration_trend": "increasing"
                },
                "quality": {
                    "data_coverage": 0.95,
                    "temporal_coverage": 0.88,
                    "average_cloud_cover": 15.2,
                    "last_analysis_date": analysis_date.isoformat() if analysis_date else datetime.utcnow().isoformat()
                }
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to get area statistics for project {project_id}: {str(e)}")
            raise
    
    async def calculate_spectral_indices(self, data_id: int, indices: List[str]) -> Dict[str, Any]:
        """
        Calculate spectral indices from satellite imagery.
        
        Args:
            data_id: Geospatial data ID
            indices: List of indices to calculate
            
        Returns:
            Calculated indices results
        """
        with RequestLogger(logger, "calculate_spectral_indices", data_id=data_id):
            try:
                # Get geospatial data
                data = await self.get_data_by_id(data_id)
                if not data:
                    raise ValueError(f"Geospatial data {data_id} not found")
                
                # Simulate spectral index calculation
                calculated_indices = {}
                
                for index in indices:
                    if index.upper() == "NDVI":
                        calculated_indices["ndvi"] = 0.65
                    elif index.upper() == "EVI":
                        calculated_indices["evi"] = 0.58
                    elif index.upper() == "SAVI":
                        calculated_indices["savi"] = 0.61
                    elif index.upper() == "NDWI":
                        calculated_indices["ndwi"] = 0.25
                    elif index.upper() == "NBR":
                        calculated_indices["nbr"] = 0.45
                
                # Update processing status
                data.processing_status = ProcessingStatus.PROCESSED
                data.processing_date = datetime.utcnow()
                await self.db.commit()
                
                result = {
                    "indices": calculated_indices,
                    "statistics": {
                        "min_values": {k: v - 0.1 for k, v in calculated_indices.items()},
                        "max_values": {k: v + 0.1 for k, v in calculated_indices.items()},
                        "std_dev": {k: 0.05 for k in calculated_indices.keys()}
                    },
                    "processing_time": 15.3  # Simulated processing time in seconds
                }
                
                logger.info(f"Calculated spectral indices for data {data_id}")
                return result
                
            except Exception as e:
                logger.error(f"Failed to calculate spectral indices for data {data_id}: {str(e)}")
                raise
    
    async def delete_data(self, data_id: int) -> bool:
        """
        Delete geospatial data and associated files.
        
        Args:
            data_id: Data ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        with RequestLogger(logger, "delete_data", data_id=data_id):
            try:
                data = await self.get_data_by_id(data_id)
                if not data:
                    return False
                
                # In a real implementation, this would also delete physical files
                if data.file_path:
                    logger.info(f"Would delete file: {data.file_path}")
                
                await self.db.delete(data)
                await self.db.commit()
                
                logger.info(f"Deleted geospatial data {data_id}")
                return True
                
            except Exception as e:
                await self.db.rollback()
                logger.error(f"Failed to delete geospatial data {data_id}: {str(e)}")
                raise