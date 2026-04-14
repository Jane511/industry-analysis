"""Canonical contract-export orchestration for upstream overlays."""

from __future__ import annotations

import pandas as pd

from src.config import (
    EXPORT_BUSINESS_CYCLE_PANEL_PARQUET,
    EXPORT_DOWNTURN_OVERLAY_TABLE_PARQUET,
    EXPORT_INDUSTRY_RISK_SCORES_PARQUET,
    EXPORT_MACRO_REGIME_FLAGS_PARQUET,
    EXPORT_PROPERTY_CYCLE_PANEL_PARQUET,
    EXPORT_PROPERTY_MARKET_OVERLAYS_PARQUET,
    EXPORTS_DIR,
)
from src.output import ensure_parquet_engine_available, save_parquet
from src.overlays.build_downturn_overlay_tables import build_downturn_overlay_tables
from src.overlays.build_industry_risk_scores import build_industry_risk_scores
from src.overlays.build_property_market_overlays import build_property_market_overlays
from src.panels.build_business_cycle_panel import build_business_cycle_panel
from src.panels.build_macro_regime_flags import build_macro_regime_flags
from src.panels.build_property_cycle_panel import build_property_cycle_panel


def _prepare_directories() -> None:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


def export_contracts() -> dict[str, pd.DataFrame]:
    _prepare_directories()
    ensure_parquet_engine_available()

    business_cycle_panel = build_business_cycle_panel()
    property_cycle_panel = build_property_cycle_panel()
    macro_regime_flags = build_macro_regime_flags()
    industry_risk_scores = build_industry_risk_scores(panel=business_cycle_panel)
    property_market_overlays = build_property_market_overlays(panel=property_cycle_panel)
    downturn_overlay_table = build_downturn_overlay_tables(property_cycle_panel=property_cycle_panel)

    save_parquet(business_cycle_panel, EXPORT_BUSINESS_CYCLE_PANEL_PARQUET)
    save_parquet(property_cycle_panel, EXPORT_PROPERTY_CYCLE_PANEL_PARQUET)
    save_parquet(macro_regime_flags, EXPORT_MACRO_REGIME_FLAGS_PARQUET)
    save_parquet(industry_risk_scores, EXPORT_INDUSTRY_RISK_SCORES_PARQUET)
    save_parquet(property_market_overlays, EXPORT_PROPERTY_MARKET_OVERLAYS_PARQUET)
    save_parquet(downturn_overlay_table, EXPORT_DOWNTURN_OVERLAY_TABLE_PARQUET)

    return {
        "business_cycle_panel": business_cycle_panel,
        "property_cycle_panel": property_cycle_panel,
        "macro_regime_flags": macro_regime_flags,
        "industry_risk_scores": industry_risk_scores,
        "property_market_overlays": property_market_overlays,
        "downturn_overlay_table": downturn_overlay_table,
    }
