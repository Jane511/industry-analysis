"""Typed readers for canonical CSV contract exports.

CSV is the published contract format, but CSV itself does not preserve
dtypes. These helpers centralise dtype restoration so Python consumers read
the same logical schema every time.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pandas as pd


STRING_COLUMNS = {
    "industry_risk_scores": ["anzsic_division_code", "industry", "industry_base_risk_level"],
    "property_market_overlays": [
        "property_segment_code",
        "property_segment",
        "cycle_stage",
        "market_softness_band",
        "market_softness_level",
        "commencements_signal",
        "completions_signal",
        "source_note",
    ],
    "downturn_overlay_table": ["scenario", "macro_path", "notes"],
    "macro_scenario_paths": [
        "scenario", "variable", "label", "unit", "stress_direction",
        "source_or_assumption", "macro_note",
    ],
    "portfolio_macro_sensitivity": [
        "segment", "parameter", "driver", "driver_stress_direction",
        "source_or_assumption",
    ],
    "macro_context": [
        "variable", "label", "unit", "reading_type", "source_or_assumption",
        "macro_note",
    ],
    "macro_regime_flags": ["cash_rate_regime", "arrears_environment_level", "arrears_trend", "macro_regime_flag", "source_dataset"],
    "industry_financial_benchmarks": ["anzsic_division_code", "industry", "benchmark_method", "source_note"],
    "business_cycle_panel": [
        "sector_key",
        "anzsic_division_code",
        "industry",
        "internal_grouping_example",
        "demand_proxy_building_type",
        "inventory_days_est_source",
        "inventory_stock_build_risk",
        "industry_base_risk_level",
    ],
    "property_cycle_panel": [
        "region",
        "property_segment",
        "commencements_signal",
        "completions_signal",
        "cycle_stage",
        "market_softness_band",
        "source_note",
        "region_risk_band",
    ],
    "property_market_overlays_by_building_type": [
        "property_segment",
        "property_segment_code",
        "aggregate_role",
        "cycle_stage",
        "market_softness_band",
        "region_risk_band",
        "commencements_signal",
        "completions_signal",
    ],
}

INTEGER_COLUMNS: dict[str, list[str]] = {}

DATE_COLUMNS = {
    "industry_risk_scores": ["as_of_date"],
    "property_market_overlays": ["as_of_date"],
    "downturn_overlay_table": ["as_of_date"],
    "macro_regime_flags": ["as_of_date"],
    "industry_financial_benchmarks": ["as_of_date"],
    "property_cycle_panel": ["as_of_date"],
    "property_market_overlays_by_building_type": ["as_of_date"],
}


def _read_export(path: Path, key: str) -> pd.DataFrame:
    dtype = {col: "string" for col in STRING_COLUMNS.get(key, [])}
    dtype.update({col: "Int64" for col in INTEGER_COLUMNS.get(key, [])})
    df = pd.read_csv(path, dtype=dtype, parse_dates=DATE_COLUMNS.get(key, []))
    for col in DATE_COLUMNS.get(key, []):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def read_industry_risk_scores(path: Path) -> pd.DataFrame:
    return _read_export(path, "industry_risk_scores")


def read_property_market_overlays(path: Path) -> pd.DataFrame:
    return _read_export(path, "property_market_overlays")


def read_downturn_overlay_table(path: Path) -> pd.DataFrame:
    return _read_export(path, "downturn_overlay_table")


def read_macro_regime_flags(path: Path) -> pd.DataFrame:
    return _read_export(path, "macro_regime_flags")


def read_industry_financial_benchmarks(path: Path) -> pd.DataFrame:
    return _read_export(path, "industry_financial_benchmarks")


def read_business_cycle_panel(path: Path) -> pd.DataFrame:
    return _read_export(path, "business_cycle_panel")


def read_property_cycle_panel(path: Path) -> pd.DataFrame:
    return _read_export(path, "property_cycle_panel")


def read_property_market_overlays_by_building_type(path: Path) -> pd.DataFrame:
    return _read_export(path, "property_market_overlays_by_building_type")


def read_macro_scenario_paths(path: Path) -> pd.DataFrame:
    return _read_export(path, "macro_scenario_paths")


def read_portfolio_macro_sensitivity(path: Path) -> pd.DataFrame:
    return _read_export(path, "portfolio_macro_sensitivity")


def read_macro_context(path: Path) -> pd.DataFrame:
    return _read_export(path, "macro_context")


READERS: dict[str, Callable[[Path], pd.DataFrame]] = {
    "industry_risk_scores": read_industry_risk_scores,
    "property_market_overlays": read_property_market_overlays,
    "downturn_overlay_table": read_downturn_overlay_table,
    "macro_regime_flags": read_macro_regime_flags,
    "industry_financial_benchmarks": read_industry_financial_benchmarks,
    "business_cycle_panel": read_business_cycle_panel,
    "property_cycle_panel": read_property_cycle_panel,
    "property_market_overlays_by_building_type": read_property_market_overlays_by_building_type,
    "macro_scenario_paths": read_macro_scenario_paths,
    "portfolio_macro_sensitivity": read_portfolio_macro_sensitivity,
    "macro_context": read_macro_context,
}


def read_canonical_csv(key: str, path: Path) -> pd.DataFrame:
    return READERS[key](path)
