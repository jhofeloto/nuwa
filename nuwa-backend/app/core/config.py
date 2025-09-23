"""
Nuwa Backend Configuration Module

Centralized configuration management using Pydantic settings.
Supports environment variables and .env files.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env files.
    """
    
    # Application Settings
    APP_NAME: str = "Nuwa Backend"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Database Configuration
    DATABASE_HOST: str = Field(default="localhost", env="DATABASE_HOST")
    DATABASE_PORT: int = Field(default=5432, env="DATABASE_PORT")
    DATABASE_NAME: str = Field(default="nuwa_db", env="DATABASE_NAME")
    DATABASE_USER: str = Field(default="postgres", env="DATABASE_USER")
    DATABASE_PASSWORD: str = Field(default="password", env="DATABASE_PASSWORD")
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct PostgreSQL connection URL"""
        return f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Construct synchronous PostgreSQL connection URL"""
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    # Security Settings
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    ALGORITHM: str = "HS256"
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000"],
        env="ALLOWED_ORIGINS"
    )
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # File Storage
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    MAX_UPLOAD_SIZE: int = Field(default=50 * 1024 * 1024, env="MAX_UPLOAD_SIZE")  # 50MB
    
    # External APIs
    # Satellite Data APIs
    SENTINEL_API_URL: str = Field(default="https://scihub.copernicus.eu/dhus", env="SENTINEL_API_URL")
    SENTINEL_API_USER: Optional[str] = Field(default=None, env="SENTINEL_API_USER")
    SENTINEL_API_PASSWORD: Optional[str] = Field(default=None, env="SENTINEL_API_PASSWORD")
    
    LANDSAT_API_URL: str = Field(default="https://earthexplorer.usgs.gov/", env="LANDSAT_API_URL")
    LANDSAT_API_KEY: Optional[str] = Field(default=None, env="LANDSAT_API_KEY")
    
    # Blockchain Configuration (Cardano)
    CARDANO_NETWORK: str = Field(default="testnet", env="CARDANO_NETWORK")
    CARDANO_NODE_URL: Optional[str] = Field(default=None, env="CARDANO_NODE_URL")
    CARDANO_WALLET_SEED: Optional[str] = Field(default=None, env="CARDANO_WALLET_SEED")
    
    # IPFS Configuration
    IPFS_NODE_URL: str = Field(default="http://localhost:5001", env="IPFS_NODE_URL")
    IPFS_GATEWAY_URL: str = Field(default="http://localhost:8080", env="IPFS_GATEWAY_URL")
    
    # Machine Learning Configuration
    ML_MODEL_PATH: str = Field(default="models", env="ML_MODEL_PATH")
    ML_BATCH_SIZE: int = Field(default=32, env="ML_BATCH_SIZE")
    ML_PREDICTION_CACHE_TTL: int = Field(default=3600, env="ML_PREDICTION_CACHE_TTL")  # 1 hour
    
    # Geospatial Configuration
    DEFAULT_SRID: int = Field(default=4326, env="DEFAULT_SRID")  # WGS84
    MAX_GEOMETRY_COMPLEXITY: int = Field(default=10000, env="MAX_GEOMETRY_COMPLEXITY")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_BURST: int = Field(default=100, env="RATE_LIMIT_BURST")
    
    # Monitoring and Analytics
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    
    # Development Settings
    RELOAD_ON_CHANGE: bool = Field(default=True, env="RELOAD_ON_CHANGE")
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        valid_envs = ["development", "staging", "production", "testing"]
        if v not in valid_envs:
            raise ValueError(f"ENVIRONMENT must be one of: {valid_envs}")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {valid_levels}")
        return v.upper()
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == "testing"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """
    Get application settings singleton.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# Configuration for different environments
def get_development_config() -> dict:
    """Development environment specific configuration."""
    return {
        "DEBUG": True,
        "LOG_LEVEL": "DEBUG",
        "DATABASE_HOST": "localhost",
        "RELOAD_ON_CHANGE": True,
        "CORS_ALLOW_ALL": True,
    }

def get_production_config() -> dict:
    """Production environment specific configuration."""
    return {
        "DEBUG": False,
        "LOG_LEVEL": "INFO",
        "RELOAD_ON_CHANGE": False,
        "CORS_ALLOW_ALL": False,
        "ENABLE_METRICS": True,
    }

def get_testing_config() -> dict:
    """Testing environment specific configuration."""
    return {
        "DEBUG": True,
        "LOG_LEVEL": "DEBUG",
        "DATABASE_NAME": "nuwa_test_db",
        "TESTING": True,
    }