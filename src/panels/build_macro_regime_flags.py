"""Build macro-regime flags for downstream overlays."""

from __future__ import annotations

import pandas as pd

from src.arrears_environment import build_base_arrears_environment
from src.config import PROCESSED_PUBLIC_PROPERTY_REFERENCE_DIR
from src.output import save_csv
from src.public_data.download_apra_property_exposures import load_optional_apra_property_context
from src.public_data.download_rba_rates import load_cash_rate_summary, load_optional_rba_housing_context


def _cash_rate_regime(cash_rate_latest_pct: float, cash_rate_change_1y_pctpts: float) -> str:
    if cash_rate_latest_pct >= 4.0 and cash_rate_change_1y_pctpts > 0:
        return "restrictive_rising"
    if cash_rate_latest_pct >= 4.0 and cash_rate_change_1y_pctpts <= 0:
        return "restrictive_easing"
    if cash_rate_latest_pct < 4.0 and cash_rate_change_1y_pctpts < 0:
        return "neutral_easing"
    return "neutral_or_tightening"


def build_macro_regime_flags() -> pd.DataFrame:
    PROCESSED_PUBLIC_PROPERTY_REFERENCE_DIR.mkdir(parents=True, exist_ok=True)

    cash_rate_summary = load_cash_rate_summary()
    rba_context = load_optional_rba_housing_context()
    apra_context = load_optional_apra_property_context()
    arrears_environment = build_base_arrears_environment(cash_rate_summary, rba_context, apra_context)

    cash_rate_latest_pct = float(cash_rate_summary["cash_rate_latest_pct"].iloc[0])
    cash_rate_change_1y_pctpts = float(cash_rate_summary["cash_rate_change_1y_pctpts"].iloc[0])
    arrears_level = str(arrears_environment["arrears_environment_level"].iloc[0]).lower()

    flags = pd.DataFrame(
        [
            {
                "as_of_date": cash_rate_summary["as_of_date"].iloc[0],
                "cash_rate_regime": _cash_rate_regime(cash_rate_latest_pct, cash_rate_change_1y_pctpts),
                "arrears_environment_level": arrears_environment["arrears_environment_level"].iloc[0],
                "arrears_trend": arrears_environment["arrears_trend"].iloc[0],
                "macro_regime_flag": "downturn_watch" if arrears_level in {"elevated", "high"} else "base",
                "source_dataset": "RBA F1 cash-rate table + staged arrears context",
            }
        ]
    )
    save_csv(flags, PROCESSED_PUBLIC_PROPERTY_REFERENCE_DIR / "macro_regime_flags.csv")
    return flags

