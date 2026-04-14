"""ASIC insolvency public-data loader (manual-stage compatible)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import RAW_MANUAL_DIR, RAW_PUBLIC_DIR


OPTIONAL_ASIC_INSOLVENCY_FILES = (
    "asic_insolvency_extract.csv",
    "asic_insolvency_extract.xlsx",
)


def _resolve_existing_file(candidates: tuple[str, ...], search_dirs: list[Path]) -> Path | None:
    for directory in search_dirs:
        for candidate in candidates:
            path = directory / candidate
            if path.exists():
                return path
    return None


def load_optional_asic_insolvency_extract() -> pd.DataFrame:
    path = _resolve_existing_file(OPTIONAL_ASIC_INSOLVENCY_FILES, [RAW_PUBLIC_DIR, RAW_MANUAL_DIR])
    if path is None:
        return pd.DataFrame(columns=["as_of_date", "industry", "insolvency_count", "source_note"])

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)

    required = {"as_of_date", "industry", "insolvency_count"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"{path.name} is missing required columns: {sorted(missing)}")

    out = df.copy()
    out["as_of_date"] = pd.to_datetime(out["as_of_date"], errors="coerce").dt.date.astype("string")
    out["insolvency_count"] = pd.to_numeric(out["insolvency_count"], errors="coerce")
    out["source_note"] = out.get("source_note", f"Staged ASIC insolvency extract ({path.name})")
    return out[["as_of_date", "industry", "insolvency_count", "source_note"]]

