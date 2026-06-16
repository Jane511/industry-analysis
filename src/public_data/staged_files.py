"""Resolve source-key -> staged-file path on disk.

ABS catalogue numbers are stable across releases; only the date suffix in the
filename rotates. Earlier code hard-coded a specific vintage filename in every
loader, which forced a code edit on every refresh and prevented the report
from detecting that a manually-staged workbook was actually present on disk.
This module centralises the mapping so loaders and the source-inventory check
share one definition.
"""

from __future__ import annotations

from pathlib import Path

from src.config import (
    RAW_PUBLIC_DIR,
    RAW_PUBLIC_DIR_ABS,
    RAW_PUBLIC_DIR_PTRS,
    RAW_PUBLIC_DIR_RBA,
)


# Per source key, the directory and glob pattern used to locate the staged
# workbook or CSV. The glob pattern matches by catalogue-number prefix where
# applicable so a fresh release replaces the prior file without any code edit.
SOURCE_KEY_STAGED_LOCATIONS: dict[str, tuple[Path, str]] = {
    # ABS Australian Industry annual workbook
    "australian_industry_xlsx": (RAW_PUBLIC_DIR_ABS, "81550DO001*.xlsx"),
    # ABS Business Indicators quarterly workbooks
    "business_indicators_profit_ratio_xlsx": (RAW_PUBLIC_DIR_ABS, "56760022*.xlsx"),
    "business_indicators_inventory_ratio_xlsx": (RAW_PUBLIC_DIR_ABS, "56760023*.xlsx"),
    "business_indicators_consumer_sales_xlsx": (RAW_PUBLIC_DIR_ABS, "56760024*.xlsx"),
    # ABS Labour Force monthly detailed workbook
    "labour_force_industry_xlsx": (RAW_PUBLIC_DIR_ABS, "6291004*.xlsx"),
    # ABS Building Approvals monthly workbook
    "building_approvals_nonres_xlsx": (RAW_PUBLIC_DIR_ABS, "87310051*.xlsx"),
    # ABS economy-wide headline workbooks (live macro base levels)
    "national_accounts_gdp_xlsx": (RAW_PUBLIC_DIR_ABS, "5206001*national_accounts*.xlsx"),
    "labour_force_headline_xlsx": (RAW_PUBLIC_DIR_ABS, "6202001*labour_force*.xlsx"),
    "wpi_xlsx": (RAW_PUBLIC_DIR_ABS, "63450001*.xlsx"),
    # ABS Macro overlay catalogues
    "cpi_all_groups_xlsx": (RAW_PUBLIC_DIR_ABS, "64010001*.xlsx"),
    "cpi_subgroups_xlsx": (RAW_PUBLIC_DIR_ABS, "64010007*.xlsx"),
    "ppi_manufacturing_xlsx": (RAW_PUBLIC_DIR_ABS, "64270012*.xlsx"),
    "ppi_construction_xlsx": (RAW_PUBLIC_DIR_ABS, "64270013*.xlsx"),
    "dwelling_approvals_xlsx": (RAW_PUBLIC_DIR_ABS, "87520006*.xlsx"),
    "dwelling_value_xlsx": (RAW_PUBLIC_DIR_ABS, "87520011*.xlsx"),
    # ABS Property reference catalogues
    "property_price_index_xlsx": (RAW_PUBLIC_DIR_ABS, "64160001*.xlsx"),
    "property_price_capitals_xlsx": (RAW_PUBLIC_DIR_ABS, "64160002*.xlsx"),
    "total_value_dwellings_xlsx": (RAW_PUBLIC_DIR_ABS, "64320001*.xlsx"),
    "lending_indicators_xlsx": (RAW_PUBLIC_DIR_ABS, "56010001*.xlsx"),
    # RBA tables and cash rate
    "rba_cash_rate_csv": (RAW_PUBLIC_DIR, "rba_f1_data.csv"),
    "rba_table_e2_xls": (RAW_PUBLIC_DIR_RBA, "rba_e2*.xls*"),
    # PTRS regulator PDFs
    "ptrs_cycle_8_pdf": (RAW_PUBLIC_DIR_PTRS, "reg-update-july-2025*.pdf"),
    "ptrs_cycle_9_pdf": (RAW_PUBLIC_DIR_PTRS, "regulators-update-202601*.pdf"),
    "ptrs_guidance": (RAW_PUBLIC_DIR_PTRS, "ptrs-guidance-materials*.pdf"),
}


def find_latest_staged_file(key: str) -> Path | None:
    """Return the latest staged file for a source key, or None when missing.

    "Latest" is determined lexicographically over the glob match list. ABS
    catalogue filenames embed a year-month token (``_dec2025_``, ``_feb2026_``)
    that sorts correctly under lexical ordering for any contiguous release
    cadence within a single decade.
    """
    location = SOURCE_KEY_STAGED_LOCATIONS.get(key)
    if location is None:
        return None
    directory, pattern = location
    if not directory.exists():
        return None
    matches = sorted(directory.glob(pattern))
    if not matches:
        return None
    return matches[-1]


def resolve_staged_file(key: str) -> Path:
    """Same as :func:`find_latest_staged_file` but raises on miss.

    Loaders should call this; presence-checks should call ``find_...`` and
    handle ``None`` themselves.
    """
    path = find_latest_staged_file(key)
    if path is None:
        location = SOURCE_KEY_STAGED_LOCATIONS.get(key)
        if location is None:
            raise KeyError(f"No staged-file pattern registered for source key: {key}")
        directory, pattern = location
        raise FileNotFoundError(
            f"No staged file matches `{pattern}` under `{directory}` for source key `{key}`."
        )
    return path
