import pandas as pd
from sqlalchemy import create_engine, text
import os

# ============================================================
# DAY 2: DATABASE SETUP + LOADING
# Star Schema Design for Bluestock MF Analytics
# ============================================================

PROCESSED_PATH = "data/processed/"
DB_PATH = "data/db/"
os.makedirs(DB_PATH, exist_ok=True)

# Create SQLite database
engine = create_engine(f'sqlite:///{DB_PATH}/bluestock_mf.db', echo=False)

print("=" * 60)
print(" ----- CREATING STAR SCHEMA DATABASE")
print("=" * 60)

# ─────────────────────────────────────────────
# STEP 1: CREATE TABLES (Star Schema)
# ─────────────────────────────────────────────
schema_sql = """
-- ============================================
-- DIMENSION TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code           INTEGER PRIMARY KEY,
    fund_house          TEXT NOT NULL,
    scheme_name         TEXT NOT NULL,
    category            TEXT,
    sub_category        TEXT,
    plan                TEXT,
    launch_date         TEXT,
    benchmark           TEXT,
    expense_ratio_pct   REAL,
    exit_load_pct       REAL,
    min_sip_amount      INTEGER,
    min_lumpsum_amount  INTEGER,
    fund_manager        TEXT,
    risk_category       TEXT,
    sebi_category_code  TEXT
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id     TEXT PRIMARY KEY,
    year        INTEGER,
    month       INTEGER,
    quarter     INTEGER,
    month_name  TEXT,
    is_weekday  INTEGER
);

-- ============================================
-- FACT TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS fact_nav (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code   INTEGER,
    date        TEXT,
    nav         REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_transactions (
    tx_id               TEXT PRIMARY KEY,
    investor_id         TEXT,
    transaction_date    TEXT,
    amfi_code           INTEGER,
    transaction_type    TEXT,
    amount_inr          INTEGER,
    state               TEXT,
    city                TEXT,
    city_tier           TEXT,
    age_group           TEXT,
    gender              TEXT,
    annual_income_lakh  REAL,
    payment_mode        TEXT,
    kyc_status          TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code           INTEGER PRIMARY KEY,
    scheme_name         TEXT,
    return_1yr_pct      REAL,
    return_3yr_pct      REAL,
    return_5yr_pct      REAL,
    benchmark_3yr_pct   REAL,
    alpha               REAL,
    beta                REAL,
    sharpe_ratio        REAL,
    sortino_ratio       REAL,
    std_dev_ann_pct     REAL,
    max_drawdown_pct    REAL,
    aum_crore           INTEGER,
    expense_ratio_pct   REAL,
    morningstar_rating  INTEGER,
    risk_grade          TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_aum (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT,
    fund_house      TEXT,
    aum_lakh_crore  REAL,
    aum_crore       INTEGER,
    num_schemes     INTEGER
);

CREATE TABLE IF NOT EXISTS fact_sip (
    id                          INTEGER PRIMARY KEY AUTOINCREMENT,
    month                       TEXT,
    sip_inflow_crore            INTEGER,
    active_sip_accounts_crore   REAL,
    new_sip_accounts_lakh       REAL,
    sip_aum_lakh_crore          REAL,
    yoy_growth_pct              REAL
);
"""

# Execute schema creation
with engine.connect() as conn:
    for statement in schema_sql.strip().split(';'):
        statement = statement.strip()
        if statement:
            conn.execute(text(statement))
    conn.commit()

print(" Star schema created successfully")
print()

# ─────────────────────────────────────────────
# STEP 2: CREATE dim_date TABLE
# ─────────────────────────────────────────────
print(" ----- Creating dim_date dimension...")
date_range = pd.date_range(start='2022-01-01', end='2026-12-31', freq='D')
dim_date = pd.DataFrame({
    'date_id':    date_range.strftime('%Y-%m-%d'),
    'year':       date_range.year,
    'month':      date_range.month,
    'quarter':    date_range.quarter,
    'month_name': date_range.strftime('%B'),
    'is_weekday': (date_range.dayofweek < 5).astype(int)
})
dim_date.to_sql('dim_date', engine, if_exists='replace', index=False)
print(f" dim_date loaded: {len(dim_date)} rows")

# ─────────────────────────────────────────────
# STEP 3: LOAD ALL CLEANED DATA INTO DB
# ─────────────────────────────────────────────
print()
print("=" * 60)
print(" ----- LOADING CLEANED DATA INTO DATABASE")
print("=" * 60)

def load_table(filename, table_name, if_exists='replace'):
    path = os.path.join(PROCESSED_PATH, filename)
    df = pd.read_csv(path)
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    
    # Verify row count
    db_count = pd.read_sql(
        f"SELECT COUNT(*) as cnt FROM {table_name}", engine
    ).iloc[0]['cnt']
    
    status = "✅" if len(df) == db_count else "❌"
    print(f"{status} {table_name}: {len(df)} source rows → {db_count} in DB")

load_table("01_fund_master.csv",           "dim_fund")
load_table("02_nav_history.csv",           "fact_nav")
load_table("08_investor_transactions.csv", "fact_transactions")
load_table("07_scheme_performance.csv",    "fact_performance")
load_table("03_aum_by_fund_house.csv",     "fact_aum")
load_table("04_monthly_sip_inflows.csv",   "fact_sip")

print()
print("=" * 60)
print(" DATABASE LOADING COMPLETE")
print(f"  Location: data/db/bluestock_mf.db")
print("=" * 60)