"""Build per-ANZSIC realised failure-rate overlay (Output B).

This panel is the free, Australian-government-data equivalent of paid
sector-outlook feeds (e.g. Experian Sector Outlook). It joins ASIC Series 1A
insolvency counts to an ABS-derived active-businesses denominator to produce
an annualised failure rate per ANZSIC division. Downstream validation (PD
backtest, ECL current-state checks) uses this table to compare predicted PDs
against realised insolvency experience.

Consumes:
    * ``load_optional_asic_insolvency_extract()`` — ASIC Series 1A
    * ABS Cat. 8165.0 "Counts of Australian Businesses" (optional) or a
      fixed fallback denominator table derived from ABS 81550DO001.

Produces:
    One row per ANZSIC division (excluding K, Financial & Insurance
    Services). Columns: ``as_of_date``, ``anzsic_division_code``,
    ``industry``, ``insolvency_count_ttm``, ``active_businesses``,
    ``failure_rate_pct``, ``failure_rate_yoy_change_pctpts``,
    ``source_note``.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from src.config import RAW_PUBLIC_DIR
from src.panels.foundation_signals import TARGET_SECTOR_CONFIG
from src.public_data.download_asic_insolvency import (
    _canonical_division_code,
    load_optional_asic_insolvency_extract,
)


ABS_BUSINESS_COUNTS_FILENAMES: tuple[str, ...] = (
    "8165_counts_of_australian_businesses.csv",
    "8165_counts_of_australian_businesses.xlsx",
    "abs_8165_businesses_by_anzsic.csv",
)


# Fallback denominator table. Values are order-of-magnitude estimates of
# active Australian businesses by ANZSIC division at 30 June 2024, derived
# from ABS Counts of Australian Businesses (Cat. 8165.0) summary releases
# and cross-checked against ABS 81550DO001 total employment and sector size
# figures. Used only when a live 8165 extract is not staged.
FALLBACK_ACTIVE_BUSINESSES_COUNTS: dict[str, int] = {
    "A": 115_000,
    "B": 10_200,
    "C": 82_000,
    "D": 6_500,
    "E": 430_000,
    "F": 60_000,
    "G": 120_000,
    "H": 95_000,
    "I": 95_000,
    "J": 25_000,
    "L": 260_000,
    "M": 380_000,
    "N": 120_000,
    "O": 3_000,
    "P": 25_000,
    "Q": 155_000,
    "R": 30_000,
    "S": 100_000,
}
FALLBACK_SOURCE_NOTE = (
    "Fallback active-business counts derived from ABS Cat. 8165.0 summary "
    "release (June 2024) plus ABS 81550DO001 cross-checks. Replace with a "
    "live 8165.0 extract in data/raw/public/abs/ when available."
)


def _load_abs_8165_counts(public_dir: Path) -> pd.DataFrame | None:
    """Load ABS Cat. 8165.0 business counts, or return None if unstaged.

    The expected staged file is a two-column CSV/XLSX with
    ``anzsic_division_code`` and ``active_businesses`` columns. If no file
    is present we return ``None`` so the caller falls back to the fixed
    table above.
    """
    if not public_dir.exists():
        return None
    for candidate in ABS_BUSINESS_COUNTS_FILENAMES:
        path = public_dir / candidate
        if not path.exists():
            continue
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path)
        rename = {}
        for col in df.columns:
            lower = str(col).strip().lower()
            if lower in {"anzsic_division_code", "division_code", "division"}:
                rename[col] = "anzsic_division_code"
            elif lower in {"active_businesses", "count", "business_count"}:
                rename[col] = "active_businesses"
        df = df.rename(columns=rename)
        if {"anzsic_division_code", "active_businesses"}.issubset(df.columns):
            df["anzsic_division_code"] = df["anzsic_division_code"].apply(_canonical_division_code)
            df["active_businesses"] = pd.to_numeric(df["active_businesses"], errors="coerce")
            df = df.dropna(subset=["anzsic_division_code", "active_businesses"])
            df["source_note"] = f"ABS Cat. 8165.0 ({path.name})"
            return df[["anzsic_division_code", "active_businesses", "source_note"]].reset_index(drop=True)
    return None


def _active_businesses_frame(public_dir: Path) -> pd.DataFrame:
    frame = _load_abs_8165_counts(public_dir)
    if frame is not None:
        return frame
    rows = [
        {
            "anzsic_division_code": code,
            "active_businesses": count,
            "source_note": FALLBACK_SOURCE_NOTE,
        }
        for code, count in FALLBACK_ACTIVE_BUSINESSES_COUNTS.items()
    ]
    return pd.DataFrame(rows)


def _industry_display_name(code: str) -> str:
    for normalised, (letter, _grouping) in TARGET_SECTOR_CONFIG.items():
        if letter == code:
            return normalised.title()
    return code


def _ttm_window(insolvencies: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
    months = pd.to_datetime(insolvencies["as_of_month"] + "-01", errors="coerce")
    cutoff_end = as_of.to_period("M").to_timestamp(how="start")
    cutoff_start = (as_of - pd.DateOffset(years=1)).to_period("M").to_timestamp(how="start")
    mask = (months >= cutoff_start) & (months < cutoff_end)
    return insolvencies.loc[mask].copy()


def _prior_year_window(insolvencies: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
    months = pd.to_datetime(insolvencies["as_of_month"] + "-01", errors="coerce")
    cutoff_end = (as_of - pd.DateOffset(years=1)).to_period("M").to_timestamp(how="start")
    cutoff_start = (as_of - pd.DateOffset(years=2)).to_period("M").to_timestamp(how="start")
    mask = (months >= cutoff_start) & (months < cutoff_end)
    return insolvencies.loc[mask].copy()


def build_industry_failure_rates(
    as_of: date | None = None,
    public_dir: Path | None = None,
) -> pd.DataFrame:
    as_of_value = as_of or date.today()
    as_of_ts = pd.Timestamp(as_of_value)
    public_dir = public_dir or (RAW_PUBLIC_DIR / "abs")

    insolvencies = load_optional_asic_insolvency_extract().copy()
    if not insolvencies.empty:
        insolvencies["anzsic_division_code"] = insolvencies["anzsic_division_code"].apply(
            _canonical_division_code
        )
        insolvencies = insolvencies.dropna(subset=["anzsic_division_code"])

    ttm = _ttm_window(insolvencies, as_of_ts) if not insolvencies.empty else insolvencies
    prior = _prior_year_window(insolvencies, as_of_ts) if not insolvencies.empty else insolvencies

    ttm_counts = (
        ttm.groupby("anzsic_division_code")["insolvency_count"].sum().rename("insolvency_count_ttm")
        if not ttm.empty
        else pd.Series(dtype="float64", name="insolvency_count_ttm")
    )
    prior_counts = (
        prior.groupby("anzsic_division_code")["insolvency_count"].sum().rename("insolvency_count_prior")
        if not prior.empty
        else pd.Series(dtype="float64", name="insolvency_count_prior")
    )

    denominators = _active_businesses_frame(public_dir)

    source_note_pieces = []
    if insolvencies.empty:
        source_note_pieces.append(
            "ASIC Series 1A file not staged — insolvency counts defaulted to 0. "
            "Run src.public_data.download_asic_insolvency.download_asic_series_1a or "
            "stage the workbook under data/raw/public/asic/ to populate."
        )
    else:
        note_sample = insolvencies["source_note"].dropna().astype(str).head(1)
        if not note_sample.empty:
            source_note_pieces.append(str(note_sample.iloc[0]))

    denominator_note = denominators["source_note"].iloc[0] if not denominators.empty else ""
    if denominator_note:
        source_note_pieces.append(denominator_note)

    rows = []
    for code in FALLBACK_ACTIVE_BUSINESSES_COUNTS:
        active = int(
            denominators.loc[denominators["anzsic_division_code"] == code, "active_businesses"].sum()
        )
        ttm_count = float(ttm_counts.get(code, 0.0))
        prior_count = float(prior_counts.get(code, 0.0))

        rate_pct = round((ttm_count / active) * 100, 3) if active else 0.0
        prior_rate_pct = round((prior_count / active) * 100, 3) if active else 0.0
        yoy_change = round(rate_pct - prior_rate_pct, 3)

        rows.append(
            {
                "as_of_date": as_of_value.isoformat(),
                "anzsic_division_code": code,
                "industry": _industry_display_name(code),
                "insolvency_count_ttm": ttm_count,
                "active_businesses": active,
                "failure_rate_pct": rate_pct,
                "failure_rate_yoy_change_pctpts": yoy_change,
                "source_note": " | ".join(piece for piece in source_note_pieces if piece),
            }
        )

    frame = pd.DataFrame(rows).sort_values("anzsic_division_code").reset_index(drop=True)
    return frame
