import pandas as pd
import numpy as np

def test_print():
    print("that worked!")


# Function for values across neighboring counties
def spatial_fill(input_df, county_df, key_cols = ['year'], include_cols = None, 
                 fill_type = "new_col", calc_type = "weighted_avg", 
                 num_counties = 5):
    """
    Does calculations on column(s) in a dataframe based on neighboring county information.

    Parameters:
        - input_df = dataframe to do calculations on
        - county_df = the county dataframe with county id's and nearest counties
        - key_cols = columns other than 'county_id' that act as keys (e.g. ['year'])
        - include_cols = list of columns to do calculations on. If None, uses all numeric cols.
        - fill_type = "new_col" (create new column) or "fill_na" (fill NAs in existing col)
        - calc_type = "weighted_avg", "avg", or "median"
        - num_counties = the number of neighboring counties to look at (<= 10)
    
    Assumptions:
        - input_df has 'county_id' and key_cols
        - county_df has columns:
            county_id,
            nearest_county_1 ... nearest_county_k,
            nearest_county_1_distance ... nearest_county_k_distance
    """

    assert "county_id" in input_df.columns, "Input df must have a column called 'county_id'"
    assert num_counties <= 10, "Number of counties must be 10 or less"
    assert fill_type in ["new_col", "fill_na"], "fill type must be either 'new_col' or 'fill_na'"
    assert calc_type in ["weighted_avg", "avg", "median"], "fill type must be 'weighted_avg', 'avg', or 'median'"

    key_cols = key_cols or []
    index_cols = ["county_id"] + key_cols

    # Find input column(s) to use
    if include_cols is None:
        value_cols = input_df.select_dtypes(include="number").columns.tolist()
        value_cols = [c for c in value_cols if c not in key_cols]
    else:
        value_cols = include_cols

    # Find county_df columns to use:
    neighbor_id_cols = [f"nearest_county_{i}" for i in range(1, num_counties + 1)]
    neighbor_dist_cols = [f"nearest_county_{i}_distance" for i in range(1, num_counties + 1)]
    
    county_df_final = county_df[["county_id"] + neighbor_id_cols + neighbor_dist_cols].copy()

    df = input_df.merge(county_df_final, on = "county_id", how = "left")

    # Compute weights
    if calc_type == "weighted_avg":
        dist_df = df[neighbor_dist_cols]
        with np.errstate(divide="ignore", invalid="ignore"):
            weights = 1.0 / dist_df
        weight_sums = weights.sum(axis = 1)
        weights = weights.div(weight_sums, axis = 0)

    # Do calculations
    for col in value_cols:
        val_by_key = input_df.set_index(index_cols)[col]

        neighbor_vals = []
        for nc in neighbor_id_cols:
            tmp_idx = pd.DataFrame({"neighbor_county_id": df[nc]})
            for k in key_cols:
                tmp_idx[k] = df[k]
            tmp_idx = tmp_idx.set_index(["neighbor_county_id"] + key_cols)
            neighbor_vals.append(tmp_idx.index.map(val_by_key))
        neighbor_vals = pd.DataFrame(neighbor_vals).T
        neighbor_vals.columns = neighbor_id_cols

        if calc_type == "avg":
            neighbor_stat = neighbor_vals.mean(axis = 1)
        elif calc_type == "median":
            neighbor_stat = neighbor_vals.median(axis = 1)
        else: # weighted avg
            neighbor_stat = (neighbor_vals.values * weights.values).sum(axis = 1)

        # Merge back into input_df
        df[f"__spatial_{col}"] = neighbor_stat

        helper_df = df[index_cols + [f"__spatial_{col}"]].copy().drop_duplicates()

        if fill_type == "new_col":
            new_col_name = f"{col}_spatial_{calc_type}_{num_counties}"
            input_df = input_df.merge(
                helper_df.rename(columns={f"__spatial_{col}": new_col_name}),
                on=index_cols,
                how="left",
            )
        else:  # fill_na
            input_df = input_df.merge(
                helper_df.rename(columns={f"__spatial_{col}": "__spatial_fill"}),
                on=index_cols,
                how="left",
            )
            input_df[col] = input_df[col].fillna(input_df["__spatial_fill"])
            input_df = input_df.drop(columns="__spatial_fill")

    return input_df

def all_county_years(county_df, year_start=2002, year_end=2022):
    """
    Creates a dataframe with all combinations of county_id and year.

    Parameters:
        - county_df: county dataframe with at least a 'county_id' column
        - year_start: first year to include (inclusive)
        - year_end: last year to include (inclusive)

    Returns:
        - DataFrame with columns ['county_id', 'year'] containing every
          county_id from county_df crossed with every year in the range.
    """

    # build year range
    years = pd.DataFrame({"year": range(year_start, year_end + 1)})

    # Cross-join
    county_df["key"] = 1
    years["key"] = 1

    out = county_df.merge(years, on="key", how="outer").drop(columns="key")

    out = out.sort_values(["county_id", "year"]).reset_index(drop=True)

    return out