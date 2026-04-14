"""Build canonical property-market overlay table."""

from __future__ import annotations

import pandas as pd

from src.panels.build_property_cycle_panel import build_property_cycle_panel


def build_property_market_overlays(panel: pd.DataFrame | None = None) -> pd.DataFrame:
    panel = panel if panel is not None else build_property_cycle_panel()
    overlays = panel[
        [
            "property_segment",
            "cycle_stage",
            "market_softness_score",
            "region_risk_score",
            "region_risk_band",
            "approvals_change_pct",
            "commencements_signal",
            "completions_signal",
        ]
    ].copy()
    overlays["market_softness_band"] = overlays["cycle_stage"].map(
        {
            "downturn": "soft",
            "slowing": "softening",
            "neutral": "normal",
            "growth": "supportive",
        }
    ).fillna("normal")
    return overlays
