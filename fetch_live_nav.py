import requests
import pandas as pd

# ============================================================
# LIVE NAV FETCH SCRIPT — Bluestock MF Analytics Platform
# Day 1: Fetch live NAV data from mfapi.in - (Task 4 & 5)
# ===========================================================

# Fetch NAV for 5 key schemes:
SCHEMES = {
    "HDFC_Top_100_Direct": 125497,
    "SBI Bluechip": 119551, 
    "ICICI Bluechip": 120503, 
    "Nippon Large Cap": 118632, 
    "Axis Bluechip": 119092, 
    "Kotak Bluechip": 120841
}    

BASE_URL = "https://api.mfapi.in/mf/" 

all_nav_data = []

print("Fetching live nav data from mfapi.in...\n")
print("=" *60)

for fund_name, scheme_code in SCHEMES.items():
    try:
        # Make API request - get
        url = f"{BASE_URL}{scheme_code}"  #Example : https://api.mfapi.in/mf/125497 (for HDFC Top 100 Direct)
        response = requests.get(url, timeout=10)

        # check if request was successful
        if response.status_code == 200:
            data = response.json()

            # extract metadata from data:
            fund_meta = data.get('meta', {})
            nav_data = data.get('data', [])

            print(f" {fund_name} (Code: {scheme_code})")
            print(f" Fund: {fund_meta.get('scheme_name', 'N/A')}")
            print(f" category: {fund_meta.get('scheme_category', 'N/A')}")
            print(f" Total NAV records: {len(nav_data)}")
            print(f" Latest NAV: ₹{nav_data[0]['nav'] if nav_data else 'N/A'}")
            print(f" Latest Date: ₹{nav_data[0]['date'] if nav_data else 'N/A'}")
            print()


            # converting nav_data into Dataframe
            df = pd.DataFrame(nav_data)
            df['scheme_code'] = scheme_code
            df['scheme_name'] = fund_name
            df['fund_house'] = fund_meta.get('fund_house', 'N/A')

            all_nav_data.append(df)

            # Save individual fund NAV as CSV
            save_path = f"data/raw/live_nav_{fund_name}.csv"
            df.to_csv(save_path, index=False)
            print(f" Saved to {save_path}")

        else:
            print(f"Failed to fetch {fund_name}: Status {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print(f" Connection error for {fund_name}: plz check your internet") 
    except requests.exceptions.Timeout:
        print(f" Timeout for {fund_name}: API might be slow")   
    except Exception as e:
        print(f" Unexpected error for {fund_name}: {e}")

    print("-" * 60)


# Combine all NAV data into one master CSV
if all_nav_data:
    combined_df = pd.concat(all_nav_data, ignore_index = True)
    combined_path = f"data/raw/live_nav_all_schemes.csv"
    combined_df.to_csv(combined_path, index=False)

    print(f"\n Combined_nav_data: {combined_df}")
    print(f" Total records: {combined_df.shape[0]}")
    print(f" Columns: {list(combined_df.columns)}")



# ============================================================
# AMFI CODE VALIDATION (Task 7)
# ============================================================

print("\n" + "=" * 60)
print("AMFI CODE VALIDATION")
print("=" * 60)

try:
    # Load fund master and nav history csv files:
    fund_master = pd.read_csv("data/raw/01_fund_master.csv")
    nav_history = pd.read_csv("data/raw/02_nav_history.csv")

    # get amfi codes for both  - here amfi codes works as sort of primary key
    fund_codes = set(fund_master['amfi_code'].astype(str).unique())
    nav_codes = set(nav_history['amfi_code'].astype(str).unique())

    # Find mistmatches:
    missing_in_nav = fund_codes - nav_codes
    extras_in_nav = nav_codes - fund_codes

    # checking len of them:
    print(f"\n Length of fund master amfi codes: {len(fund_codes)}")
    print(f" Length of nav_history amfi codes: {len(nav_codes)}")

    if missing_in_nav:
        print(f"\n amfi codes in fund master NOT in nav_history {len(missing_in_nav)}")
        print(missing_in_nav)
    else:
        print(f"\n  ALL fund_master amfi codes exists in nav_history")

    if extras_in_nav:
        print(f"\n amfi codes in nav history NOT in fund master {len(extras_in_nav)}")
        print(extras_in_nav)

    # Data quality summary
    print("\n" + "=" * 60)
    print("DATA QUALITY SUMMARY")
    print("=" * 60)
    print(f"Total schemes in fund_master:     {len(fund_codes)}")
    print(f"Total schemes with NAV history:   {len(nav_codes)}")
    print(f"Schemes missing NAV data:         {len(missing_in_nav)}")
    print(f"Orphan NAV records:               {len(extras_in_nav)}")
    print(f"Data completeness:                {round((1 - len(missing_in_nav)/len(fund_codes))*100, 2)}%")


except FileNotFoundError as e:
    print(f" File not found: {e}")    