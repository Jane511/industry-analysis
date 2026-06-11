"""Loaders for ABS property-reference catalogues (6416.0, 6432.0, 5601.0).

Each loader returns a DataFrame keyed by ``(as_of_date, region, property_type)``
or ``(as_of_date, state)`` depending on the source's natural granularity.
When the underlying ABS xlsx is absent (the brief expects manual staging),
loaders return an empty DataFrame with the canonical columns.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import (
    ABS_PROPERTY_REFERENCE_FILENAMES,
    RAW_PUBLIC_DIR_ABS,
)
from src.property_reference._common import empty_with_columns
from src.public_data.load_abs_manual_exports import _abs_long_series, _read_abs_data1


_PROPERTY_PRICE_COLUMNS = [
    "as_of_date",
    "region",
    "abs_price_index_value",
    "abs_price_index_yoy_pct",
    "abs_price_index_qoq_pct",
    "source_note",
]
_TOTAL_VALUE_COLUMNS = [
    "as_of_date",
    "state",
    "total_value_dwellings_aud_millions",
    "yoy_pct_change",
    "source_note",
]
_LENDING_COLUMNS = [
    "as_of_date",
    "state",
    "abs_new_housing_finance_aud_millions",
    "abs_new_finance_yoy_pct",
    "source_note",
]


def _resolve(filename_key: str) -> Path:
    return RAW_PUBLIC_DIR_ABS / ABS_PROPERTY_REFERENCE_FILENAMES[filename_key]


def _yoy_qoq_from_series(series: pd.Series) -> tuple[float, float]:
    series = series.dropna()
    if len(series) < 2:
        return float("nan"), float("nan")
    latest = float(series.iloc[-1])
    prev_q = float(series.iloc[-2])
    qoq = (latest / prev_q - 1) * 100 if prev_q else float("nan")
    yoy = float("nan")
    if len(series) >= 5 and series.iloc[-5]:
        yoy = (latest / float(series.iloc[-5]) - 1) * 100
    return yoy, qoq


def load_abs_property_price_index() -> pd.DataFrame:
    """Cat. 6416.0 Residential Property Price Indexes (capital city, quarterly).

    Source: https://www.abs.gov.au/.../residential-property-price-indexes-eight-capital-cities/
    Cadence: quarterly. Granularity: 8 capital cities + weighted national.
    """
    path = _resolve("property_price_index")
    if not path.exists():
        return empty_with_columns(_PROPERTY_PRICE_COLUMNS)

    long_df = _abs_long_series(_read_abs_data1(path), header_part_index=1)
    if long_df.empty:
        return empty_with_columns(_PROPERTY_PRICE_COLUMNS)

    rows = []
    for label, group in long_df.groupby("series_label"):
        group = group.sort_values("date").dropna(subset=["value"])
        if group.empty:
            continue
        latest_q = group["date"].max()
        for q in sorted(group["date"].unique())[-8:]:
            until = group[group["date"] <= q]["value"]
            yoy, qoq = _yoy_qoq_from_series(until)
            rows.append(
                {
                    "as_of_date": pd.Timestamp(q).date().isoformat(),
                    "region": label,
                    "abs_price_index_value": float(until.iloc[-1]) if not until.empty else float("nan"),
                    "abs_price_index_yoy_pct": round(yoy, 2) if pd.notna(yoy) else float("nan"),
                    "abs_price_index_qoq_pct": round(qoq, 2) if pd.notna(qoq) else float("nan"),
                    "source_note": f"ABS Cat. 6416.0 ({path.name})",
                }
            )
    return pd.DataFrame(rows, columns=_PROPERTY_PRICE_COLUMNS)


def load_abs_total_value_dwellings() -> pd.DataFrame:
    """Cat. 6432.0 Total Value of Dwellings (state, quarterly).

    Source: https://www.abs.gov.au/.../total-value-dwellings/
    """
    path = _resolve("total_value_dwellings")
    if not path.exists():
        return empty_with_columns(_TOTAL_VALUE_COLUMNS)

    long_df = _abs_long_series(_read_abs_data1(path), header_part_index=1)
    if long_df.empty:
        return empty_with_columns(_TOTAL_VALUE_COLUMNS)

    rows = []
    for label, group in long_df.groupby("series_label"):
        group = group.sort_values("date").dropna(subset=["value"])
        if group.empty:
            continue
        latest = group.iloc[-1]
        prev = group[group["date"] <= latest["date"] - pd.DateOffset(years=1)]
        prev_value = float(prev.iloc[-1]["value"]) if not prev.empty else None
        yoy = (
            (float(latest["value"]) / prev_value - 1) * 100
            if prev_value
            else float("nan")
        )
        rows.append(
            {
                "as_of_date": pd.Timestamp(latest["date"]).date().isoformat(),
                "state": label,
                "total_value_dwellings_aud_millions": float(latest["value"]),
                "yoy_pct_change": round(yoy, 2) if pd.notna(yoy) else float("nan"),
                "source_note": f"ABS Cat. 6432.0 ({path.name})",
            }
        )
    return pd.DataFrame(rows, columns=_TOTAL_VALUE_COLUMNS)


def load_abs_lending_indicators() -> pd.DataFrame:
    """Cat. 5601.0 Lending Indicators — housing finance commitments by state.

    Source: https://www.abs.gov.au/.../lending-indicators/
    Cadence: monthly.
    """
    path = _resolve("lending_indicators")
    if not path.exists():
        return empty_with_columns(_LENDING_COLUMNS)

    long_df = _abs_long_series(_read_abs_data1(path), header_part_index=1)
    if long_df.empty:
        return empty_with_columns(_LENDING_COLUMNS)

    rows = []
    for label, group in long_df.groupby("series_label"):
        group = group.sort_values("date").dropna(subset=["value"])
        if group.empty:
            continue
        latest = group.iloc[-1]
        prev = group[group["date"] <= latest["date"] - pd.DateOffset(years=1)]
        prev_value = float(prev.iloc[-1]["value"]) if not prev.empty else None
        yoy = (
            (float(latest["value"]) / prev_value - 1) * 100
            if prev_value
            else float("nan")
        )
        rows.append(
            {
                "as_of_date": pd.Timestamp(latest["date"]).date().isoformat(),
                "state": label,
                "abs_new_housing_finance_aud_millions": float(latest["value"]),
                "abs_new_finance_yoy_pct": round(yoy, 2) if pd.notna(yoy) else float("nan"),
                "source_note": f"ABS Cat. 5601.0 ({path.name})",
            }
        )
    return pd.DataFrame(rows, columns=_LENDING_COLUMNS)
