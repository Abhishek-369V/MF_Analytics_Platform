# Data Dictionary — Bluestock MF Analytics Platform

## dim_fund (40 rows)
| Column | Type | Description |
|--------|------|-------------|
| amfi_code | INTEGER PK | AMFI unique scheme identifier |
| fund_house | TEXT | AMC name (e.g. SBI Mutual Fund) |
| scheme_name | TEXT | Full official AMFI scheme name |
| category | TEXT | Equity or Debt |
| sub_category | TEXT | Large Cap, Mid Cap, Small Cap etc. |
| plan | TEXT | Regular or Direct |
| expense_ratio_pct | REAL | Annual fee % (valid range: 0.1-2.5%) |
| risk_category | TEXT | SEBI risk: Low/Moderate/High/Very High |

## fact_nav (46,000+ rows)
| Column | Type | Description |
|--------|------|-------------|
| amfi_code | INTEGER FK | Links to dim_fund |
| date | TEXT | Trading date (YYYY-MM-DD) |
| nav | REAL | NAV in ₹, forward-filled for holidays |

## fact_transactions (32,778 rows)
| Column | Type | Description |
|--------|------|-------------|
| investor_id | TEXT | Unique investor ID (INV000001+) |
| transaction_type | TEXT | SIP / Lumpsum / Redemption |
| amount_inr | INTEGER | Transaction amount in ₹ |
| city_tier | TEXT | T30 (top cities) or B30 (smaller cities) |
| kyc_status | TEXT | Verified or Pending |

## fact_performance (40 rows)
| Column | Type | Description |
|--------|------|-------------|
| sharpe_ratio | REAL | Risk-adjusted return (>1 = good) |
| alpha | REAL | Return above benchmark (positive = outperforming) |
| beta | REAL | Market sensitivity (1.0 = moves with market) |
| max_drawdown_pct | REAL | Worst peak-to-trough decline (negative) |

## Sources
- AMFI India: amfiindia.com
- mfapi.in: Live NAV API
- NSE/BSE: Benchmark indices