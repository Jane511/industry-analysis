"""Validation helpers for upstream overlay exports."""

from __future__ import annotations

import pandas as pd

from src.config import (
    EXPORT_BUSINESS_CYCLE_PANEL_PARQUET,
    EXPORT_DOWNTURN_OVERLAY_TABLE_PARQUET,
    EXPORT_INDUSTRY_RISK_SCORES_PARQUET,
    EXPORT_MACRO_REGIME_FLAGS_PARQUET,
    EXPORT_PROPERTY_CYCLE_PANEL_PARQUET,
    EXPORT_PROPERTY_MARKET_OVERLAYS_PARQUET,
)


REQUIRED_EXPORT_KEYS = [
    "business_cycle_panel",
    "property_cycle_panel",
    "macro_regime_flags",
    "industry_risk_scores",
    "property_market_overlays",
    "downturn_overlay_table",
]

EXPORT_PATHS = {
    "business_cycle_panel": EXPORT_BUSINESS_CYCLE_PANEL_PARQUET,
    "property_cycle_panel": EXPORT_PROPERTY_CYCLE_PANEL_PARQUET,
    "macro_regime_flags": EXPORT_MACRO_REGIME_FLAGS_PARQUET,
    "industry_risk_scores": EXPORT_INDUSTRY_RISK_SCORES_PARQUET,
    "property_market_overlays": EXPORT_PROPERTY_MARKET_OVERLAYS_PARQUET,
    "downturn_overlay_table": EXPORT_DOWNTURN_OVERLAY_TABLE_PARQUET,
}


def validate_upstream_outputs(outputs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    checks = []
    for key in REQUIRED_EXPORT_KEYS:
        present = key in outputs and isinstance(outputs[key], pd.DataFrame) and not outputs[key].empty
        checks.append(
            {
                "check_name": f"required_output::{key}",
                "status": bool(present),
                "detail": "present and non-empty" if present else "missing or empty",
            }
        )

        export_path = EXPORT_PATHS[key]
        exists = export_path.exists()
        has_content = exists and export_path.stat().st_size > 0
        checks.append(
            {
                "check_name": f"export_file::{export_path.name}",
                "status": bool(has_content),
                "detail": str(export_path) if has_content else f"missing or empty file at {export_path}",
            }
        )

    return pd.DataFrame(checks)
