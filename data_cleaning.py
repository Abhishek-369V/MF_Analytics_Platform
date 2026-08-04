import pandas as pd
import numpy as np
import os

# ============================================================
# DAY 2: DATA CLEANING SCRIPT
# Bluestock MF Analytics Platform
# ============================================================

RAW_PATH = "data/raw"
PROCESSED_PATH = "data/processed"
os.makedirs(PROCESSED_PATH, exist_ok=True)

print("=" * 60)
print("STARTING DATA CLEANING PIPELINE")
print("=" * 60)

# ─────────────────────────────────────────────
# HELPER FUNCTION: Save + Report
# ─────────────────────────────────────────────
def save_and_report(df, filename, original_rows):
    path = os.path.join(PROCESSED_PATH, filename)
    df.to_csv(path, index=False)
    print(f"  SAVED: {filename}")
    print(f"  ROWS: {original_rows} -> {len(df)} ({original_rows - len(df)} removed)")
    print()


# ─────────────────────────────────────────────
# 1. CLEAN: 02_nav_history.csv
# ─────────────────────────────────────────────
print("\n ----- Cleaning: 02_nav_history.csv")
df_nav = pd.read_csv(os.path.join(RAW_PATH, "02_nav_history.csv"))
original_rows = len(df_nav)

# parsing dates str to datetime
df_nav['date'] = pd.to_datetime(df_nav['date'])

#  sort by amfi_code + date ----> (required for ffill to work correctly)
df_nav = df_nav.sort_values(['amfi_code', 'date']).reset_index(drop=True)

# Remove Duplicates
df_nav = df_nav.drop_duplicates(subset=['amfi_code', 'date'])

# Validate NAV > 0 (flag and remove invalid)
invalid_nav = df_nav[df_nav['nav'] <= 0]
if len(invalid_nav)>0:
    print(f"  Found {len(invalid_nav)} rows with NAV <= 0 ----> removing")
    df_nav = df_nav[df_nav['nav'] > 0]
else:
    print(f"  All NAV values > 0")

# Forward-fill missing dates (weekends/holidays)
# Create complete date range for each fund and ffill
df_nav = df_nav.set_index('date')
df_nav_filled = []

for code in df_nav['amfi_code'].unique():
    fund_df = df_nav[df_nav['amfi_code'] == code].copy()
    # Reindex to full date range
    full_range = pd.date_range(start=fund_df.index.min(), 
                                end=fund_df.index.max(), 
                                freq='D')  
    fund_df = fund_df.reindex(full_range)
    fund_df['amfi_code'] = code
    # Forward fill NAV for weekends/holidays
    fund_df['nav'] = fund_df['nav'].ffill()
    df_nav_filled.append(fund_df)

df_nav = pd.concat(df_nav_filled).reset_index()
df_nav.rename(columns={'index': 'date'}, inplace=True)
df_nav = df_nav.dropna(subset=['nav'])  # drop any remaining NaN

save_and_report(df_nav, "02_nav_history.csv", original_rows)


# ─────────────────────────────────────────────
# 2. CLEAN: 08_investor_transactions.csv
# ─────────────────────────────────────────────
print("\n ----- Cleaning: 08_investor_transactions.csv")
df_tx = pd.read_csv(os.path.join(RAW_PATH, "08_investor_transactions.csv"))
original_rows = len(df_tx)

# Fix date format
df_tx['transaction_date'] = pd.to_datetime(df_tx['transaction_date'])

# Standardise transaction_type — strip spaces + title case
df_tx['transaction_type'] = df_tx['transaction_type'].str.strip().str.title()
print(f"  Transaction types found: {df_tx['transaction_type'].unique()}")

# Validate amount > 0
invalid_amt = df_tx[df_tx['amount_inr'] <= 0]
if len(invalid_amt) > 0:
    print(f"    {len(invalid_amt)} transactions with amount <= 0 — removing")
    df_tx = df_tx[df_tx['amount_inr'] > 0]
else: 
    print(f"    All amount_inr values > 0")

# Check KYC status enum values
valid_kyc = ['Verified', 'Pending']
df_tx['kyc_status'] = df_tx['kyc_status'].str.strip().str.title()
invalid_kyc = df_tx[~df_tx['kyc_status'].isin(valid_kyc)]
if len(invalid_kyc) > 0:
    print(f"   {len(invalid_kyc)} rows with invalid KYC status")
    print(f"     Values found: {invalid_kyc['kyc_status'].unique()}")
else:
    print(f"   KYC status values valid: {df_tx['kyc_status'].unique()}")

# Remove duplicates
df_tx = df_tx.drop_duplicates()

save_and_report(df_tx, "08_investor_transactions.csv", original_rows)


# ─────────────────────────────────────────────
# 3. CLEAN: 07_scheme_performance.csv (MEDIUM)
# ─────────────────────────────────────────────
print("\n ----- Cleaning: 07_scheme_performance.csv")
df_perf = pd.read_csv(os.path.join(RAW_PATH, "07_scheme_performance.csv"))
original_rows = len(df_perf)

# Validate return values are numeric
numeric_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct',
                'sharpe_ratio', 'sortino_ratio', 'alpha', 'beta',
                'max_drawdown_pct', 'std_dev_ann_pct']

for col in numeric_cols:
    df_perf[col] = pd.to_numeric(df_perf[col], errors='coerce')
    nulls = df_perf[col].isnull().sum()
    if nulls > 0:
        print(f"    {col}: {nulls} non-numeric values found → set to NaN")

# Check expense_ratio range (0.1% to 2.5%)
expense_issues = df_perf[
    (df_perf['expense_ratio_pct'] < 0.1) | 
    (df_perf['expense_ratio_pct'] > 2.5)
]
if len(expense_issues) > 0:
    print(f"    {len(expense_issues)} funds with expense_ratio outside 0.1-2.5% range:")
    print(expense_issues[['scheme_name', 'expense_ratio_pct']])
else:
    print(f"   All expense ratios within valid range (0.1% - 2.5%)")

# Flag negative Sharpe ratios
negative_sharpe = df_perf[df_perf['sharpe_ratio'] < 0]
if len(negative_sharpe) > 0:
    print(f"    {len(negative_sharpe)} funds with negative Sharpe ratio (underperforming risk-free rate):")
    print(negative_sharpe[['scheme_name', 'sharpe_ratio']])

save_and_report(df_perf, "07_scheme_performance.csv", original_rows)


# ─────────────────────────────────────────────
# 4. LIGHT CLEAN: Remaining 7 CSVs
#    (date conversion + remove duplicates - save)
# ─────────────────────────────────────────────
light_clean_files = {
    "01_fund_master.csv": ['launch_date'],
    "03_aum_by_fund_house.csv": ['date'],
    "04_monthly_sip_inflows.csv": ['month'],
    "05_category_inflows.csv": ['month'],
    "06_industry_folio_count.csv": ['month'],
    "09_portfolio_holdings.csv": ['portfolio_date'],
    "10_benchmark_indices.csv": ['date']
}

for filename, date_cols in light_clean_files.items():
    print(f"\n ----- Light cleaning: {filename}")
    df = pd.read_csv(os.path.join(RAW_PATH, filename))
    original_rows = len(df)
    
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    df = df.drop_duplicates()
    save_and_report(df, filename, original_rows)

print("=" * 60)
print("✅ ALL 10 DATASETS CLEANED AND SAVED TO data/processed/")
print("=" * 60)