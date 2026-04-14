"""Build the canonical business-cycle panel from public data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import PROCESSED_PUBLIC_INDUSTRY_DIR, RAW_PUBLIC_DIR_ABS
from src.panels.foundation_signals import build_foundation
from src.panels.macro_signals import build_macro_view
from src.output import save_csv


def build_business_cycle_panel(
    public_dir: Path | None = None,
    processed_dir: Path | None = None,
) -> pd.DataFrame:
    public_dir = public_dir or RAW_PUBLIC_DIR_ABS
    processed_dir = processed_dir or PROCESSED_PUBLIC_INDUSTRY_DIR
    processed_dir.mkdir(parents=True, exist_ok=True)

    foundation_df = build_foundation(public_dir, processed_dir)
    macro_df = build_macro_view(foundation_df, public_dir, processed_dir)
    save_csv(macro_df, processed_dir / "business_cycle_panel.csv")
    return macro_df
