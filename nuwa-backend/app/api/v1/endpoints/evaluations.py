"""
Project Evaluations API Endpoints

API endpoints for managing project evaluations and assessment results.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from app.core.database import get_db
from app.schemas.evaluations import (
    EvaluationCreate, EvaluationUpdate, EvaluationResponse,
    EvaluationListResponse, EvaluationSummary, EvaluationAnalysisRequest
)
from app.services.evaluations import EvaluationService
from app.core.logging_config import RequestLogger

router = APIRouter()
logger = logging.getLogger("app.api.evaluations")

@router.post("/", response_model=EvaluationResponse, summary="Create New Evaluation")
async def create_evaluation(
    evaluation_data: EvaluationCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new project evaluation.
    
    This endpoint initiates an evaluation process for a carbon capture project.
    The evaluation can include satellite data analysis, ML predictions, and
    various environmental and carbon metrics.
    """
    with RequestLogger(logger, "create_evaluation", project_id=evaluation_data.project_id):
        try:
            evaluation_service = EvaluationService(db)
            evaluation = await evaluation_service.create_evaluation(evaluation_data)
            
            logger.info(f"Created evaluation {evaluation.id} for project {evaluation.project_id}")
            
            return EvaluationResponse.from_orm(evaluation)
            
        except ValueError as e:
            logger.warning(f"Invalid evaluation data: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to create evaluation: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create evaluation")

@router.get("/", response_model=EvaluationListResponse, summary="List Evaluations")
async def list_evaluations(
    skip: int = Query(0, ge=0, description="Number of evaluations to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of evaluations to return"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    evaluation_type: Optional[str] = Query(None, description="Filter by evaluation type"),
    status: Optional[str] = Query(None, description="Filter by evaluation status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a paginated list of project evaluations.
    
    Supports filtering by project, evaluation type, and status.
    """
    with RequestLogger(logger, "list_evaluations", skip=skip, limit=limit):
        try:
            evaluation_service = EvaluationService(db)
            evaluations, total = await evaluation_service.get_evaluations(
                skip=skip,
                limit=limit,
                project_id=project_id,
                evaluation_type=evaluation_type,
                status=status
            )
            
            evaluation_summaries = [
                EvaluationSummary.from_orm(evaluation) for evaluation in evaluations
            ]
            
            return EvaluationListResponse(
                evaluations=evaluation_summaries,
                total=total,
                skip=skip,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Failed to list evaluations: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve evaluations")

@router.get("/{evaluation_id}", response_model=EvaluationResponse, summary="Get Evaluation Details")
async def get_evaluation(
    evaluation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve detailed information about a specific evaluation.
    """
    with RequestLogger(logger, "get_evaluation", evaluation_id=evaluation_id):
        try:
            evaluation_service = EvaluationService(db)
            evaluation = await evaluation_service.get_evaluation_by_id(evaluation_id)
            
            if not evaluation:
                raise HTTPException(status_code=404, detail="Evaluation not found")
            
            return EvaluationResponse.from_orm(evaluation)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get evaluation {evaluation_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve evaluation")

@router.put("/{evaluation_id}", response_model=EvaluationResponse, summary="Update Evaluation")
async def update_evaluation(
    evaluation_id: int,
    evaluation_data: EvaluationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing evaluation with new results or metadata.
    """
    with RequestLogger(logger, "update_evaluation", evaluation_id=evaluation_id):
        try:
            evaluation_service = EvaluationService(db)
            evaluation = await evaluation_service.update_evaluation(evaluation_id, evaluation_data)
            
            if not evaluation:
                raise HTTPException(status_code=404, detail="Evaluation not found")
            
            logger.info(f"Updated evaluation {evaluation.id}")
            
            return EvaluationResponse.from_orm(evaluation)
            
        except HTTPException:
            raise
        except ValueError as e:
            logger.warning(f"Invalid update data for evaluation {evaluation_id}: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to update evaluation {evaluation_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update evaluation")

@router.delete("/{evaluation_id}", summary="Delete Evaluation")
async def delete_evaluation(
    evaluation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an evaluation and all associated data.
    """
    with RequestLogger(logger, "delete_evaluation", evaluation_id=evaluation_id):
        try:
            evaluation_service = EvaluationService(db)
            success = await evaluation_service.delete_evaluation(evaluation_id)
            
            if not success:
                raise HTTPException(status_code=404, detail="Evaluation not found")
            
            logger.info(f"Deleted evaluation {evaluation_id}")
            
            return {"message": "Evaluation deleted successfully", "evaluation_id": evaluation_id}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete evaluation {evaluation_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete evaluation")

@router.get("/project/{project_id}", response_model=EvaluationListResponse, summary="Get Project Evaluations")
async def get_project_evaluations(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    evaluation_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all evaluations for a specific project.
    """
    with RequestLogger(logger, "get_project_evaluations", project_id=project_id):
        try:
            evaluation_service = EvaluationService(db)
            evaluations, total = await evaluation_service.get_evaluations(
                skip=skip,
                limit=limit,
                project_id=project_id,
                evaluation_type=evaluation_type
            )
            
            evaluation_summaries = [
                EvaluationSummary.from_orm(evaluation) for evaluation in evaluations
            ]
            
            return EvaluationListResponse(
                evaluations=evaluation_summaries,
                total=total,
                skip=skip,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Failed to get project evaluations for {project_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve project evaluations")

@router.post("/analyze", summary="Request Evaluation Analysis")
async def request_evaluation_analysis(
    analysis_request: EvaluationAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Request automated evaluation analysis for a project.
    
    This endpoint triggers satellite data processing, ML model inference,
    and comprehensive carbon capture analysis for the specified project.
    """
    with RequestLogger(logger, "request_evaluation_analysis", 
                      project_id=analysis_request.project_id,
                      evaluation_type=analysis_request.evaluation_type):
        try:
            evaluation_service = EvaluationService(db)
            analysis_result = await evaluation_service.request_analysis(analysis_request)
            
            return {
                "message": "Analysis request submitted successfully",
                "analysis_id": analysis_result.get("analysis_id"),
                "estimated_completion": analysis_result.get("estimated_completion"),
                "status": "processing",
                "project_id": analysis_request.project_id
            }
            
        except ValueError as e:
            logger.warning(f"Invalid analysis request: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to request evaluation analysis: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to request evaluation analysis")

@router.get("/{evaluation_id}/metrics", summary="Get Evaluation Metrics")
async def get_evaluation_metrics(
    evaluation_id: int,
    metric_category: Optional[str] = Query(None, description="Filter by metric category"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed metrics for a specific evaluation.
    """
    with RequestLogger(logger, "get_evaluation_metrics", evaluation_id=evaluation_id):
        try:
            evaluation_service = EvaluationService(db)
            metrics = await evaluation_service.get_evaluation_metrics(
                evaluation_id, metric_category
            )
            
            if metrics is None:
                raise HTTPException(status_code=404, detail="Evaluation not found")
            
            return {
                "evaluation_id": evaluation_id,
                "metrics": metrics,
                "total_metrics": len(metrics)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get evaluation metrics {evaluation_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve evaluation metrics")

@router.post("/{evaluation_id}/verify", summary="Verify Evaluation Results")
async def verify_evaluation(
    evaluation_id: int,
    verification_notes: str = Body(..., description="Verification notes and observations"),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark an evaluation as verified with verification notes.
    """
    with RequestLogger(logger, "verify_evaluation", evaluation_id=evaluation_id):
        try:
            evaluation_service = EvaluationService(db)
            evaluation = await evaluation_service.verify_evaluation(
                evaluation_id, verification_notes
            )
            
            if not evaluation:
                raise HTTPException(status_code=404, detail="Evaluation not found")
            
            logger.info(f"Verified evaluation {evaluation_id}")
            
            return {
                "message": "Evaluation verified successfully",
                "evaluation_id": evaluation_id,
                "verification_date": evaluation.verification_date.isoformat() if evaluation.verification_date else None
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to verify evaluation {evaluation_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to verify evaluation")

@router.get("/{evaluation_id}/summary", summary="Get Evaluation Summary")
async def get_evaluation_summary(
    evaluation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a comprehensive summary of evaluation results and insights.
    """
    with RequestLogger(logger, "get_evaluation_summary", evaluation_id=evaluation_id):
        try:
            evaluation_service = EvaluationService(db)
            summary = await evaluation_service.get_evaluation_summary(evaluation_id)
            
            if not summary:
                raise HTTPException(status_code=404, detail="Evaluation not found")
            
            return summary
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get evaluation summary {evaluation_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve evaluation summary")