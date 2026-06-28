-- author: Logan Rosell

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

drop table if exists county_gdp;

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