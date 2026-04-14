"""Build canonical downturn overlay table."""

from __future__ import annotations

import pandas as pd

from src.arrears_environment import build_base_arrears_environment
from src.overlays.downturn_overlay_core import build_property_downturn_overlays
from src.panels.build_property_cycle_panel import build_property_cycle_panel
from src.public_data.download_apra_property_exposures import load_optional_apra_property_context
from src.public_data.download_rba_rates import load_cash_rate_summary, load_optional_rba_housing_context


def build_downturn_overlay_tables(property_cycle_panel: pd.DataFrame | None = None) -> pd.DataFrame:
    property_cycle_panel = property_cycle_panel if property_cycle_panel is not None else build_property_cycle_panel()
    property_cycle = property_cycle_panel.drop(
        columns=["region_risk_score", "region_risk_level"],
        errors="ignore",
    )

    cash_rate_summary = load_cash_rate_summary()
    rba_context = load_optional_rba_housing_context()
    apra_context = load_optional_apra_property_context()
    arrears_environment = build_base_arrears_environment(cash_rate_summary, rba_context, apra_context)

    downturn_overlay = build_property_downturn_overlays(arrears_environment, property_cycle)
    return downturn_overlay
