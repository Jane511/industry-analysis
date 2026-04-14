"""Build canonical property-cycle panel tables."""

from __future__ import annotations

import pandas as pd

from src.config import PROCESSED_PUBLIC_PROPERTY_DIR
from src.output import save_csv
from src.panels.property_cycle_core import build_property_cycle_table
from src.public_data.load_abs_manual_exports import (
    build_building_activity_summary,
    build_building_approvals_summary,
    build_housing_finance_summary,
    load_building_approvals_reference,
    load_optional_building_activity_extract,
    load_optional_lending_indicator_extract,
)
from src.public_data.download_rba_rates import load_cash_rate_summary
from src.panels.region_risk_core import build_region_risk_table


def build_property_cycle_panel() -> pd.DataFrame:
    PROCESSED_PUBLIC_PROPERTY_DIR.mkdir(parents=True, exist_ok=True)

    approvals = load_building_approvals_reference()
    approvals_summary = build_building_approvals_summary(approvals)
    activity_summary = build_building_activity_summary(load_optional_building_activity_extract())
    finance_summary = build_housing_finance_summary(load_optional_lending_indicator_extract())
    cash_rate_summary = load_cash_rate_summary()

    property_cycle = build_property_cycle_table(approvals_summary, activity_summary)
    region_risk = build_region_risk_table(
        approvals_summary,
        activity_summary,
        finance_summary,
        cash_rate_summary,
    )
    panel = property_cycle.merge(
        region_risk[["property_segment", "region_risk_score", "region_risk_band"]],
        on="property_segment",
        how="left",
    )

    save_csv(panel, PROCESSED_PUBLIC_PROPERTY_DIR / "property_cycle_panel.csv")
    return panel
