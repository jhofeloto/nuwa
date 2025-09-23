"""
User Pydantic Schemas

Data validation and serialization schemas for user management.
"""

from pydantic import BaseModel, Field, validator, EmailStr, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.users import UserRole

# Enums for validation
class UserRoleSchema(str, Enum):
    ADMIN = "admin"
    PROJECT_MANAGER = "project_manager"
    EVALUATOR = "evaluator"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    API_USER = "api_user"

# Base schemas
class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: str = Field(..., min_length=3, max_length=100, description="Username")
    email: EmailStr = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, max_length=200, description="Full name")
    organization: Optional[str] = Field(None, max_length=200, description="Organization")
    job_title: Optional[str] = Field(None, max_length=100, description="Job title")
    
    # Contact information
    phone_number: Optional[str] = Field(None, max_length=50, description="Phone number")
    country: Optional[str] = Field(None, max_length=100, description="Country")
    timezone: Optional[str] = Field(None, max_length=100, description="Timezone")
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum() and '_' not in v and '-' not in v:
            raise ValueError('Username must contain only alphanumeric characters, underscores, and hyphens')
        return v.lower()

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, description="Password")
    role: UserRoleSchema = Field(UserRoleSchema.VIEWER, description="User role")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check for at least one uppercase, lowercase, digit, and special character
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        
        return v

class UserUpdate(BaseModel):
    """Schema for updating an existing user."""
    full_name: Optional[str] = Field(None, max_length=200)
    organization: Optional[str] = Field(None, max_length=200)
    job_title: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=100)
    role: Optional[UserRoleSchema] = Field(None)
    is_active: Optional[bool] = Field(None)
    preferences: Optional[Dict[str, Any]] = Field(None)

class UserResponse(BaseModel):
    """Complete user response schema."""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    organization: Optional[str] = None
    job_title: Optional[str] = None
    phone_number: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    
    # Role and status
    role: UserRoleSchema
    is_active: bool
    is_verified: bool
    email_verified: bool
    
    # Activity information
    last_login: Optional[datetime] = None
    login_count: int = 0
    
    # API access
    api_enabled: bool = False
    
    # Metadata
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Computed properties
    is_admin: bool = Field(default=False, description="Whether user has admin role")
    can_create_projects: bool = Field(default=False, description="Whether user can create projects")
    can_evaluate_projects: bool = Field(default=False, description="Whether user can evaluate projects")
    can_access_api: bool = Field(default=False, description="Whether user can access API")
    
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    """Schema for user login."""
    username_or_email: str = Field(..., description="Username or email address")
    password: str = Field(..., description="Password")
    remember_me: bool = Field(False, description="Remember login session")

class UserLoginResponse(BaseModel):
    """Schema for login response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")

class PasswordChangeRequest(BaseModel):
    """Schema for password change requests."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('confirm_password')
    def validate_passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check for at least one uppercase, lowercase, digit, and special character
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        
        return v

class PasswordResetRequest(BaseModel):
    """Schema for password reset requests."""
    email: EmailStr = Field(..., description="Email address")

class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    reset_token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('confirm_password')
    def validate_passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class EmailVerificationRequest(BaseModel):
    """Schema for email verification requests."""
    email: EmailStr = Field(..., description="Email address to verify")

class EmailVerificationConfirm(BaseModel):
    """Schema for email verification confirmation."""
    verification_token: str = Field(..., description="Email verification token")

class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences."""
    preferences: Dict[str, Any] = Field(..., description="User preferences dictionary")
    
    @validator('preferences')
    def validate_preferences(cls, v):
        # Define allowed preference keys
        allowed_keys = [
            'theme', 'language', 'timezone', 'notifications',
            'dashboard_layout', 'data_refresh_interval', 'default_map_view',
            'email_notifications', 'api_rate_limit'
        ]
        
        # Check for invalid keys
        invalid_keys = [key for key in v.keys() if key not in allowed_keys]
        if invalid_keys:
            raise ValueError(f"Invalid preference keys: {invalid_keys}")
        
        return v

class APIKeyRequest(BaseModel):
    """Schema for API key requests."""
    name: str = Field(..., max_length=100, description="API key name/description")
    expires_in_days: Optional[int] = Field(None, gt=0, le=365, description="API key expiration in days")

class APIKeyResponse(BaseModel):
    """Schema for API key response."""
    api_key: str = Field(..., description="Generated API key")
    name: str = Field(..., description="API key name")
    created_at: datetime = Field(..., description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    
class UserActivityLog(BaseModel):
    """Schema for user activity logging."""
    user_id: int
    activity_type: str = Field(..., description="Type of activity")
    activity_description: str = Field(..., description="Activity description")
    ip_address: Optional[str] = Field(None, description="User IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    timestamp: datetime = Field(..., description="Activity timestamp")
    additional_data: Optional[Dict[str, Any]] = Field(None, description="Additional activity data")

class UserStatistics(BaseModel):
    """Schema for user statistics."""
    user_id: int
    
    # Activity statistics
    total_logins: int = 0
    last_login: Optional[datetime] = None
    login_streak_days: int = 0
    
    # Project statistics
    projects_created: int = 0
    projects_managed: int = 0
    evaluations_performed: int = 0
    
    # API usage statistics
    api_calls_total: int = 0
    api_calls_last_30_days: int = 0
    
    # Time statistics
    account_age_days: int = 0
    active_days_count: int = 0
    
    # Performance metrics
    average_session_duration_minutes: Optional[float] = None
    preferred_features: List[str] = Field(default_factory=list)

class UserListResponse(BaseModel):
    """Response schema for paginated user lists."""
    users: List[UserResponse]
    total: int = Field(..., description="Total number of users")
    skip: int = Field(..., description="Number of users skipped")
    limit: int = Field(..., description="Maximum number of users returned")
    has_more: bool = Field(..., description="Whether there are more users available")
    
    @validator('has_more', always=True)
    def calculate_has_more(cls, v, values):
        if 'total' in values and 'skip' in values and 'limit' in values:
            return values['skip'] + values['limit'] < values['total']
        return False