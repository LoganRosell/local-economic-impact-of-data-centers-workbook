
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix

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