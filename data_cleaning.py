"""
Data Cleaning Script — Bluestock MF Analytics Platform
Day 2: Cleans NAV history, investor transactions, and scheme performance
datasets, and lightly cleans the remaining 7 CSVs. Saves all outputs to
data/processed/.
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAW_PATH = BASE_DIR / "data" / "raw"
PROCESSED_PATH = BASE_DIR / "data" / "processed"
PROCESSED_PATH.mkdir(parents=True, exist_ok=True)


def save_and_report(df: pd.DataFrame, filename: str, original_rows: int) -> None:
    """Save a cleaned DataFrame and print a before/after row-count summary."""
    path = PROCESSED_PATH / filename
    df.to_csv(path, index=False)
    print(f"  Saved: {filename}")
    print(f"  Rows: {original_rows} -> {len(df)} ({original_rows - len(df)} removed)\n")


def clean_nav_history() -> None:
    """Parse dates, sort, dedupe, validate NAV > 0, and forward-fill weekends/holidays."""
    print("\n----- Cleaning: 02_nav_history.csv")
    df_nav = pd.read_csv(RAW_PATH / "02_nav_history.csv")
    original_rows = len(df_nav)

    df_nav["date"] = pd.to_datetime(df_nav["date"])
    df_nav = df_nav.sort_values(["amfi_code", "date"]).reset_index(drop=True)
    df_nav = df_nav.drop_duplicates(subset=["amfi_code", "date"])

    invalid_nav = df_nav[df_nav["nav"] <= 0]
    if len(invalid_nav) > 0:
        print(f"  Found {len(invalid_nav)} rows with NAV <= 0 — removing")
        df_nav = df_nav[df_nav["nav"] > 0]
    else:
        print("  All NAV values > 0")

    # Forward-fill missing dates (weekends/holidays) per fund
    df_nav = df_nav.set_index("date")
    filled_frames = []
    for code in df_nav["amfi_code"].unique():
        fund_df = df_nav[df_nav["amfi_code"] == code].copy()
        full_range = pd.date_range(start=fund_df.index.min(), end=fund_df.index.max(), freq="D")
        fund_df = fund_df.reindex(full_range)
        fund_df["amfi_code"] = code
        fund_df["nav"] = fund_df["nav"].ffill()
        filled_frames.append(fund_df)

    df_nav = pd.concat(filled_frames).reset_index().rename(columns={"index": "date"})
    df_nav = df_nav.dropna(subset=["nav"])

    save_and_report(df_nav, "02_nav_history.csv", original_rows)


def clean_investor_transactions() -> None:
    """Standardise transaction types, validate amounts, and check KYC status values."""
    print("\n----- Cleaning: 08_investor_transactions.csv")
    df_tx = pd.read_csv(RAW_PATH / "08_investor_transactions.csv")
    original_rows = len(df_tx)

    df_tx["transaction_date"] = pd.to_datetime(df_tx["transaction_date"])
    df_tx["transaction_type"] = df_tx["transaction_type"].str.strip().str.title()
    print(f"  Transaction types found: {df_tx['transaction_type'].unique()}")

    invalid_amt = df_tx[df_tx["amount_inr"] <= 0]
    if len(invalid_amt) > 0:
        print(f"  {len(invalid_amt)} transactions with amount <= 0 — removing")
        df_tx = df_tx[df_tx["amount_inr"] > 0]
    else:
        print("  All amount_inr values > 0")

    valid_kyc = ["Verified", "Pending"]
    df_tx["kyc_status"] = df_tx["kyc_status"].str.strip().str.title()
    invalid_kyc = df_tx[~df_tx["kyc_status"].isin(valid_kyc)]
    if len(invalid_kyc) > 0:
        print(f"  {len(invalid_kyc)} rows with invalid KYC status: {invalid_kyc['kyc_status'].unique()}")
    else:
        print(f"  KYC status values valid: {df_tx['kyc_status'].unique()}")

    df_tx = df_tx.drop_duplicates()
    save_and_report(df_tx, "08_investor_transactions.csv", original_rows)


def clean_scheme_performance() -> None:
    """Validate numeric return/risk columns and flag expense ratio / Sharpe anomalies."""
    print("\n----- Cleaning: 07_scheme_performance.csv")
    df_perf = pd.read_csv(RAW_PATH / "07_scheme_performance.csv")
    original_rows = len(df_perf)

    numeric_cols = [
        "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
        "sharpe_ratio", "sortino_ratio", "alpha", "beta",
        "max_drawdown_pct", "std_dev_ann_pct",
    ]
    for col in numeric_cols:
        df_perf[col] = pd.to_numeric(df_perf[col], errors="coerce")
        nulls = df_perf[col].isnull().sum()
        if nulls > 0:
            print(f"  {col}: {nulls} non-numeric values found -> set to NaN")

    expense_issues = df_perf[
        (df_perf["expense_ratio_pct"] < 0.1) | (df_perf["expense_ratio_pct"] > 2.5)
    ]
    if len(expense_issues) > 0:
        print(f"  {len(expense_issues)} funds with expense_ratio outside 0.1-2.5% range:")
        print(expense_issues[["scheme_name", "expense_ratio_pct"]])
    else:
        print("  All expense ratios within valid range (0.1% - 2.5%)")

    negative_sharpe = df_perf[df_perf["sharpe_ratio"] < 0]
    if len(negative_sharpe) > 0:
        print(f"  {len(negative_sharpe)} funds with negative Sharpe ratio (underperforming risk-free rate):")
        print(negative_sharpe[["scheme_name", "sharpe_ratio"]])

    save_and_report(df_perf, "07_scheme_performance.csv", original_rows)


def light_clean_remaining() -> None:
    """Parse date columns and drop duplicates for the remaining 7 CSVs."""
    light_clean_files = {
        "01_fund_master.csv": ["launch_date"],
        "03_aum_by_fund_house.csv": ["date"],
        "04_monthly_sip_inflows.csv": ["month"],
        "05_category_inflows.csv": ["month"],
        "06_industry_folio_count.csv": ["month"],
        "09_portfolio_holdings.csv": ["portfolio_date"],
        "10_benchmark_indices.csv": ["date"],
    }

    for filename, date_cols in light_clean_files.items():
        print(f"\n----- Light cleaning: {filename}")
        df = pd.read_csv(RAW_PATH / filename)
        original_rows = len(df)

        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        df = df.drop_duplicates()
        save_and_report(df, filename, original_rows)


if __name__ == "__main__":
    print("=" * 60)
    print("STARTING DATA CLEANING PIPELINE")
    print("=" * 60)

    clean_nav_history()
    clean_investor_transactions()
    clean_scheme_performance()
    light_clean_remaining()

    print("=" * 60)
    print("ALL 10 DATASETS CLEANED AND SAVED TO data/processed/")
    print("=" * 60)