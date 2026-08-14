# Bluestock MF Analytics Platform

End-to-end Mutual Fund Analytics capstone built during the Data Analyst internship at **Bluestock Fintech**. Covers ETL, SQLite database design, exploratory data analysis, performance analytics (Sharpe/Sortino/Alpha/Beta), risk metrics (VaR/CVaR, HHI), an interactive Power BI dashboard, and a fund recommender — built on 40 mutual fund schemes across 10 AMCs with 46,000+ daily NAV records (2022–2026).

---

## Project Overview

| | |
|---|---|
| **Scope** | 40 fund schemes, 10 AMCs, 46,000+ daily NAV records |
| **Data window** | Jan 2022 – Dec 2025 (NAV, AUM, SIP, transactions) |
| **Stack** | Python, Pandas, NumPy, SciPy, Seaborn, Plotly, SQLAlchemy, SQLite, Power BI |
| **Deliverables** | ETL scripts, SQLite DB, EDA notebook, Performance Analytics notebook, Advanced Analytics notebook, Power BI dashboard (4 pages + drill-through), Fund Recommender |

**What it does:**
1. Ingests fund master, NAV history, AUM, SIP, transaction, portfolio holding, and benchmark index data (10 raw CSVs) plus live NAV via the [mfapi.in](https://www.mfapi.in/) API.
2. Cleans, validates, and loads everything into a SQLite star-schema database.
3. Explores the data — NAV trends, AUM growth, SIP inflows, investor demographics, sector concentration.
4. Computes fund performance metrics — CAGR, Sharpe, Sortino, Alpha/Beta (OLS vs Nifty 100), Max Drawdown, and a composite 0–100 Fund Scorecard.
5. Computes advanced risk metrics — Historical VaR/CVaR, rolling 90-day Sharpe, investor cohort behavior, SIP continuity/lapse risk, sector HHI concentration, and a risk-based fund recommender.
6. Visualizes everything in a 4-page interactive Power BI dashboard with drill-through and slicers.

---

## Folder Structure
```
MF_Analytics_Platform/
├── data/
│ ├── raw/ ← original downloaded CSVs + live NAV pulls
│ ├── processed/ ← cleaned CSVs + all computed metric outputs
│ └── db/ ← bluestock_mf.db (SQLite)
├── notebooks/
│ ├── EDA_Analysis.ipynb
│ ├── Performance_Analytics.ipynb
│ └── Advanced_Analytics.ipynb
├── scripts/
│ └── recommender.py
├── sql/
│ └── queries.sql
├── dashboard/
│ └── bluestock_mf_dashboard.pbix
├── reports/
│ ├── EDA_Findings.md
│ └── charts/ ← 12 exported PNG charts
├── data_ingestion.py
├── fetch_live_nav.py
├── data_cleaning.py
├── database_setup.py
├── data_dictionary.md
└── requirements.txt
```

---

## Setup Instructions

**1. Clone the repo and install dependencies:**
```bash
git clone <repo-url>
cd MF_Analytics_Platform
pip install -r requirements.txt
```

**2. Run the ETL pipeline (in order):**
```bash
python data_ingestion.py
python fetch_live_nav.py
python data_cleaning.py
python database_setup.py
```
This loads the 10 raw CSVs, fetches live NAV data from mfapi.in, cleans and validates everything, and builds `data/db/bluestock_mf.db`.

**3. Run the analytics notebooks (in order):**

notebooks/EDA_Analysis.ipynb
notebooks/Performance_Analytics.ipynb
notebooks/Advanced_Analytics.ipynb

Open in Jupyter and run top-to-bottom. Each notebook writes its outputs (CSVs, chart PNGs) to `data/processed/` and `reports/charts/`.

**4. Run the fund recommender (standalone):**
```bash
cd scripts
python recommender.py --risk High --top 3
```
`--risk` accepts `Low`, `Moderate`, or `High` (default: `Moderate`). `--top` controls number of results (default: 3).

**5. Open the dashboard:**
Open `dashboard/bluestock_mf_dashboard.pbix` in Power BI Desktop. Requires the SQLite ODBC driver if refreshing data via ODBC — see project notes for driver setup, or refresh directly from `data/processed/` CSVs.

---

## Dashboard Pages

| Page | Contents |
|---|---|
| **1. Industry Overview** | KPI cards (Total AUM, SIP Inflows, Folios, Schemes), industry AUM trend, AUM by AMC |
| **2. Fund Performance** | Return vs Risk scatter (bubble = AUM), sortable fund scorecard, NAV vs benchmark, slicers (fund house, category, plan) |
| **3. Investor Analytics** | Transaction amount by state, SIP/Lumpsum/Redemption split, age group vs avg SIP, monthly transaction volume, slicers (state, age group, city tier) |
| **4. SIP & Market Trends** | SIP inflow vs Nifty 50 dual-axis, category inflow heatmap, top 5 categories by FY25 net inflow |
| **5. NAV Details (hidden)** | Drill-through detail page from the fund scorecard table |

---

## Key Datasets

| File | Description |
|---|---|
| `01_fund_master.csv` | Fund metadata — AMFI code, scheme name, fund house, category, risk category, expense ratio |
| `02_nav_history.csv` | Daily NAV per scheme, 2022–2026 |
| `03_aum_by_fund_house.csv` | AUM by fund house, yearly |
| `04_monthly_sip_inflows.csv` | Monthly industry-wide SIP inflow |
| `05_category_inflows.csv` | Net inflow by fund category, monthly |
| `06_industry_folio_count.csv` | Total investor folio count over time |
| `07_scheme_performance.csv` | Pre-computed return/risk metrics per scheme |
| `08_investor_transactions.csv` | Investor-level SIP/Lumpsum/Redemption transactions |
| `09_portfolio_holdings.csv` | Sector-wise portfolio weight per fund |
| `10_benchmark_indices.csv` | Nifty 50, Nifty 100, BSE SmallCap daily index values |

**Computed outputs** (in `data/processed/`): `returns_computed.csv`, `cagr_report.csv`, `sharpe_values.csv`, `sortino_values.csv`, `alpha_beta.csv`, `max_drawdown.csv`, `fund_scorecard.csv`, `var_cvar_report.csv`.

---

## Methodology Notes

- **Risk-free rate:** 6.5% (RBI repo rate proxy), used in Sharpe and Sortino calculations.
- **Annualization:** 252 trading days/year used throughout (not calendar days) for CAGR, Sharpe, Sortino, Alpha, and tracking error.
- **Benchmark:** Nifty 100 used for Alpha/Beta regression; Nifty 50 and Nifty 100 both used in benchmark comparison charts.
- **Fund Scorecard weighting:** 30% 3yr return rank + 25% Sharpe rank + 20% Alpha rank + 15% expense ratio rank (inverse) + 10% max drawdown rank (inverse), normalized to 0–100.
- **VaR/CVaR:** 95% confidence, historical method (5th percentile of daily returns; CVaR = mean of returns beyond that threshold).
- **HHI:** Sector concentration index, scaled 0–10,000 (Σ weight² × 10,000). >2,500 = highly concentrated.

---

## Limitations

- Dataset is a 40-fund sample, not full AMFI industry data (~1,908 real schemes) — KPI totals reflect this smaller scope, not true industry-wide figures.
- NAV/transaction data is a mix of live-fetched and generated sample data for project purposes; not suitable for real investment decisions.
- Fund recommender uses Sharpe ratio only within a matched risk bucket — a simplified heuristic, not a full portfolio-optimization approach.

---

## Author

**Madanala Abhishek Varma** — B.Tech CSE (2026), Data Analyst Intern, Bluestock Fintech