SELECT * FROM pg_matviews WHERE matviewname LIKE 'parcels_agbs_project_%';
SELECT * FROM pg_indexes WHERE indexname LIKE 'idx_parcels_agbs_project_%';

DO $$ 
DECLARE 
    view_row RECORD;
BEGIN
    FOR view_row IN (
        SELECT matviewname FROM pg_matviews WHERE matviewname LIKE 'parcels_agbs_project_%'
    ) LOOP
        EXECUTE 'DROP MATERIALIZED VIEW IF EXISTS ' || view_row.matviewname || ' CASCADE';
    END LOOP;
END $$;