import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

data_dir = Path(os.environ["DATA_DIR"])
csv_path = data_dir / "gdp_data.csv"

df_raw = pd.read_csv(csv_path, encoding='latin-1')

df_long = df_raw.melt(
    id_vars = ['GeoFIPS', 'GeoName', 'Region', 'TableName', 'LineCode', 'IndustryClassification','Description', 'Unit'],
    value_vars = [str(year) for year in range(2001, 2025)],
    var_name = 'year',
    value_name = 'gdp_value'
    )

df_final = df_long.pivot(
    index = ["GeoFIPS", "GeoName", "year"],
    columns = "Description",
    values = "gdp_value"
).reset_index()

# Get rid of the extra quotes
df_final["GeoFIPS"] = df_final["GeoFIPS"].str.replace('"','') 

# Only keep counties (have a comma)
df_final = df_final[df_final["GeoName"].str.contains(',', na = False)].reset_index(drop=True)

# Now split county and state into their own columns
df_final[["county", "state_code"]] = df_final['GeoName'].str.split(', ', n=1, expand = True)

df_final["state_code"] = df_final['state_code'].str.split(', ').str[-1]

df_final["state_code"] = df_final['state_code'].str.split('*').str[0]

df_final = df_final.drop(columns = "GeoName")

df_final.columns = df_final.columns.str.strip()

# Then rename columns
df_final = df_final.rename(columns={
    "Chain-type quantity indexes for real GDP": "Quantity Indexes for real GDP",
    "Current-dollar GDP (thousands of current dollars)": "Current-Dollar GDP (thousands of dollars)",
    "Real GDP (thousands of chained 2017 dollars)": "Real GDP (thousands of 2017 dollars)"
})

df_final["year"] = df_final["year"].astype(int)

df_final["Quantity Indexes for real GDP"] = pd.to_numeric(
    df_final["Quantity Indexes for real GDP"], 
    errors='coerce'
)

df_final["Current-Dollar GDP (thousands of dollars)"] = pd.to_numeric(
    df_final["Current-Dollar GDP (thousands of dollars)"], 
    errors='coerce'
).astype('Int64') 

df_final["Real GDP (thousands of 2017 dollars)"] = pd.to_numeric(
    df_final["Real GDP (thousands of 2017 dollars)"], 
    errors='coerce'
).astype('Int64')

load_dotenv()

database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)

df_final.to_sql(
    "county_gdp",
    con=engine,
    if_exists="replace",
    index=False
)