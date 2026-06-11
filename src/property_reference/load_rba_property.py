"""RBA loaders for the property reference layer (Table E2 + FSR aggregates)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import RAW_PUBLIC_DIR_RBA, RBA_PROPERTY_REFERENCE_FILENAMES
from src.property_reference._common import empty_with_columns


_TABLE_E2_COLUMNS = [
    "as_of_date",
    "metric",
    "value",
    "source_note",
]
_FSR_COLUMNS = [
    "as_of_date",
    "metric",
    "value",
    "source_note",
    "chart_reference",
]


def _resolve(filename_key: str) -> Path:
    return RAW_PUBLIC_DIR_RBA / RBA_PROPERTY_REFERENCE_FILENAMES[filename_key]


def load_rba_table_e2() -> pd.DataFrame:
    """RBA Statistical Table E2 — Housing Loan Payments.

    Source: https://www.rba.gov.au/statistics/tables/xls/e02hist.xls
    Cadence: quarterly.

    Returns a long ``(as_of_date, metric, value, source_note)`` frame so the
    macro / property-reference panels can read whichever metric they want
    without having to know the table's wide schema. Empty frame if file
    absent.
    """
    path = _resolve("table_e2_housing_loan_payments")
    if not path.exists():
        return empty_with_columns(_TABLE_E2_COLUMNS)

    try:
        raw = pd.read_excel(path, sheet_name="Data", header=None)
    except Exception:
        # Some E2 vintages put the data on the only sheet rather than "Data".
        raw = pd.read_excel(path, header=None)

    # The first column is dates; the row at index 10 (0-based 10) is typically
    # the first numeric row. Header rows vary across RBA vintages, so we
    # skip rows where column 0 is not a recognisable date.
    rows = []
    for _, r in raw.iterrows():
        date_val = pd.to_datetime(r.iloc[0], errors="coerce")
        if pd.isna(date_val):
            continue
        for j in range(1, raw.shape[1]):
            val = pd.to_numeric(r.iloc[j], errors="coerce")
            if pd.isna(val):
                continue
            metric_label = str(raw.iloc[0, j]) if pd.notna(raw.iloc[0, j]) else f"col_{j}"
            rows.append(
                {
                    "as_of_date": date_val.date().isoformat(),
                    "metric": metric_label,
                    "value": float(val),
                    "source_note": f"RBA Table E2 ({path.name})",
                }
            )
    return pd.DataFrame(rows, columns=_TABLE_E2_COLUMNS)


def load_rba_fsr_aggregates() -> pd.DataFrame:
    """Manually-extracted RBA Financial Stability Review aggregates.

    Source: https://www.rba.gov.au/publications/fsr/
    Cadence: semi-annual. Manual extraction — see
    ``data/raw/public/rba/rba_fsr_aggregates_<MMMYYYY>.csv``.
    """
    path = _resolve("fsr_aggregates")
    if not path.exists():
        return empty_with_columns(_FSR_COLUMNS)

    df = pd.read_csv(path)
    expected = {"as_of_date", "metric", "value"}
    missing = expected.difference(df.columns)
    if missing:
        raise RuntimeError(
            f"{path.name} missing required FSR columns: {sorted(missing)}"
        )
    if "source_note" not in df.columns:
        df["source_note"] = f"RBA FSR aggregates ({path.name})"
    if "chart_reference" not in df.columns:
        df["chart_reference"] = ""
    return df[_FSR_COLUMNS].copy()
