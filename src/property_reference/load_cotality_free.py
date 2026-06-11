"""Loaders for Cotality free monthly + weekly extracts.

Manual extraction. The Cotality public site publishes HTML-only — we copy
the headline numbers into a CSV per quarter following the canonical schema
documented in the brief.
"""

from __future__ import annotations

import pandas as pd

from src.config import (
    PROPERTY_REFERENCE_MANUAL_GLOBS,
    RAW_PUBLIC_DIR_COTALITY,
)
from src.property_reference._common import (
    empty_with_columns,
    resolve_latest_by_glob,
    validate_required_columns,
)


_HVI_COLUMNS = [
    "as_of_date",
    "region",
    "property_type",
    "median_value_aud",
    "monthly_pct_change",
    "quarterly_pct_change",
    "annual_pct_change",
    "peak_to_trough_decline_pct",
    "source_note",
]
_AUCTION_COLUMNS = [
    "as_of_date",
    "region",
    "quarter_avg_clearance_rate_pct",
    "quarter_min_clearance_rate_pct",
    "quarter_max_clearance_rate_pct",
    "total_auctions_held_count",
    "source_note",
]


def load_cotality_hvi() -> pd.DataFrame:
    """Cotality Home Value Index monthly release (manual quarterly aggregation).

    Source: https://www.cotality.com/au/news-research/insights/home-value-index/
    Granularity: national + 8 capital cities + combined regional.
    """
    path = resolve_latest_by_glob(
        RAW_PUBLIC_DIR_COTALITY,
        PROPERTY_REFERENCE_MANUAL_GLOBS["cotality_hvi"],
    )
    if path is None:
        return empty_with_columns(_HVI_COLUMNS)
    df = pd.read_csv(path, comment="#")
    validate_required_columns(df, _HVI_COLUMNS, path)
    return df[_HVI_COLUMNS].copy()


def load_cotality_auction_clearance() -> pd.DataFrame:
    """Cotality weekly auction clearance (manual quarterly aggregation).

    Source: https://www.cotality.com/au/our-data/auction-results
    """
    path = resolve_latest_by_glob(
        RAW_PUBLIC_DIR_COTALITY,
        PROPERTY_REFERENCE_MANUAL_GLOBS["cotality_auction_clearance"],
    )
    if path is None:
        return empty_with_columns(_AUCTION_COLUMNS)
    df = pd.read_csv(path, comment="#")
    validate_required_columns(df, _AUCTION_COLUMNS, path)
    return df[_AUCTION_COLUMNS].copy()
