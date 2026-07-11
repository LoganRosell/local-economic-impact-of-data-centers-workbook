# type: ignore
# flake8: noqa
#
#
#
#
#
#
#
#
#
#
#
#
#
import pandas as pd
from pandas.api.types import is_numeric_dtype
import numpy as np
from pathlib import Path
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import subprocess
import sys
from skimpy import skim
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from sklearn.metrics import PredictionErrorDisplay
from scipy.stats import probplot
from statsmodels.stats.outliers_influence import variance_inflation_factor
import statsmodels.api as sm 

load_dotenv()
data_dir = Path(os.environ["DATA_DIR"])
#
#
#
# setup connection variables to local sql db
database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)
#
#
#
# Load data
dc_df = pd.read_sql_table("data_centers", engine)
air_df = pd.read_sql_table("air_quality", engine)
bus_df = pd.read_sql_table("business_patterns", engine)
gdp_df = pd.read_sql_table("gdp", engine)
inc_df = pd.read_sql_table("personal_income", engine)
pop_df = pd.read_sql_table("population", engine)
perm_df = pd.read_sql_table("res_construction_permits", engine)
emp_df = pd.read_sql_table("unemployment", engine)
county_df = pd.read_sql_table("us_counties", engine)
#
#
#
#
#
#
#
def combine_dfs(base_df, dfs_to_join):
    out_df = base_df.copy()

    for i, df in enumerate(dfs_to_join):
        if "county_id" not in df.columns:
            raise ValueError(f"No `county_id` column found in dfs_to_join[{i}]")

        # Make sure all tables only have one row per county
        dupes = df["county_id"][df["county_id"].duplicated()].unique()
        if len(dupes) > 0:
            raise ValueError(f"dfs_to_join[{i}] is not unique on `county_id`. Problematic Counties: {list(dupes)}")

        out_df = pd.merge(out_df, df, how = "left", on = "county_id", validate = "one_to_one")

    missing_summary_table = (
        out_df.isna()
        .mean()
        .sort_values(ascending = False)
        .rename("missing_share")
        .reset_index()
        .rename(columns={"index":"column"})
    )

    print("Missing Summary: \n", missing_summary_table)

    return out_df
#
#
#
# slice df to specific year
def return_specific_year(df, year):
    assert"year" in df.columns, "data frame does not have a year column"
    year = int(year)
    sliced_df = df[df["year"]==year]
    sliced_df = sliced_df.drop(columns = ["year"])
    return sliced_df
#
#
#
# keep only 2022 (closest to when we know data center counts to be true)

df_with_years = [air_df, bus_df, gdp_df, inc_df, pop_df, perm_df, emp_df]

dfs_only_2022 = [return_specific_year(x, 2022) for x in df_with_years]

#
#
#
#
# Aggregate all industry codes per county into one summed row

dfs_only_2022[1] = dfs_only_2022[1].groupby(
    ["county_id"],
    as_index=False
    ).sum()

dfs_only_2022[1] = dfs_only_2022[1].drop(columns = ["naics_industry_code"])
#
#
#
# Add column to county_df which indicates the presence of one or more data centers in a county
counties_with_dc = dc_df["county_id"].unique()

county_df["has_datacenter"] = county_df["county_id"].isin(counties_with_dc).astype(int)
county_df = county_df.drop(columns!=["county_id, has_datacenter"])
#
#
#
# combine all data together

combined_df = combine_dfs(county_df, dfs_only_2022)
#
#
#
