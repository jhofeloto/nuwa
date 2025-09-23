"""
Authentication and Security Middleware for Nuwa Carbon Platform
Provides comprehensive security features including rate limiting, CORS, and auth protection
"""

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Callable, Dict, Any, Optional
import time
import logging
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import asyncio

from app.models.users import User, UserSession, AuditLog
from app.core.security import security_service
from app.core.database import get_db

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware for authentication, rate limiting, and auditing"""
    
    def __init__(self, app, enable_rate_limiting: bool = True, enable_audit_logging: bool = True):
        super().__init__(app)
        self.enable_rate_limiting = enable_rate_limiting
        self.enable_audit_logging = enable_audit_logging
        
        # Rate limiting storage (in production, use Redis)
        self.rate_limit_storage: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'requests': 0,
            'reset_time': time.time() + 60  # Reset every minute
        })
        
        # Protected paths that require authentication
        self.protected_paths = [
            "/api/v1/projects",
            "/api/v1/evaluations", 
            "/api/v1/ml/predict-co2",
            "/api/v1/satellite/analyze-project",
            "/api/v1/geospatial/spatial-query",
            "/api/v1/analytics/database-stats",
            "/api/v1/auth/me",
            "/api/v1/auth/logout",
            "/api/v1/users"
        ]
        
        # Public paths that don't require authentication
        self.public_paths = [
            "/",
            "/health",
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/auth/refresh",
            "/api/v1/satellite/status",  # Public satellite status
            "/docs",
            "/redoc",
            "/openapi.json"
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Main middleware dispatch method"""
        
        start_time = time.time()
        
        try:
            # Skip middleware for health checks and docs
            if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
                response = await call_next(request)
                return response
            
            # Rate limiting
            if self.enable_rate_limiting:
                rate_limit_response = await self._check_rate_limit(request)
                if rate_limit_response:
                    return rate_limit_response
            
            # Authentication check for protected paths
            user = None
            if self._requires_authentication(request.url.path):
                user = await self._authenticate_request(request)
                if not user:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Authentication required", "success": False}
                    )
            
            # Add user to request state if authenticated
            if user:
                request.state.user = user
            
            # Process request
            response = await call_next(request)
            
            # Audit logging
            if self.enable_audit_logging:
                await self._log_request(request, response, user, time.time() - start_time)
            
            # Add security headers
            self._add_security_headers(response)
            
            return response
            
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            
            # Log the error
            if self.enable_audit_logging:
                await self._log_request(request, None, None, time.time() - start_time, str(e))
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error", "success": False}
            )

    def _requires_authentication(self, path: str) -> bool:
        """Check if path requires authentication"""
        
        # Check if it's explicitly public
        for public_path in self.public_paths:
            if path.startswith(public_path):
                return False
        
        # Check if it's protected
        for protected_path in self.protected_paths:
            if path.startswith(protected_path):
                return True
        
        # Default to requiring authentication for API paths
        return path.startswith("/api/v1/")

    async def _authenticate_request(self, request: Request) -> Optional[User]:
        """Authenticate request and return user if valid"""
        
        try:
            # Get authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            # Extract token
            token = auth_header.split(" ")[1] if " " in auth_header else None
            if not token:
                return None
            
            # Verify token
            payload = security_service.verify_token(token, "access")
            if not payload:
                return None
            
            user_id = payload.get("user_id")
            session_id = payload.get("session_id")
            
            if not user_id:
                return None
            
            # TODO: Implement proper database session handling
            # For now, return None to allow imports to work
            return None
            
            # Get user from database
            # async with async_session() as db:
            #     result = await db.execute(
            #         select(User).where(User.id == user_id)
            #     )
            #     user = result.scalar_one_or_none()
            #     
            #     if not user or not user.is_active or user.is_locked:
            #         return None
            #     
            #     # Verify session if present
            #     if session_id:
            #         session_result = await db.execute(
            #             select(UserSession).where(
            #                 UserSession.id == session_id,
            #                 UserSession.is_active == True,
            #                 UserSession.expires_at > datetime.now(timezone.utc)
            #             )
            #         )
            #         session = session_result.scalar_one_or_none()
            #         
            #         if not session:
            #             return None
            #         
            #         # Update session activity
            #         session.last_activity = datetime.now(timezone.utc)
            #         await db.commit()
            #     
            #     # Update user activity
            #     user.last_activity = datetime.now(timezone.utc)
            #     await db.commit()
            #     
            #     return user
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None

    async def _check_rate_limit(self, request: Request) -> Optional[JSONResponse]:
        """Check and enforce rate limiting"""
        
        try:
            # Get client identifier (IP address)
            client_ip = request.client.host
            current_time = time.time()
            
            # Clean up expired entries
            if current_time > self.rate_limit_storage[client_ip]['reset_time']:
                self.rate_limit_storage[client_ip] = {
                    'requests': 0,
                    'reset_time': current_time + 60
                }
            
            # Check rate limit
            requests = self.rate_limit_storage[client_ip]['requests']
            max_requests = 100  # 100 requests per minute
            
            if requests >= max_requests:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Rate limit exceeded. Try again later.",
                        "success": False,
                        "retry_after": int(self.rate_limit_storage[client_ip]['reset_time'] - current_time)
                    },
                    headers={
                        "X-RateLimit-Limit": str(max_requests),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(self.rate_limit_storage[client_ip]['reset_time'])),
                        "Retry-After": str(int(self.rate_limit_storage[client_ip]['reset_time'] - current_time))
                    }
                )
            
            # Increment request count
            self.rate_limit_storage[client_ip]['requests'] += 1
            
            return None
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return None

    async def _log_request(
        self, 
        request: Request, 
        response: Optional[Response], 
        user: Optional[User], 
        duration: float,
        error_message: Optional[str] = None
    ):
        """Log request for audit purposes"""
        
        try:
            # TODO: Implement proper audit logging with database session
            return
            
            # async with async_session() as db:
            #     audit_log = AuditLog(
            #         event_type="api_request",
            #         action=request.method,
            #         resource_type="api",
            #         user_id=user.id if user else None,
            #         ip_address=request.client.host,
            #         user_agent=request.headers.get("user-agent", ""),
            #         endpoint=str(request.url.path),
            #         http_method=request.method,
            #         success=response.status_code < 400 if response else False,
            #         error_message=error_message,
            #         metadata={
            #             "duration_ms": round(duration * 1000, 2),
            #             "status_code": response.status_code if response else None,
            #             "query_params": dict(request.query_params),
            #             "path_params": dict(request.path_params) if hasattr(request, 'path_params') else {}
            #         }
            #     )
            #     
            #     db.add(audit_log)
            #     await db.commit()
                
        except Exception as e:
            logger.error(f"Audit logging error: {e}")

    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Simplified authentication middleware for specific routes"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add authentication context to request"""
        
        # Try to authenticate user if Authorization header is present
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
            payload = security_service.verify_token(token, "access")
            if payload:
                user_id = payload.get("user_id")
                if user_id:
                    try:
                        # TODO: Implement proper user lookup
                        pass
                        # async with async_session() as db:
                        #     result = await db.execute(
                        #         select(User).where(User.id == user_id)
                        #     )
                        #     user = result.scalar_one_or_none()
                        #     
                        #     if user and user.is_active and not user.is_locked:
                        #         request.state.user = user
                        #         request.state.user_id = user.id
                        #         request.state.user_role = user.role
                        #         request.state.is_authenticated = True
                        #     else:
                        #         request.state.is_authenticated = False
                        request.state.is_authenticated = False
                    except Exception as e:
                        logger.error(f"User lookup error: {e}")
                        request.state.is_authenticated = False
                else:
                    request.state.is_authenticated = False
            else:
                request.state.is_authenticated = False
        else:
            request.state.is_authenticated = False
        
        response = await call_next(request)
        return response

def setup_cors_middleware(app):
    """Setup CORS middleware with appropriate settings"""
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:3001",
            "https://3001-*.e2b.dev",  # E2B sandbox domains
            "https://8001-*.e2b.dev",  # E2B sandbox domains
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "Accept",
            "Origin",
            "User-Agent",
            "DNT",
            "Cache-Control",
            "X-Mx-ReqToken",
            "Keep-Alive",
            "X-Requested-With",
            "If-Modified-Since",
        ],
    )

def setup_security_middleware(app, enable_rate_limiting: bool = True):
    """Setup comprehensive security middleware"""
    
    # Add CORS first
    setup_cors_middleware(app)
    
    # Add security middleware
    app.add_middleware(
        SecurityMiddleware, 
        enable_rate_limiting=enable_rate_limiting,
        enable_audit_logging=True
    )