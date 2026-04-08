"""Borrower archetype generation and borrower scorecard assembly."""

from pathlib import Path

import numpy as np
import pandas as pd

from src.output import save_csv
from src.utils import risk_band, score_gap_higher_is_worse, score_gap_lower_is_worse, score_icr


def _generate_borrowers(public_df: pd.DataFrame, benchmark_df: pd.DataFrame) -> pd.DataFrame:
    df = public_df.merge(benchmark_df, on=["sector_key", "industry"], how="left", suffixes=("", "_benchmark"))
    rows = []
    for _, row in df.iterrows():
        stress = max(0.15, ((row["classification_risk_score"] + row["macro_risk_score"]) / 2 - 2.2) / 4)
        revenue = float(np.clip((row["sales_m_latest"] * 1_000_000) / 40_000, 6_000_000, 22_000_000))
        margin_base = row["ebitda_margin_pct_latest"]
        if pd.isna(margin_base):
            margin_base = 10.0
        margin = max(2.0, float(margin_base) - stress * 3.2)
        debt_to_ebitda = float(row["debt_to_ebitda_benchmark"]) * (1 + stress * 0.22)
        icr = max(1.1, float(row["icr_benchmark"]) - stress * 0.45)
        ar_days = float(row["ar_days_benchmark"]) * (1 + stress * 0.10)
        ap_days = float(row["ap_days_benchmark"]) * (1 + stress * 0.06)
        inventory_days = float(row["inventory_days_benchmark"]) * (1 + stress * 0.12)

        ebitda = revenue * margin / 100
        total_debt = ebitda * debt_to_ebitda
        interest_expense = ebitda / icr
        cogs_ratio = np.clip(1 - margin / 100, 0.45, 0.95)
        cogs_or_purchases = revenue * cogs_ratio

        rows.append(
            {
                "borrower_name": f'{row["industry"].replace(" and ", " & ")} Archetype',
                "industry": row["industry"],
                "sector_key": row["sector_key"],
                "revenue": round(revenue, 0),
                "ebitda": round(ebitda, 0),
                "total_debt": round(total_debt, 0),
                "interest_expense": round(interest_expense, 0),
                "accounts_receivable": round(revenue * ar_days / 365, 0),
                "accounts_payable": round(cogs_or_purchases * ap_days / 365, 0),
                "inventory": round(cogs_or_purchases * inventory_days / 365, 0),
                "cogs_or_purchases": round(cogs_or_purchases, 0),
                "borrower_profile_source": "public-data-generated sector archetype aligned to benchmark and risk settings",
            }
        )

    borrowers = pd.DataFrame(rows)
    borrowers["ebitda_margin_pct"] = borrowers["ebitda"] / borrowers["revenue"] * 100
    borrowers["debt_to_ebitda"] = borrowers["total_debt"] / borrowers["ebitda"]
    borrowers["icr"] = borrowers["ebitda"] / borrowers["interest_expense"]
    borrowers["ar_days"] = borrowers["accounts_receivable"] / borrowers["revenue"] * 365
    borrowers["ap_days"] = borrowers["accounts_payable"] / borrowers["cogs_or_purchases"] * 365
    borrowers["inventory_days"] = borrowers["inventory"] / borrowers["cogs_or_purchases"] * 365
    return borrowers


def build_bottom_up(public_df: pd.DataFrame, benchmark_df: pd.DataFrame, processed_dir: Path) -> pd.DataFrame:
    borrowers = _generate_borrowers(public_df, benchmark_df)

    df = borrowers.merge(
        public_df[["sector_key", "industry", "ebitda_margin_pct_latest", "classification_risk_score", "macro_risk_score"]],
        on="sector_key",
        how="left",
        suffixes=("", "_public"),
    )
    df = df.merge(
        benchmark_df[
            [
                "sector_key",
                "debt_to_ebitda_benchmark",
                "icr_benchmark",
                "ar_days_benchmark",
                "ap_days_benchmark",
                "inventory_days_benchmark",
                "benchmark_origin",
            ]
        ],
        on="sector_key",
        how="left",
    )

    df["ebitda_margin_score"] = [score_gap_lower_is_worse(a, b) for a, b in zip(df["ebitda_margin_pct"], df["ebitda_margin_pct_latest"])]
    df["debt_to_ebitda_score"] = [score_gap_higher_is_worse(a, b) for a, b in zip(df["debt_to_ebitda"], df["debt_to_ebitda_benchmark"])]
    df["icr_score"] = [score_icr(a, b) for a, b in zip(df["icr"], df["icr_benchmark"])]
    df["ar_days_score"] = [score_gap_higher_is_worse(a, b) for a, b in zip(df["ar_days"], df["ar_days_benchmark"])]
    df["ap_days_score"] = [score_gap_higher_is_worse(a, b) for a, b in zip(df["ap_days"], df["ap_days_benchmark"])]
    df["inventory_days_score"] = [score_gap_higher_is_worse(a, b) for a, b in zip(df["inventory_days"], df["inventory_days_benchmark"])]

    df["bottom_up_risk_score"] = (
        df[["ebitda_margin_score", "debt_to_ebitda_score", "icr_score", "ar_days_score", "ap_days_score", "inventory_days_score"]]
        .mean(axis=1)
        .round(2)
    )

    save_csv(df, processed_dir / "borrower_benchmark_comparison.csv")
    return df


def build_scorecard(bottom_up_df: pd.DataFrame, processed_dir: Path, output_tables_dir: Path) -> pd.DataFrame:
    """Combine structural, macro, and borrower views into the final borrower scorecard."""
    df = bottom_up_df.copy()
    df["final_industry_risk_score"] = (
        0.35 * df["classification_risk_score"]
        + 0.30 * df["macro_risk_score"]
        + 0.35 * df["bottom_up_risk_score"]
    ).round(2)
    df["risk_level"] = df["final_industry_risk_score"].apply(risk_band)
    summary = df[
        [
            "borrower_name",
            "industry",
            "classification_risk_score",
            "macro_risk_score",
            "bottom_up_risk_score",
            "final_industry_risk_score",
            "risk_level",
        ]
    ].sort_values(["final_industry_risk_score", "borrower_name"], ascending=[False, True])
    save_csv(summary, processed_dir / "borrower_industry_risk_scorecard.csv")
    save_csv(summary, output_tables_dir / "borrower_industry_risk_scorecard.csv")
    return summary
