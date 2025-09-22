CREATE OR REPLACE FUNCTION generate_species_data(
    species_names TEXT[], -- Array of species names
    max_year INT,
    OUT year INT,
    OUT species TEXT,
    OUT growth_model TEXT,
    OUT altura NUMERIC,
    OUT diametro NUMERIC,
    OUT agb NUMERIC,
    OUT bgb NUMERIC,
    OUT co2eq NUMERIC,
    OUT delta_co2 NUMERIC
) RETURNS SETOF RECORD AS $$
DECLARE
    species_name TEXT; -- Variable to store the current species name
    max_h NUMERIC;
    g_b NUMERIC;
    g_c NUMERIC;
    avg_dbh NUMERIC;
    g_b_dbh NUMERIC;
    g_c_dbh NUMERIC;
    allometric_a NUMERIC;
    allometric_b NUMERIC;
    r_coefficient NUMERIC;
    prev_agb_bgb NUMERIC := NULL;
BEGIN
    -- Ensure max_year does not exceed 50
    IF max_year > 50 THEN
        max_year := 50;
    END IF;

    -- Loop through each species in the array
    FOR species_name IN SELECT UNNEST(species_names) LOOP

        -- Get species parameters
        SELECT 
            (values -> 'max_height' ->> 'value')::NUMERIC,
            (values -> 'g_b' ->> 'value')::NUMERIC,
            (values -> 'g_c' ->> 'value')::NUMERIC,
            (values -> 'avg_dbh' ->> 'value')::NUMERIC,
            (values -> 'g_b_dbh' ->> 'value')::NUMERIC,
            (values -> 'g_c_dbh' ->> 'value')::NUMERIC,
            (values -> 'allometric_coeff_a' ->> 'value')::NUMERIC,
            (values -> 'allometric_coeff_b' ->> 'value')::NUMERIC,
            (values -> 'r_coeff' ->> 'value')::NUMERIC
        INTO max_h, g_b, g_c, avg_dbh, g_b_dbh, g_c_dbh, allometric_a, allometric_b, r_coefficient
        FROM "Species"
        WHERE common_name = species_name;

        -- If species not found, skip to the next species
        IF NOT FOUND THEN
            CONTINUE;
        END IF;

        -- Loop through years 0 to max_year
        FOR y IN 0..max_year LOOP
            -- Assign OUT parameter values
            year := y;
            species := species_name;
            growth_model := 'G-Gompertz';

            -- Compute height (Altura(t))
            altura := max_h * EXP(- g_b * EXP(- g_c * y));

            -- Compute diameter (Diámetro(t))
            diametro := avg_dbh * EXP(- g_b_dbh * EXP(- g_c_dbh * y));

            -- Compute Above-Ground Biomass (AGB)
            agb := allometric_a * POWER(diametro, allometric_b);

            -- Compute Below-Ground Biomass (BGB)
            bgb := agb * r_coefficient;

            -- Compute CO2 Equivalent (AGB + BGB)
            co2eq := (agb + bgb) * 0.47 * 44 / 12;

            -- Compute Delta T (Yearly Increase in Biomass)
            IF delta_co2 IS NULL THEN
                delta_co2 := co2eq;
            ELSE
                delta_co2 := co2eq - delta_co2;
            END IF;

            -- Return the row
            RETURN NEXT;
        END LOOP;

    END LOOP;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION calculate_parcel_co2eq(
    max_year INT
)
RETURNS TABLE (
    parcel_id UUID,
    parcel_name TEXT,
    year INT,
    co2eq_ton NUMERIC
) AS $$
DECLARE
    retrieved_species_name TEXT[];
BEGIN
    -- Ensure max_year does not exceed 50 for generate_species_data
    IF max_year > 50 THEN
        max_year := 50;
    END IF;

    -- Loop through all parcels and their associated species
    RETURN QUERY
    SELECT 
        p.parcel_id,
        p.parcel_name,
        g.year,
        (p.individuals * g.delta_co2) / 1000 AS co2eq_ton
    FROM 
        parcels_agbs_calculations p
    CROSS JOIN 
        LATERAL generate_species_data(STRING_TO_ARRAY(p.species, ', '), max_year) g
    WHERE 
        g.year BETWEEN 0 AND max_year;
END;
$$ LANGUAGE plpgsql;
