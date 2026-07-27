import pandas as pd
import os

# ============================================================
# DATA INGESTION SCRIPT — Bluestock MF Analytics Platform
# Day 1: Load all 10 CSV datasets and inspect them - (Task 3)
# ============================================================


# Raw_data_path folder:
RAW_DATA_PATH = "data/raw/"

# List all CSV files in the raw folder
csv_files = [f for f in os.listdir(RAW_DATA_PATH) if f.endswith(".csv")]

print(f"\nTotal csv file found: {len(csv_files)}")
print("=" *60)

# Empty list to store all dataframes
dataframes = {}

for file in csv_files:
    file_path = os.path.join(RAW_DATA_PATH, file) 
    df = pd.read_csv(file_path)

    # Storing dataframes
    dataset_name = file.replace('csv', '')


    # checking with data:
    print(f"\nDataset: {file}")
    print(f"Shape: {df.shape}, {df.shape[0]} rows and {df.shape[1]} columns")
    print(f"Columns: {list(df.columns)}")
    print(f"dftype: {df.dtypes}")
    print(f"First 3 rows: {df.head(3)}")


    # Note Anomolies
    null_counts = df.isnull().sum()
    if null_counts.any():
        print(f"\n Null values found: {null_counts}")
    else: 
        print(f"\n No Null Values found!....")


    # Check for duplicates:
    duplicates = df.duplicated().sum()
    if duplicates.any():
        print(f"\n Duplicated rows = {duplicates}")
    else:
        print(f"\n No duplicated rows!....")

    print("=" *60)

print(f"\n ---------- Data Ingestion Completed: All data loaded successfully! ----------\n" )


# ============================================================
# FUND MASTER EXPLORATION (Task 6)
# ============================================================

# Load fund master specifically
# fund master has no null, duplicates - no need for cleaning
fund_master_file = "01_fund_master.csv"

if fund_master_file in [f for f in csv_files]:
    df_fund = pd.read_csv(os.path.join(RAW_DATA_PATH, fund_master_file))

    print(f"\n ------ Fund Master Exploration: ----------")
    print("=" *60)

    # finding unique fund_houses
    if 'fund_house' in df_fund.columns:
        print(f"\nUnique fund houses are : {df_fund['fund_house'].nunique()}")
        print(df_fund['fund_house'].unique())

    #  finding unique categories
    if 'category' in df_fund.columns:
        print(f"\nUnique categories are : {df_fund['category'].nunique()}")
        print(df_fund['category'].unique())

    #  finding unique sub-categories
    if 'sub_category' in df_fund.columns:
        print(f"\nUnique sub_categories are : {df_fund['sub_category'].nunique()}")
        print(df_fund['sub_category'].unique())

    #  finding unique risk grades
    if 'risk_category' in df_fund.columns:
        print(f"\nUnique risk grades are : {df_fund['risk_category'].nunique()}")
        print(df_fund['risk_category'].unique())

    print(f"\n ---------- Fund master exploration complete! ----------\n" )