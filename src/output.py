from __future__ import annotations

from pathlib import Path

import pandas as pd


def save_csv(df: pd.DataFrame, path: Path) -> None:
    """Write a flat CSV contract with deterministic formatting.

    CSV does not preserve dtypes. Callers and downstream consumers should read
    canonical exports through ``src.csv_io`` helpers, which enforce date,
    nullable-integer, string, boolean, and numeric dtypes on load. The current
    11 exports are flat tables; CSV is not suitable for future nested or
    multi-index structures without a separate design decision.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8", lineterminator="\n")


def validate_csv_roundtrip(df: pd.DataFrame, path: Path) -> pd.DataFrame:
    """Write ``df`` to CSV and read it back, asserting schema parity."""
    save_csv(df, path)
    roundtrip = pd.read_csv(path)
    if list(roundtrip.columns) != list(df.columns):
        raise ValueError(
            f"CSV roundtrip schema mismatch for {path}: "
            f"{list(roundtrip.columns)} != {list(df.columns)}"
        )
    return roundtrip
