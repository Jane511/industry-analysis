"""Loader for SQM Research free headline data (manual extract)."""

from __future__ import annotations

import pandas as pd

from src.config import (
    PROPERTY_REFERENCE_MANUAL_GLOBS,
    RAW_PUBLIC_DIR_SQM,
)
from src.property_reference._common import (
    empty_with_columns,
    resolve_latest_by_glob,
    validate_required_columns,
)


_SQM_COLUMNS = [
    "as_of_date",
    "region",
    "vacancy_rate_pct",
    "vendor_discount_pct",
    "stock_on_market_count",
    "asking_price_houses_aud",
    "asking_price_units_aud",
    "source_note",
]


def load_sqm_headline() -> pd.DataFrame:
    """SQM Research free headline — vacancy, vendor discount, stock on market.

    Source: https://sqmresearch.com.au/
    Granularity: capital city.
    """
    path = resolve_latest_by_glob(
        RAW_PUBLIC_DIR_SQM,
        PROPERTY_REFERENCE_MANUAL_GLOBS["sqm_headline"],
    )
    if path is None:
        return empty_with_columns(_SQM_COLUMNS)
    df = pd.read_csv(path, comment="#")
    validate_required_columns(df, _SQM_COLUMNS, path)
    return df[_SQM_COLUMNS].copy()
