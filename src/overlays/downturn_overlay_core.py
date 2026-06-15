"""Downturn scenario overlays for downstream PD, LGD, and EL use.

The mild/moderate/severe multipliers and haircuts are methodology
ASSUMPTIONS (illustrative scenario parameters), not observed data. They are
nudged by a real, ABS-derived property-softness backdrop and a qualitative
arrears baseline (itself an assumption read from the RBA FSR). They are not
calibrated regulatory stress parameters.

Each scenario carries a ``macro_path`` note so the multipliers read as
*derived from* a named macroeconomic path rather than standalone dials
(ST-IA-1). The **mild** scenario is the Basel CRE36.51 mandatory minimum —
two consecutive quarters of zero GDP growth.

No diversification benefit is assumed (APG 113 para 92): the overlays are
applied per sector/segment with no offsetting correlation relief. See
``docs/CONTRACT_FOR_DOWNSTREAM.md`` for the reverse-stress view and the
downstream stress -> limits / appetite linkage.
"""

from __future__ import annotations

import pandas as pd

from src.utils import clamp


# No-diversification assumption (APG 113 para 92) — stated on the published
# overlay rows so the boundary is explicit to downstream consumers.
NO_DIVERSIFICATION_NOTE = (
    "No diversification benefit assumed (APG 113 para 92)."
)


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
            "macro_path": (
                "Current environment, no recession overlay: GDP growth around "
                "trend, unemployment broadly stable, house prices at latest "
                "observed levels."
            ),
            "notes": (
                f"Current environment (base scenario). {backdrop_note} "
                f"{NO_DIVERSIFICATION_NOTE}"
            ),
            "as_of_date": as_of_date,
        },
        {
            "scenario": "mild",
            "pd_multiplier": round(1.20 + backdrop_adjustment, 2),
            "lgd_multiplier": round(1.10 + (backdrop_adjustment / 2), 2),
            "ccf_multiplier": round(1.05 + (backdrop_adjustment / 3), 2),
            "property_value_haircut": round(0.05 + (backdrop_adjustment / 2), 2),
            "macro_path": (
                "Basel CRE36.51 mandatory minimum — two consecutive quarters "
                "of zero GDP growth; unemployment +~1.0-1.5pp; house prices "
                "~-5 to -10%."
            ),
            "notes": (
                "ASSUMPTION (scenario parameter) — mild recession = Basel "
                "CRE36.51 two-quarters-zero-growth minimum, for conservative "
                f"portfolio calibration. {NO_DIVERSIFICATION_NOTE}"
            ),
            "as_of_date": as_of_date,
        },
        {
            "scenario": "moderate",
            "pd_multiplier": round(1.50 + backdrop_adjustment, 2),
            "lgd_multiplier": round(1.20 + (backdrop_adjustment / 2), 2),
            "ccf_multiplier": round(1.10 + (backdrop_adjustment / 3), 2),
            "property_value_haircut": round(0.10 + (backdrop_adjustment / 2), 2),
            "macro_path": (
                "Deeper recession: multi-quarter contraction; unemployment "
                "+~2-3pp; house prices ~-10 to -15%."
            ),
            "notes": (
                "ASSUMPTION (scenario parameter) — illustrative moderate "
                "downturn for stressed pricing and EL scenario analysis. "
                f"{NO_DIVERSIFICATION_NOTE}"
            ),
            "as_of_date": as_of_date,
        },
        {
            "scenario": "severe",
            "pd_multiplier": round(2.00 + (backdrop_adjustment * 1.5), 2),
            "lgd_multiplier": round(1.30 + (backdrop_adjustment / 2), 2),
            "ccf_multiplier": round(1.20 + (backdrop_adjustment / 3), 2),
            "property_value_haircut": round(0.20 + (backdrop_adjustment / 2), 2),
            "macro_path": (
                "GFC-like severe-but-plausible path: deep multi-quarter "
                "contraction; unemployment +~3-4pp; house prices ~-20 to -30%."
            ),
            "notes": (
                "ASSUMPTION (scenario parameter) — illustrative severe "
                "downturn; not a calibrated regulatory stress parameter. "
                f"{NO_DIVERSIFICATION_NOTE}"
            ),
            "as_of_date": as_of_date,
        },
    ]

    return pd.DataFrame(rows)
