import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

data_dir = Path(os.environ["DATA_DIR"])
txt_path = data_dir / "population" / "us.1990_2024.20ages.adjusted.txt"

df_raw = pd.read_fwf(txt_path, header = None, names=['FIPS_info', 'other_info'])

df_raw['year'] = df_raw['FIPS_info'].str[:4].astype(int)

df_raw = df_raw[df_raw['year'] > 2000]

df_raw['county_id'] = df_raw['FIPS_info'].str[-5:]

df_raw['population'] = df_raw['other_info'].astype(str).str[-8:].astype(int)

df_final = df_raw.groupby(['year', 'county_id'], as_index = False)['population'].sum()

database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)

df_final.to_sql(
    "county_population",
    con=engine,
    if_exists="replace",
    index=False
)