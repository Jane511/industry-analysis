from pathlib import Path

import pandas as pd

from src.output import save_csv


def build_portfolio_proxy(macro_df: pd.DataFrame, processed_dir: Path) -> pd.DataFrame:
    df = macro_df[["industry", "sales_m_latest", "employment_000_latest"]].copy()
    df["sales_share"] = df["sales_m_latest"] / df["sales_m_latest"].sum()
    df["employment_share"] = df["employment_000_latest"] / df["employment_000_latest"].sum()
    df["current_exposure_pct"] = ((0.7 * df["sales_share"] + 0.3 * df["employment_share"]) * 100).round(1)
    df["exposure_proxy_source"] = (
        "public proxy based on 70% industry sales share and 30% employment share from ABS Australian Industry"
    )
    out = df[["industry", "current_exposure_pct", "exposure_proxy_source"]]
    save_csv(out, processed_dir / "industry_portfolio_proxy.csv")
    return out
