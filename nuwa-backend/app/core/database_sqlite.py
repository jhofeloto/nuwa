"""
Nuwa Backend Database Configuration (SQLite Alternative)

SQLite database connection management for development/testing
when PostgreSQL is not available.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine, text, event
from sqlalchemy.pool import StaticPool
import logging
import asyncio
import sqlite3
import os
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
    Database manager handling SQLite connections for development.
    """
    
    def __init__(self):
        self.async_engine = None
        self.async_session_factory = None
        self.sync_engine = None
        self.sync_session_factory = None
        self._initialized = False
        self.db_path = None
    
    async def initialize(self):
        """Initialize SQLite database connections."""
        if self._initialized:
            return
            
        settings = get_settings()
        
        try:
            # Create databases directory
            db_dir = "/home/user/webapp/nuwa-backend/data"
            os.makedirs(db_dir, exist_ok=True)
            
            # Database file path
            self.db_path = f"{db_dir}/nuwa_development.db"
            
            # Create async engine for SQLite
            database_url = f"sqlite+aiosqlite:///{self.db_path}"
            self.async_engine = create_async_engine(
                database_url,
                echo=settings.is_development,
                poolclass=StaticPool,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 30
                },
                pool_pre_ping=True,
            )
            
            # Create sync engine for migrations
            sync_database_url = f"sqlite:///{self.db_path}"
            self.sync_engine = create_engine(
                sync_database_url,
                echo=settings.is_development,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False}
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
            
            # Test connections
            await self._verify_connections()
            
            self._initialized = True
            logger.info("✅ SQLite database connections initialized successfully")
            logger.info(f"📁 Database file: {self.db_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database connections: {str(e)}")
            raise
    
    async def _verify_connections(self):
        """Verify database connections and setup."""
        
        # Test async connection
        async with self.async_engine.begin() as conn:
            result = await conn.execute(text("SELECT sqlite_version()"))
            version = result.scalar()
            logger.info(f"📡 Connected to SQLite: {version}")
        
        # Enable foreign keys and other pragmas
        async with self.async_engine.begin() as conn:
            await conn.execute(text("PRAGMA foreign_keys=ON"))
            await conn.execute(text("PRAGMA journal_mode=WAL"))
            await conn.execute(text("PRAGMA synchronous=NORMAL"))
            await conn.execute(text("PRAGMA temp_store=memory"))
            await conn.execute(text("PRAGMA mmap_size=268435456"))  # 256MB
            logger.info("🔧 SQLite pragmas configured for performance")
    
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
    
    # Create sample data if database is empty
    await _create_sample_data()

async def _create_sample_data():
    """Create sample data for development."""
    try:
        async with db_manager.get_async_session() as session:
            # Check if we already have data
            from sqlalchemy import select, func
            from app.models.projects_sqlite import Project
            
            result = await session.execute(select(func.count(Project.id)))
            count = result.scalar()
            
            if count == 0:
                # Create sample projects
                sample_projects = [
                    Project(
                        name="Amazon Rainforest Conservation",
                        description="Large-scale reforestation project in the Amazon basin for carbon sequestration",
                        project_type="reforestation",
                        country="Brazil",
                        region="Amazonas",
                        latitude=-3.4653,
                        longitude=-62.2159,
                        project_area_hectares=5000.0,
                        estimated_co2_capture_tons_year=25000.0,
                        methodology="AR-ACM0003",
                        standard="VCS",
                        climate_zone="Tropical Rainforest"
                    ),
                    Project(
                        name="Costa Rica Agroforestry Initiative",
                        description="Sustainable agroforestry practices combining coffee cultivation with native tree species",
                        project_type="agroforestry",
                        country="Costa Rica",
                        region="Central Valley",
                        latitude=9.7489,
                        longitude=-83.7534,
                        project_area_hectares=1200.0,
                        estimated_co2_capture_tons_year=6000.0,
                        methodology="AR-AMS0007",
                        standard="Gold Standard",
                        climate_zone="Tropical Highland"
                    ),
                    Project(
                        name="Kenya Grassland Restoration",
                        description="Restoration of degraded grasslands through improved grazing management",
                        project_type="grassland_management",
                        country="Kenya",
                        region="Rift Valley",
                        latitude=-1.0232,
                        longitude=37.9062,
                        project_area_hectares=3000.0,
                        estimated_co2_capture_tons_year=9000.0,
                        methodology="AMS-III.AU",
                        standard="VCS",
                        climate_zone="Savanna"
                    )
                ]
                
                for project in sample_projects:
                    session.add(project)
                
                await session.commit()
                logger.info(f"✅ Created {len(sample_projects)} sample projects")
    
    except Exception as e:
        logger.warning(f"⚠️ Could not create sample data: {str(e)}")

async def close_database():
    """Close database connections."""
    await db_manager.close()

# Database session context manager
@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Standalone database session context manager.
    """
    async with db_manager.get_async_session() as session:
        yield session

# Database transaction context manager
@asynccontextmanager
async def database_transaction() -> AsyncGenerator[AsyncSession, None]:
    """
    Database transaction context manager with automatic rollback on error.
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
        "database_type": "sqlite",
        "version": None,
        "file_path": None,
        "file_size_mb": None,
        "tables_count": 0
    }
    
    try:
        if not db_manager._initialized:
            await db_manager.initialize()
        
        async with db_manager.async_engine.begin() as conn:
            # Check SQLite version
            result = await conn.execute(text("SELECT sqlite_version()"))
            health_info["version"] = result.scalar()
            health_info["connected"] = True
            health_info["file_path"] = db_manager.db_path
            
            # Get file size
            if db_manager.db_path and os.path.exists(db_manager.db_path):
                file_size = os.path.getsize(db_manager.db_path)
                health_info["file_size_mb"] = round(file_size / 1024 / 1024, 2)
            
            # Count tables
            result = await conn.execute(text(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
            ))
            health_info["tables_count"] = result.scalar()
    
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_info["error"] = str(e)
    
    return health_info