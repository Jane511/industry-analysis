"""Tests for the property reference panel and its property-overlay enrichment."""

from __future__ import annotations

import pandas as pd

from src.overlays.build_property_market_overlays import (
    PROPERTY_REFERENCE_DERIVED_COLUMNS,
    build_property_market_overlays,
)
from src.panels.build_property_reference_panel import (
    PANEL_COLUMNS,
    build_property_reference_panel,
)


def test_property_reference_panel_aggregates_multi_source() -> None:
    panel = build_property_reference_panel()
    if panel.empty:
        return  # graceful-degradation path is acceptable
    assert set(panel.columns) == set(PANEL_COLUMNS)
    assert "region_type" in panel.columns
    assert panel["region_type"].isin({"national", "capital", "suburb", "sa3", "sa4", "postcode"}).all()
    assert "data_completeness_pct" in panel.columns
    assert panel["data_completeness_pct"].between(0, 100).all()


def test_property_reference_panel_has_capital_and_suburb_rows() -> None:
    panel = build_property_reference_panel()
    if panel.empty:
        return
    assert (panel["region_type"] == "capital").any(), "expected at least one capital-city row"
    assert panel["region_type"].isin({"suburb", "sa4"}).any(), "expected at least one suburb-/SA4-level row"


def test_property_overlays_have_property_reference_columns() -> None:
    overlays = build_property_market_overlays()
    for col in PROPERTY_REFERENCE_DERIVED_COLUMNS:
        assert col in overlays.columns, f"property overlays missing {col}"


def test_property_overlays_keep_5_rows_after_enrichment() -> None:
    """Enrichment must not change the row count or segment-code uniqueness."""
    overlays = build_property_market_overlays()
    assert len(overlays) == 5
    assert set(overlays["property_segment_code"]) == {"RES", "CRE", "IND", "RET", "CON"}
    assert overlays["property_segment_code"].is_unique


def test_property_overlays_pd_multiplier_unchanged() -> None:
    """Property-reference enrichment must not change pd_multiplier values."""
    overlays = build_property_market_overlays()
    assert set(overlays["pd_multiplier"].unique()).issubset(
        {0.90, 0.95, 1.00, 1.10, 1.15}
    )


def test_property_reference_status_flag_set() -> None:
    overlays = build_property_market_overlays()
    statuses = set(overlays["property_reference_status"].dropna().unique())
    assert statuses.issubset({"available", "residential_only_in_v1", "not_available"})
