from pathlib import Path

import pandas as pd

from src.load_public_data import parse_australian_industry_totals
from src.output import save_csv
from src.utils import normalise_text


TARGET_SECTOR_CONFIG = {
    "agriculture forestry and fishing": ("A", "Primary production and agribusiness"),
    "manufacturing": ("C", "Industrial and manufacturing"),
    "construction": ("E", "Building, civil and trade services"),
    "wholesale trade": ("F", "Wholesale and distribution"),
    "retail trade": ("G", "Consumer retail and discretionary"),
    "accommodation and food services": ("H", "Hospitality and leisure"),
    "transport postal and warehousing": ("I", "Freight, logistics and storage"),
    "professional scientific and technical services": ("M", "Professional and technical services"),
    "health care and social assistance private": ("Q", "Health and care services"),
}


def _score_cyclicality(sales_growth_pct: float) -> int:
    if pd.isna(sales_growth_pct):
        return 3
    if sales_growth_pct < 0:
        return 5
    if sales_growth_pct < 2:
        return 4
    if sales_growth_pct < 6:
        return 3
    if sales_growth_pct < 12:
        return 2
    return 1


def _score_rate_sensitivity(margin_pct: float, wages_pct: float) -> int:
    if pd.isna(margin_pct) and pd.isna(wages_pct):
        return 3
    margin_pct = 10 if pd.isna(margin_pct) else margin_pct
    wages_pct = 20 if pd.isna(wages_pct) else wages_pct
    pressure = wages_pct - margin_pct
    if pressure > 25:
        return 5
    if pressure > 15:
        return 4
    if pressure > 8:
        return 3
    if pressure > 2:
        return 2
    return 1


def _score_demand_dependency(sales_growth_pct: float, wages_pct: float) -> int:
    growth = 3 if pd.isna(sales_growth_pct) else sales_growth_pct
    wages = 20 if pd.isna(wages_pct) else wages_pct
    signal = wages / 8 - growth / 4
    if signal > 4.5:
        return 5
    if signal > 3.5:
        return 4
    if signal > 2.5:
        return 3
    if signal > 1.5:
        return 2
    return 1


def _score_external_shock(margin_pct: float, wages_pct: float, employment_000: float) -> int:
    margin = 10 if pd.isna(margin_pct) else margin_pct
    wages = 20 if pd.isna(wages_pct) else wages_pct
    employment_000 = 500 if pd.isna(employment_000) else employment_000
    signal = max(0, 14 - margin) + wages / 6 + min(employment_000 / 700, 2.5)
    if signal > 10.5:
        return 5
    if signal > 8.5:
        return 4
    if signal > 6.5:
        return 3
    if signal > 4.5:
        return 2
    return 1


def build_foundation(public_dir: Path, processed_dir: Path) -> pd.DataFrame:
    ai = parse_australian_industry_totals(public_dir / "81550DO001_202324.xlsx")
    ai["sector_key"] = ai["sector"].map(normalise_text)

    latest = ai[ai["year"] == "2023-24"].copy()
    prev = ai[ai["year"] == "2022-23"][["sector_key", "sales_m"]].rename(columns={"sales_m": "sales_m_prev"})
    latest = latest.merge(prev, on="sector_key", how="left")
    latest["sales_growth_pct"] = (latest["sales_m"] / latest["sales_m_prev"] - 1) * 100

    rows = []
    for _, row in latest.iterrows():
        sector_key = row["sector_key"]
        if sector_key not in TARGET_SECTOR_CONFIG:
            continue

        division_code, grouping = TARGET_SECTOR_CONFIG[sector_key]
        display_industry = row["sector"].title()
        if sector_key == "health care and social assistance private":
            display_industry = "Health Care and Social Assistance"
            sector_key = "health care and social assistance"

        cyclical_score = _score_cyclicality(row["sales_growth_pct"])
        rate_sensitivity_score = _score_rate_sensitivity(row["ebitda_margin_pct"], row["wages_to_sales_pct"])
        demand_dependency_score = _score_demand_dependency(row["sales_growth_pct"], row["wages_to_sales_pct"])
        external_shock_score = _score_external_shock(row["ebitda_margin_pct"], row["wages_to_sales_pct"], row["employment_000"])

        rows.append(
            {
                "anzsic_division_code": division_code,
                "industry": display_industry,
                "internal_grouping_example": grouping,
                "cyclical_score": cyclical_score,
                "rate_sensitivity_score": rate_sensitivity_score,
                "demand_dependency_score": demand_dependency_score,
                "external_shock_score": external_shock_score,
                "sales_growth_pct_foundation": row["sales_growth_pct"],
                "ebitda_margin_pct_foundation": row["ebitda_margin_pct"],
                "wages_to_sales_pct_foundation": row["wages_to_sales_pct"],
                "employment_000_foundation": row["employment_000"],
                "sector_key": sector_key,
            }
        )

    df = pd.DataFrame(rows).sort_values("industry").reset_index(drop=True)
    df["classification_risk_score"] = (
        df[["cyclical_score", "rate_sensitivity_score", "demand_dependency_score", "external_shock_score"]]
        .mean(axis=1)
        .round(2)
    )
    df["foundation_source"] = (
        "generated from ABS Australian Industry public data using deterministic bank-style classification rules"
    )
    save_csv(df, processed_dir / "industry_classification_foundation.csv")
    return df
