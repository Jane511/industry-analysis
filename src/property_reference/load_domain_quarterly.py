"""Loader for the Domain Quarterly House Price Report (manual extract)."""

from __future__ import annotations

import pandas as pd

from src.config import (
    PROPERTY_REFERENCE_MANUAL_GLOBS,
    RAW_PUBLIC_DIR_DOMAIN,
)
from src.property_reference._common import (
    empty_with_columns,
    resolve_latest_by_glob,
    validate_required_columns,
)


_DOMAIN_COLUMNS = [
    "as_of_date",
    "region_type",
    "region",
    "state",
    "property_type",
    "median_price_aud",
    "quarterly_pct_change",
    "annual_pct_change",
    "median_days_on_market",
    "median_vendor_discount_pct",
    "median_rental_yield_gross_pct",
    "source_note",
]


def load_domain_quarterly() -> pd.DataFrame:
    """Domain Quarterly House Price Report — capital cities + selected suburbs.

    Source: https://www.domain.com.au/research/house-price-report/
    Cadence: quarterly. Suburb rows are limited to whatever Domain explicitly
    publishes (typically top ~50-100 per capital).
    """
    path = resolve_latest_by_glob(
        RAW_PUBLIC_DIR_DOMAIN,
        PROPERTY_REFERENCE_MANUAL_GLOBS["domain_quarterly"],
    )
    if path is None:
        return empty_with_columns(_DOMAIN_COLUMNS)
    df = pd.read_csv(path, comment="#")
    validate_required_columns(df, _DOMAIN_COLUMNS, path)
    return df[_DOMAIN_COLUMNS].copy()
