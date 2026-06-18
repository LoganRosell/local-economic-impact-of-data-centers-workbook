import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

data_dir = Path(os.environ["DATA_DIR"])
csv_path = data_dir / "personal_income_data.csv"

df_raw = pd.read_csv(csv_path, encoding='latin-1')

df_long = df_raw.melt(
    id_vars = ['GeoFIPS', 'GeoName', 'Region', 'TableName', 'LineCode', 'IndustryClassification','Description', 'Unit'],
    value_vars = [str(year) for year in range(1969, 2025)],
    var_name = 'year',
    value_name = 'personal_income_value'
    )

df_final = df_long.pivot(
    index = ["GeoFIPS", "GeoName", "year"],
    columns = "Description",
    values = "personal_income_value"
).reset_index()

# Get rid of the extra quotes
df_final["GeoFIPS"] = df_final["GeoFIPS"].str.replace('"','') 

# Only keep counties (have a comma)
df_final = df_final[df_final["GeoName"].str.contains(',', na = False)].reset_index(drop=True)

# Now split county and state into their own columns
df_final[["county", "state_code"]] = df_final['GeoName'].str.split(', ', n=1, expand = True)

df_final["state_code"] = df_final['state_code'].str.split(', ').str[-1]

df_final["state_code"] = df_final['state_code'].str.split('*').str[0]

# Drop GeoName and empty column
df_final = df_final.drop(columns = ["GeoName", np.nan])

df_final.columns = df_final.columns.str.strip()

# Then rename columns
df_final = df_final.rename(columns={
    "Per capita personal income (dollars) 2/": "Per Capita Personal Income (dollars)",
    "Personal income (thousands of dollars)": "Personal Income (thousands of dollars)",
    "Population (persons) 1/": "Population"
})

df_final["year"] = df_final["year"].astype(int)

value_columns = ["Per Capita Personal Income (dollars)", "Personal Income (thousands of dollars)", "Population"]

for col in value_columns:
    df_final[col] = pd.to_numeric(
        df_final[col], 
        errors='coerce'
    ).astype('Int64') 

database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)

df_final.to_sql(
    "personal_income",
    con=engine,
    if_exists="replace",
    index=False
)