
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


