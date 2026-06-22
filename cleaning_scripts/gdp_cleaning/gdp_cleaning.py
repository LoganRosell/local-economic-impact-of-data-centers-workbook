import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

data_dir = Path(os.environ["DATA_DIR"])
csv_path = data_dir / 'gdp' / "CAGDP1__ALL_AREAS_2001_2024.csv"

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

df_final = df_final[['GeoFIPS', 'Real GDP (thousands of chained 2017 dollars) ', 'Current-dollar GDP (thousands of current dollars) ', 'Chain-type quantity indexes for real GDP ', 'year']]

# Then rename columns
df_final = df_final.rename(columns={
    "GeoFIPS": "county_id",
    "Chain-type quantity indexes for real GDP ": "quantity_index_gdp",
    "Current-dollar GDP (thousands of current dollars) ": "current_gdp_dollars_thousands",
    "Real GDP (thousands of chained 2017 dollars) ": "real_gdp_2017_dollars_thousands"
})

df_final["year"] = df_final["year"].astype(int)

df_final["quantity_index_gdp"] = pd.to_numeric(
    df_final["quantity_index_gdp"], 
    errors='coerce'
)

df_final["current_gdp_dollars_thousands"] = pd.to_numeric(
    df_final["current_gdp_dollars_thousands"], 
    errors='coerce'
).astype('Int64') 

df_final["real_gdp_2017_dollars_thousands"] = pd.to_numeric(
    df_final["real_gdp_2017_dollars_thousands"], 
    errors='coerce'
).astype('Int64')

database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)

df_final.to_sql(
    "gdp",
    con=engine,
    if_exists="replace",
    index=False
)