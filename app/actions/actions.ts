"use server";

import { prisma } from '@/prisma';
import { configSchema, explanationsSchema, Result, Config } from "@/app/ui/analytics/types";
import { generateObject } from "ai";
import { openai } from "@ai-sdk/openai";
import { z } from "zod";
import { Growth } from '@/app/lib/definitions';

/**
 * Executes a SQL query and returns the result data
 * @param {string} query - The SQL query to execute
 * @returns {Promise<Result[]>} Array of query results
 * @throws {Error} If query is not a SELECT statement or table doesn't exist
 */
export const runGeneratedSQLQuery = async (query: string) => {
  "use server";
  // Ensure the query is a SELECT statement. Otherwise, throw an error
  if (
    !query.trim().toLowerCase().startsWith("select") ||
    query.trim().toLowerCase().includes("drop") ||
    query.trim().toLowerCase().includes("delete") ||
    query.trim().toLowerCase().includes("insert") ||
    query.trim().toLowerCase().includes("update") ||
    query.trim().toLowerCase().includes("alter") ||
    query.trim().toLowerCase().includes("truncate") ||
    query.trim().toLowerCase().includes("create") ||
    query.trim().toLowerCase().includes("grant") ||
    query.trim().toLowerCase().includes("revoke")
  ) {
    throw new Error("Only SELECT queries are allowed");
  }

  let data: Result[];
  try {
    data = await prisma.$queryRawUnsafe(query);
  } catch (e: unknown) {
    if (e instanceof Error && e.message.includes('relation "unicorns" does not exist')) {
      console.log(
        "Table does not exist, creating and seeding it with dummy data now...",
      );
      // throw error
      throw Error("Table does not exist");
    } else {
      throw e;
    }
  }

  return data as Result[];
};

export const generateQuery = async (input: string) => {
  "use server";
  try {
    
    const result = await generateObject({
      model: openai('gpt-4o'),
      system: `You are a SQL (postgres) and data visualization expert. 
      Your job is to help the user write a SQL query to retrieve the data they need. The database is a complex schema defined as follows:

      model User {
        id       String    @id @default(uuid()) @db.Uuid
        name     String?
        email    String    @unique
        emailVerified DateTime?
        role     Role      @default(GESTOR)
        password String 

        accounts      Account[]
        sessions      Session[]
        projects Project[]

        createdAt DateTime @default(now())
        updatedAt DateTime @updatedAt
      }

      model Account {
        userId            String @db.Uuid
        type              String
        provider          String
        providerAccountId String
        refresh_token     String?
        access_token      String?
        expires_at        Int?
        token_type        String?
        scope             String?
        id_token          String?
        session_state     String?
      
        createdAt DateTime @default(now())
        updatedAt DateTime @updatedAt
      
        user User @relation(fields: [userId], references: [id], onDelete: Cascade)
      
        @@id([provider, providerAccountId])
      }
      
      model Session {
        sessionToken String   @unique
        userId       String @db.Uuid
        expires      DateTime
        user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)
      
        createdAt DateTime @default(now())
        updatedAt DateTime @updatedAt
      }
      
      model VerificationToken {
        identifier String
        token      String
        expires    DateTime
      
        @@id([identifier, token])
      }

      model MathModels {
        id   String @id @default(uuid()) @db.Uuid
        name String @unique
      }

      model Species {
        id              String    @id @default(uuid()) @db.Uuid
        common_name     String    @unique
        scientific_name String    @unique
        family          String?
        functional_type String?
        values          Json
        comments        String?
        parcels         Parcels[]
      }

      model Keyword {
        id              String           @id @default(uuid()) @db.Uuid
        name            String           @unique
        projectKeywords ProjectKeyword[]
      }

      model Ecosystem {
        description String?
        values      Json
        type        String    @unique
        id          String    @id @default(uuid()) @db.Uuid

        parcels     Parcels[]
        coverages   Coverage[]
      }

      model Project {
        id          String           @id @default(uuid()) @db.Uuid
        title       String           @db.VarChar(255)
        country     String?          @db.VarChar(255)
        status      Status           @default(Seed)
        department  String?          @db.VarChar(255)
        values      Json?
        createdAt   DateTime         @default(now())
        updatedAt   DateTime         @updatedAt
        creatorId   String           @db.Uuid
        description String?
        name        String           @unique

        parcels     Parcels[]
        creator     User             @relation(fields: [creatorId], references: [id], onDelete: Cascade)
        keywords    ProjectKeyword[]
      }

      model ProjectKeyword {
        projectId String  @db.Uuid
        keywordId String  @db.Uuid
        keyword   Keyword @relation(fields: [keywordId], references: [id], onDelete: Cascade)
        project   Project @relation(fields: [projectId], references: [id], onDelete: Cascade)

        @@id([projectId, keywordId])
      }

      model Parcels {
        id           String     @id @default(uuid()) @db.Uuid
        name         String     @unique
        projectId    String?    @db.Uuid
        ecosystemId  String?    @db.Uuid
        speciesId    String    @db.Uuid
        area         Int?
        municipality String?
        department   String?
        cadastral_id String?
        geolocation  Json?
        polygon      Json?
        area_factor  Int      @default(0)

        analysis     ParcelAnalysis[]

        ecosystem    Ecosystem? @relation(fields: [ecosystemId], references: [id])
        project      Project?   @relation(fields: [projectId], references: [id])
        species      Species   @relation(fields: [speciesId], references: [id])
      }

      enum Role {
        GESTOR
        ADMIN
      }

      enum Status {
        Seed
        InProgress
        Finished
        Canceled
      }

      model Coverage {
        id          String   @id @default(uuid()) @db.Uuid
        ecosystemId String?   @db.Uuid
        description String?
        type        String?
        index       Index   @default(NDVI)
        values      Json

        ecosystem  Ecosystem? @relation(fields: [ecosystemId], references: [id])
      }
      enum Index {
        NDVI
        NDWI
        SAVI
        OSAVI
      }

      model ParcelAnalysis {
        id           String @id @default(uuid()) @db.Uuid
        parcelId     String @db.Uuid
        analysisType AnalysisType @default(ML)
        values       Json
        createdAt    DateTime @default(now())
        updatedAt    DateTime @updatedAt

        parcel  Parcels @relation(fields: [parcelId], references: [id], onDelete: Cascade)
      }
      enum AnalysisType {
        MANUAL
        ML
      }
        This application is a data visualization tool that allows users to analyze and visualize data related to projects, parcels, coverage, and parcel analysis and the idea is to provide an assessment on the potential of 
        the project or the parcel to make part of a carbon credit program. Which means that there are additional calculations configured in postgresql as materialized views, functions and procedures to quantify the carbon
        sequestration potential of the project or the parcel. These are the additional calculations created:

        CREATE OR REPLACE VIEW total_impact AS
  SELECT sum((("Project"."values" -> 'impact'::text) ->> 'value'::text)::integer) AS total_impact
    FROM public."Project"
    WHERE (("Project"."values" -> 'impact'::text) ->> 'value'::text) IS NOT NULL;
    
  CREATE OR REPLACE VIEW total_investment AS
  SELECT sum((("Project"."values" -> 'total_investment'::text) ->> 'value'::text)::integer) AS total_investment
    FROM public."Project"
    WHERE (("Project"."values" -> 'total_investment'::text) ->> 'value'::text) IS NOT NULL;

  CREATE OR REPLACE VIEW total_bankable_investment AS
  SELECT sum((("Project"."values" -> 'bankable_investment'::text) ->> 'value'::text)::integer) AS total_bankable_investment
    FROM public."Project"
    WHERE (("Project"."values" -> 'bankable_investment'::text) ->> 'value'::text) IS NOT NULL;
    
  CREATE OR REPLACE VIEW total_income AS
  SELECT sum((("Project"."values" -> 'income'::text) ->> 'value'::text)::integer) AS total_income
    FROM public."Project"
    WHERE (("Project"."values" -> 'income'::text) ->> 'value'::text) IS NOT NULL;

  CREATE OR REPLACE VIEW species_calculation AS
    WITH base_values AS (
          SELECT s.id AS species_id,
              s.common_name,
              ((s."values" -> 'allometric_coeff_a'::text) ->> 'value'::text)::numeric AS allometric_coeff_a,
              ((s."values" -> 'avg_dbh'::text) ->> 'value'::text)::numeric AS avg_dbh,
              ((s."values" -> 'allometric_coeff_b'::text) ->> 'value'::text)::numeric AS allometric_coeff_b,
              ((s."values" -> 'r_coeff'::text) ->> 'value'::text)::numeric AS r_coeff
            FROM public."Species" s
          ), agb_calc AS (
          SELECT base_values.species_id,
              base_values.common_name,
              base_values.allometric_coeff_a,
              base_values.avg_dbh,
              base_values.allometric_coeff_b,
              base_values.r_coeff,
              base_values.allometric_coeff_a * (base_values.avg_dbh ^ base_values.allometric_coeff_b) AS agb_species
            FROM base_values
          ), bgb_calc AS (
          SELECT agb_calc.species_id,
              agb_calc.common_name,
              agb_calc.allometric_coeff_a,
              agb_calc.avg_dbh,
              agb_calc.allometric_coeff_b,
              agb_calc.r_coeff,
              agb_calc.agb_species,
              agb_calc.agb_species * agb_calc.r_coeff AS bgb_species
            FROM agb_calc
          ), co2_calc AS (
          SELECT bgb_calc.species_id,
              bgb_calc.common_name,
              bgb_calc.allometric_coeff_a,
              bgb_calc.avg_dbh,
              bgb_calc.allometric_coeff_b,
              bgb_calc.r_coeff,
              bgb_calc.agb_species,
              bgb_calc.bgb_species,
              bgb_calc.agb_species * 0.47 * 44::numeric / 12::numeric AS co2eq_captured,
              bgb_calc.bgb_species * 0.47 * 44::numeric / 12::numeric AS co2eq_subt
            FROM bgb_calc
          )
  SELECT co2_calc.species_id,
      co2_calc.common_name,
      co2_calc.allometric_coeff_a,
      co2_calc.avg_dbh,
      co2_calc.allometric_coeff_b,
      co2_calc.r_coeff,
      co2_calc.agb_species,
      co2_calc.bgb_species,
      co2_calc.co2eq_captured,
      co2_calc.co2eq_subt
    FROM co2_calc;

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
          FROM public."Species"
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

  CREATE OR REPLACE PROCEDURE parcels_agbs_calculations_materialized()
  LANGUAGE plpgsql
  AS $$
  DECLARE 
      project_row RECORD;
      project_id_sanitized TEXT;
      sql_stmt TEXT;
      index_stmt TEXT;
      view_exists BOOLEAN;
      index_exists BOOLEAN;
  BEGIN
      FOR project_row IN (SELECT DISTINCT "id" FROM "Project") LOOP
          -- Sanitize UUID: Remove hyphens and truncate to 20 characters
          project_id_sanitized := left(replace(project_row."id"::TEXT, '-', ''), 20);
          
          -- Check if the materialized view already exists
          SELECT EXISTS (
              SELECT 1 FROM pg_matviews WHERE matviewname = 'parcels_agbs_project_' || project_id_sanitized
          ) INTO view_exists;

          -- If the materialized view does not exist, create it
          IF NOT view_exists THEN
              sql_stmt := 'CREATE MATERIALIZED VIEW parcels_agbs_project_' || project_id_sanitized || ' AS
                  WITH base_values AS (
                      SELECT p.id AS parcel_id,
                            p.name AS parcel_name,
                            e.type AS ecosystem,
                            sc.common_name AS species,
                            p.area,
                            p.area_factor * p.area AS individuals,
                            ((s."values" -> ''r_coeff'') ->> ''value'')::numeric AS r_coeff,
                            sc.agb_species,
                            p.area::numeric * (((e."values" -> ''SOC'') ->> ''value'')::numeric) AS parcel_soc_total
                      FROM public."Parcels" p
                      LEFT JOIN "Species" s ON p."speciesId" = s.id
                      LEFT JOIN species_calculation sc ON s.id = sc.species_id
                      LEFT JOIN "Ecosystem" e ON p."ecosystemId" = e.id
                      LEFT JOIN "Project" pr ON pr.id = p."projectId"
                      WHERE p."projectId" = ''' || project_row."id" || '''
                  ), parcel_agb_calc AS (
                      SELECT *, (base_values.individuals)::numeric * base_values.agb_species / 1000::numeric AS parcel_agb
                      FROM base_values
                  ), parcel_bgb_calc AS (
                      SELECT *, parcel_agb * r_coeff AS parcel_bgb
                      FROM parcel_agb_calc
                  ), parcel_co2_calcs AS (
                      SELECT *, parcel_agb * 0.47 * 44::numeric / 12::numeric AS parcel_co2eq_captured,
                                parcel_bgb * 0.47 * 44::numeric / 12::numeric AS parcel_co2eq_subt
                      FROM parcel_bgb_calc
                  ), parcel_co2_total AS (
                      SELECT *, (parcel_co2eq_captured + parcel_co2eq_subt) * 1000::numeric AS parcel_co2eq_total,
                                parcel_co2eq_captured + parcel_co2eq_subt + parcel_soc_total AS parcel_total_carbon
                      FROM parcel_co2_calcs
                  ), parcel_carbon_total AS (
                      SELECT *, parcel_total_carbon - parcel_soc_total AS parcel_co2_additional
                      FROM parcel_co2_total
                  )
                  SELECT parcel_id,
                        parcel_name,
                        ecosystem,
                        species,
                        area,
                        individuals,
                        parcel_agb,
                        parcel_bgb,
                        parcel_co2eq_captured,
                        parcel_co2eq_subt,
                        parcel_co2eq_total,
                        parcel_soc_total,
                        parcel_total_carbon,
                        parcel_co2_additional 
                  FROM parcel_carbon_total;';

              -- Execute creation
              EXECUTE sql_stmt;
          ELSE
              -- If the view exists, refresh it instead of creating a new one
              EXECUTE 'REFRESH MATERIALIZED VIEW parcels_agbs_project_' || project_id_sanitized;
          END IF;

          -- Check if index exists
          SELECT EXISTS (
              SELECT 1 FROM pg_indexes WHERE indexname = 'idx_parcels_agbs_project_' || project_id_sanitized
          ) INTO index_exists;

          -- If index does not exist, create it
          IF NOT index_exists THEN
              index_stmt := 'CREATE INDEX idx_parcels_agbs_project_' || project_id_sanitized ||
                            ' ON parcels_agbs_project_' || project_id_sanitized || ' (parcel_id);';
              EXECUTE index_stmt;
          END IF;
      END LOOP;
  END $$;

  CREATE OR REPLACE PROCEDURE parcels_co2eq_materialized()
  LANGUAGE plpgsql
  AS $$ 
  DECLARE 
      project_row RECORD;
      project_id_sanitized TEXT;
      sql_stmt TEXT;
      index_stmt TEXT;
      view_exists BOOLEAN;
      index_exists BOOLEAN;
  BEGIN
      FOR project_row IN (SELECT DISTINCT "id" FROM public."Project") LOOP
          -- Sanitize UUID: Remove hyphens and truncate to 20 characters
          project_id_sanitized := left(replace(project_row."id"::TEXT, '-', ''), 20);

          -- Check if the materialized view already exists
          SELECT EXISTS (
              SELECT 1 FROM pg_matviews WHERE matviewname = 'parcels_co2eq_project_' || project_id_sanitized
          ) INTO view_exists;

          -- If the materialized view does not exist, create it
          IF NOT view_exists THEN
              sql_stmt := 'CREATE MATERIALIZED VIEW parcels_co2eq_project_' || project_id_sanitized || ' AS
                  SELECT 
                      p.parcel_id,
                      p.parcel_name,
                      p.ecosystem,
                      p.species,
                      g.year,
                      (p.individuals * g.delta_co2) / 1000 AS co2eq_ton
                  FROM 
                      parcels_agbs_project_' || project_id_sanitized || ' p
                  CROSS JOIN 
                      LATERAL generate_species_data(STRING_TO_ARRAY(p.species, '', ''), 20) g'; 
              
              EXECUTE sql_stmt;
          ELSE
              -- If the view exists, refresh it instead of creating a new one
              EXECUTE 'REFRESH MATERIALIZED VIEW parcels_co2eq_project_' || project_id_sanitized;
          END IF;

          -- Check if index exists
          SELECT EXISTS (
              SELECT 1 FROM pg_indexes WHERE indexname = 'idx_parcels_co2eq_project_' || project_id_sanitized
          ) INTO index_exists;

          -- If index does not exist, create it
          IF NOT index_exists THEN
              index_stmt := 'CREATE INDEX idx_parcels_co2eq_project_' || project_id_sanitized ||
                            ' ON parcels_co2eq_project_' || project_id_sanitized || ' (parcel_id);';
              EXECUTE index_stmt;
          END IF;
      END LOOP;
  END $$;

  CREATE OR REPLACE FUNCTION sum_all_parcels_agbs_totals()
  RETURNS TABLE (grand_total_co2 NUMERIC, grand_total_area NUMERIC) 
  LANGUAGE plpgsql
  AS $$
  DECLARE 
      project_row RECORD;
      project_id_sanitized TEXT;
      union_query TEXT := '';
      first_table BOOLEAN := true;
  BEGIN
      FOR project_row IN (SELECT DISTINCT "id" FROM public."Project") LOOP
          project_id_sanitized := left(replace(project_row."id"::TEXT, '-', ''), 20);
          
          IF NOT first_table THEN
              union_query := union_query || ' UNION ALL ';
          END IF;
          
          union_query := union_query || 
              format('SELECT SUM(parcel_co2eq_total) as totalco2, SUM(area) as area FROM parcels_agbs_project_%s', 
                    project_id_sanitized);
          
          first_table := false;
      END LOOP;

      IF union_query <> '' THEN
          RETURN QUERY EXECUTE 
              'SELECT SUM(totalco2) as grand_total_co2, SUM(area) as grand_total_area FROM (' || 
              union_query || ') as combined_results';
      ELSE
          RETURN QUERY SELECT 0::NUMERIC, 0::NUMERIC;
      END IF;
  END;
  $$;

  CREATE OR REPLACE FUNCTION avg_all_parcels_co2eq_totals()
  RETURNS TABLE (sum_co2_total NUMERIC, average_co2_total NUMERIC)
  LANGUAGE plpgsql
  AS $$
  DECLARE 
      project_row RECORD;
      project_id_sanitized TEXT;
      union_query TEXT := '';
      first_table BOOLEAN := true;
  BEGIN
      -- Loop through all project IDs
      FOR project_row IN (SELECT DISTINCT "id" FROM public."Project") LOOP
          -- Sanitize UUID: Remove hyphens and truncate to 20 characters
          project_id_sanitized := left(replace(project_row."id"::TEXT, '-', ''), 20);

          -- Build UNION ALL query dynamically
          IF NOT first_table THEN
              union_query := union_query || ' UNION ALL ';
          END IF;

          union_query := union_query || 
              format('SELECT parcel_name, SUM(co2eq_ton) as co2Total, (SUM(co2eq_ton) / p.area) as co2TotalArea
                      FROM parcels_co2eq_project_%s as co2parcel
                      LEFT JOIN public."Parcels" as p ON co2parcel.parcel_id = p.id
                      GROUP BY parcel_name, area', 
                    project_id_sanitized);

          first_table := false;
      END LOOP;

      -- Wrap the UNION ALL in a query to compute the sum and average
      IF union_query <> '' THEN
          RETURN QUERY EXECUTE 
              'SELECT SUM(co2Total) as sum_co2_total, AVG(co2TotalArea) as average_co2_total 
              FROM (' || union_query || ') as combined_results';
      ELSE
          RETURN QUERY SELECT 0::NUMERIC AS sum_co2_total, 0::NUMERIC AS average_co2_total;
      END IF;
  END;
  $$;

  CREATE OR REPLACE FUNCTION generate_growth_project(
      project_id_param UUID,
      species_param VARCHAR,
      start_date_param DATE,
      end_date_param DATE,
      events_param JSON
  )
  RETURNS TABLE (
      period INT,
      population INTEGER,
      co2eq_tonnes NUMERIC,
      co2eq_accumulated NUMERIC  -- New column for accumulated CO2eq
  ) AS $$
  DECLARE
      initial_population NUMERIC;
      current_population NUMERIC;
      current_year INT;
      event_record JSON;
      harvest_percent NUMERIC;
      table_name TEXT;
      year_offset INT;
      total_years INT;
      co2eq_per_individual NUMERIC;
      cumulative_co2eq NUMERIC := 0;  -- Variable to track accumulated CO2eq
  BEGIN
      -- Sanitize UUID: Remove hyphens and truncate to 20 characters
      table_name := 'parcels_agbs_project_' || left(replace(project_id_param::TEXT, '-', ''), 20);

      -- Get initial population
      EXECUTE format('
          SELECT SUM(individuals)
          FROM %I
          WHERE species = $1', table_name)
      INTO initial_population
      USING species_param;

      -- If no initial population found, set to 0
      IF initial_population IS NULL THEN
          initial_population := 0;
      END IF;

      -- Calculate total years between start and end date
      total_years := EXTRACT(YEAR FROM end_date_param) - EXTRACT(YEAR FROM start_date_param);

      -- Call generate_species_data once to get CO2eq for all years
      CREATE TEMP TABLE temp_species_data AS
      SELECT year, co2eq
      FROM generate_species_data(ARRAY[species_param], total_years);

      current_population := initial_population;
      current_year := EXTRACT(YEAR FROM start_date_param);

      -- Loop through years from start to end
      WHILE current_year <= EXTRACT(YEAR FROM end_date_param) LOOP
          period := current_year;
          
          -- Check if there's a harvest event for this year
          harvest_percent := 0;
          FOR event_record IN SELECT * FROM json_array_elements(events_param)
          LOOP
              IF (event_record->>'year')::INT = current_year THEN
                  harvest_percent := (event_record->>'percentage')::NUMERIC / 100;
                  EXIT;
              END IF;
          END LOOP;

          -- Apply harvest if any
          IF harvest_percent > 0 THEN
              current_population := current_population * (1 - harvest_percent);
          END IF;

          -- Cast population to INTEGER to remove decimals
          population := current_population::INTEGER;

          -- Calculate year offset and get CO2eq from temp table
          year_offset := current_year - EXTRACT(YEAR FROM start_date_param);
          SELECT co2eq
          INTO co2eq_per_individual
          FROM temp_species_data
          WHERE temp_species_data.year = year_offset;

          -- If no CO2eq found (shouldn't happen), default to 0
          IF co2eq_per_individual IS NULL THEN
              co2eq_per_individual := 0;
          END IF;

          -- Calculate CO2eq in tonnes and round to 2 decimal places
          co2eq_tonnes := ROUND((co2eq_per_individual * current_population) / 1000, 2);

          -- Update accumulated CO2eq
          cumulative_co2eq := cumulative_co2eq + co2eq_tonnes;
          co2eq_accumulated := ROUND(cumulative_co2eq, 2);  -- Round to 2 decimal places

          RETURN NEXT;
          current_year := current_year + 1;
      END LOOP;

      -- Clean up temp table
      DROP TABLE temp_species_data;
  END;
  $$ LANGUAGE plpgsql;


        Only retrieval queries are allowed.

        EVERY QUERY SHOULD RETURN QUANTITATIVE DATA THAT CAN BE PLOTTED ON A CHART! 
        There should always be at least two columns. If the user asks for a single column, return the column and the count of the column. If the user asks for a rate, return the rate as a decimal. For example, 0.1 would be 10%.
        The tables need to be enclosed in quotes because they combine uppercase and lowercase letters, and it is better to prepend the word "public."`,
        prompt: `Generate the query necessary to retrieve the data the user wants: ${input}`,
        schema: z.object({
          query: z.string(),
        }),
    });
    return result.object.query;
  } catch (e: unknown) {
    console.error(e);
    throw new Error("An error occurred while generating the query");
  }
}

export const explainQuery = async (input: string, sqlQuery: string) => {
  "use server";
  try {
    const result = await generateObject({
      model: openai("gpt-4o"),
      schema: z.object({
        explanations: explanationsSchema,
      }),
      system: `You are a SQL (postgres) expert. Your job is to explain to the user write a SQL query you wrote to retrieve the data they asked for. The table schema is as follows:
    unicorns (
      id SERIAL PRIMARY KEY,
      company VARCHAR(255) NOT NULL UNIQUE,
      valuation DECIMAL(10, 2) NOT NULL,
      date_joined DATE,
      country VARCHAR(255) NOT NULL,
      city VARCHAR(255) NOT NULL,
      industry VARCHAR(255) NOT NULL,
      select_investors TEXT NOT NULL
    );

    When you explain you must take a section of the query, and then explain it. Each "section" should be unique. So in a query like: "SELECT * FROM unicorns limit 20", the sections could be "SELECT *", "FROM UNICORNS", "LIMIT 20".
    If a section doesnt have any explanation, include it, but leave the explanation empty.

    `,
      prompt: `Explain the SQL query you generated to retrieve the data the user wanted. Assume the user is not an expert in SQL. Break down the query into steps. Be concise.

      User Query:
      ${input}

      Generated SQL Query:
      ${sqlQuery}`,
    });
    return result.object;
  } catch (e) {
    console.error(e);
    throw new Error("Failed to generate query");
  }
};

export const generateChartConfig = async (
  results: Result[],
  userQuery: string,
) => {
  "use server";
  const system = `You are a data visualization expert. `;

  try {
    const { object: config } = await generateObject({
      model: openai("gpt-4o"),
      system,
      prompt: `Given the following data from a SQL query result, generate the chart config that best visualises the data and answers the users query.
      For multiple groups use multi-lines.

      Here is an example complete config:
      export const chartConfig = {
        type: "pie",
        xKey: "month",
        yKeys: ["sales", "profit", "expenses"],
        colors: {
          sales: "#4CAF50",    // Green for sales
          profit: "#2196F3",   // Blue for profit
          expenses: "#F44336"  // Red for expenses
        },
        legend: true
      }

      User Query:
      ${userQuery}

      Data:
      ${JSON.stringify(results, null, 2)}`,
      schema: configSchema,
    });

    const colors: Record<string, string> = {};
    config.yKeys.forEach((key, index) => {
      colors[key] = `hsl(var(--chart-${index + 1}))`;
    });

    const updatedConfig: Config = { ...config, colors };
    return { config: updatedConfig };
  } catch (e) {
    // @ts-expect-error: Property 'message' does not exist on type 'unknown'
    console.error(e.message);
    throw new Error("Failed to generate chart suggestion");
  }
};

export async function getProjects(): Promise<Growth[]> {
  try {
    const projectsData = await prisma.project.findMany();

    return projectsData.map(project => {
      // Define default values structure
      const defaultValues = {
        total_investment: { value: 0 },
        impact: { value: 0 },
        bankable_investment: { value: 0 },
        income: { value: 0 },
        tree_quantity: { value: 0 },
        lands: { value: 0 },
        abstract: { value: '' },
        polygone: { value: '' },
        geolocation_point: { value: '' },
        investment_teaser: { value: '' },
        token_granularity: { value: 0 },
      };

      // Parse and merge the values from the database with defaults
      const projectValues = project.values ? 
        (typeof project.values === 'string' ? 
          JSON.parse(project.values) : project.values) : {};
      
      // Transform to Growth type
      return {
        id: project.id,
        name: project.name,
        title: project.title,
        description: project.description,
        country: project.country,
        status: String(project.status), // Convert enum to string
        department: project.department,
        // Merge default values with actual values
        values: {
          ...defaultValues,
          ...Object.entries(projectValues).reduce((acc, [key, value]) => {
            // Check if the value is an object with a 'value' property
            if (value && typeof value === 'object' && 'value' in value) {
              acc[key] = value;
            } 
            // If it's just a value, wrap it in the expected structure
            else if (value !== undefined && value !== null) {
              acc[key] = { value };
            }
            return acc;
          }, {} as Record<string, { value: unknown }>)
        },
        // Convert string dates to Date objects
        createdAt: new Date(project.createdAt || new Date()),
        updatedAt: new Date(project.updatedAt || new Date()),
      } as Growth;
    });
  } catch (error) {
    console.error("Error fetching projects:", error);
    throw new Error("Failed to fetch projects");
  }
}