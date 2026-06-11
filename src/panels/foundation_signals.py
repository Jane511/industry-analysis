"""Stage 1: structural industry classification signals.

Normalises ABS Australian Industry totals into an 18-division foundation
table keyed by ANZSIC division code (A..S, excluding K — Financial &
Insurance Services is out of scope for this overlay). Anchor integers in
``STRUCTURAL_SCORE_ANCHORS`` are the APRA-informed priors that the
engine blends with live ABS signals to produce the structural sub-scores.
Full per-anchor citations are maintained in ``docs/anchor_sources.md``.
"""

from pathlib import Path

import pandas as pd

from src.public_data.load_abs_manual_exports import parse_australian_industry_totals
from src.public_data.staged_files import resolve_staged_file
from src.output import save_csv
from src.utils import normalise_text


# ABS Australian Industry reports three divisions suffixed with "(private)"
# — Health, Public Administration, and Education — because the public-sector
# totals are excluded. These aliases normalise those sector keys back to the
# canonical ANZSIC division label used throughout the engine.
PRIVATE_SUFFIX_SECTORS: frozenset[str] = frozenset(
    {
        "health care and social assistance",
        "public administration and safety",
        "education and training",
    }
)


def _normalise_sector_key(raw: str) -> str:
    """Normalise an ABS sector label into a canonical join key.

    Lower-cases, strips punctuation (via ``normalise_text``), and drops the
    trailing ``" private"`` token produced by ABS's ``(private)`` suffix on
    Health, Public Administration, and Education. Any other sector passes
    through unchanged.
    """
    key = normalise_text(raw)
    if key.endswith(" private"):
        stripped = key[: -len(" private")].strip()
        if stripped in PRIVATE_SUFFIX_SECTORS:
            return stripped
    return key


# Canonical ANZSIC division display names. The ABS publishes these with
# lowercase "and" connectors; preserving that style here keeps the report
# tables consistent regardless of which sector the row describes.
ANZSIC_DIVISION_DISPLAY_NAMES: dict[str, str] = {
    "agriculture forestry and fishing": "Agriculture, Forestry and Fishing",
    "mining": "Mining",
    "manufacturing": "Manufacturing",
    "electricity gas water and waste services": "Electricity, Gas, Water and Waste Services",
    "construction": "Construction",
    "wholesale trade": "Wholesale Trade",
    "retail trade": "Retail Trade",
    "accommodation and food services": "Accommodation and Food Services",
    "transport postal and warehousing": "Transport, Postal and Warehousing",
    "information media and telecommunications": "Information Media and Telecommunications",
    "rental hiring and real estate services": "Rental, Hiring and Real Estate Services",
    "professional scientific and technical services": "Professional, Scientific and Technical Services",
    "administrative and support services": "Administrative and Support Services",
    "public administration and safety": "Public Administration and Safety",
    "education and training": "Education and Training",
    "health care and social assistance": "Health Care and Social Assistance",
    "arts and recreation services": "Arts and Recreation Services",
    "other services": "Other Services",
}


# One entry per ANZSIC division A..S, excluding K (Financial & Insurance
# Services) which is out of scope for this overlay. Keys are the normalised
# sector name returned by ``_normalise_sector_key``.
TARGET_SECTOR_CONFIG = {
    "agriculture forestry and fishing": ("A", "Primary production and agribusiness"),
    "mining": ("B", "Mining and resources"),
    "manufacturing": ("C", "Industrial and manufacturing"),
    "electricity gas water and waste services": ("D", "Utilities and infrastructure"),
    "construction": ("E", "Building, civil and trade services"),
    "wholesale trade": ("F", "Wholesale and distribution"),
    "retail trade": ("G", "Consumer retail and discretionary"),
    "accommodation and food services": ("H", "Hospitality and leisure"),
    "transport postal and warehousing": ("I", "Freight, logistics and storage"),
    "information media and telecommunications": ("J", "Media, telco and information services"),
    "rental hiring and real estate services": ("L", "Real estate and rental services"),
    "professional scientific and technical services": ("M", "Professional and technical services"),
    "administrative and support services": ("N", "Administrative and support services"),
    "public administration and safety": ("O", "Public administration and safety"),
    "education and training": ("P", "Education and training"),
    "health care and social assistance": ("Q", "Health and care services"),
    "arts and recreation services": ("R", "Arts and recreation services"),
    "other services": ("S", "Other services"),
}


# APRA-informed anchors (rate_sensitivity, demand_dependency, external_shock).
# Values are integers 1..5 where higher = more risk. Citations are short
# pointers; full rationale lives in docs/anchor_sources.md.
STRUCTURAL_SCORE_ANCHORS = {
    # A — Agriculture: commodity-price and weather exposure, cyclical demand via exports.
    "agriculture forestry and fishing": {"rate_sensitivity": 3, "demand_dependency": 4, "external_shock": 4},  # ASIC 1A mid-rank; RBA FSR: commodity & weather shocks
    # B — Mining: rate-sensitive capex but defensive cashflows; commodity shocks dominate.
    "mining": {"rate_sensitivity": 3, "demand_dependency": 4, "external_shock": 5},  # RBA FSR Ch.3: commodity price shocks are top external risk
    # C — Manufacturing: thin margins, input-cost and FX exposure, cyclical demand.
    "manufacturing": {"rate_sensitivity": 3, "demand_dependency": 4, "external_shock": 4},  # ASIC 1A top-5 insolvencies; APG 113 cyclical sector
    # D — Electricity/Gas/Water: regulated utilities, defensive demand, capex sensitivity.
    "electricity gas water and waste services": {"rate_sensitivity": 2, "demand_dependency": 2, "external_shock": 3},  # APRA Pillar 3: utilities low cyclicality; regulatory/price-cap shocks
    # E — Construction: top insolvency cohort; direct rate and demand sensitivity.
    "construction": {"rate_sensitivity": 4, "demand_dependency": 5, "external_shock": 4},  # ASIC 1A #1 insolvency share; APG 223 rate-sensitive
    # F — Wholesale: pass-through margins; inventory cycle exposure.
    "wholesale trade": {"rate_sensitivity": 3, "demand_dependency": 3, "external_shock": 3},  # ABS BI: thin-margin pass-through; moderate cyclicality
    # G — Retail: consumer-rate-sensitive demand; discretionary exposure.
    "retail trade": {"rate_sensitivity": 4, "demand_dependency": 4, "external_shock": 4},  # RBA FSR: household-rate pass-through; ASIC 1A top-5
    # H — Accommodation & food: discretionary demand, tourism cyclicality, thin margins.
    "accommodation and food services": {"rate_sensitivity": 4, "demand_dependency": 5, "external_shock": 4},  # ASIC 1A: second-highest insolvency share
    # I — Transport: fuel-price exposure; cyclical freight demand.
    "transport postal and warehousing": {"rate_sensitivity": 3, "demand_dependency": 3, "external_shock": 3},  # RBA FSR: fuel and supply-chain exposure
    # J — Info media & telecoms: capital-heavy, defensive subscription demand.
    "information media and telecommunications": {"rate_sensitivity": 2, "demand_dependency": 2, "external_shock": 3},  # Pillar 3: defensive cashflows; tech obsolescence shock
    # L — Rental/real estate: most rate-sensitive division per APG 223.
    "rental hiring and real estate services": {"rate_sensitivity": 5, "demand_dependency": 4, "external_shock": 3},  # APG 223 §4: real estate is most rate-sensitive
    # M — Professional services: low capex, defensive demand.
    "professional scientific and technical services": {"rate_sensitivity": 2, "demand_dependency": 2, "external_shock": 2},  # Pillar 3 low-severity; stable demand
    # N — Admin & support: low margin, labour-intensive, cyclical staffing demand.
    "administrative and support services": {"rate_sensitivity": 3, "demand_dependency": 3, "external_shock": 2},  # ABS BI: thin margins; cyclical outsourced demand
    # O — Public administration: policy-insulated, non-cyclical.
    "public administration and safety": {"rate_sensitivity": 1, "demand_dependency": 1, "external_shock": 2},  # APRA defensive; budget/policy shocks only
    # P — Education: largely non-cyclical demand; modest international exposure.
    "education and training": {"rate_sensitivity": 2, "demand_dependency": 1, "external_shock": 2},  # RBA FSR: defensive demand; international student shock
    # Q — Health care: defensive demand; labour and reimbursement shock risk.
    "health care and social assistance": {"rate_sensitivity": 2, "demand_dependency": 1, "external_shock": 2},  # APRA Pillar 3: defensive; labour-reform risk
    # R — Arts & recreation: discretionary demand; event and venue cyclicality.
    "arts and recreation services": {"rate_sensitivity": 4, "demand_dependency": 4, "external_shock": 3},  # ABS BI: discretionary demand; COVID cohort insolvencies
    # S — Other services: small business heavy; moderate rate and demand sensitivity.
    "other services": {"rate_sensitivity": 3, "demand_dependency": 3, "external_shock": 2},  # ASIC 1A mid-rank; small-business exposure
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


def _blend_with_anchor(raw_score: int, sector_key: str, metric: str) -> float:
    """Blend a discrete raw sub-score (1-5) with the APRA-informed anchor.

    Returns a float so the average over four sub-scores preserves the
    granularity of period-on-period movement. The previous integer-rounded
    output flattened small ABS data shifts into the same band.
    """
    anchor = STRUCTURAL_SCORE_ANCHORS.get(sector_key, {}).get(metric)
    if anchor is None:
        return float(raw_score)
    return (float(raw_score) + float(anchor)) / 2.0


def _score_rate_sensitivity(margin_pct: float, sector_key: str) -> float:
    if pd.isna(margin_pct):
        raw_score = 3
    elif margin_pct < 6:
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


def _score_demand_dependency(sales_growth_pct: float, sector_key: str) -> float:
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


def _score_external_shock(margin_pct: float, sales_growth_pct: float, sector_key: str) -> float:
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


def _display_industry(raw_sector: str, sector_key: str) -> str:
    canonical = ANZSIC_DIVISION_DISPLAY_NAMES.get(sector_key)
    if canonical is not None:
        return canonical
    # Fallback: defensive title-case for any sector outside the canonical map.
    return raw_sector.replace("(private)", "").strip().title()


def build_foundation(public_dir: Path, processed_dir: Path) -> pd.DataFrame:
    ai = parse_australian_industry_totals(resolve_staged_file("australian_industry_xlsx"))
    ai["sector_key"] = ai["sector"].map(_normalise_sector_key)

    latest = ai[ai["year"] == "2023-24"].copy()
    prev = ai[ai["year"] == "2022-23"][["sector_key", "sales_m"]].rename(
        columns={"sales_m": "sales_m_prev"}
    )
    latest = latest.merge(prev, on="sector_key", how="left")
    latest["sales_growth_pct"] = (latest["sales_m"] / latest["sales_m_prev"] - 1) * 100

    rows = []
    for _, row in latest.iterrows():
        sector_key = row["sector_key"]
        if sector_key not in TARGET_SECTOR_CONFIG:
            continue

        division_code, grouping = TARGET_SECTOR_CONFIG[sector_key]
        display_industry = _display_industry(row["sector"], sector_key)

        rows.append(
            {
                "anzsic_division_code": division_code,
                "industry": display_industry,
                "internal_grouping_example": grouping,
                "cyclical_score": _score_cyclicality(row["sales_growth_pct"]),
                "rate_sensitivity_score": _score_rate_sensitivity(row["ebitda_margin_pct"], sector_key),
                "demand_dependency_score": _score_demand_dependency(row["sales_growth_pct"], sector_key),
                "external_shock_score": _score_external_shock(row["ebitda_margin_pct"], row["sales_growth_pct"], sector_key),
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
        "generated from ABS Australian Industry public data using deterministic "
        "APRA-informed proxy classification rules"
    )
    save_csv(df, processed_dir / "industry_classification_foundation.csv")
    return df
