
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
from statsmodels.stats.outliers_influence import variance_inflation_factor

# slice df to specific year
def return_specific_year(df, year):
    assert"year" in df.columns, "data frame does not have a year column"
    year = int(year)
    sliced_df = df[df["year"]==year]
    sliced_df = sliced_df.drop(columns = ["year"])
    return sliced_df



# return updated version of dataframe with specified columns made to be per-capita
def make_per_capita(df, per_capita_cols):

    for col in per_capita_cols:
        df[f"{col}_per_capita"] = df[col] / df["population"]

    df = df.drop(columns=per_capita_cols)
    return df



# Check for high correlation between x variables indicating a violation of the independence assumption
def show_correlation_heat_map(df):
    corr_matrix = df.corr()
    # Plot heatmap correlations
    plt.figure(figsize=(16, 12))
    sns.heatmap(corr_matrix, cmap="coolwarm", annot=False, vmin=-1, vmax=1)
    plt.title("Correlation Matrix Heatmap")
    plt.show()



# function to return model accuracy report
def model_accuracy_report(model, X_train, y_train, X_test, y_test):
    # training calculations
    y_pred_train = model.predict(X_train)
    train_acc = sum(y_pred_train == y_train) / len(y_train)
    print(f"Overall Training Accuracy: {train_acc:.4f}")
    
    actual_pos_train = (y_train == 1)
    true_pos_train = (y_pred_train == 1) & actual_pos_train
    tpr_train = sum(true_pos_train) / sum(actual_pos_train)
    print(f"True Positive Training Accuracy: {tpr_train:.4f}")
    
    print("-" * 20) 
    
    # test calculations
    y_pred_test = model.predict(X_test)
    test_acc = sum(y_pred_test == y_test) / len(y_test)
    print(f"Overall Test Accuracy: {test_acc:.4f}")
    
    actual_pos_test = (y_test == 1)
    true_pos_test = (y_pred_test == 1) & actual_pos_test
    tpr_test = sum(true_pos_test) / sum(actual_pos_test)
    print(f"True Positive Test Accuracy: {tpr_test:.4f}")

    ConfusionMatrixDisplay(
    confusion_matrix=confusion_matrix(y_test, y_pred_test), 
    display_labels=model.classes_
    ).plot()

    plt.show()



# Help select numeric columns which meet different model assumptions
def column_selector(
    df,
    no_na = False,
    vif_cut_off = 5.0,
    outlier_sd_cut_off = 3.0,
    only_normal = False,
    return_report = False,
    cols_to_preserve = None
    ):
    """Filters DataFrame columns based on missingness, VIF, outliers, and normality.

    Examines all numeric columns in a DataFrame and filters them sequentially
    through missing value checks, Variance Inflation Factor (VIF) limits,
    standard deviation outlier cutoffs, and D'Agostino-Pearson normality tests.
    Non-numeric columns and user-specified preserved columns bypass these checks
    and are always retained.

    Args:
        df: The pandas DataFrame containing features to evaluate.
        no_na: If True, drops numeric columns that contain any NA/NaN values.
            Defaults to False.
        vif_cut_off: Maximum allowed Variance Inflation Factor threshold.
            Numeric columns with a VIF equal to or exceeding this threshold are
            dropped to reduce multicollinearity. Defaults to 5.0.
        outlier_sd_cut_off: Number of standard deviations from the mean used to
            define outlier boundaries. Columns containing values beyond this
            range are dropped. Defaults to 3.0.
        only_normal: If True, retains only numeric columns that satisfy
            normality criteria (p-value > 0.05 from D'Agostino-Pearson test or
            absolute skewness < 1.0). Defaults to False.
        return_report: If True, returns both the list of retained column names
            and a pandas DataFrame detailing reasons for dropped columns.
            Defaults to False.
        cols_to_preserve: A list of column names to bypass filtering and retain
            unconditionally in the output. Defaults to None.

    Returns:
        If return_report is False:
            A list of column names retained after filtering.
        If return_report is True:
            A tuple containing:
                - List[str]: Column names retained after filtering.
                - pd.DataFrame: Audit trail with columns ['dropped_col', 'reason'].
    """
    if cols_to_preserve is None:
        cols_to_preserve = []
    df = df.drop(columns=cols_to_preserve)
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    non_numeric_cols = df.select_dtypes(exclude="number").columns.tolist()
    cols_to_keep = numeric_cols.copy()
    df_num = df[numeric_cols]
    drop_reasons = []
    
    #na filter
    if no_na:
        filter_results = []
        for col in cols_to_keep:
            if not df_num[col].hasnans:
                filter_results.append(col)
            else: 
                drop_reasons.append({"dropped_col": col, "reason": "contained NA values"})
                
        cols_to_keep = filter_results
    
    df_num = df[cols_to_keep].dropna()

    #vif filter
    filter_results = []
    for idx, col in enumerate(cols_to_keep):
        vif = variance_inflation_factor(df_num.values, idx)
        if vif < vif_cut_off:
            filter_results.append(col)
        else:
            drop_reasons.append({"dropped_col": col, "reason": f"high VIF ({vif:.2f})"})
    cols_to_keep = filter_results
    
    #outlier filter
    filter_results = []
    for col in cols_to_keep:
        mean = df_num[col].mean()
        std = df_num[col].std()
        lower_bound = mean - (outlier_sd_cut_off * std)
        upper_bound = mean + (outlier_sd_cut_off * std)
        if ((df_num[col] > lower_bound) & (df_num[col] < upper_bound)).all():
            filter_results.append(col)
        else:
            drop_reasons.append({"dropped_col": col, "reason": f"exceeded {outlier_sd_cut_off} SD outliers"})
    cols_to_keep = filter_results

    #normality filter
    if only_normal:
        filter_results = []
        for col in cols_to_keep:
            skew = abs(stats.skew(df_num[col]))
            p_val = stats.normaltest(df_num[col]).pvalue
            if p_val > 0.05 or skew < 1:
                filter_results.append(col)
            else:
                drop_reasons.append({"dropped_col": col, "reason": f"non-normal (skew={skew:.2f}, p={p_val:.4f})"})
        cols_to_keep = filter_results

    drop_report_df = pd.DataFrame(drop_reasons)
    cols_to_keep = non_numeric_cols + cols_to_preserve + cols_to_keep 
    if return_report:
        return cols_to_keep, drop_report_df
    return cols_to_keep

def pivot_naics(bus_df, code_df, cols_to_pivot = ["tot_employee_count", "annual_payroll", "tot_establishment_count"]):
    """
    Groups similar NAICS codes via shared sector names and pivots into wide format.
    
    Parameters:
        bus_df = df with naics_industry_code key column
        code_df = code lookup df
        cols_to_pivot = list of columns to pivot 

    Returns:
        Wide DataFrame with one row per (county_id, year)
    """

    # Clean sector names
    code_df = code_df.copy()
    bucket_map = {
        "Agriculture, Forestry, Fishing and Hunting": "primary_industries",
        "Mining, Quarrying, and Oil and Gas Extraction": "primary_industries",
        "Utilities": "primary_industries",

        "Construction": "industrial",
        "Manufacturing": "industrial",

        "Wholesale Trade": "trade_transport",
        "Retail Trade": "trade_transport",
        "Transportation and Warehousing": "trade_transport",

        "Information": "information",

        "Finance and Insurance": "professional",
        "Real Estate and Rental and Leasing": "professional",
        "Professional, Scientific, and Technical Services": "professional",
        "Management of Companies and Enterprises": "professional",

        "Administrative and Support and Waste Management and Remediation Services": "public_services",
        "Educational Services": "public_services",
        "Health Care and Social Assistance": "public_services",
        "Arts, Entertainment, and Recreation": "public_services",
        "Accommodation and Food Services": "public_services",
        "Other Services (except Public Administration)": "public_services",
        "Public Administration": "public_services",
        
        "Unknown": "unknown",
    }
    
    code_df["bucket"] = code_df["definition"].map(bucket_map)

    # Merge codes and bus_df
    output_df = bus_df.merge(code_df, left_on = "naics_industry_code", right_on = "sector", how = "left")

    grouped_df = (
        output_df.groupby(["county_id", "year", "bucket"], as_index=False)
        [cols_to_pivot]
        .sum()
    )

    # Pivot
    pivot_df = grouped_df.pivot_table(
        index=["county_id", "year"],
        columns="bucket",
        values=cols_to_pivot,
        aggfunc="sum"
    )

    pivot_df.columns = [
        f"{metric}_{sector}" for metric, sector in pivot_df.columns
    ]

    pivot_df = pivot_df.reset_index()

    return pivot_df

def eda_summary(df):
    """
    Returns missingness, number of unique observations, standard deviation, 
    and skew for all numeric columns in a dataframe
    """
    num_df = df.select_dtypes(include="number").copy()

    eda_summary = pd.DataFrame({
        "missing_share": num_df.isna().mean(),
        "n_unique": num_df.nunique(),
        "std": num_df.std(numeric_only=True),
        "skew": num_df.skew(numeric_only=True),
    }).sort_values("skew", ascending=False).reset_index().rename(columns={"index": "column"})

    return eda_summary

def run_lasso(df, y_col):
    """
    Runs lasso in report mode on a dataframe against a specified response variable,
    which helps narrow down variables that may be predictive of that response variable.
    Variables with a higher coefficient should be included,
    whereas variables at or near zero should be considered for exclusion from the final model.
    """
    target_col = y_col
    drop_cols = ["county_id", "year", target_col]

    lasso_df = df.dropna().copy()
    lasso_df.columns = lasso_df.columns.map(str)

    x_cols = [str(c) for c in lasso_df.columns if str(c) not in drop_cols]
    
    X = lasso_df[x_cols]
    y = lasso_df[target_col]

    lasso_pipe = make_pipeline(
        StandardScaler(),
        LassoCV(cv = 5, random_state = 15215, max_iter = 10000)
    )

    lasso_pipe.fit(X, y)

    lasso_model = lasso_pipe.named_steps["lassocv"]
    coef_df = pd.DataFrame({
        "feature": x_cols,
        "coef": lasso_model.coef_
    }).sort_values("coef", key = lambda s: s.abs(), ascending = False)

    print(coef_df.to_string(index=False))

def run_linear_regression(df, y_col, x_cols, county_fe = True, year_fe = True):
    """
    Runs a linear regression and prints the regression output,
    residuals plot (Linearity and Equal Variance assumptions),
    QQ plot (Normally-distributed errors/residuals assumption),
    and VIF results (Independent observations (given X) assumption)

    Parameters:
        - df = the dataframe you want to do regression on
        - y_col = the response variable
        - x_cols = the explanatory variables
        - county_fe = whether you want to use a county fixed effect
        - year_fe = whether you want to use a year fixed effect

    Assumption(s):
        - Always clusters by county
    """

    needed_cols = [y_col] + x_cols
    if county_fe:
        needed_cols.append("county_id")
    if year_fe:
        needed_cols.append("year")

    needed_cols = list(dict.fromkeys(needed_cols))
    reg_df = df[needed_cols].dropna().copy()

    rhs_terms = x_cols.copy()
    if county_fe:
        rhs_terms.append("C(county_id)")
    if year_fe:
        rhs_terms.append("C(year)")

    formula = f"{y_col} ~ " + " + ".join(rhs_terms)

    model = smf.ols(formula=formula, data=reg_df).fit(
            cov_type="cluster",
            cov_kwds={"groups": reg_df["county_id"]}
        )

    fitted = model.fittedvalues
    resid = model.resid

    print("Formula:")
    print(formula)
    print("\n")
    print(model.summary())

    # Examine Residuals
    plt.figure(figsize=(7, 5))
    plt.scatter(fitted, resid, alpha=0.6)
    plt.axhline(0, color="red", linestyle = "--")
    plt.xlabel("Fitted values")
    plt.ylabel("Residuals")
    plt.title("Residuals vs Fitted Values")
    plt.show()

    # Check For Normal Distribution
    plt.figure(figsize=(7, 5))
    probplot(resid, dist = "norm", plot = plt)
    plt.title("Q-Q Plot of Residuals")
    plt.show()

    # Check VIF
    vif_X = reg_df[x_cols].copy()
    vif_X = sm.add_constant(vif_X, has_constant="add")

    vif_df = pd.DataFrame({
        "variable": vif_X.columns,
        "vif": [
            np.nan if col == "const" else variance_inflation_factor(vif_X.values, i)
            for i, col in enumerate(vif_X.columns)
        ]
    })

    print(vif_df)

    return model