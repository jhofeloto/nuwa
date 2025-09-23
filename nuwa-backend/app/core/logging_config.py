"""
Nuwa Backend Logging Configuration

Centralized logging setup with structured logging for production environments.
"""

import logging
import logging.config
import sys
from datetime import datetime
from typing import Dict, Any
import json

from app.core.config import get_settings

class StructuredFormatter(logging.Formatter):
    """
    Custom formatter for structured JSON logging in production.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        # Create structured log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        if hasattr(record, 'operation'):
            log_entry["operation"] = record.operation
        if hasattr(record, 'duration_ms'):
            log_entry["duration_ms"] = record.duration_ms
        
        return json.dumps(log_entry, ensure_ascii=False)

class ColoredFormatter(logging.Formatter):
    """
    Custom formatter with colors for development environments.
    """
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # Add colors to level name
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{level_color}{record.levelname}{self.COLORS['RESET']}"
        
        # Format the message
        formatted = super().format(record)
        
        return formatted

def setup_logging():
    """
    Setup application logging configuration.
    """
    settings = get_settings()
    
    # Base logging configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "structured": {
                "()": StructuredFormatter,
            },
            "colored": {
                "()": ColoredFormatter,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "colored" if settings.is_development else "structured",
                "stream": sys.stdout
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "structured" if settings.is_production else "detailed",
                "filename": "logs/nuwa-backend.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "structured" if settings.is_production else "detailed",
                "filename": "logs/nuwa-backend-errors.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            }
        },
        "loggers": {
            # Root logger
            "": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False
            },
            # Application loggers
            "app": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False
            },
            "app.api": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False
            },
            "app.core": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False
            },
            "app.services": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False
            },
            "app.models": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False
            },
            # Third-party loggers
            "sqlalchemy.engine": {
                "level": "WARNING" if settings.is_production else "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "sqlalchemy.pool": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "fastapi": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            }
        }
    }
    
    # Add error file handler in production
    if settings.is_production:
        config["loggers"]["app"]["handlers"].append("error_file")
        config["loggers"]["app.api"]["handlers"].append("error_file")
        config["loggers"]["app.core"]["handlers"].append("error_file")
        config["loggers"]["app.services"]["handlers"].append("error_file")
        config["loggers"]["app.models"]["handlers"].append("error_file")
    
    # Create logs directory if it doesn't exist
    import os
    os.makedirs("logs", exist_ok=True)
    
    # Apply logging configuration
    logging.config.dictConfig(config)
    
    # Log startup message
    logger = logging.getLogger("app.core.logging")
    logger.info(f"🔧 Logging configured for {settings.ENVIRONMENT} environment")
    logger.info(f"📊 Log level set to {settings.LOG_LEVEL}")

# Utility functions for structured logging
def log_performance(logger: logging.Logger, operation: str, duration_ms: float, **kwargs):
    """
    Log performance metrics in a structured way.
    """
    logger.info(
        f"Performance: {operation} completed in {duration_ms:.2f}ms",
        extra={
            "operation": operation,
            "duration_ms": duration_ms,
            **kwargs
        }
    )

def log_api_request(logger: logging.Logger, method: str, path: str, status_code: int, duration_ms: float, **kwargs):
    """
    Log API request details in a structured way.
    """
    logger.info(
        f"API {method} {path} -> {status_code} ({duration_ms:.2f}ms)",
        extra={
            "operation": "api_request",
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
            **kwargs
        }
    )

def log_database_operation(logger: logging.Logger, operation: str, table: str, duration_ms: float, **kwargs):
    """
    Log database operation details in a structured way.
    """
    logger.info(
        f"Database {operation} on {table} completed in {duration_ms:.2f}ms",
        extra={
            "operation": f"db_{operation}",
            "table": table,
            "duration_ms": duration_ms,
            **kwargs
        }
    )

def log_external_api_call(logger: logging.Logger, service: str, endpoint: str, status_code: int, duration_ms: float, **kwargs):
    """
    Log external API call details in a structured way.
    """
    logger.info(
        f"External API {service} {endpoint} -> {status_code} ({duration_ms:.2f}ms)",
        extra={
            "operation": "external_api_call",
            "service": service,
            "endpoint": endpoint,
            "status_code": status_code,
            "duration_ms": duration_ms,
            **kwargs
        }
    )

class RequestLogger:
    """
    Context manager for logging request processing.
    """
    
    def __init__(self, logger: logging.Logger, operation: str, **context):
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        self.logger.info(f"Starting {self.operation}", extra=self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        duration_ms = (time.time() - self.start_time) * 1000
        
        if exc_type is None:
            self.logger.info(
                f"Completed {self.operation} in {duration_ms:.2f}ms",
                extra={
                    **self.context,
                    "operation": self.operation,
                    "duration_ms": duration_ms,
                    "success": True
                }
            )
        else:
            self.logger.error(
                f"Failed {self.operation} after {duration_ms:.2f}ms: {exc_val}",
                extra={
                    **self.context,
                    "operation": self.operation,
                    "duration_ms": duration_ms,
                    "success": False,
                    "error": str(exc_val)
                },
                exc_info=True
            )