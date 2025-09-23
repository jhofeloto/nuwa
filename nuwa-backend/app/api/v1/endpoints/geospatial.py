"""
Geospatial Analysis API Endpoints

API endpoints for geospatial data management and satellite imagery analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from app.core.database import get_db
from app.schemas.geospatial import (
    GeospatialDataCreate, GeospatialDataResponse, SatelliteImageResponse
)
from app.services.geospatial import GeospatialService
from app.core.logging_config import RequestLogger

router = APIRouter()
logger = logging.getLogger("app.api.geospatial")

@router.post("/data", response_model=GeospatialDataResponse, summary="Upload Geospatial Data")
async def upload_geospatial_data(
    data_info: GeospatialDataCreate,
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload geospatial data for a project.
    
    This endpoint accepts various types of geospatial data including:
    - Satellite imagery (GeoTIFF, NetCDF)
    - Vector data (Shapefile, GeoJSON)
    - Point cloud data
    - Analysis results
    """
    with RequestLogger(logger, "upload_geospatial_data", 
                      project_id=data_info.project_id,
                      data_type=data_info.data_type):
        try:
            geospatial_service = GeospatialService(db)
            geospatial_data = await geospatial_service.upload_data(data_info, file)
            
            logger.info(f"Uploaded geospatial data {geospatial_data.id} for project {data_info.project_id}")
            
            return GeospatialDataResponse.from_orm(geospatial_data)
            
        except ValueError as e:
            logger.warning(f"Invalid geospatial data: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to upload geospatial data: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to upload geospatial data")

@router.get("/data/project/{project_id}", response_model=List[GeospatialDataResponse], 
           summary="Get Project Geospatial Data")
async def get_project_geospatial_data(
    project_id: int,
    data_type: Optional[str] = Query(None, description="Filter by data type"),
    source: Optional[str] = Query(None, description="Filter by data source"),
    processed_only: bool = Query(False, description="Show only processed data"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all geospatial data associated with a project.
    """
    with RequestLogger(logger, "get_project_geospatial_data", project_id=project_id):
        try:
            geospatial_service = GeospatialService(db)
            data_list = await geospatial_service.get_project_data(
                project_id=project_id,
                data_type=data_type,
                source=source,
                processed_only=processed_only
            )
            
            return [GeospatialDataResponse.from_orm(data) for data in data_list]
            
        except Exception as e:
            logger.error(f"Failed to get project geospatial data for {project_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve geospatial data")

@router.get("/data/{data_id}", response_model=GeospatialDataResponse, summary="Get Geospatial Data Details")
async def get_geospatial_data(
    data_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about specific geospatial data.
    """
    with RequestLogger(logger, "get_geospatial_data", data_id=data_id):
        try:
            geospatial_service = GeospatialService(db)
            data = await geospatial_service.get_data_by_id(data_id)
            
            if not data:
                raise HTTPException(status_code=404, detail="Geospatial data not found")
            
            return GeospatialDataResponse.from_orm(data)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get geospatial data {data_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve geospatial data")

@router.post("/analyze/vegetation", summary="Analyze Vegetation from Satellite Data")
async def analyze_vegetation(
    project_id: int,
    data_sources: List[str] = Query(..., description="Satellite data sources to analyze"),
    start_date: Optional[datetime] = Query(None, description="Analysis start date"),
    end_date: Optional[datetime] = Query(None, description="Analysis end date"),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform vegetation analysis using available satellite data.
    
    This endpoint analyzes vegetation indices (NDVI, EVI, etc.) and
    calculates biomass estimates, vegetation cover, and change detection.
    """
    with RequestLogger(logger, "analyze_vegetation", project_id=project_id):
        try:
            geospatial_service = GeospatialService(db)
            analysis_result = await geospatial_service.analyze_vegetation(
                project_id=project_id,
                data_sources=data_sources,
                start_date=start_date,
                end_date=end_date
            )
            
            return {
                "message": "Vegetation analysis completed",
                "project_id": project_id,
                "analysis_date": datetime.utcnow().isoformat(),
                "results": analysis_result
            }
            
        except ValueError as e:
            logger.warning(f"Invalid vegetation analysis request: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to analyze vegetation for project {project_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to analyze vegetation")

@router.post("/analyze/change-detection", summary="Perform Change Detection Analysis")
async def change_detection_analysis(
    project_id: int,
    baseline_date: datetime = Query(..., description="Baseline date for comparison"),
    comparison_date: datetime = Query(..., description="Comparison date"),
    change_threshold: float = Query(0.1, ge=0, le=1, description="Change detection threshold"),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform change detection analysis between two time periods.
    
    Detects changes in land cover, vegetation, and potential deforestation
    events by comparing satellite imagery from different dates.
    """
    with RequestLogger(logger, "change_detection_analysis", project_id=project_id):
        try:
            geospatial_service = GeospatialService(db)
            change_result = await geospatial_service.detect_changes(
                project_id=project_id,
                baseline_date=baseline_date,
                comparison_date=comparison_date,
                threshold=change_threshold
            )
            
            return {
                "message": "Change detection analysis completed",
                "project_id": project_id,
                "baseline_date": baseline_date.isoformat(),
                "comparison_date": comparison_date.isoformat(),
                "changes_detected": change_result.get("changes_detected", False),
                "change_areas": change_result.get("change_areas", []),
                "total_changed_area_hectares": change_result.get("total_changed_area", 0),
                "change_statistics": change_result.get("statistics", {})
            }
            
        except ValueError as e:
            logger.warning(f"Invalid change detection request: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Failed change detection for project {project_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to perform change detection")

@router.get("/satellite-data/available", summary="Get Available Satellite Data")
async def get_available_satellite_data(
    project_id: int,
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    satellite: Optional[str] = Query(None, description="Satellite filter (sentinel-2, landsat-8, etc.)"),
    max_cloud_cover: float = Query(50, ge=0, le=100, description="Maximum cloud cover percentage"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get available satellite data for a project area and time period.
    """
    with RequestLogger(logger, "get_available_satellite_data", project_id=project_id):
        try:
            geospatial_service = GeospatialService(db)
            available_data = await geospatial_service.get_available_satellite_data(
                project_id=project_id,
                start_date=start_date,
                end_date=end_date,
                satellite=satellite,
                max_cloud_cover=max_cloud_cover
            )
            
            return {
                "project_id": project_id,
                "available_scenes": available_data.get("scenes", []),
                "total_scenes": len(available_data.get("scenes", [])),
                "date_range": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                },
                "satellites": available_data.get("satellites", []),
                "coverage_statistics": available_data.get("coverage_stats", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to get available satellite data for project {project_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve satellite data availability")

@router.post("/download/satellite-data", summary="Download Satellite Data")
async def download_satellite_data(
    project_id: int,
    scenes: List[str] = Query(..., description="Scene IDs to download"),
    processing_level: str = Query("L2A", description="Processing level (L1C, L2A, etc.)"),
    bands: Optional[List[str]] = Query(None, description="Specific bands to download"),
    db: AsyncSession = Depends(get_db)
):
    """
    Request download of satellite data for a project.
    
    This endpoint initiates the download process for specified satellite scenes.
    The actual download happens asynchronously in the background.
    """
    with RequestLogger(logger, "download_satellite_data", project_id=project_id):
        try:
            geospatial_service = GeospatialService(db)
            download_result = await geospatial_service.request_satellite_download(
                project_id=project_id,
                scenes=scenes,
                processing_level=processing_level,
                bands=bands
            )
            
            return {
                "message": "Satellite data download requested",
                "project_id": project_id,
                "download_id": download_result.get("download_id"),
                "requested_scenes": scenes,
                "estimated_completion": download_result.get("estimated_completion"),
                "status": "queued"
            }
            
        except ValueError as e:
            logger.warning(f"Invalid download request: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to request satellite data download: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to request satellite data download")

@router.get("/analysis/area-statistics", summary="Get Area Statistics")
async def get_area_statistics(
    project_id: int,
    analysis_date: Optional[datetime] = Query(None, description="Specific analysis date"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive area statistics for a project including:
    - Total project area
    - Vegetation coverage
    - Land use distribution
    - Change statistics over time
    """
    with RequestLogger(logger, "get_area_statistics", project_id=project_id):
        try:
            geospatial_service = GeospatialService(db)
            statistics = await geospatial_service.get_area_statistics(
                project_id=project_id,
                analysis_date=analysis_date
            )
            
            return {
                "project_id": project_id,
                "analysis_date": analysis_date.isoformat() if analysis_date else None,
                "area_statistics": statistics.get("area_stats", {}),
                "vegetation_statistics": statistics.get("vegetation_stats", {}),
                "land_use_distribution": statistics.get("land_use", {}),
                "temporal_trends": statistics.get("trends", {}),
                "quality_metrics": statistics.get("quality", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to get area statistics for project {project_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve area statistics")

@router.post("/process/spectral-indices", summary="Calculate Spectral Indices")
async def calculate_spectral_indices(
    data_id: int,
    indices: List[str] = Query(..., description="Spectral indices to calculate (NDVI, EVI, SAVI, etc.)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate spectral indices from satellite imagery.
    
    Supported indices:
    - NDVI: Normalized Difference Vegetation Index
    - EVI: Enhanced Vegetation Index
    - SAVI: Soil-Adjusted Vegetation Index
    - NDWI: Normalized Difference Water Index
    - NBR: Normalized Burn Ratio
    """
    with RequestLogger(logger, "calculate_spectral_indices", data_id=data_id):
        try:
            geospatial_service = GeospatialService(db)
            calculation_result = await geospatial_service.calculate_spectral_indices(
                data_id=data_id,
                indices=indices
            )
            
            return {
                "message": "Spectral indices calculated successfully",
                "data_id": data_id,
                "calculated_indices": calculation_result.get("indices", {}),
                "statistics": calculation_result.get("statistics", {}),
                "processing_time_seconds": calculation_result.get("processing_time", 0)
            }
            
        except ValueError as e:
            logger.warning(f"Invalid spectral index calculation request: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to calculate spectral indices for data {data_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to calculate spectral indices")

@router.delete("/data/{data_id}", summary="Delete Geospatial Data")
async def delete_geospatial_data(
    data_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete geospatial data and associated files.
    """
    with RequestLogger(logger, "delete_geospatial_data", data_id=data_id):
        try:
            geospatial_service = GeospatialService(db)
            success = await geospatial_service.delete_data(data_id)
            
            if not success:
                raise HTTPException(status_code=404, detail="Geospatial data not found")
            
            logger.info(f"Deleted geospatial data {data_id}")
            
            return {"message": "Geospatial data deleted successfully", "data_id": data_id}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete geospatial data {data_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete geospatial data")