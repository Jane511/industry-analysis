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


STRUCTURAL_SCORE_ANCHORS = {
    "agriculture forestry and fishing": {
        "rate_sensitivity": 3,
        "demand_dependency": 4,
        "external_shock": 4,
    },
    "manufacturing": {
        "rate_sensitivity": 3,
        "demand_dependency": 4,
        "external_shock": 4,
    },
    "construction": {
        "rate_sensitivity": 4,
        "demand_dependency": 5,
        "external_shock": 4,
    },
    "wholesale trade": {
        "rate_sensitivity": 3,
        "demand_dependency": 3,
        "external_shock": 3,
    },
    "retail trade": {
        "rate_sensitivity": 4,
        "demand_dependency": 4,
        "external_shock": 4,
    },
    "accommodation and food services": {
        "rate_sensitivity": 4,
        "demand_dependency": 5,
        "external_shock": 4,
    },
    "transport postal and warehousing": {
        "rate_sensitivity": 3,
        "demand_dependency": 3,
        "external_shock": 3,
    },
    "professional scientific and technical services": {
        "rate_sensitivity": 2,
        "demand_dependency": 2,
        "external_shock": 2,
    },
    "health care and social assistance": {
        "rate_sensitivity": 2,
        "demand_dependency": 1,
        "external_shock": 2,
    },
    "health care and social assistance private": {
        "rate_sensitivity": 2,
        "demand_dependency": 1,
        "external_shock": 2,
    },
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


def _blend_with_anchor(raw_score: int, sector_key: str, metric: str) -> int:
    anchor = STRUCTURAL_SCORE_ANCHORS.get(sector_key, {}).get(metric)
    if anchor is None:
        return raw_score
    return int(round((raw_score + anchor) / 2))


def _score_rate_sensitivity(margin_pct: float, sector_key: str) -> int:
    if pd.isna(margin_pct):
        return 3
    if margin_pct < 6:
        raw_score = 5
    elif margin_pct < 9:
        raw_score = 4
    elif margin_pct < 12:
        raw_score = 3
    elif margin_pct < 16:
        raw_score = 2
    else:
        raw_score = 1
    return _blend_with_anchor(raw_score, sector_key, "rate_sensitivity")


def _score_demand_dependency(sales_growth_pct: float, sector_key: str) -> int:
    growth = 3 if pd.isna(sales_growth_pct) else sales_growth_pct
    if growth < -8:
        raw_score = 5
    elif growth < -2:
        raw_score = 4
    elif growth < 2:
        raw_score = 3
    elif growth < 6:
        raw_score = 2
    else:
        raw_score = 1
    return _blend_with_anchor(raw_score, sector_key, "demand_dependency")


def _score_external_shock(margin_pct: float, sales_growth_pct: float, sector_key: str) -> int:
    margin = 10 if pd.isna(margin_pct) else margin_pct
    growth = 3 if pd.isna(sales_growth_pct) else sales_growth_pct
    signal = max(0, 10 - margin) / 2 + max(0, 2 - growth / 4)
    if signal > 4.5:
        raw_score = 5
    elif signal > 3.0:
        raw_score = 4
    elif signal > 2.0:
        raw_score = 3
    elif signal > 1.0:
        raw_score = 2
    else:
        raw_score = 1
    return _blend_with_anchor(raw_score, sector_key, "external_shock")


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
        rate_sensitivity_score = _score_rate_sensitivity(row["ebitda_margin_pct"], sector_key)
        demand_dependency_score = _score_demand_dependency(row["sales_growth_pct"], sector_key)
        external_shock_score = _score_external_shock(row["ebitda_margin_pct"], row["sales_growth_pct"], sector_key)

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
        "generated from ABS Australian Industry public data using deterministic APRA-informed proxy classification rules"
    )
    save_csv(df, processed_dir / "industry_classification_foundation.csv")
    return df
