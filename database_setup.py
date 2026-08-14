"""
Database Setup Script — Bluestock MF Analytics Platform
Day 2: Creates the SQLite star schema (from sql/schema.sql), builds the
dim_date dimension, and loads all cleaned CSVs into the database.
"""

import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_PATH = BASE_DIR / "data" / "processed"
DB_PATH = BASE_DIR / "data" / "db"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"
DB_PATH.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH / 'bluestock_mf.db'}", echo=False)


def create_schema() -> None:
    """Execute all CREATE TABLE statements from sql/schema.sql."""
    print("=" * 60)
    print("CREATING STAR SCHEMA DATABASE")
    print("=" * 60)

    schema_sql = SCHEMA_PATH.read_text()
    with engine.connect() as conn:
        for statement in schema_sql.strip().split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))
        conn.commit()

    print("Star schema created successfully.\n")


def create_dim_date() -> None:
    """Build and load the dim_date dimension table (2022-2026 daily calendar)."""
    print("----- Creating dim_date dimension...")
    date_range = pd.date_range(start="2022-01-01", end="2026-12-31", freq="D")
    dim_date = pd.DataFrame({
        "date_id": date_range.strftime("%Y-%m-%d"),
        "year": date_range.year,
        "month": date_range.month,
        "quarter": date_range.quarter,
        "month_name": date_range.strftime("%B"),
        "is_weekday": (date_range.dayofweek < 5).astype(int),
    })
    dim_date.to_sql("dim_date", engine, if_exists="replace", index=False)
    print(f"dim_date loaded: {len(dim_date)} rows\n")


def load_table(filename: str, table_name: str, if_exists: str = "replace") -> None:
    """Load a processed CSV into the database and verify the row count matches."""
    df = pd.read_csv(PROCESSED_PATH / filename)
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)

    db_count = pd.read_sql(f"SELECT COUNT(*) as cnt FROM {table_name}", engine).iloc[0]["cnt"]
    status = "OK" if len(df) == db_count else "MISMATCH"
    print(f"[{status}] {table_name}: {len(df)} source rows -> {db_count} in DB")


def load_all_tables() -> None:
    """Load all cleaned CSVs into their corresponding fact/dim tables."""
    print("=" * 60)
    print("LOADING CLEANED DATA INTO DATABASE")
    print("=" * 60)

    load_table("01_fund_master.csv", "dim_fund")
    load_table("02_nav_history.csv", "fact_nav")
    load_table("08_investor_transactions.csv", "fact_transactions")
    load_table("07_scheme_performance.csv", "fact_performance")
    load_table("03_aum_by_fund_house.csv", "fact_aum")
    load_table("04_monthly_sip_inflows.csv", "fact_sip")

    print("\n" + "=" * 60)
    print("DATABASE LOADING COMPLETE")
    print(f"Location: {DB_PATH / 'bluestock_mf.db'}")
    print("=" * 60)


if __name__ == "__main__":
    create_schema()
    create_dim_date()
    load_all_tables()