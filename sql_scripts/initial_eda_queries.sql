-- Make a sql table for scatterplot 
-- granularity: one dot per county averaged across all years (for cross-year variables)
-- variables: 
--- x = per_capita_personal_income_dollars (from personal_income table)
--- y = data_centers (not at the year level, from data_centers table)
--- dot size = population (from population table)

WITH population_data AS (
  SELECT county_id,
    ROUND(AVG(population), 0) AS avg_population
  FROM county_population
  WHERE year >= 2001 AND year <= 2022
  GROUP BY county_id
),
income_data AS (
  SELECT ltrim(county_id, ' ') as county_id,
    ROUND(AVG(per_capita_personal_income_dollars), 0) AS avg_personal_income
  FROM personal_income
  WHERE year >= 2001 AND year <= 2022
  GROUP BY county_id
),
data_centers_per_county AS (
  SELECT county_id,
    COUNT(data_center_id) AS data_center_count
  FROM data_centers
  GROUP BY county_id
)
SELECT
  uc.combined_state_county_code,
  COALESCE(dcpc.data_center_count, 0) AS data_center_count,
  inc.avg_personal_income,
  pd.avg_population
FROM us_counties uc
LEFT JOIN data_centers_per_county dcpc
  ON uc.combined_state_county_code = dcpc.county_id
LEFT JOIN income_data inc
  ON uc.combined_state_county_code = inc.county_id
LEFT JOIN population_data pd
  ON uc.combined_state_county_code = pd.county_id
WHERE inc.avg_personal_income IS NOT NULL AND pd.avg_population IS NOT NULL;


-- Make a sql table for lineplot 
-- granularity: year (collapse across counties)
-- variables: 
--- real_gdp_2017_dollars_thousands (from gdp table) AS Real GDP
--- unemployment_rate (from unemployment table) AS Unemployment Rate
--- pm25_mean_daily_avg (from air_quality table) AS Average Air Quality (PM25)

WITH gdp_yearly AS (
    SELECT
        year,
        AVG(real_gdp_2017_dollars_thousands) AS real_gdp
    FROM gdp
    GROUP BY year
),
unemployment_yearly AS (
    SELECT
        year,
        AVG(unemployment_rate) AS unemployment_rate
    FROM unemployment
    GROUP BY year
),
air_quality_yearly AS (
    SELECT
        year,
        AVG(pm25_mean_daily_avg) AS average_air_quality_pm25
    FROM air_quality
    GROUP BY year
)
SELECT
    g.year,
    g.real_gdp,
    u.unemployment_rate,
    a.average_air_quality_pm25
FROM gdp_yearly g
LEFT JOIN unemployment_yearly u
    ON g.year = u.year
LEFT JOIN air_quality_yearly a
    ON g.year = a.year
WHERE g.year BETWEEN 2001 AND 2022 
ORDER BY g.year;
