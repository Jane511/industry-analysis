"""Build canonical industry-risk overlay table."""

from __future__ import annotations

import pandas as pd

from src.panels.build_business_cycle_panel import build_business_cycle_panel


def build_industry_risk_scores(panel: pd.DataFrame | None = None) -> pd.DataFrame:
    panel = panel if panel is not None else build_business_cycle_panel()
    scores = panel[
        [
            "industry",
            "classification_risk_score",
            "macro_risk_score",
            "industry_base_risk_score",
            "industry_base_risk_level",
            "cash_rate_latest_pct",
            "cash_rate_change_1y_pctpts",
        ]
    ].sort_values("industry_base_risk_score", ascending=False)
    return scores
