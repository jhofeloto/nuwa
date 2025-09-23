"""
User Authentication and Authorization Models for Nuwa Carbon Platform
Includes comprehensive role-based access control with PostgreSQL + PostGIS integration
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
import enum
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from app.core.database import Base

class UserRole(str, enum.Enum):
    """User roles with hierarchical permissions"""
    SUPER_ADMIN = "super_admin"        # Full system access
    ADMIN = "admin"                    # Organization management
    PROJECT_MANAGER = "project_manager"  # Project CRUD operations
    ANALYST = "analyst"                # Read/analysis operations
    VIEWER = "viewer"                  # Read-only access
    AUDITOR = "auditor"                # Audit and verification access
    EXTERNAL = "external"              # Limited external partner access

class UserStatus(str, enum.Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive" 
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    PENDING_APPROVAL = "pending_approval"
    ARCHIVED = "archived"

class Permission(str, enum.Enum):
    """Granular permissions for resources"""
    # Project permissions
    PROJECT_CREATE = "project:create"
    PROJECT_READ = "project:read"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"
    PROJECT_APPROVE = "project:approve"
    
    # Evaluation permissions
    EVALUATION_CREATE = "evaluation:create"
    EVALUATION_READ = "evaluation:read"
    EVALUATION_UPDATE = "evaluation:update"
    EVALUATION_DELETE = "evaluation:delete"
    EVALUATION_VERIFY = "evaluation:verify"
    
    # Satellite data permissions
    SATELLITE_READ = "satellite:read"
    SATELLITE_ANALYZE = "satellite:analyze"
    SATELLITE_MANAGE = "satellite:manage"
    
    # ML model permissions
    ML_PREDICT = "ml:predict"
    ML_TRAIN = "ml:train"
    ML_MANAGE = "ml:manage"
    
    # User management permissions
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_MANAGE_ROLES = "user:manage_roles"
    
    # System permissions
    SYSTEM_CONFIG = "system:config"
    SYSTEM_MONITOR = "system:monitor"
    SYSTEM_AUDIT = "system:audit"
    
    # Geospatial permissions
    GIS_READ = "gis:read"
    GIS_ANALYZE = "gis:analyze"
    GIS_MANAGE = "gis:manage"

class Organization(Base):
    """Organization model for multi-tenant support"""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    
    # Contact information
    email = Column(String(255))
    phone = Column(String(50))
    website = Column(String(255))
    
    # Address and location
    address = Column(Text)
    city = Column(String(100))
    country = Column(String(100))
    location = Column(Geometry('POINT', srid=4326))  # PostGIS point for organization location
    
    # Organization metadata
    industry = Column(String(100))
    organization_type = Column(String(50))  # NGO, Corporation, Government, etc.
    size = Column(String(20))  # Small, Medium, Large, Enterprise
    
    # Settings and configuration
    settings = Column(JSON, default=dict)
    api_limits = Column(JSON, default=dict)
    
    # Status and lifecycle
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")

class User(Base):
    """Enhanced user model with comprehensive authentication features"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic user information
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    full_name = Column(String(200))  # Computed or provided full name
    
    # Authentication
    hashed_password = Column(String(255))
    is_email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(255))
    email_verification_expires = Column(DateTime(timezone=True))
    
    # Password reset
    password_reset_token = Column(String(255))
    password_reset_expires = Column(DateTime(timezone=True))
    
    # Account management
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER, nullable=False, index=True)
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING_VERIFICATION, nullable=False, index=True)
    
    # Organization relationship
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    organization = relationship("Organization", back_populates="users")
    
    # Profile information
    avatar_url = Column(String(500))
    bio = Column(Text)
    title = Column(String(200))  # Job title
    department = Column(String(100))
    phone = Column(String(50))
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="en")
    
    # Location (optional)
    location = Column(Geometry('POINT', srid=4326))  # PostGIS point for user location
    address = Column(Text)
    city = Column(String(100))
    country = Column(String(100))
    
    # Preferences and settings
    preferences = Column(JSON, default=dict)
    notification_settings = Column(JSON, default=dict)
    
    # Security and access
    last_login = Column(DateTime(timezone=True))
    last_login_ip = Column(String(45))  # Support IPv6
    login_count = Column(Integer, default=0)
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime(timezone=True))
    
    # Two-factor authentication
    is_2fa_enabled = Column(Boolean, default=False)
    totp_secret = Column(String(255))  # Encrypted TOTP secret
    backup_codes = Column(JSON)  # Encrypted backup codes
    
    # API access
    api_key = Column(String(255))  # For API access
    api_key_expires = Column(DateTime(timezone=True))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    last_activity = Column(DateTime(timezone=True))
    
    # Relationships
    user_permissions = relationship("UserPermission", back_populates="user", cascade="all, delete-orphan", foreign_keys="UserPermission.user_id")
    user_sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    @property
    def display_name(self) -> str:
        """Get display name for user"""
        if self.full_name:
            return self.full_name
        elif self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.username:
            return self.username
        return self.email
    
    @property
    def is_active(self) -> bool:
        """Check if user account is active"""
        return self.status == UserStatus.ACTIVE
    
    @property
    def is_locked(self) -> bool:
        """Check if user account is locked"""
        return (
            self.account_locked_until is not None 
            and self.account_locked_until > datetime.now(timezone.utc)
        )

class UserPermission(Base):
    """User-specific permissions (in addition to role-based permissions)"""
    __tablename__ = "user_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    permission = Column(SQLEnum(Permission), nullable=False, index=True)
    
    # Permission scope (e.g., specific project, organization)
    resource_type = Column(String(50))  # "project", "organization", "global"
    resource_id = Column(Integer)  # ID of specific resource
    
    # Permission metadata
    granted_by = Column(Integer, ForeignKey("users.id"))
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True))  # Optional expiration
    
    # Relationships
    user = relationship("User", back_populates="user_permissions", foreign_keys=[user_id])
    granted_by_user = relationship("User", foreign_keys=[granted_by])

class UserSession(Base):
    """Track user sessions for security and analytics"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Session information
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=True)
    
    # Session metadata
    ip_address = Column(String(45))
    user_agent = Column(Text)
    device_info = Column(JSON)
    location = Column(Geometry('POINT', srid=4326))  # Session location
    
    # Session lifecycle
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    ended_at = Column(DateTime(timezone=True))
    
    # Security flags
    is_suspicious = Column(Boolean, default=False)
    risk_score = Column(Integer, default=0)  # 0-100 security risk score
    
    # Relationships
    user = relationship("User", back_populates="user_sessions")

class AuditLog(Base):
    """Comprehensive audit logging for security and compliance"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Event information
    event_type = Column(String(100), nullable=False, index=True)  # login, logout, create_project, etc.
    action = Column(String(50), nullable=False)  # CREATE, READ, UPDATE, DELETE, LOGIN, etc.
    resource_type = Column(String(50))  # user, project, evaluation, etc.
    resource_id = Column(Integer)
    
    # User and session context
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(Integer, ForeignKey("user_sessions.id"), nullable=True)
    
    # Request context
    ip_address = Column(String(45))
    user_agent = Column(Text)
    endpoint = Column(String(255))  # API endpoint
    http_method = Column(String(10))  # GET, POST, etc.
    
    # Event details
    old_values = Column(JSON)  # Previous values for updates
    new_values = Column(JSON)  # New values for updates
    event_metadata = Column(JSON)  # Additional context
    
    # Success/failure
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")

# Role-based permission mappings
ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: [
        # All permissions
        Permission.PROJECT_CREATE, Permission.PROJECT_READ, Permission.PROJECT_UPDATE, Permission.PROJECT_DELETE, Permission.PROJECT_APPROVE,
        Permission.EVALUATION_CREATE, Permission.EVALUATION_READ, Permission.EVALUATION_UPDATE, Permission.EVALUATION_DELETE, Permission.EVALUATION_VERIFY,
        Permission.SATELLITE_READ, Permission.SATELLITE_ANALYZE, Permission.SATELLITE_MANAGE,
        Permission.ML_PREDICT, Permission.ML_TRAIN, Permission.ML_MANAGE,
        Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE, Permission.USER_DELETE, Permission.USER_MANAGE_ROLES,
        Permission.SYSTEM_CONFIG, Permission.SYSTEM_MONITOR, Permission.SYSTEM_AUDIT,
        Permission.GIS_READ, Permission.GIS_ANALYZE, Permission.GIS_MANAGE,
    ],
    UserRole.ADMIN: [
        Permission.PROJECT_CREATE, Permission.PROJECT_READ, Permission.PROJECT_UPDATE, Permission.PROJECT_DELETE, Permission.PROJECT_APPROVE,
        Permission.EVALUATION_CREATE, Permission.EVALUATION_READ, Permission.EVALUATION_UPDATE, Permission.EVALUATION_DELETE,
        Permission.SATELLITE_READ, Permission.SATELLITE_ANALYZE,
        Permission.ML_PREDICT, Permission.ML_TRAIN,
        Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE,
        Permission.SYSTEM_MONITOR,
        Permission.GIS_READ, Permission.GIS_ANALYZE,
    ],
    UserRole.PROJECT_MANAGER: [
        Permission.PROJECT_CREATE, Permission.PROJECT_READ, Permission.PROJECT_UPDATE,
        Permission.EVALUATION_CREATE, Permission.EVALUATION_READ, Permission.EVALUATION_UPDATE,
        Permission.SATELLITE_READ, Permission.SATELLITE_ANALYZE,
        Permission.ML_PREDICT,
        Permission.USER_READ,
        Permission.GIS_READ, Permission.GIS_ANALYZE,
    ],
    UserRole.ANALYST: [
        Permission.PROJECT_READ,
        Permission.EVALUATION_CREATE, Permission.EVALUATION_READ, Permission.EVALUATION_UPDATE,
        Permission.SATELLITE_READ, Permission.SATELLITE_ANALYZE,
        Permission.ML_PREDICT,
        Permission.GIS_READ, Permission.GIS_ANALYZE,
    ],
    UserRole.VIEWER: [
        Permission.PROJECT_READ,
        Permission.EVALUATION_READ,
        Permission.SATELLITE_READ,
        Permission.GIS_READ,
    ],
    UserRole.AUDITOR: [
        Permission.PROJECT_READ,
        Permission.EVALUATION_READ, Permission.EVALUATION_VERIFY,
        Permission.SATELLITE_READ,
        Permission.SYSTEM_AUDIT,
        Permission.GIS_READ,
    ],
    UserRole.EXTERNAL: [
        Permission.PROJECT_READ,  # Limited project access
        Permission.SATELLITE_READ,  # Limited satellite data
    ],
}

def get_role_permissions(role: UserRole) -> List[Permission]:
    """Get all permissions for a given role"""
    return ROLE_PERMISSIONS.get(role, [])

def has_permission(user_role: UserRole, permission: Permission) -> bool:
    """Check if a role has a specific permission"""
    return permission in ROLE_PERMISSIONS.get(user_role, [])