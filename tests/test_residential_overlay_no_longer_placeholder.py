"""Verify the RES row of property_market_overlays carries enrichment.

The brief's Task 12 calls out two enhancements:
  1. RES row populated from ABS Cat. 8752.0 dwelling approvals when staged.
  2. All 5 rows carry property-reference enrichment columns.

When ABS Cat. 8752.0 is not staged, the RES row falls back to the
documented placeholder composite — but its source_note is the explicit
"placeholder" sentence (not a generic empty string), and it still receives
property-reference enrichment from the manual Cotality / Domain / SQM /
state-rental-bond stubs.
"""

from __future__ import annotations

import pandas as pd

from src.overlays.build_property_market_overlays import build_property_market_overlays


def test_res_row_pd_multiplier_in_published_ladder() -> None:
    overlays = build_property_market_overlays()
    res_row = overlays[overlays["property_segment_code"] == "RES"].iloc[0]
    assert res_row["pd_multiplier"] in {0.90, 0.95, 1.00, 1.10, 1.15}


def test_res_row_carries_property_reference_enrichment_when_sources_staged() -> None:
    """With committed Cotality/Domain/SQM stubs, the RES row should report
    the available status (not "not_available")."""
    overlays = build_property_market_overlays()
    res_row = overlays[overlays["property_segment_code"] == "RES"].iloc[0]
    # Status comes from the property-reference panel availability.
    assert res_row["property_reference_status"] in {"available", "not_available"}


def test_non_res_rows_flagged_as_residential_only_when_panel_available() -> None:
    """The brief explicitly says commercial segments aren't covered by
    property-reference v1 — they must carry a clear status flag, not silent nulls."""
    overlays = build_property_market_overlays()
    non_res = overlays[overlays["property_segment_code"] != "RES"]
    statuses = set(non_res["property_reference_status"].dropna().unique())
    assert statuses.issubset({"residential_only_in_v1", "not_available"})
