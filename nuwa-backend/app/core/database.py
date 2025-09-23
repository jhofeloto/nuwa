"""
Nuwa Backend Database Configuration

Async database connection management using SQLAlchemy and asyncpg.
Includes PostGIS support for geospatial operations.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine, text, event
from sqlalchemy.pool import StaticPool
import logging
import asyncio
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# SQLAlchemy setup
Base = declarative_base()

# Global engine and session variables
async_engine = None
async_session_factory = None
sync_engine = None
sync_session_factory = None

class DatabaseManager:
    """
    Database manager handling both async and sync connections.
    """
    
    def __init__(self):
        self.async_engine = None
        self.async_session_factory = None
        self.sync_engine = None
        self.sync_session_factory = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize database connections and verify PostGIS."""
        if self._initialized:
            return
            
        settings = get_settings()
        
        try:
            # Create async engine
            self.async_engine = create_async_engine(
                settings.DATABASE_URL,
                echo=settings.is_development,
                pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_MAX_OVERFLOW,
                pool_pre_ping=True,
                pool_recycle=3600,  # Recycle connections every hour
            )
            
            # Create sync engine (for migrations and administrative tasks)
            self.sync_engine = create_engine(
                settings.SYNC_DATABASE_URL,
                echo=settings.is_development,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
            
            # Create session factories
            self.async_session_factory = async_sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=True,
                autocommit=False,
            )
            
            self.sync_session_factory = sessionmaker(
                bind=self.sync_engine,
                autoflush=True,
                autocommit=False,
            )
            
            # Test connections and verify PostGIS
            await self._verify_connections()
            
            self._initialized = True
            logger.info("✅ Database connections initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database connections: {str(e)}")
            raise
    
    async def _verify_connections(self):
        """Verify database connections and PostGIS availability."""
        
        # Test async connection
        async with self.async_engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"📡 Connected to PostgreSQL: {version}")
        
        # Test PostGIS availability
        try:
            async with self.async_engine.begin() as conn:
                result = await conn.execute(text("SELECT PostGIS_Version()"))
                postgis_version = result.scalar()
                logger.info(f"🗺️ PostGIS available: {postgis_version}")
        except Exception as e:
            logger.warning(f"⚠️ PostGIS not available: {str(e)}")
            logger.info("💡 To enable PostGIS, run: CREATE EXTENSION IF NOT EXISTS postgis;")
    
    async def create_tables(self):
        """Create all database tables."""
        try:
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database tables created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create database tables: {str(e)}")
            raise
    
    async def drop_tables(self):
        """Drop all database tables (use with caution)."""
        try:
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.info("🗑️ Database tables dropped successfully")
        except Exception as e:
            logger.error(f"❌ Failed to drop database tables: {str(e)}")
            raise
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session with automatic cleanup."""
        if not self._initialized:
            await self.initialize()
        
        session = self.async_session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    def get_sync_session(self):
        """Get sync database session."""
        if not self.sync_session_factory:
            raise RuntimeError("Database not initialized")
        return self.sync_session_factory()
    
    async def close(self):
        """Close all database connections."""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.sync_engine:
            self.sync_engine.dispose()
        
        self._initialized = False
        logger.info("🔌 Database connections closed")

# Global database manager instance
db_manager = DatabaseManager()

# Dependency functions for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for getting async database session.
    
    Usage:
        @app.get("/projects")
        async def get_projects(db: AsyncSession = Depends(get_db)):
            # Use db session here
    """
    async with db_manager.get_async_session() as session:
        yield session

async def get_db_connection():
    """Get database connection for health checks."""
    if not db_manager._initialized:
        await db_manager.initialize()
    return db_manager.async_engine

# Database initialization functions
async def init_database():
    """Initialize database connections and create tables."""
    await db_manager.initialize()
    
    # Create tables if they don't exist
    await db_manager.create_tables()
    
    # Enable PostGIS extension if not already enabled
    await _ensure_postgis_extension()

async def _ensure_postgis_extension():
    """Ensure PostGIS extension is enabled."""
    try:
        async with db_manager.async_engine.begin() as conn:
            # Check if PostGIS is already enabled
            result = await conn.execute(
                text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'postgis')")
            )
            if not result.scalar():
                # Try to enable PostGIS
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
                logger.info("✅ PostGIS extension enabled")
            else:
                logger.info("✅ PostGIS extension already enabled")
    except Exception as e:
        logger.warning(f"⚠️ Could not enable PostGIS extension: {str(e)}")
        logger.info("💡 Please manually enable PostGIS: CREATE EXTENSION IF NOT EXISTS postgis;")

async def close_database():
    """Close database connections."""
    await db_manager.close()

# Database session context manager
@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Standalone database session context manager.
    
    Usage:
        async with get_db_session() as db:
            # Use db session here
    """
    async with db_manager.get_async_session() as session:
        yield session

# Database transaction context manager
@asynccontextmanager
async def database_transaction() -> AsyncGenerator[AsyncSession, None]:
    """
    Database transaction context manager with automatic rollback on error.
    
    Usage:
        async with database_transaction() as db:
            # All operations in this block are in a single transaction
            # Automatic rollback on any exception
    """
    async with db_manager.get_async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# Health check function
async def check_database_health() -> dict:
    """
    Comprehensive database health check.
    """
    health_info = {
        "connected": False,
        "postgis_available": False,
        "version": None,
        "postgis_version": None,
        "connection_pool": {
            "size": 0,
            "checked_in": 0,
            "checked_out": 0,
            "overflow": 0,
        }
    }
    
    try:
        if not db_manager._initialized:
            await db_manager.initialize()
        
        async with db_manager.async_engine.begin() as conn:
            # Check PostgreSQL version
            result = await conn.execute(text("SELECT version()"))
            health_info["version"] = result.scalar()
            health_info["connected"] = True
            
            # Check PostGIS
            try:
                result = await conn.execute(text("SELECT PostGIS_Version()"))
                health_info["postgis_version"] = result.scalar()
                health_info["postgis_available"] = True
            except Exception:
                pass
            
            # Get connection pool info
            pool = db_manager.async_engine.pool
            if pool:
                health_info["connection_pool"] = {
                    "size": pool.size(),
                    "checked_in": pool.checkedin(),
                    "checked_out": pool.checkedout(),
                    "overflow": pool.overflow(),
                }
    
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_info["error"] = str(e)
    
    return health_info