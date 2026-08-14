"""
Data Ingestion Script — Bluestock MF Analytics Platform
Day 1: Loads all raw CSV datasets, inspects shape/dtypes/nulls/duplicates,
and explores fund master metadata (unique fund houses, categories, risk grades).
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw"


def load_and_inspect_all_csvs(raw_path: Path) -> dict:
    """Load every CSV in raw_path, print shape/dtype/null/duplicate summary, return as dict of DataFrames."""
    csv_files = [f for f in raw_path.iterdir() if f.suffix == ".csv"]
    print(f"\nTotal CSV files found: {len(csv_files)}")
    print("=" * 60)

    dataframes = {}
    for file_path in csv_files:
        df = pd.read_csv(file_path)
        dataset_name = file_path.stem
        dataframes[dataset_name] = df

        print(f"\nDataset: {file_path.name}")
        print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        print(f"Columns: {list(df.columns)}")

        null_counts = df.isnull().sum()
        if null_counts.any():
            print(f"Null values found:\n{null_counts[null_counts > 0]}")
        else:
            print("No null values found.")

        duplicates = df.duplicated().sum()
        print(f"Duplicated rows: {duplicates}" if duplicates else "No duplicated rows.")
        print("=" * 60)

    print("\nData ingestion complete: all datasets loaded successfully.\n")
    return dataframes


def explore_fund_master(dataframes: dict) -> None:
    """Print unique fund houses, categories, sub-categories, and risk grades from fund master."""
    df_fund = dataframes.get("01_fund_master")
    if df_fund is None:
        print("Fund master file not found — skipping exploration.")
        return

    print("\n------ Fund Master Exploration ------")
    print("=" * 60)

    for col, label in [
        ("fund_house", "fund houses"),
        ("category", "categories"),
        ("sub_category", "sub-categories"),
        ("risk_category", "risk grades"),
    ]:
        if col in df_fund.columns:
            print(f"\nUnique {label}: {df_fund[col].nunique()}")
            print(df_fund[col].unique())

    print("\nFund master exploration complete.\n")


if __name__ == "__main__":
    dataframes = load_and_inspect_all_csvs(RAW_DATA_PATH)
    explore_fund_master(dataframes)