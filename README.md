# The Local Economic Impact of Data Centers

**Authors:** Logan Rosell & Ian Walsh  
**Affiliation:** Willamette University — Master of Science in Data Science (MSDS) Capstone  
**Companion Research Repository:** [github.com/LoganRosell/local-economic-impacts-of-data-centers](https://github.com/LoganRosell/local-economic-impacts-of-data-centers)  
**Project Writeup & Presentation Website:** [wu-msds-capstones.github.io/The-Local-Economic-Impact-of-Data-Centers](https://wu-msds-capstones.github.io/The-Local-Economic-Impact-of-Data-Centers/)  

---

## Project Overview

This repository contains the complete data engineering pipeline, database architecture, exploratory analysis, and econometric/machine learning modeling code for our capstone research project, **"The Local Economic Impact of Data Centers."**

While our final research report, findings, and interactive visual narratives are published on our [Project Website](https://wu-msds-capstones.github.io/The-Local-Economic-Impact-of-Data-Centers/) and companion [Results Repository](https://github.com/LoganRosell/local-economic-impacts-of-data-centers), this workbook is dedicated to **methodological transparency and full reproducibility**. It provides researchers and practitioners with the tools to rebuild the dataset from raw federal sources and run the analytical models locally.

### Research Scope & Methodology
- **Industry Proxy:** We proxy data center establishments using NAICS Code 518 (*Computing Infrastructure, Data Processing, Web Hosting, and Related Services*) from U.S. Census Bureau County Business Patterns.
- **Geographic & Temporal Panel:** Spanning contiguous U.S. counties from 2001 to 2022.
- **Outcomes Analyzed:** Real GDP per capita, personal income per capita, unemployment rates, residential construction permit activity (single- and multi-family), and fine particulate air pollution ($PM_{2.5}$).
- **Predictive Modeling:** Identifying county-level demographic, economic, and geographic features predictive of data center locations using Logistic Regression, Balanced Random Forests (SMOTE), and PyTorch Neural Networks.
- **Causal Econometrics:** Employing staggered Difference-in-Differences (Callaway & Sant'Anna) and Two-Way Fixed Effects (TWFE) models to estimate treatment effects across distinct Urban vs. Rural county clusters identified via K-Means and Principal Component Analysis (PCA).

---

## Installation and Setup

### 1. Prerequisites
- **Python:** Python 3.12+ recommended (tested on Python 3.12.8).
- **PostgreSQL:** A local PostgreSQL instance (the database can have any name, configured via your `.env` file).
- **Quarto CLI:** [Quarto](https://quarto.org/) is recommended for executing and rendering `.qmd` pipeline notebooks.

### 2. Clone the Repository & Install Dependencies
Clone this repository and install all required Python packages:

```bash
git clone https://github.com/LoganRosell/local-economic-impact-of-data-centers-workbook.git
cd local-economic-impact-of-data-centers-workbook
pip install -r requirements.txt
```

> **Note on Custom Utilities (`utils/`):**  
> `requirements.txt` includes `-e .` (editable local package installation). This registers the project root so that custom modules located in `utils/` (such as `utils.db_cleaning_utils`, `utils.ml_modeling_utils`, and `utils.map_utils`) can be seamlessly imported across all subdirectories, scripts, and Quarto notebooks without path manipulation.

### 3. Environment Configuration (`.env`)
Create a `.env` file in the root directory of this repository to configure your local data path and database connections. The file must define the following three variables:

```env
# Path to the shared_data folder within this repository
DATA_DIR=/path/to/project-workbook-ian_and_logan/shared_data

# Connection string to your local PostgreSQL database
DATABASE_URL=postgresql://<username>:<password>@localhost:5432/<your_database_name>

# DuckDB PostgreSQL attachment string (typically identical to DATABASE_URL)
DUCKDB_DB_URL=postgresql://<username>:<password>@localhost:5432/<your_database_name>
```

---

## Data

Raw source data files are not tracked in this repository due to size constraints. You can acquire the source data in one of two ways:

1. **Automated Download:**  
   Run `download_source_data.qmd` from the project root. This notebook will fetch and stage the required data sources.  
   > *Note:* Automated downloads rely on public government and institutional endpoints that may shift or expire over time. If any download link fails, use the manual download sources below.

2. **Manual Download & Directory Structure:**  
   If downloading files manually, organize them into the following folder structure within `shared_data/`:

```text
shared_data/
├── air/
│   └── Daily_County-Level_PM2.5_Concentrations_2001-2022_20260611.csv
├── business_patterns/
│   └── cbp01co.txt through cbp22co.txt
├── construction_permits/
│   └── Residential_Construction_Permits_by_County_6297027898887955680.csv
├── county_fips_codes/
│   ├── county_2020_fips_codes.csv
│   ├── geojson_counties_fips.json
│   └── US_Counties_Centroids.csv
├── gdp/
│   └── gdp_data.csv
├── personal_income/
│   └── personal_income_data.csv
├── population/
│   └── us.1990_2024.20ages.adjusted.txt
├── qrtly_census_emp_and_wages/
│   └── [Quarterly QCEW single-file CSVs 2002–2022]
└── unemployment_and_income/
    └── Unemployment2023.csv
```

### Data Sources Reference

| Domain / Dataset | Provider | Description & Source Link |
|---|---|---|
| **Air Quality ($PM_{2.5}$)** | CDC WONDER / EPA | [Daily County-Level $PM_{2.5}$ Concentrations (2001–2022)](https://data.cdc.gov/Environmental-Health-Toxicology/Daily-County-Level-PM2-5-Concentrations-2001-2022/53mz-4zqd/about_data) |
| **Business Patterns** | U.S. Census Bureau | [County Business Patterns (CBP) 2001–2022](https://www.census.gov/programs-surveys/cbp.html) (2-digit NAICS & NAICS 518) |
| **Employment & Wages** | Bureau of Labor Statistics (BLS) | [Quarterly Census of Employment and Wages (QCEW) 2002–2022](https://www.bls.gov/cew/downloadable-data-files.htm) |
| **County FIPS & Centroids** | U.S. Census Bureau / CA GIS | [Census ANSI County FIPS](https://www.census.gov/library/reference/code-lists/ansi.html#cou), [County Centroids GIS](https://gis.data.chhs.ca.gov/datasets/7495f87cfe1040468238b5b73042da9f/explore?layer=1&location=45.164011%2C-122.593435%2C3), [GeoJSON FIPS](https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json) |
| **County Land & Water Area** | U.S. Census Bureau | [Census Gazetteer County Files](https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html) |
| **County GDP** | Bureau of Economic Analysis (BEA) | [Gross Domestic Product by County](https://www.bea.gov/data/gdp/gdp-by-county) (Real chained 2017 dollars) |
| **Personal Income** | Bureau of Economic Analysis (BEA) | [Local Area Personal Income by County](https://www.bea.gov/data/income-saving/personal-income-by-county) |
| **County Population** | NCI SEER | [U.S. County Population Data (1990–2024)](https://seer.cancer.gov/popdata.thru.2023/download.html) |
| **Building Permits** | U.S. Census Bureau / HUD | [Residential Construction Permits by County](https://catalog.data.gov/dataset/residential-construction-permits-by-county) |
| **Unemployment** | USDA ERS / BLS | [County-Level Unemployment & Labor Force](https://www.ers.usda.gov/data-products/county-level-data-sets/county-level-data-sets-download-data) |
| **Industry Classifications** | U.S. Census Bureau | [2022 NAICS Definitions](https://www.census.gov/naics/?58967?yearbck=2022) |

---

### Data Processing & Pipeline

Data cleaning, harmonization, and database building are orchestrated end-to-end:

1. **Automated Database Building (`db_builder_script.qmd`):**  
   Executing `cleaning_scripts/db_builder/db_builder_script.qmd` renders all cleaning scripts sequentially and populates your configured PostgreSQL database under the `transformed` schema.
2. **FIPS Harmonization & Administrative Changes:**  
   Standardizes 5-digit county FIPS codes across the 2001–2022 panel, filtering out incompatible re-codings (such as Connecticut's post-2022 transition from counties to planning regions) to preserve longitudinal panel integrity.
3. **Spatial Feature Engineering:**  
   Calculates Haversine distances between county centroids to identify nearest neighbor counties and computes a **50-mile radius spatial density metric** (`nearby_datacenters_50mi`), adjusted for land area versus water area.
4. **Spatial Smoothing & Imputation:**  
   Applies spatial distance-weighted neighbor averaging and vectorized linear interpolations to handle intermittent reporting gaps in federal county series.
5. **Database Architecture & Documentation:**  
   Refer to [`db_documentation/capstone_db_erd.png`](db_documentation/capstone_db_erd.png) and [`db_documentation/data_pipeline_diagram.png`](db_documentation/data_pipeline_diagram.png) for full entity-relationship and pipeline flow diagrams. SQL integrity and quality checks are maintained in `sql_scripts/db_data_quality_checks.sql`.

---

## Repository Structure

```text
├── README.md                           <- Project overview, setup, and pipeline documentation
├── requirements.txt                    <- Python package dependencies (includes -e . for local utils)
├── .env                                <- Local environment variables (database connection & data path)
├── download_source_data.qmd            <- Script to automate fetching raw external data files
│
├── cleaning_scripts/                   <- Data cleaning, harmonization, and pipeline execution
│   ├── air_quality/                    <- Processing CDC PM2.5 and AQI data
│   ├── business_patterns/              <- Processing Census CBP NAICS 2-digit & NAICS 518 data
│   ├── census_of_emp_and_wages_cleaning/<- BLS QCEW employment and wage cleaning
│   ├── centroids_lookup/               <- Centroid coordinates and spatial lookup tables
│   ├── county_codes/                   <- FIPS code crosswalks and land/water area tables
│   ├── db_builder/                     <- Master execution script (db_builder_script.qmd)
│   ├── gdp_cleaning/                   <- BEA county-level GDP cleaning
│   ├── personal_income_cleaning/       <- BEA county personal income cleaning
│   ├── population_cleaning/            <- SEER county population data processing
│   ├── res_construction_permits/       <- HUD / Census residential building permit processing
│   ├── spatial_temporal_calculations/  <- Haversine distances and 50-mile radius density metrics
│   └── unemployment_cleaning/          <- USDA ERS / BLS unemployment cleaning
│
├── db_documentation/                   <- Schemas, entity-relationship diagrams, and source lists
│   ├── capstone_db_erd.png             <- Entity-relationship diagram of transformed database
│   ├── data_pipeline_diagram.png       <- Visual ETL pipeline architecture diagram
│   └── raw_data_sources.txt            <- Documentation of upstream source download links
│
├── eda_scripts/                        <- Domain-specific exploratory data analysis notebooks
│   ├── air_quality_eda.qmd
│   ├── business_patterns_eda.qmd
│   ├── census_of_emp_and_wages_eda.qmd
│   ├── county_codes_eda.qmd
│   ├── gdp_eda.qmd
│   ├── personal_income_eda.qmd
│   ├── population_eda.qmd
│   ├── res_construction_permits_eda.qmd
│   └── unemployment_eda.qmd
│
├── models/                             <- Statistical, econometric, and ML model notebooks
│   ├── diff_in_diff_linear_reg.qmd     <- Callaway-Sant'Anna DiD and TWFE models on county clusters
│   ├── linear_regression.qmd           <- Linear regressions and fixed effects panel models
│   ├── predict_data_center_presence_by_county.qmd <- Logistic regression & Random Forest classifiers
│   ├── neural_networks.qmd             <- PyTorch neural networks for data center prediction
│   ├── pca_all_features.qmd            <- Dimensionality reduction across all county features
│   └── pca_visualizations.qmd          <- Visualizations of county clusters in PCA space
│
├── poster_plots/                       <- High-resolution plots generated for presentation & poster
├── shared_data/                        <- Local storage directory for raw and staged datasets
├── sql_scripts/                        <- SQL data quality checks and initial exploratory queries
│   ├── db_data_quality_checks.sql
│   └── initial_eda_queries.sql
│
└── utils/                              <- Reusable Python module installed locally via -e .
    ├── db_cleaning_utils.py            <- Imputation, spatial neighbor joins, and data reshaping
    ├── ml_modeling_utils.py            <- DiD model runners, coefficient plots, and evaluation tools
    └── map_utils.py                    <- Spatial visualization helpers
```

---

## Results

This repository contains the full executable modeling code to generate all estimations and visualizations. For our complete empirical findings, policy discussions, interactive maps, and final report writeup, please visit:

- **Interactive Presentation Website:** [The Local Economic Impact of Data Centers](https://wu-msds-capstones.github.io/The-Local-Economic-Impact-of-Data-Centers/)
- **Public Research Repository:** [github.com/LoganRosell/local-economic-impacts-of-data-centers](https://github.com/LoganRosell/local-economic-impacts-of-data-centers)

All exported visualization assets and event-study plots from the models can also be found in the [`poster_plots/`](poster_plots/) directory.

---

## Acknowledgments & References

- **Faculty Advisor:** We extend our deepest gratitude to our faculty advisor, **Dr. Rachel Brown**, for her invaluable guidance, support, and feedback throughout the development of this capstone project.
- **Cohort:** We thank our colleagues in the Willamette University MSDS cohort for their thoughtful feedback, suggestions, and collaborative discussions.

---

## License

This project is licensed under the [MIT License](LICENSE).