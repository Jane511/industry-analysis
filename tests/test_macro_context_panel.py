"""Tests for the macro context panel (Task 10 deliverable).

The panel is published as ``macro_context.parquet`` (Task 13). It must
return a quarterly schema regardless of whether the ABS Cat. 6401.0 / 6427.0
inputs are staged — graceful-degradation contract from TASK 16 of the brief.
"""

from __future__ import annotations

import pandas as pd

from src.panels.build_macro_context_panel import (
    PANEL_COLUMNS,
    build_macro_context_panel,
)


def test_macro_context_panel_returns_quarterly_rows() -> None:
    panel = build_macro_context_panel()
    assert "as_of_date" in panel.columns
    assert "cpi_yoy_pct" in panel.columns
    assert "ppi_manufacturing_yoy_pct" in panel.columns
    # The brief calls for ~8 quarters; minimum-data path still yields >=4.
    assert len(panel) >= 4


def test_macro_context_panel_publishes_canonical_schema() -> None:
    panel = build_macro_context_panel()
    assert list(panel.columns) == PANEL_COLUMNS


def test_macro_context_cash_rate_populated() -> None:
    """RBA F1 cash rate is always staged in the repo, so the cash_rate_pct
    column should never be entirely null."""
    panel = build_macro_context_panel()
    assert panel["cash_rate_pct"].notna().any()


def test_macro_context_cpi_values_in_plausible_range_when_present() -> None:
    panel = build_macro_context_panel()
    cpi_values = panel["cpi_yoy_pct"].dropna()
    if cpi_values.empty:
        # Graceful-degradation path — ABS CPI not staged.
        return
    # Headline CPI YoY ranged roughly -5%..15% in the past 50 years.
    assert cpi_values.between(-5, 15).all()
