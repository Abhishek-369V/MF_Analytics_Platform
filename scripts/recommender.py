"""
Simple Fund Recommender — Bluestock MF Analytics Platform
Day 6: Recommends top N funds by risk appetite, ranked by Sharpe ratio.
"""

import pandas as pd
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED = BASE_DIR / "data" / "processed"


def load_data():
    df_fund = pd.read_csv(PROCESSED / "01_fund_master.csv")
    df_sharpe = pd.read_csv(PROCESSED / "sharpe_values.csv")
    return df_fund, df_sharpe


def recommend_funds(risk_appetite: str, top_n: int = 3) -> pd.DataFrame:
    df_fund, df_sharpe = load_data()

    risk_map = {
        "Low": ["Low"],
        "Moderate": ["Moderate", "Moderately High"],
        "High": ["High", "Very High"],
    }
    matching_risk = risk_map.get(risk_appetite, [])
    if not matching_risk:
        raise ValueError(f"Invalid risk_appetite: {risk_appetite}. Use Low, Moderate, or High.")

    matched = df_fund[df_fund["risk_category"].isin(matching_risk)][
        ["amfi_code", "scheme_name", "risk_category"]
    ]
    matched = matched.merge(df_sharpe[["amfi_code", "sharpe_ratio_computed"]], on="amfi_code")
    matched = matched.sort_values("sharpe_ratio_computed", ascending=False).head(top_n)

    return matched[["scheme_name", "risk_category", "sharpe_ratio_computed"]]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recommend mutual funds by risk appetite")
    parser.add_argument("--risk", type=str, default="Moderate", choices=["Low", "Moderate", "High"])
    parser.add_argument("--top", type=int, default=3)
    args = parser.parse_args()

    result = recommend_funds(args.risk, args.top)
    print(f"\nTop {args.top} Recommended Funds for '{args.risk}' Risk Appetite:\n")
    print(result.to_string(index=False))