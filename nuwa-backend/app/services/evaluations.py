"""
Evaluation Service Layer

Business logic for project evaluations and assessment operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional, Dict, Any, Tuple
import logging
from datetime import datetime, timedelta

from app.models.evaluations import Evaluation, EvaluationStatus, EvaluationType, EvaluationMetrics
from app.models.projects import Project
from app.schemas.evaluations import EvaluationCreate, EvaluationUpdate, EvaluationAnalysisRequest
from app.core.logging_config import RequestLogger

logger = logging.getLogger("app.services.evaluations")

class EvaluationService:
    """
    Service class for evaluation management operations.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_evaluation(self, evaluation_data: EvaluationCreate) -> Evaluation:
        """
        Create a new project evaluation.
        
        Args:
            evaluation_data: Evaluation creation data
            
        Returns:
            Created evaluation instance
        """
        with RequestLogger(logger, "create_evaluation", project_id=evaluation_data.project_id):
            try:
                # Verify project exists
                project_query = select(Project).where(Project.id == evaluation_data.project_id)
                project_result = await self.db.execute(project_query)
                project = project_result.scalar_one_or_none()
                
                if not project:
                    raise ValueError(f"Project {evaluation_data.project_id} not found")
                
                # Create evaluation instance
                evaluation = Evaluation(
                    project_id=evaluation_data.project_id,
                    evaluation_type=EvaluationType(evaluation_data.evaluation_type.value),
                    status=EvaluationStatus.PENDING,
                    evaluation_date=evaluation_data.evaluation_date,
                    period_start=evaluation_data.period_start,
                    period_end=evaluation_data.period_end,
                    satellite_data_sources=evaluation_data.satellite_data_sources,
                    ground_truth_data=evaluation_data.ground_truth_data,
                    field_measurements=evaluation_data.field_measurements,
                    analysis_method=evaluation_data.analysis_method,
                    model_version=evaluation_data.model_version,
                    notes=evaluation_data.notes if hasattr(evaluation_data, 'notes') else None
                )
                
                # Add to database
                self.db.add(evaluation)
                await self.db.commit()
                await self.db.refresh(evaluation)
                
                logger.info(f"Created evaluation {evaluation.id} for project {evaluation_data.project_id}")
                return evaluation
                
            except Exception as e:
                await self.db.rollback()
                logger.error(f"Failed to create evaluation: {str(e)}")
                raise
    
    async def get_evaluations(
        self,
        skip: int = 0,
        limit: int = 50,
        project_id: Optional[int] = None,
        evaluation_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> Tuple[List[Evaluation], int]:
        """
        Get paginated list of evaluations with optional filtering.
        
        Args:
            skip: Number of evaluations to skip
            limit: Maximum number of evaluations to return
            project_id: Filter by project ID
            evaluation_type: Filter by evaluation type
            status: Filter by evaluation status
            
        Returns:
            Tuple of (evaluations list, total count)
        """
        with RequestLogger(logger, "get_evaluations", skip=skip, limit=limit):
            try:
                # Build query with filters
                query = select(Evaluation)
                count_query = select(func.count(Evaluation.id))
                
                # Apply filters
                filters = []
                if project_id:
                    filters.append(Evaluation.project_id == project_id)
                if evaluation_type:
                    filters.append(Evaluation.evaluation_type == EvaluationType(evaluation_type))
                if status:
                    filters.append(Evaluation.status == EvaluationStatus(status))
                
                if filters:
                    query = query.where(and_(*filters))
                    count_query = count_query.where(and_(*filters))
                
                # Get total count
                total_result = await self.db.execute(count_query)
                total = total_result.scalar()
                
                # Get paginated results
                query = query.offset(skip).limit(limit).order_by(Evaluation.evaluation_date.desc())
                result = await self.db.execute(query)
                evaluations = result.scalars().all()
                
                return evaluations, total
                
            except Exception as e:
                logger.error(f"Failed to get evaluations: {str(e)}")
                raise
    
    async def get_evaluation_by_id(self, evaluation_id: int) -> Optional[Evaluation]:
        """
        Get an evaluation by its ID.
        
        Args:
            evaluation_id: Evaluation ID
            
        Returns:
            Evaluation instance or None if not found
        """
        try:
            query = select(Evaluation).where(Evaluation.id == evaluation_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get evaluation {evaluation_id}: {str(e)}")
            raise
    
    async def update_evaluation(self, evaluation_id: int, evaluation_data: EvaluationUpdate) -> Optional[Evaluation]:
        """
        Update an existing evaluation.
        
        Args:
            evaluation_id: Evaluation ID to update
            evaluation_data: Updated evaluation data
            
        Returns:
            Updated evaluation instance or None if not found
        """
        with RequestLogger(logger, "update_evaluation", evaluation_id=evaluation_id):
            try:
                evaluation = await self.get_evaluation_by_id(evaluation_id)
                if not evaluation:
                    return None
                
                # Update fields that are provided
                update_data = evaluation_data.dict(exclude_unset=True)
                
                for field, value in update_data.items():
                    if field == "status" and value:
                        setattr(evaluation, field, EvaluationStatus(value))
                    elif field == "confidence_level" and value:
                        from app.models.evaluations import ConfidenceLevel
                        setattr(evaluation, field, ConfidenceLevel(value))
                    else:
                        setattr(evaluation, field, value)
                
                await self.db.commit()
                await self.db.refresh(evaluation)
                
                logger.info(f"Updated evaluation {evaluation.id}")
                return evaluation
                
            except Exception as e:
                await self.db.rollback()
                logger.error(f"Failed to update evaluation {evaluation_id}: {str(e)}")
                raise
    
    async def delete_evaluation(self, evaluation_id: int) -> bool:
        """
        Delete an evaluation and all associated data.
        
        Args:
            evaluation_id: Evaluation ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        with RequestLogger(logger, "delete_evaluation", evaluation_id=evaluation_id):
            try:
                evaluation = await self.get_evaluation_by_id(evaluation_id)
                if not evaluation:
                    return False
                
                await self.db.delete(evaluation)
                await self.db.commit()
                
                logger.info(f"Deleted evaluation {evaluation_id}")
                return True
                
            except Exception as e:
                await self.db.rollback()
                logger.error(f"Failed to delete evaluation {evaluation_id}: {str(e)}")
                raise
    
    async def request_analysis(self, analysis_request: EvaluationAnalysisRequest) -> Dict[str, Any]:
        """
        Request automated evaluation analysis.
        
        Args:
            analysis_request: Analysis request parameters
            
        Returns:
            Analysis request results with status and estimated completion
        """
        with RequestLogger(logger, "request_analysis", project_id=analysis_request.project_id):
            try:
                # Create evaluation record for tracking
                evaluation_data = EvaluationCreate(
                    project_id=analysis_request.project_id,
                    evaluation_type=analysis_request.evaluation_type,
                    evaluation_date=datetime.utcnow(),
                    period_start=analysis_request.period_start,
                    period_end=analysis_request.period_end,
                    satellite_data_sources=analysis_request.preferred_satellite_sources,
                    analysis_method="automated_ml_analysis",
                    model_version="v1.0"
                )
                
                evaluation = await self.create_evaluation(evaluation_data)
                
                # Set status to in_progress
                evaluation.status = EvaluationStatus.IN_PROGRESS
                await self.db.commit()
                
                # Simulate analysis scheduling (in real implementation, this would trigger background processing)
                estimated_completion = datetime.utcnow() + timedelta(minutes=30)
                
                return {
                    "analysis_id": evaluation.id,
                    "estimated_completion": estimated_completion.isoformat(),
                    "status": "processing"
                }
                
            except Exception as e:
                logger.error(f"Failed to request analysis: {str(e)}")
                raise
    
    async def get_evaluation_metrics(self, evaluation_id: int, metric_category: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Get detailed metrics for an evaluation.
        
        Args:
            evaluation_id: Evaluation ID
            metric_category: Optional category filter
            
        Returns:
            List of metrics or None if evaluation not found
        """
        try:
            # Check if evaluation exists
            evaluation = await self.get_evaluation_by_id(evaluation_id)
            if not evaluation:
                return None
            
            # Build metrics query
            query = select(EvaluationMetrics).where(EvaluationMetrics.evaluation_id == evaluation_id)
            
            if metric_category:
                query = query.where(EvaluationMetrics.metric_category == metric_category)
            
            result = await self.db.execute(query)
            metrics = result.scalars().all()
            
            # Convert to dict format
            metrics_list = []
            for metric in metrics:
                metric_dict = {
                    "id": metric.id,
                    "metric_name": metric.metric_name,
                    "metric_category": metric.metric_category,
                    "numeric_value": metric.numeric_value,
                    "text_value": metric.text_value,
                    "json_value": metric.json_value,
                    "unit": metric.unit,
                    "confidence_score": metric.confidence_score,
                    "measurement_date": metric.measurement_date.isoformat() if metric.measurement_date else None,
                    "created_at": metric.created_at.isoformat()
                }
                metrics_list.append(metric_dict)
            
            return metrics_list
            
        except Exception as e:
            logger.error(f"Failed to get evaluation metrics {evaluation_id}: {str(e)}")
            raise
    
    async def verify_evaluation(self, evaluation_id: int, verification_notes: str) -> Optional[Evaluation]:
        """
        Mark an evaluation as verified.
        
        Args:
            evaluation_id: Evaluation ID to verify
            verification_notes: Verification notes
            
        Returns:
            Updated evaluation or None if not found
        """
        with RequestLogger(logger, "verify_evaluation", evaluation_id=evaluation_id):
            try:
                evaluation = await self.get_evaluation_by_id(evaluation_id)
                if not evaluation:
                    return None
                
                evaluation.verified = True
                evaluation.verification_date = datetime.utcnow()
                evaluation.verification_notes = verification_notes
                
                await self.db.commit()
                await self.db.refresh(evaluation)
                
                logger.info(f"Verified evaluation {evaluation_id}")
                return evaluation
                
            except Exception as e:
                await self.db.rollback()
                logger.error(f"Failed to verify evaluation {evaluation_id}: {str(e)}")
                raise
    
    async def get_evaluation_summary(self, evaluation_id: int) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive evaluation summary.
        
        Args:
            evaluation_id: Evaluation ID
            
        Returns:
            Evaluation summary or None if not found
        """
        with RequestLogger(logger, "get_evaluation_summary", evaluation_id=evaluation_id):
            try:
                evaluation = await self.get_evaluation_by_id(evaluation_id)
                if not evaluation:
                    return None
                
                # Get metrics count
                metrics_query = select(func.count(EvaluationMetrics.id)).where(
                    EvaluationMetrics.evaluation_id == evaluation_id
                )
                metrics_result = await self.db.execute(metrics_query)
                metrics_count = metrics_result.scalar()
                
                summary = {
                    "evaluation": evaluation.to_dict(),
                    "metrics_summary": {
                        "total_metrics": metrics_count,
                        "co2_efficiency_rating": evaluation.co2_efficiency_rating,
                        "has_high_confidence": evaluation.has_high_confidence,
                        "is_completed": evaluation.is_completed,
                    },
                    "quality_indicators": {
                        "data_quality_score": evaluation.data_quality_score,
                        "cloud_cover_percentage": evaluation.cloud_cover_percentage,
                        "verified": evaluation.verified,
                        "verification_date": evaluation.verification_date.isoformat() if evaluation.verification_date else None
                    }
                }
                
                return summary
                
            except Exception as e:
                logger.error(f"Failed to get evaluation summary {evaluation_id}: {str(e)}")
                raise