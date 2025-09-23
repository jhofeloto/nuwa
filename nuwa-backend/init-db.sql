-- Nuwa Database Initialization Script
-- Sets up PostgreSQL database with PostGIS extension and initial configuration

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Create database user (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'nuwa_user') THEN
        CREATE USER nuwa_user WITH PASSWORD 'nuwa_pass123';
    END IF;
END
$$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE nuwa_db TO nuwa_user;
GRANT ALL ON SCHEMA public TO nuwa_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO nuwa_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO nuwa_user;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO nuwa_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO nuwa_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO nuwa_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO nuwa_user;

-- Create some sample spatial reference systems if needed
-- (Most common ones are already included in PostGIS)

-- Insert sample data for development/testing (optional)
-- This would be executed after tables are created by SQLAlchemy

-- Create indices for better performance
-- These will be created automatically by SQLAlchemy, but can be optimized here

-- Log the initialization
INSERT INTO public.spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) 
SELECT 4326, 'EPSG', 4326, '+proj=longlat +datum=WGS84 +no_defs', 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
WHERE NOT EXISTS (SELECT 1 FROM public.spatial_ref_sys WHERE srid = 4326);

-- Create a function to log database setup
CREATE OR REPLACE FUNCTION log_db_setup() RETURNS void AS $$
BEGIN
    RAISE NOTICE 'Nuwa database initialized successfully with PostGIS extension';
    RAISE NOTICE 'PostGIS version: %', postgis_version();
    RAISE NOTICE 'Available spatial reference systems: %', (SELECT count(*) FROM spatial_ref_sys);
END;
$$ LANGUAGE plpgsql;

-- Execute the logging function
SELECT log_db_setup();