import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

data_dir = Path(os.environ["DATA_DIR"])
csv_path = data_dir / "unemployment_and_income" / "Unemployment2023.csv"

df_raw = pd.read_csv(csv_path, encoding='latin-1')

df_raw[["Attribute", "Year"]] = df_raw['Attribute'].str.rsplit('_', n=1, expand = True)

df_final = df_raw.pivot(
    index = ["FIPS_Code", "State", "Area_Name", "Year"],
    columns = "Attribute",
    values = "Value"
).reset_index()

df_final = df_final[df_final['Area_Name'].str.contains('County', na = False)].reset_index(drop=True)

df_final["FIPS_Code"] = df_final["FIPS_Code"].astype(str).str.zfill(5)

df_final = df_final[['FIPS_Code', 'Civilian_labor_force', 'Employed', 'Unemployed', 'Unemployment_rate', 'Year']]

df_final = df_final.rename(columns={
    "FIPS_Code": "county_id",
    "Civilian_labor_force": "civilian_labor_force",
    "Employed": "employed",
    "Unemployed": "unemployed",
    "Unemployment_rate": "unemployment_rate",
    "Year": "year"
})

df_final["civilian_labor_force"] = df_final["civilian_labor_force"].astype(int)
df_final["employed"] = df_final["employed"].astype(int)
df_final["unemployed"] = df_final["unemployed"].astype(int)
df_final["year"] = df_final["year"].astype(int)

database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)

df_final.to_sql(
    "unemployment",
    con=engine,
    if_exists="replace",
    index=False
)