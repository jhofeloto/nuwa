"""
Security utilities for JWT authentication and password management
Comprehensive security implementation for Nuwa Carbon Platform
"""

import secrets
import hashlib
import base64
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt
import pyotp
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = "nuwa-carbon-platform-super-secret-key-change-in-production"  # TODO: Use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
EMAIL_VERIFICATION_EXPIRE_HOURS = 24
PASSWORD_RESET_EXPIRE_HOURS = 2

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Encryption for sensitive data (TOTP secrets, etc.)
ENCRYPTION_KEY = Fernet.generate_key()  # TODO: Use environment variable
cipher_suite = Fernet(ENCRYPTION_KEY)

class SecurityService:
    """Comprehensive security service for authentication and authorization"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hash"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def generate_secure_token() -> str:
        """Generate a cryptographically secure random token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure API key"""
        return f"nwa_{secrets.token_urlsafe(40)}"
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Verify token type
            if payload.get("type") != token_type:
                return None
            
            # Check expiration
            exp = payload.get("exp")
            if exp is None or datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                return None
            
            return payload
        
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    @staticmethod
    def create_email_verification_token(email: str) -> str:
        """Create token for email verification"""
        data = {
            "email": email,
            "purpose": "email_verification",
            "exp": datetime.now(timezone.utc) + timedelta(hours=EMAIL_VERIFICATION_EXPIRE_HOURS)
        }
        return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_email_verification_token(token: str) -> Optional[str]:
        """Verify email verification token and return email"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            if payload.get("purpose") != "email_verification":
                return None
            
            return payload.get("email")
        
        except JWTError:
            return None
    
    @staticmethod
    def create_password_reset_token(user_id: int, email: str) -> str:
        """Create token for password reset"""
        data = {
            "user_id": user_id,
            "email": email,
            "purpose": "password_reset",
            "exp": datetime.now(timezone.utc) + timedelta(hours=PASSWORD_RESET_EXPIRE_HOURS)
        }
        return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_password_reset_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify password reset token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            if payload.get("purpose") != "password_reset":
                return None
            
            return {
                "user_id": payload.get("user_id"),
                "email": payload.get("email")
            }
        
        except JWTError:
            return None
    
    @staticmethod
    def generate_totp_secret() -> str:
        """Generate TOTP secret for 2FA"""
        return pyotp.random_base32()
    
    @staticmethod
    def encrypt_sensitive_data(data: str) -> str:
        """Encrypt sensitive data (TOTP secrets, etc.)"""
        try:
            return cipher_suite.encrypt(data.encode()).decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise
    
    @staticmethod
    def decrypt_sensitive_data(encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            return cipher_suite.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise
    
    @staticmethod
    def verify_totp(secret: str, token: str) -> bool:
        """Verify TOTP token for 2FA"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=1)  # Allow 30-second window
        except Exception as e:
            logger.error(f"TOTP verification error: {e}")
            return False
    
    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[str]:
        """Generate backup codes for 2FA"""
        return [secrets.token_hex(4).upper() for _ in range(count)]
    
    @staticmethod
    def hash_backup_code(code: str) -> str:
        """Hash backup code for storage"""
        return hashlib.sha256(code.encode()).hexdigest()
    
    @staticmethod
    def verify_backup_code(code: str, hashed_codes: List[str]) -> bool:
        """Verify backup code against list of hashed codes"""
        hashed_input = hashlib.sha256(code.encode()).hexdigest()
        return hashed_input in hashed_codes
    
    @staticmethod
    def calculate_risk_score(
        ip_address: str,
        user_agent: str,
        location: Optional[Dict[str, float]] = None,
        failed_attempts: int = 0,
        last_login_location: Optional[Dict[str, float]] = None
    ) -> int:
        """Calculate risk score for login attempt (0-100)"""
        risk_score = 0
        
        # Failed login attempts
        if failed_attempts > 0:
            risk_score += min(failed_attempts * 10, 40)
        
        # Location-based risk (if available)
        if location and last_login_location:
            # Simple distance calculation (would use proper geospatial calculation in production)
            distance = abs(location.get("lat", 0) - last_login_location.get("lat", 0))
            if distance > 10:  # More than 10 degrees difference
                risk_score += 20
        
        # User agent changes (simplified check)
        # In production, would compare against historical user agents
        
        return min(risk_score, 100)
    
    @staticmethod
    def is_password_strong(password: str) -> tuple[bool, List[str]]:
        """Check password strength and return issues"""
        issues = []
        
        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one number")
        
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            issues.append("Password must contain at least one special character")
        
        # Check for common passwords (simplified)
        common_passwords = ["password", "123456", "qwerty", "admin", "letmein"]
        if password.lower() in common_passwords:
            issues.append("Password is too common")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate secure session token"""
        return f"sess_{secrets.token_urlsafe(32)}"

class TokenData:
    """Token data structure"""
    
    def __init__(self, user_id: int, email: str, role: str, permissions: List[str] = None):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.permissions = permissions or []

class SecurityConfig:
    """Security configuration constants"""
    
    # Token expiration times
    ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_DAYS = REFRESH_TOKEN_EXPIRE_DAYS
    EMAIL_VERIFICATION_EXPIRE_HOURS = EMAIL_VERIFICATION_EXPIRE_HOURS
    PASSWORD_RESET_EXPIRE_HOURS = PASSWORD_RESET_EXPIRE_HOURS
    
    # Security limits
    MAX_FAILED_LOGIN_ATTEMPTS = 5
    ACCOUNT_LOCKOUT_MINUTES = 15
    SESSION_TIMEOUT_MINUTES = 60
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBERS = True
    REQUIRE_SPECIAL_CHARS = True
    
    # Rate limiting
    LOGIN_RATE_LIMIT = 5  # attempts per minute
    API_RATE_LIMIT = 100  # requests per minute
    
    # 2FA settings
    TOTP_ISSUER_NAME = "Nuwa Carbon Platform"
    BACKUP_CODES_COUNT = 10

# Export security service instance
security_service = SecurityService()