-- author: Logan Rosell

-- clear tables with old names if needed
DROP TABLE IF EXISTS county_population;
drop table if exists county_gdp;

-- Check for duplicates in composite keys across all db tables
SELECT
  year,
  county_id,
  COUNT(*) AS dup_count
FROM air_quality
GROUP BY year, county_id
HAVING COUNT(*) > 1;

SELECT
  year,
  county_id,
  naics_industry_code,
  COUNT(*) AS dup_count
FROM business_patterns
GROUP BY year, county_id, naics_industry_code
HAVING COUNT(*) > 1;

SELECT
  year,
  county_id,
  COUNT(*) AS dup_count
FROM gdp
GROUP BY year, county_id
HAVING COUNT(*) > 1;

SELECT
  year,
  county_id,
  COUNT(*) AS dup_count
FROM personal_income
GROUP BY year, county_id
HAVING COUNT(*) > 1;

SELECT
  year,
  county_id,
  COUNT(*) AS dup_count
FROM population
GROUP BY year, county_id
HAVING COUNT(*) > 1;

SELECT
  year,
  county_id,
  COUNT(*) AS dup_count
FROM res_construction_permits
GROUP BY year, county_id
HAVING COUNT(*) > 1;

SELECT
  year,
  county_id,
  COUNT(*) AS dup_count
FROM unemployment
GROUP BY year, county_id
HAVING COUNT(*) > 1;

SELECT
  county_id,
  COUNT(*) AS dup_count
FROM us_counties
GROUP BY county_id
HAVING COUNT(*) > 1;

SELECT
  data_center_id,
  COUNT(*) AS dup_count
FROM data_centers
GROUP BY data_center_id
HAVING COUNT(*) > 1;

--========================================
-- Check for records present in one table but not another

SELECT
  c.county_id
FROM us_counties AS c
LEFT JOIN air_quality AS a
ON c.county_id = a.county_id
WHERE a.county_id IS NULL;

SELECT *
FROM us_counties
WHERE county_id = '02013';

-- return number of unique counties in each dataset
SELECT 
    (SELECT COUNT(*) FROM us_counties) AS total_us_counties,
    (SELECT COUNT(DISTINCT county_id) FROM air_quality) AS air_quality_counties,
    (SELECT COUNT(DISTINCT county_id) FROM business_patterns) AS business_counties,
    (SELECT COUNT(DISTINCT county_id) FROM population) AS population_counties,
    (SELECT COUNT(DISTINCT county_id) FROM data_centers) AS data_center_counties,
    (SELECT COUNT(DISTINCT county_id) FROM gdp) AS gdp_counties,
    (SELECT COUNT(DISTINCT county_id) FROM personal_income) AS income_counties,
    (SELECT COUNT(DISTINCT county_id) FROM res_construction_permits) AS permit_counties,
    (SELECT COUNT(DISTINCT county_id) FROM unemployment) AS unemployment_counties;


-- return only counties found in all tables except for the data_centers table
SELECT DISTINCT 
    county_id,
    county_name,
    state,
    functional_status,
    fips_class_code
FROM us_counties
WHERE county_id IN (
    SELECT DISTINCT CAST(county_id AS varchar) FROM us_counties
    INTERSECT
    (
      SELECT DISTINCT CAST(county_id AS varchar) FROM us_counties
      INTERSECT 
      SELECT DISTINCT CAST(county_id AS varchar) FROM air_quality
      INTERSECT 
      SELECT DISTINCT CAST(county_id AS varchar) FROM business_patterns
      INTERSECT 
      SELECT DISTINCT CAST(county_id AS varchar) FROM population
      INTERSECT 
      SELECT DISTINCT CAST(county_id AS varchar) FROM gdp
      INTERSECT
      SELECT DISTINCT CAST(county_id AS varchar) FROM personal_income
      INTERSECT
      SELECT DISTINCT CAST(county_id AS varchar) FROM res_construction_permits
      INTERSECT
      SELECT DISTINCT CAST(county_id AS varchar) FROM unemployment
    )
);


-- return counties which do not appear in all datasets
SELECT DISTINCT 
    county_id,
    county_name,
    state,
    functional_status,
    fips_class_code
FROM us_counties
WHERE county_id IN (
    SELECT DISTINCT CAST(county_id AS varchar) FROM us_counties
    EXCEPT
    (
      SELECT DISTINCT CAST(county_id AS varchar) FROM us_counties
      INTERSECT 
      SELECT DISTINCT CAST(county_id AS varchar) FROM air_quality
      INTERSECT 
      SELECT DISTINCT CAST(county_id AS varchar) FROM business_patterns
      INTERSECT 
      SELECT DISTINCT CAST(county_id AS varchar) FROM population
      INTERSECT 
      SELECT DISTINCT CAST(county_id AS varchar) FROM gdp
      INTERSECT
      SELECT DISTINCT CAST(county_id AS varchar) FROM personal_income
      INTERSECT
      SELECT DISTINCT CAST(county_id AS varchar) FROM res_construction_permits
      INTERSECT
      SELECT DISTINCT CAST(county_id AS varchar) FROM unemployment
    )
);


-- For each county which is not present in all tables, show which specific tables it is missing from
WITH county_presence AS (
    SELECT 
        c.county_id,
        c.county_name,
        c.state,
        c.functional_status,
        c.fips_class_code,
        -- Check presence in each table (1 if exists, 0 if missing)
        CASE WHEN aq.county_id IS NOT NULL THEN 1 ELSE 0 END AS in_air_quality,
        CASE WHEN bp.county_id IS NOT NULL THEN 1 ELSE 0 END AS in_business_patterns,
        CASE WHEN p.county_id  IS NOT NULL THEN 1 ELSE 0 END AS in_population,
        CASE WHEN g.county_id  IS NOT NULL THEN 1 ELSE 0 END AS in_gdp,
        CASE WHEN pi.county_id IS NOT NULL THEN 1 ELSE 0 END AS in_personal_income,
        CASE WHEN rcp.county_id IS NOT NULL THEN 1 ELSE 0 END AS in_res_construction_permits,
        CASE WHEN u.county_id  IS NOT NULL THEN 1 ELSE 0 END AS in_unemployment
    FROM us_counties c
    LEFT JOIN (SELECT DISTINCT CAST(county_id AS varchar) AS county_id FROM air_quality) aq 
        ON CAST(c.county_id AS varchar) = aq.county_id
    LEFT JOIN (SELECT DISTINCT CAST(county_id AS varchar) AS county_id FROM business_patterns) bp 
        ON CAST(c.county_id AS varchar) = bp.county_id
    LEFT JOIN (SELECT DISTINCT CAST(county_id AS varchar) AS county_id FROM population) p 
        ON CAST(c.county_id AS varchar) = p.county_id
    LEFT JOIN (SELECT DISTINCT CAST(county_id AS varchar) AS county_id FROM gdp) g 
        ON CAST(c.county_id AS varchar) = g.county_id
    LEFT JOIN (SELECT DISTINCT CAST(county_id AS varchar) AS county_id FROM personal_income) pi 
        ON CAST(c.county_id AS varchar) = pi.county_id
    LEFT JOIN (SELECT DISTINCT CAST(county_id AS varchar) AS county_id FROM res_construction_permits) rcp 
        ON CAST(c.county_id AS varchar) = rcp.county_id
    LEFT JOIN (SELECT DISTINCT CAST(county_id AS varchar) AS county_id FROM unemployment) u 
        ON CAST(c.county_id AS varchar) = u.county_id
),
scored_presence AS (
    SELECT 
        *,
        -- Sum the individual flags to get the total row score
        (in_air_quality + 
         in_business_patterns + 
         in_population + 
         in_gdp + 
         in_personal_income + 
         in_res_construction_permits + 
         in_unemployment) AS total_tables_present
    FROM county_presence
)
SELECT *
FROM scored_presence
WHERE total_tables_present < 7
ORDER BY total_tables_present ASC, state, county_name;







-- ================================================
-- Check range of years covered by each table

SELECT 
  (SELECT MAX(year) FROM air_quality) AS air_quality_max_year,
  (SELECT MIN(year) FROM air_quality) AS air_quality_min_year,
  (SELECT MAX(year) FROM business_patterns) AS business_patterns_max_year,
  (SELECT MIN(year) FROM business_patterns) AS business_patterns_min_year,
  (SELECT MAX(year) FROM population) AS population_max_year,
  (SELECT MIN(year) FROM population) AS population_min_year,
  (SELECT MAX(year) FROM gdp) AS gdp_max_year,
  (SELECT MIN(year) FROM gdp) AS gdp_min_year,
  (SELECT MAX(year) FROM personal_income) AS personal_income_max_year,
  (SELECT MIN(year) FROM personal_income) AS personal_income_min_year,
  (SELECT MAX(year) FROM res_construction_permits) AS res_construction_permits_max_year,
  (SELECT MIN(year) FROM res_construction_permits) AS res_construction_permits_min_year,
  (SELECT MAX(year) FROM unemployment) AS unemployment_max_year,
  (SELECT MIN(year) FROM unemployment) AS unemployment_min_year;


-- ================================================

-- Check for county_ids which appear in air_quality but not in us_counties table
SELECT DISTINCT 
    county_id
FROM air_quality
WHERE county_id IN (
    SELECT DISTINCT CAST(county_id AS varchar) FROM air_quality
    EXCEPT
    (
      SELECT DISTINCT CAST(county_id AS varchar) FROM us_counties
    )
);

-- Check for county_ids which appear in business_patterns but not in us_counties table
SELECT DISTINCT 
    county_id
FROM business_patterns
WHERE county_id IN (
    SELECT DISTINCT CAST(county_id AS varchar) FROM business_patterns
    EXCEPT
    (
      SELECT DISTINCT CAST(county_id AS varchar) FROM us_counties
    )
);


-- Check for county_ids which appear in data_centers but not in us_counties table
SELECT DISTINCT 
    county_id
FROM data_centers
WHERE county_id IN (
    SELECT DISTINCT CAST(county_id AS varchar) FROM data_centers
    EXCEPT
    (
      SELECT DISTINCT CAST(county_id AS varchar) FROM us_counties
    )
);



-- Check for county_ids which appear in gdp but not in us_counties table
SELECT DISTINCT 
    county_id
FROM gdp
WHERE county_id IN (
    SELECT DISTINCT CAST(county_id AS varchar) FROM gdp
    EXCEPT
    (
      SELECT DISTINCT CAST(county_id AS varchar) FROM us_counties
    )
);

-- Check for county_ids which appear in personal_income but not in us_counties table
SELECT DISTINCT 
    county_id
FROM personal_income
WHERE county_id IN (
    SELECT DISTINCT CAST(county_id AS varchar) FROM personal_income
    EXCEPT
    (
      SELECT DISTINCT CAST(county_id AS varchar) FROM us_counties
    )
);

-- Check for county_ids which appear in population but not in us_counties table
SELECT DISTINCT 
    county_id
FROM population
WHERE county_id IN (
    SELECT DISTINCT CAST(county_id AS varchar) FROM population
    EXCEPT
    (
      SELECT DISTINCT CAST(county_id AS varchar) FROM us_counties
    )
);

-- Check for county_ids which appear in res_construction_permits but not in us_counties table
SELECT DISTINCT 
    county_id
FROM res_construction_permits
WHERE county_id IN (
    SELECT DISTINCT CAST(county_id AS varchar) FROM res_construction_permits
    EXCEPT
    (
      SELECT DISTINCT CAST(county_id AS varchar) FROM us_counties
    )
);

-- Check for county_ids which appear in unemployment but not in us_counties table
SELECT DISTINCT 
    county_id
FROM unemployment
WHERE county_id IN (
    SELECT DISTINCT CAST(county_id AS varchar) FROM unemployment
    EXCEPT
    (
      SELECT DISTINCT CAST(county_id AS varchar) FROM us_counties
    )
);