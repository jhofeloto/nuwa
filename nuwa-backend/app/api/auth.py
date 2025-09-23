"""
Authentication and Authorization API endpoints
Comprehensive auth system for Nuwa Carbon Platform with JWT, 2FA, and role-based access
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, or_
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import logging
import pyotp
import qrcode
from io import BytesIO
import base64

from app.core.database import get_db
from app.core.security import security_service, SecurityConfig, TokenData
from app.models.users import (
    User, UserRole, UserStatus, Permission, Organization, UserSession, AuditLog,
    get_role_permissions, has_permission
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)

# Pydantic models for request/response
class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    username: Optional[str] = None
    organization_name: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        is_strong, issues = security_service.is_password_strong(v)
        if not is_strong:
            raise ValueError(f"Password requirements not met: {', '.join(issues)}")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    totp_code: Optional[str] = None
    remember_me: bool = False

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        is_strong, issues = security_service.is_password_strong(v)
        if not is_strong:
            raise ValueError(f"Password requirements not met: {', '.join(issues)}")
        return v

class ChangePassword(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        is_strong, issues = security_service.is_password_strong(v)
        if not is_strong:
            raise ValueError(f"Password requirements not met: {', '.join(issues)}")
        return v

class TwoFactorSetup(BaseModel):
    totp_code: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: Optional[str]
    role: str
    status: str
    is_2fa_enabled: bool
    last_login: Optional[datetime]
    created_at: datetime
    organization: Optional[Dict[str, Any]] = None
    permissions: List[str] = []

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class MessageResponse(BaseModel):
    message: str
    success: bool = True

# Dependency to get current user from JWT token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token
    payload = security_service.verify_token(credentials.credentials, "access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    # Get user from database
    result = await db.execute(
        select(User)
        .options(selectinload(User.organization))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )
    
    if user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is locked",
        )
    
    return user

# Permission checking dependency factory
def require_permission(permission: Permission):
    """Factory function to create permission requirement dependency"""
    
    async def check_permission(current_user: User = Depends(get_current_user)) -> User:
        # Check role-based permissions
        if has_permission(current_user.role, permission):
            return current_user
        
        # Check user-specific permissions (TODO: implement user_permissions lookup)
        # For now, only check role-based permissions
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied. Required: {permission.value}",
        )
    
    return check_permission

# Authentication endpoints
@router.post("/register", response_model=MessageResponse)
async def register_user(
    user_data: UserRegistration,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user account"""
    
    try:
        # Check if user already exists
        result = await db.execute(
            select(User).where(
                or_(User.email == user_data.email, User.username == user_data.username)
            )
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists"
            )
        
        # Hash password
        hashed_password = security_service.get_password_hash(user_data.password)
        
        # Create organization if provided
        organization = None
        if user_data.organization_name:
            organization = Organization(
                name=user_data.organization_name,
                slug=user_data.organization_name.lower().replace(" ", "-"),
                is_active=True,
                is_verified=False
            )
            db.add(organization)
            await db.flush()  # Get the organization ID
        
        # Create user
        user = User(
            email=user_data.email,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            full_name=f"{user_data.first_name} {user_data.last_name}",
            hashed_password=hashed_password,
            role=UserRole.VIEWER,  # Default role
            status=UserStatus.PENDING_VERIFICATION,
            organization_id=organization.id if organization else None,
            api_key=security_service.generate_api_key(),
        )
        
        # Generate email verification token
        user.email_verification_token = security_service.create_email_verification_token(user.email)
        user.email_verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)
        
        db.add(user)
        await db.commit()
        
        # Log registration
        audit_log = AuditLog(
            event_type="user_registration",
            action="CREATE",
            resource_type="user",
            resource_id=user.id,
            user_id=user.id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            success=True,
            metadata={"email": user.email, "organization": user_data.organization_name}
        )
        db.add(audit_log)
        await db.commit()
        
        logger.info(f"User registered: {user.email}")
        
        return MessageResponse(
            message="Registration successful. Please check your email to verify your account.",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(
    user_data: UserLogin,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return JWT tokens"""
    
    try:
        # Get user
        result = await db.execute(
            select(User)
            .options(selectinload(User.organization))
            .where(User.email == user_data.email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Log failed login attempt
            audit_log = AuditLog(
                event_type="login_failed",
                action="LOGIN",
                resource_type="user",
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
                success=False,
                error_message="User not found",
                metadata={"email": user_data.email}
            )
            db.add(audit_log)
            await db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if account is locked
        if user.is_locked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is temporarily locked due to multiple failed login attempts"
            )
        
        # Verify password
        if not security_service.verify_password(user_data.password, user.hashed_password):
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            # Lock account if too many failures
            if user.failed_login_attempts >= SecurityConfig.MAX_FAILED_LOGIN_ATTEMPTS:
                user.account_locked_until = datetime.now(timezone.utc) + timedelta(
                    minutes=SecurityConfig.ACCOUNT_LOCKOUT_MINUTES
                )
            
            await db.commit()
            
            # Log failed login
            audit_log = AuditLog(
                event_type="login_failed",
                action="LOGIN",
                resource_type="user",
                resource_id=user.id,
                user_id=user.id,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
                success=False,
                error_message="Invalid password",
                metadata={"failed_attempts": user.failed_login_attempts}
            )
            db.add(audit_log)
            await db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check 2FA if enabled
        if user.is_2fa_enabled:
            if not user_data.totp_code:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="2FA code required"
                )
            
            # Decrypt TOTP secret
            try:
                totp_secret = security_service.decrypt_sensitive_data(user.totp_secret)
                if not security_service.verify_totp(totp_secret, user_data.totp_code):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid 2FA code"
                    )
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="2FA verification failed"
                )
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.account_locked_until = None
        user.last_login = datetime.now(timezone.utc)
        user.last_login_ip = request.client.host
        user.login_count += 1
        user.last_activity = datetime.now(timezone.utc)
        
        # Create session
        session_token = security_service.generate_session_token()
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=SecurityConfig.SESSION_TIMEOUT_MINUTES
        )
        
        user_session = UserSession(
            user_id=user.id,
            session_token=session_token,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            expires_at=expires_at,
            is_active=True
        )
        db.add(user_session)
        
        await db.commit()
        
        # Create JWT tokens
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value,
            "session_id": user_session.id
        }
        
        access_token = security_service.create_access_token(token_data)
        refresh_token = security_service.create_refresh_token(token_data)
        
        # Log successful login
        audit_log = AuditLog(
            event_type="login_success",
            action="LOGIN",
            resource_type="user",
            resource_id=user.id,
            user_id=user.id,
            session_id=user_session.id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            success=True,
            metadata={"login_count": user.login_count}
        )
        db.add(audit_log)
        await db.commit()
        
        # Get user permissions
        permissions = [p.value for p in get_role_permissions(user.role)]
        
        # Prepare user response
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            role=user.role.value,
            status=user.status.value,
            is_2fa_enabled=user.is_2fa_enabled,
            last_login=user.last_login,
            created_at=user.created_at,
            organization=user.organization.__dict__ if user.organization else None,
            permissions=permissions
        )
        
        logger.info(f"User logged in: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token"""
    
    try:
        # Verify refresh token
        payload = security_service.verify_token(refresh_token, "refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        user_id = payload.get("user_id")
        session_id = payload.get("session_id")
        
        # Get user and session
        result = await db.execute(
            select(User)
            .options(selectinload(User.organization))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Verify session is still active
        if session_id:
            session_result = await db.execute(
                select(UserSession).where(
                    UserSession.id == session_id,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.now(timezone.utc)
                )
            )
            session = session_result.scalar_one_or_none()
            
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session expired"
                )
        
        # Create new access token
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value,
            "session_id": session_id
        }
        
        access_token = security_service.create_access_token(token_data)
        
        # Get user permissions
        permissions = [p.value for p in get_role_permissions(user.role)]
        
        # Prepare user response
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            role=user.role.value,
            status=user.status.value,
            is_2fa_enabled=user.is_2fa_enabled,
            last_login=user.last_login,
            created_at=user.created_at,
            organization=user.organization.__dict__ if user.organization else None,
            permissions=permissions
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,  # Return same refresh token
            expires_in=SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout", response_model=MessageResponse)
async def logout_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout user and invalidate session"""
    
    try:
        # Deactivate all user sessions
        await db.execute(
            update(UserSession)
            .where(UserSession.user_id == current_user.id, UserSession.is_active == True)
            .values(is_active=False, ended_at=datetime.now(timezone.utc))
        )
        
        await db.commit()
        
        logger.info(f"User logged out: {current_user.email}")
        
        return MessageResponse(
            message="Logged out successfully",
            success=True
        )
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    
    permissions = [p.value for p in get_role_permissions(current_user.role)]
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        full_name=current_user.full_name,
        role=current_user.role.value,
        status=current_user.status.value,
        is_2fa_enabled=current_user.is_2fa_enabled,
        last_login=current_user.last_login,
        created_at=current_user.created_at,
        organization=current_user.organization.__dict__ if current_user.organization else None,
        permissions=permissions
    )