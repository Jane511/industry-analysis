"""Build canonical industry-risk overlay table.

Single source of truth for the score-to-multiplier ladder used across the
engine. Consumes the business-cycle panel (one row per ANZSIC division) and
produces the ``industry_risk_scores`` contract export that downstream PD,
pricing, ECL, and governance systems read.
"""

from __future__ import annotations

import math
from datetime import date

import pandas as pd


# Five-band ladder used across the engine. Every downstream file that needs a
# multiplier or a risk-level label imports these symbols rather than
# re-implementing the thresholds. Lower bound is inclusive, upper bound is
# exclusive. The top band extends to +inf; the bottom band extends to -inf.
SCORE_TO_MULTIPLIER_LADDER: tuple[tuple[float, float, str, float], ...] = (
    (-math.inf, 1.60, "Low", 0.90),
    (1.60, 2.00, "Moderate-low", 0.95),
    (2.00, 2.80, "Medium", 1.00),
    (2.80, 3.23, "Moderate-high", 1.10),
    (3.23, math.inf, "Elevated", 1.15),
)


def _ladder_lookup(score: float) -> tuple[str, float]:
    if score is None or (isinstance(score, float) and math.isnan(score)):
        return ("Medium", 1.00)
    for lower, upper, label, multiplier in SCORE_TO_MULTIPLIER_LADDER:
        if lower <= score < upper:
            return (label, multiplier)
    return ("Medium", 1.00)


def score_to_pd_multiplier(score: float) -> float:
    """Return the pd_multiplier published for a given composite risk score."""
    return _ladder_lookup(score)[1]


def score_to_risk_level(score: float) -> str:
    """Return the five-band risk-level label for a given composite risk score."""
    return _ladder_lookup(score)[0]


def build_industry_risk_scores(
    panel: pd.DataFrame | None = None,
    as_of: date | None = None,
) -> pd.DataFrame:
    if panel is None:
        # Late import avoids a circular dependency: macro_signals imports
        # score_to_risk_level from this module, and build_business_cycle_panel
        # pulls macro_signals in transitively.
        from src.panels.build_business_cycle_panel import build_business_cycle_panel

        panel = build_business_cycle_panel()

    as_of_value = (as_of or date.today()).isoformat()

    scores = panel[
        [
            "anzsic_division_code",
            "industry",
            "classification_risk_score",
            "macro_risk_score",
            "industry_base_risk_score",
            "cash_rate_latest_pct",
            "cash_rate_change_1y_pctpts",
        ]
    ].copy()

    scores["industry_base_risk_level"] = scores["industry_base_risk_score"].apply(
        score_to_risk_level
    )
    scores["pd_multiplier"] = scores["industry_base_risk_score"].apply(
        score_to_pd_multiplier
    )
    scores["as_of_date"] = as_of_value

    ordered_columns = [
        "anzsic_division_code",
        "industry",
        "classification_risk_score",
        "macro_risk_score",
        "industry_base_risk_score",
        "industry_base_risk_level",
        "pd_multiplier",
        "cash_rate_latest_pct",
        "cash_rate_change_1y_pctpts",
        "as_of_date",
    ]
    scores = (
        scores[ordered_columns]
        .sort_values("anzsic_division_code")
        .reset_index(drop=True)
    )
    return scores
