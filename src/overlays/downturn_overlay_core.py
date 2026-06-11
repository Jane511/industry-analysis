"""Downturn scenario overlays for downstream PD, LGD, and EL use.

The mild/moderate/severe multipliers and haircuts are methodology
ASSUMPTIONS (illustrative scenario parameters), not observed data. They are
nudged by a real, ABS-derived property-softness backdrop and a qualitative
arrears baseline (itself an assumption read from the RBA FSR). They are not
calibrated regulatory stress parameters.
"""

from __future__ import annotations

import pandas as pd

from src.utils import clamp


def build_property_downturn_overlays(
    arrears_environment: pd.DataFrame,
    property_cycle_table: pd.DataFrame,
) -> pd.DataFrame:
    arrears_row = arrears_environment.iloc[0]
    average_softness = (
        float(property_cycle_table["market_softness_score"].mean())
        if not property_cycle_table.empty
        else 3.0
    )
    backdrop_adjustment = clamp(
        ((average_softness - 3.0) * 0.05) + ((float(arrears_row["macro_housing_risk_score"]) - 2.5) * 0.05),
        0.0,
        0.15,
    )

    as_of_date = str(arrears_row["as_of_date"])
    backdrop_note = (
        f"Anchored to a {arrears_row['arrears_environment_level'].lower()} / "
        f"{arrears_row['arrears_trend'].lower()} arrears backdrop (qualitative "
        f"assumption from RBA FSR) and an average property-cycle softness score "
        f"of {average_softness:.2f} (real, ABS building approvals)."
    )

    rows = [
        {
            "scenario": "base",
            "pd_multiplier": 1.00,
            "lgd_multiplier": 1.00,
            "ccf_multiplier": 1.00,
            "property_value_haircut": 0.00,
            "notes": f"Current environment (base scenario). {backdrop_note}",
            "as_of_date": as_of_date,
        },
        {
            "scenario": "mild",
            "pd_multiplier": round(1.20 + backdrop_adjustment, 2),
            "lgd_multiplier": round(1.10 + (backdrop_adjustment / 2), 2),
            "ccf_multiplier": round(1.05 + (backdrop_adjustment / 3), 2),
            "property_value_haircut": round(0.05 + (backdrop_adjustment / 2), 2),
            "notes": "ASSUMPTION (scenario parameter) — illustrative mild downturn for conservative portfolio calibration.",
            "as_of_date": as_of_date,
        },
        {
            "scenario": "moderate",
            "pd_multiplier": round(1.50 + backdrop_adjustment, 2),
            "lgd_multiplier": round(1.20 + (backdrop_adjustment / 2), 2),
            "ccf_multiplier": round(1.10 + (backdrop_adjustment / 3), 2),
            "property_value_haircut": round(0.10 + (backdrop_adjustment / 2), 2),
            "notes": "ASSUMPTION (scenario parameter) — illustrative moderate downturn for stressed pricing and EL scenario analysis.",
            "as_of_date": as_of_date,
        },
        {
            "scenario": "severe",
            "pd_multiplier": round(2.00 + (backdrop_adjustment * 1.5), 2),
            "lgd_multiplier": round(1.30 + (backdrop_adjustment / 2), 2),
            "ccf_multiplier": round(1.20 + (backdrop_adjustment / 3), 2),
            "property_value_haircut": round(0.20 + (backdrop_adjustment / 2), 2),
            "notes": "ASSUMPTION (scenario parameter) — illustrative severe downturn; not a calibrated regulatory stress parameter.",
            "as_of_date": as_of_date,
        },
    ]

    return pd.DataFrame(rows)
