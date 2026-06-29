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
SELECT DISTINCT CAST(county_id AS varchar)
FROM us_counties
INTERSECT 
SELECT DISTINCT CAST(county_id AS varchar)
FROM air_quality
INTERSECT 
SELECT DISTINCT CAST(county_id AS varchar)
FROM business_patterns
INTERSECT 
SELECT DISTINCT CAST(county_id AS varchar)
FROM population
INTERSECT 
SELECT DISTINCT CAST(county_id AS varchar)
FROM gdp
INTERSECT
SELECT DISTINCT CAST(county_id AS varchar)
FROM personal_income
INTERSECT
SELECT DISTINCT CAST(county_id AS varchar)
FROM res_construction_permits
INTERSECT
SELECT DISTINCT CAST(county_id AS varchar)
FROM unemployment;


-- return counties which do not appear in all datasets
SELECT DISTINCT 
    county_id,
    county_name,
    state
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









