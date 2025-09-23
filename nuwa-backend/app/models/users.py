"""
User Database Models

SQLAlchemy models for user management and authentication.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, JSON
from sqlalchemy.sql import func
import enum
from datetime import datetime
from typing import Optional, Dict, Any

from app.core.database import Base

class UserRole(enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    PROJECT_MANAGER = "project_manager"
    EVALUATOR = "evaluator"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    API_USER = "api_user"

class User(Base):
    """
    User Model
    
    Represents users of the Nuwa platform with authentication
    and authorization capabilities.
    """
    __tablename__ = "users"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile information
    full_name = Column(String(200))
    organization = Column(String(200))
    job_title = Column(String(100))
    
    # Contact information
    phone_number = Column(String(50))
    country = Column(String(100))
    timezone = Column(String(100))
    
    # Role and permissions
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # API access
    api_key = Column(String(255), unique=True, index=True)
    api_enabled = Column(Boolean, default=False, nullable=False)
    
    # Activity tracking
    last_login = Column(DateTime)
    login_count = Column(Integer, default=0)
    
    # User preferences
    preferences = Column(JSON, default=dict)
    
    # Account status
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String(255))
    
    # Password reset
    password_reset_token = Column(String(255))
    password_reset_expires = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role={self.role})>"
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN
    
    @property
    def can_create_projects(self) -> bool:
        """Check if user can create projects."""
        return self.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]
    
    @property
    def can_evaluate_projects(self) -> bool:
        """Check if user can evaluate projects."""
        return self.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER, UserRole.EVALUATOR]
    
    @property
    def can_access_api(self) -> bool:
        """Check if user can access API."""
        return self.api_enabled and self.is_active
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Convert user to dictionary representation.
        
        Args:
            include_sensitive: Whether to include sensitive information
        """
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "organization": self.organization,
            "job_title": self.job_title,
            "role": self.role.value if self.role else None,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_sensitive:
            data.update({
                "api_key": self.api_key,
                "api_enabled": self.api_enabled,
                "email_verified": self.email_verified,
                "preferences": self.preferences,
            })
        
        return data