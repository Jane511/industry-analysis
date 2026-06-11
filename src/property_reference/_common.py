"""Shared helpers for property-reference loaders."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def resolve_latest_by_glob(directory: Path, pattern: str) -> Path | None:
    """Return the most recent file in ``directory`` matching ``pattern``.

    Files are sorted lexicographically by name. The naming convention
    (``<source>_<YYYYQN>.csv``) makes lex-order equivalent to chronological
    order. Files matching ``*TEMPLATE*`` are skipped — those are committed
    headers-only schemas, not data.
    """
    if not directory.exists():
        return None
    candidates = sorted(
        p
        for p in directory.glob(pattern)
        if "TEMPLATE" not in p.name
    )
    return candidates[-1] if candidates else None


def empty_with_columns(columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=columns)


def validate_required_columns(df: pd.DataFrame, required: list[str], path: Path) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise RuntimeError(
            f"{path.name} missing required columns: {missing}. "
            f"Expected canonical schema: {required}"
        )
