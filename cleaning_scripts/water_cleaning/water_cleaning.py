import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

data_dir = Path(os.environ["DATA_DIR"])
water_dir = data_dir / "water"

values_path = water_dir / "all_water_values.csv"
locations_path = water_dir / "all_monitoring_locations.csv"
parameters_path = water_dir / "parameter_info.csv"

locations_df =  pd.read_csv(locations_path, dtype = str)
parameters_df = pd.read_csv(parameters_path, dtype = str)

## This script assumes that `water_data_aggregated.csv` has already been generated.
## To generate a new `water_data_aggregated.csv` using new variables, rerun the .qmd script with the same name.

output_path = water_dir / "final_data" /"water_data_aggregated.csv"

aggregated_df = pd.read_csv(output_path)

aggregated_df = aggregated_df.groupby(["county_id", "year", "parameter_unit"], as_index = False).sum()

aggregated_df["mean_value"] = aggregated_df["sum_value"] / aggregated_df["count_value"]

df_final = aggregated_df.pivot(
        index = ["county_id", "year"],
        columns = "parameter_unit",
        values = "mean_value"
    ).reset_index()

database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)

df_final.to_sql(
    "water_quality",
    con=engine,
    if_exists="replace",
    index=False
)