import pandas as pd
import numpy as np

def test_print():
    print("that worked!")


# Function for values across neighboring counties
def spatial_fill(input_df, county_df, key_cols = None, include_cols = None, 
                 fill_type = "new_col", calc_type = "weighted_avg", 
                 num_counties = 5, self_weight=0.0):
    """
    Does calculations on column(s) in a dataframe based on neighboring county information.

    Parameters:
        - input_df = dataframe to do calculations on
        - county_df = the county dataframe with county id's and nearest counties
        - key_cols = columns other than 'county_id' and 'year' that act as keys (e.g. ['naics_industry_code'])
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
    index_cols = ["county_id", "year"] + key_cols

    # Find input column(s) to use
    if include_cols is None:
        value_cols = input_df.select_dtypes(include="number").columns.tolist()
        value_cols = [c for c in value_cols if c not in index_cols]
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

    # Do calculations
    for col in value_cols:
        val_by_key = input_df.set_index(index_cols)[col]

        neighbor_vals = []
        for nc in neighbor_id_cols:
            tmp_idx = pd.DataFrame({
                "county_id": df[nc],      # neighbor county id
                "year": df["year"],       # keep same year
            })
            for k in key_cols:
                tmp_idx[k] = df[k]
            tmp_idx = tmp_idx.set_index(index_cols)
            neighbor_vals.append(tmp_idx.index.map(val_by_key))
        neighbor_vals = pd.DataFrame(neighbor_vals).T
        neighbor_vals.columns = neighbor_id_cols

        if calc_type == "avg":
            neighbor_stat = neighbor_vals.mean(axis = 1)
        elif calc_type == "median":
            neighbor_stat = neighbor_vals.median(axis = 1)
        else: # weighted avg
            raw_weights = weights[neighbor_dist_cols].copy()
            raw_weights.columns = neighbor_id_cols
            valid_mask = ~neighbor_vals.isna()
            masked_weights = raw_weights.where(valid_mask, other=0.0)
            weight_sums = masked_weights.sum(axis=1)
            normalized_weights = masked_weights.div(weight_sums.replace(0, np.nan), axis=0)
            products = neighbor_vals * normalized_weights
            neighbor_stat = products.sum(axis=1)

            if self_weight is not None and self_weight > 0:
                own_vals = df[col]

                self_missing = own_vals.isna()

                neighbor_weight = max(0.0, 1.0 - self_weight)

                blended = (
                    self_weight * own_vals +
                    neighbor_weight * neighbor_stat
                )

                blended = blended.where(~self_missing, neighbor_stat)

                neighbor_stat = blended

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

def yoy_change(df, key_cols=None, include_cols=None):
    """
    Adds year-over-year percentage change columns for selected numeric columns.

    Parameters:
        - df: dataframe to do year-over-year calculations on
        - key_cols: columns (besides 'county_id' and 'year') that act as keys, e.g. ['naics_industry_code']; default: []
        - include_cols: list of columns to do YoY on. If None, uses all numeric cols excluding key columns and 'year'.
    """

    key_cols = key_cols or []
    all_keys = ["county_id", "year"] + key_cols

    # choose value columns
    if include_cols is None:
        value_cols = df.select_dtypes(include="number").columns.tolist()
        value_cols = [c for c in value_cols if c not in key_cols + ["year"]]
    else:
        value_cols = include_cols

    df = df.sort_values(all_keys).reset_index(drop=True)

    group_keys = ["county_id"] + key_cols
    grouped = df.groupby(group_keys, dropna=False)

    for col in value_cols:
        change_col = f"{col}_yoy_change"
        df[change_col] = grouped[col].pct_change(fill_method=None)

        prev = grouped[col].shift(1)

        df.loc[prev==0, change_col] = np.nan

    return df

def spatial_then_yoy(input_df,
                     county_df,
                     key_cols=None,
                     include_cols=None,
                     fill_type="new_col",
                     calc_type="weighted_avg",
                     num_counties=5, 
                     self_weight=0.0):
    """
    Apply spatial_fill, then yoy_change on the same set of value columns.
    """
    key_cols = key_cols or []

    # If include_cols not provided, auto-select base columns
    if include_cols is None:
        base_cols = input_df.select_dtypes(include="number").columns.tolist()
        base_cols = [c for c in base_cols if c not in key_cols + ["year"]]
        # Optionally skip already-derived stuff here
        base_cols = [
            c for c in base_cols
            if not c.endswith("_yoy_change") and "_spatial_" not in c
        ]
        include_cols = base_cols

    df_spatial = spatial_fill(
        input_df,
        county_df,
        key_cols=key_cols,
        include_cols=include_cols,
        fill_type=fill_type,
        calc_type=calc_type,
        num_counties=num_counties
    )

    df_yoy = yoy_change(
        df_spatial,
        key_cols=key_cols,
        include_cols=include_cols
    )

    return df_yoy

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

    out = out[["county_id", "year"]]

    out = out.sort_values(["county_id", "year"]).reset_index(drop=True)

    return out

def remove_rows_not_in_mainland_states(df, id_col_name):
    """
    returns a version of the df provided with any row that
    has a fips code from a state not in the lower-48 removed
    
    Args:
        df (Pandas DataFrame): df containing a column with FIPS codes
        id_col_name (str): the name of the column with FIPS codes

    Returns:
        pandas df: trimmed version of inputted df
     """
    
    continental_us_fips = [
        "01", "04", "05", "06", "08", "09", "10", "11", "12", "13", 
        "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", 
        "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", 
        "36", "37", "38", "39", "40", "41", "42", "44", "45", "46", 
        "47", "48", "49", "50", "51", "53", "54", "55", "56"
    ]

    output_df = df[df[id_col_name].str[0:2].isin(continental_us_fips)]

    return output_df

def impute_estabs_for_county(group):
    """
    Impute estabs for a single county across years:
    - Fill internal gaps by linear interpolation.
    - Set leading and trailing missing values to 0.

    For use in a groupby function
    """
    group = group.sort_values("year").copy()
    vals = group["estabs"]

    # Interpolation for gaps
    vals_interp = vals.interpolate(method = "linear")

    # Leading missing values -> 0
    first_valid_idx = vals_interp.first_valid_index()
    if first_valid_idx is not None:
        mask_leading = vals_interp.index < first_valid_idx
        vals_interp.loc[mask_leading] = 0
    else:
        vals_interp[:] = 0
        group["estabs_imputed"] = vals_interp
        return group
    
    # Trailing missing values -> 0
    last_valid_idx = vals.last_valid_index()
    mask_trailing = vals.index > last_valid_idx
    vals_interp.loc[mask_trailing] = 0

    vals_interp = vals_interp.round()

    group["estabs_imputed"] = vals_interp

    # Flag whether this row was imputed
    group["estabs_was_imputed"] = group["estabs"].isna()

    return group
