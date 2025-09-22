CREATE OR REPLACE VIEW total_impact AS
 SELECT sum((("Project"."values" -> 'impact'::text) ->> 'value'::text)::integer) AS total_impact
   FROM "Project"
  WHERE (("Project"."values" -> 'impact'::text) ->> 'value'::text) IS NOT NULL;
  
CREATE OR REPLACE VIEW total_investment AS
 SELECT sum((("Project"."values" -> 'total_investment'::text) ->> 'value'::text)::integer) AS total_investment
   FROM "Project"
  WHERE (("Project"."values" -> 'total_investment'::text) ->> 'value'::text) IS NOT NULL;

CREATE OR REPLACE VIEW total_bankable_investment AS
 SELECT sum((("Project"."values" -> 'bankable_investment'::text) ->> 'value'::text)::integer) AS total_bankable_investment
   FROM "Project"
  WHERE (("Project"."values" -> 'bankable_investment'::text) ->> 'value'::text) IS NOT NULL;
  
CREATE OR REPLACE VIEW total_income AS
 SELECT sum((("Project"."values" -> 'income'::text) ->> 'value'::text)::integer) AS total_income
   FROM "Project"
  WHERE (("Project"."values" -> 'income'::text) ->> 'value'::text) IS NOT NULL;

CREATE OR REPLACE VIEW species_calculation AS
  WITH base_values AS (
         SELECT s.id AS species_id,
            s.common_name,
            ((s."values" -> 'allometric_coeff_a'::text) ->> 'value'::text)::numeric AS allometric_coeff_a,
            ((s."values" -> 'avg_dbh'::text) ->> 'value'::text)::numeric AS avg_dbh,
            ((s."values" -> 'allometric_coeff_b'::text) ->> 'value'::text)::numeric AS allometric_coeff_b,
            ((s."values" -> 'r_coeff'::text) ->> 'value'::text)::numeric AS r_coeff
           FROM "Species" s
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

CREATE OR REPLACE VIEW parcels_agbs_calculations AS
 WITH base_values AS (
         SELECT p.id AS parcel_id,
            p.name AS parcel_name,
            p."projectId" AS projectid,
		 	   pr.name AS project,
            e.type AS ecosystem,
            sc.common_name AS species,
            p.area,
            p.area_factor * p.area AS individuals,
            ((s."values" -> 'r_coeff'::text) ->> 'value'::text)::numeric AS r_coeff,
            sc.agb_species,
            p.area::numeric * (((e."values" -> 'SOC'::text) ->> 'value'::text)::numeric) AS parcel_soc_total
           FROM "Parcels" p
             LEFT JOIN "Species" s ON p."speciesId" = s.id
             LEFT JOIN species_calculation sc ON s.id = sc.species_id
             LEFT JOIN "Ecosystem" e ON p."ecosystemId" = e.id
			 LEFT JOIN "Project" pr ON pr.id = p."projectId"
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
    projectid,
    project,
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
    FROM parcel_carbon_total;