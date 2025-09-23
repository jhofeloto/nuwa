"""
PostgreSQL Models Module

Imports all PostgreSQL-compatible models with PostGIS support.
"""

from app.models.projects import Project, ProjectStatus, ProjectType
from app.models.evaluations import Evaluation, EvaluationStatus
from app.models.geospatial import GeospatialData, SatelliteImage, DataSource, ProcessingStatus
from app.models.users import User

__all__ = [
    "Project",
    "ProjectStatus", 
    "ProjectType",
    "Evaluation",
    "EvaluationStatus",
    "GeospatialData",
    "SatelliteImage",
    "DataSource",
    "ProcessingStatus",
    "User"
]