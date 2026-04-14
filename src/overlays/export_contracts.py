"""Canonical contract-export orchestration for upstream overlays."""

from __future__ import annotations

import pandas as pd

from src.config import (
    ALL_CONTRACT_EXPORTS,
    EXPORTS_DIR,
    SECONDARY_INSPECTION_CSV_EXPORTS,
)
from src.output import ensure_parquet_engine_available, save_csv, save_parquet
from src.overlays.build_downturn_overlay_tables import build_downturn_overlay_tables
from src.overlays.build_industry_risk_scores import build_industry_risk_scores
from src.overlays.build_property_market_overlays import build_property_market_overlays
from src.panels.build_business_cycle_panel import build_business_cycle_panel
from src.panels.build_macro_regime_flags import build_macro_regime_flags
from src.panels.build_property_cycle_panel import build_property_cycle_panel


def _prepare_directories() -> None:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _write_secondary_inspection_csvs_from_exports() -> None:
    for key, csv_path in SECONDARY_INSPECTION_CSV_EXPORTS.items():
        parquet_path = ALL_CONTRACT_EXPORTS[key]
        save_csv(pd.read_parquet(parquet_path), csv_path)


def export_contracts() -> dict[str, pd.DataFrame]:
    _prepare_directories()
    ensure_parquet_engine_available()

    business_cycle_panel = build_business_cycle_panel()
    property_cycle_panel = build_property_cycle_panel()
    macro_regime_flags = build_macro_regime_flags()
    industry_risk_scores = build_industry_risk_scores(panel=business_cycle_panel)
    property_market_overlays = build_property_market_overlays(panel=property_cycle_panel)
    downturn_overlay_table = build_downturn_overlay_tables(property_cycle_panel=property_cycle_panel)

    outputs = {
        "industry_risk_scores": industry_risk_scores,
        "property_market_overlays": property_market_overlays,
        "downturn_overlay_table": downturn_overlay_table,
        "macro_regime_flags": macro_regime_flags,
        "business_cycle_panel": business_cycle_panel,
        "property_cycle_panel": property_cycle_panel,
    }

    for key, export_path in ALL_CONTRACT_EXPORTS.items():
        save_parquet(outputs[key], export_path)

    _write_secondary_inspection_csvs_from_exports()

    return outputs
