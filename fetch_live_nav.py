"""
Live NAV Fetch Script — Bluestock MF Analytics Platform
Day 1: Fetches live NAV data from mfapi.in for key schemes and
validates AMFI code consistency between fund_master and nav_history.
"""

import requests
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw"
BASE_URL = "https://api.mfapi.in/mf/"

SCHEMES = {
    "HDFC_Top_100_Direct": 125497,
    "SBI Bluechip": 119551,
    "ICICI Bluechip": 120503,
    "Nippon Large Cap": 118632,
    "Axis Bluechip": 119092,
    "Kotak Bluechip": 120841,
}


def fetch_scheme_nav(fund_name: str, scheme_code: int) -> pd.DataFrame | None:
    """Fetch NAV history for a single scheme from mfapi.in. Returns None on failure."""
    url = f"{BASE_URL}{scheme_code}"
    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.ConnectionError:
        print(f"Connection error for {fund_name}: check your internet.")
        return None
    except requests.exceptions.Timeout:
        print(f"Timeout for {fund_name}: API might be slow.")
        return None

    if response.status_code != 200:
        print(f"Failed to fetch {fund_name}: status {response.status_code}")
        return None

    data = response.json()
    fund_meta = data.get("meta", {})
    nav_data = data.get("data", [])

    print(f"{fund_name} (Code: {scheme_code})")
    print(f"  Fund: {fund_meta.get('scheme_name', 'N/A')}")
    print(f"  Category: {fund_meta.get('scheme_category', 'N/A')}")
    print(f"  Total NAV records: {len(nav_data)}")
    if nav_data:
        print(f"  Latest NAV: ₹{nav_data[0]['nav']} on {nav_data[0]['date']}")

    df = pd.DataFrame(nav_data)
    df["scheme_code"] = scheme_code
    df["scheme_name"] = fund_name
    df["fund_house"] = fund_meta.get("fund_house", "N/A")

    save_path = RAW_DATA_PATH / f"live_nav_{fund_name}.csv"
    df.to_csv(save_path, index=False)
    print(f"  Saved to {save_path}")
    return df


def fetch_all_schemes(schemes: dict) -> pd.DataFrame:
    """Fetch NAV for all schemes, save individual + combined CSVs, return combined DataFrame."""
    print("Fetching live NAV data from mfapi.in...\n")
    print("=" * 60)

    all_nav_data = []
    for fund_name, scheme_code in schemes.items():
        df = fetch_scheme_nav(fund_name, scheme_code)
        if df is not None:
            all_nav_data.append(df)
        print("-" * 60)

    if not all_nav_data:
        print("No NAV data fetched.")
        return pd.DataFrame()

    combined_df = pd.concat(all_nav_data, ignore_index=True)
    combined_path = RAW_DATA_PATH / "live_nav_all_schemes.csv"
    combined_df.to_csv(combined_path, index=False)

    print(f"\nCombined records: {combined_df.shape[0]}")
    print(f"Columns: {list(combined_df.columns)}")
    return combined_df


def validate_amfi_codes() -> None:
    """Cross-check AMFI codes between fund_master and nav_history, print data quality summary."""
    print("\n" + "=" * 60)
    print("AMFI CODE VALIDATION")
    print("=" * 60)

    try:
        fund_master = pd.read_csv(RAW_DATA_PATH / "01_fund_master.csv")
        nav_history = pd.read_csv(RAW_DATA_PATH / "02_nav_history.csv")
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return

    fund_codes = set(fund_master["amfi_code"].astype(str).unique())
    nav_codes = set(nav_history["amfi_code"].astype(str).unique())

    missing_in_nav = fund_codes - nav_codes
    extras_in_nav = nav_codes - fund_codes

    print(f"Fund master AMFI codes: {len(fund_codes)}")
    print(f"NAV history AMFI codes: {len(nav_codes)}")

    if missing_in_nav:
        print(f"\nAMFI codes in fund_master NOT in nav_history: {len(missing_in_nav)}")
        print(missing_in_nav)
    else:
        print("\nAll fund_master AMFI codes exist in nav_history.")

    if extras_in_nav:
        print(f"\nAMFI codes in nav_history NOT in fund_master: {len(extras_in_nav)}")
        print(extras_in_nav)

    print("\n" + "=" * 60)
    print("DATA QUALITY SUMMARY")
    print("=" * 60)
    completeness = round((1 - len(missing_in_nav) / len(fund_codes)) * 100, 2)
    print(f"Total schemes in fund_master:    {len(fund_codes)}")
    print(f"Total schemes with NAV history:  {len(nav_codes)}")
    print(f"Schemes missing NAV data:        {len(missing_in_nav)}")
    print(f"Orphan NAV records:              {len(extras_in_nav)}")
    print(f"Data completeness:               {completeness}%")


if __name__ == "__main__":
    fetch_all_schemes(SCHEMES)
    validate_amfi_codes()