from pathlib import Path
import os

import numpy as np
import pandas as pd

from src.config import PTRS_AR_WORKBOOK_FILENAME, RAW_PUBLIC_DIR_PTRS
from src.load_public_data import parse_ptrs_ar_workbook
from src.output import save_csv

QUARTER_DAYS = 91.25


def _clip_round(series: pd.Series, lower: float, upper: float, digits: int = 1) -> pd.Series:
    return series.clip(lower=lower, upper=upper).round(digits)


def _first_available(row: pd.Series, columns: list[str], default: float = np.nan) -> float:
    for column in columns:
        value = row.get(column)
        if pd.notna(value):
            return float(value)
    return default


def _estimate_inventory_days(row: pd.Series) -> float:
    inventory_ratio = row.get("inventories_to_sales_ratio_latest")
    if pd.notna(inventory_ratio):
        margin = _first_available(
            row,
            ["gross_operating_profit_to_sales_ratio_latest", "ebitda_margin_pct_latest"],
            default=0.10,
        )
        if margin > 1:
            margin = margin / 100
        cogs_ratio = float(np.clip(1 - margin, 0.45, 0.95))
        return round(float(inventory_ratio) * QUARTER_DAYS / cogs_ratio, 1)

    wages_ratio = row.get("wages_to_sales_pct_latest")
    demand_growth = row.get("demand_yoy_growth_pct")
    base_days = 20.0
    if pd.notna(wages_ratio):
        base_days -= min(float(wages_ratio) / 4, 10)
    if pd.notna(demand_growth) and demand_growth < 0:
        base_days += min(abs(float(demand_growth)) / 5, 15)
    return round(float(np.clip(base_days, 5, 90)), 1)


def _resolve_ptrs_workbook_path(ptrs_workbook_path: Path | None = None) -> Path | None:
    if ptrs_workbook_path is not None and Path(ptrs_workbook_path).exists():
        return Path(ptrs_workbook_path)

    env_path = os.environ.get("PTRS_AR_WORKBOOK_PATH")
    if env_path and Path(env_path).exists():
        return Path(env_path)

    default_path = RAW_PUBLIC_DIR_PTRS / PTRS_AR_WORKBOOK_FILENAME
    if default_path.exists():
        return default_path

    return None


def _load_ptrs_ar_benchmarks(ptrs_workbook_path: Path | None = None) -> pd.DataFrame:
    resolved_path = _resolve_ptrs_workbook_path(ptrs_workbook_path)
    if resolved_path is None:
        return pd.DataFrame()

    ptrs = parse_ptrs_ar_workbook(resolved_path)
    if ptrs.empty:
        return ptrs

    ptrs["ar_days_benchmark"] = ptrs["ptrs_adjusted_base_ar_days"].combine_first(ptrs["ptrs_base_ar_days"])
    ptrs["ar_days_stress_benchmark"] = ptrs["ptrs_adjusted_stress_ar_days"].combine_first(ptrs["ptrs_stress_ar_days"])
    ptrs["ar_days_severe_benchmark"] = ptrs["ptrs_adjusted_severe_ar_days"].combine_first(ptrs["ptrs_severe_ar_days"])
    ptrs["ar_days_benchmark_source"] = "PTRS official public payment-times proxy"
    ptrs["ap_days_benchmark"] = ptrs["ptrs_adjusted_base_ar_days"].combine_first(ptrs["ptrs_base_ar_days"])
    ptrs["ap_days_stress_benchmark"] = ptrs["ptrs_adjusted_stress_ar_days"].combine_first(ptrs["ptrs_stress_ar_days"])
    ptrs["ap_days_severe_benchmark"] = ptrs["ptrs_adjusted_severe_ar_days"].combine_first(ptrs["ptrs_severe_ar_days"])
    ptrs["ap_days_benchmark_source"] = "PTRS official public payment-times proxy"
    return ptrs[
        [
            "anzsic_division_code",
            "ptrs_industry",
            "ptrs_cycle8_avg_payment_days",
            "ptrs_cycle9_avg_payment_days",
            "ar_days_benchmark",
            "ar_days_stress_benchmark",
            "ar_days_severe_benchmark",
            "ap_days_benchmark",
            "ap_days_stress_benchmark",
            "ap_days_severe_benchmark",
            "ptrs_cycle8_paid_on_time_pct",
            "ptrs_cycle9_paid_on_time_pct",
            "ptrs_latest_cycle_used",
            "ar_days_benchmark_source",
            "ap_days_benchmark_source",
        ]
    ].copy()


def build_industry_benchmarks(
    public_df: pd.DataFrame,
    processed_dir: Path,
    ptrs_workbook_path: Path | None = None,
) -> pd.DataFrame:
    df = public_df.copy()

    df["profit_margin_pct"] = df.apply(
        lambda row: _first_available(
            row,
            ["gross_operating_profit_to_sales_ratio_latest", "ebitda_margin_pct_latest"],
            default=10.0,
        ),
        axis=1,
    )
    df["profit_margin_pct"] = df["profit_margin_pct"].where(df["profit_margin_pct"] > 1, df["profit_margin_pct"] * 100)
    if "inventory_days_est" in df.columns:
        df["inventory_days_benchmark"] = df["inventory_days_est"].combine_first(df.apply(_estimate_inventory_days, axis=1))
    else:
        df["inventory_days_benchmark"] = df.apply(_estimate_inventory_days, axis=1)
    df["inventory_days_yoy_change"] = df.get("inventory_days_yoy_change", np.nan)
    df["inventory_stock_build_risk"] = df.get("inventory_stock_build_risk", np.nan)
    df["inventory_days_benchmark_source"] = df.get(
        "inventory_days_est_source",
        "Fallback inventory-days estimate derived from public margin, sales, demand, and sector inventory profile",
    )

    low_receivable_sectors = {
        "retail trade",
        "accommodation and food services",
    }
    low_receivable_mask = df["sector_key"].isin(low_receivable_sectors)
    ar_base = (
        18
        + df["inventory_days_benchmark"].fillna(0) * 0.22
        + df["classification_risk_score"].fillna(3) * 3.2
        - df["profit_margin_pct"].fillna(10) * 0.35
    )
    ar_base = ar_base.where(~low_receivable_mask, ar_base * 0.35)
    df["ar_days_benchmark_formula"] = _clip_round(ar_base, 5, 75)

    ptrs = _load_ptrs_ar_benchmarks(ptrs_workbook_path)
    if not ptrs.empty and "anzsic_division_code" in df.columns:
        df = df.merge(ptrs, on="anzsic_division_code", how="left")
        df["ar_days_benchmark"] = df["ar_days_benchmark"].combine_first(df["ar_days_benchmark_formula"])
        df["ar_days_benchmark_source"] = df["ar_days_benchmark_source"].fillna(
            "Derived from public industry signals using deterministic proxy formula"
        )
    else:
        df["ar_days_benchmark"] = df["ar_days_benchmark_formula"]
        df["ar_days_benchmark_source"] = "Derived from public industry signals using deterministic proxy formula"
        df["ar_days_stress_benchmark"] = np.nan
        df["ar_days_severe_benchmark"] = np.nan
        df["ptrs_cycle8_avg_payment_days"] = np.nan
        df["ptrs_cycle9_avg_payment_days"] = np.nan
        df["ptrs_cycle8_paid_on_time_pct"] = np.nan
        df["ptrs_cycle9_paid_on_time_pct"] = np.nan
        df["ptrs_latest_cycle_used"] = np.nan

    ap_base = (
        24
        + df["inventory_days_benchmark"].fillna(0) * 0.18
        + df["macro_risk_score"].fillna(3) * 2.5
        - df["profit_margin_pct"].fillna(10) * 0.20
    )
    df["ap_days_benchmark_formula"] = _clip_round(ap_base, 20, 70)

    if not ptrs.empty and "anzsic_division_code" in df.columns:
        df["ap_days_benchmark"] = df["ap_days_benchmark"].combine_first(df["ap_days_benchmark_formula"])
        df["ap_days_benchmark_source"] = df["ap_days_benchmark_source"].fillna(
            "Derived from public industry signals using deterministic proxy formula"
        )
    else:
        df["ap_days_benchmark"] = df["ap_days_benchmark_formula"]
        df["ap_days_benchmark_source"] = "Derived from public industry signals using deterministic proxy formula"
        df["ap_days_stress_benchmark"] = np.nan
        df["ap_days_severe_benchmark"] = np.nan

    leverage_base = (
        1.2
        + (18 - df["profit_margin_pct"].fillna(10)).clip(lower=0) * 0.07
        + df["classification_risk_score"].fillna(3) * 0.22
        + df["macro_risk_score"].fillna(3) * 0.12
        + df["inventory_days_benchmark"].fillna(0) / 120
    )
    df["debt_to_ebitda_benchmark"] = _clip_round(leverage_base, 1.5, 4.5)

    icr_base = (
        5.3
        - df["debt_to_ebitda_benchmark"] * 0.75
        + df["profit_margin_pct"].fillna(10) * 0.04
        - (df["classification_risk_score"].fillna(3) - 3) * 0.10
    )
    df["icr_benchmark"] = _clip_round(icr_base, 1.5, 4.5)

    benchmark = df[
        [
            "sector_key",
            "industry",
            "ebitda_margin_pct_latest",
            "debt_to_ebitda_benchmark",
            "icr_benchmark",
            "ar_days_benchmark",
            "ar_days_stress_benchmark",
            "ar_days_severe_benchmark",
            "ap_days_benchmark",
            "ap_days_stress_benchmark",
            "ap_days_severe_benchmark",
            "inventory_days_benchmark",
            "inventory_days_yoy_change",
            "inventory_stock_build_risk",
            "inventory_days_benchmark_source",
            "ptrs_cycle8_avg_payment_days",
            "ptrs_cycle9_avg_payment_days",
            "ptrs_cycle8_paid_on_time_pct",
            "ptrs_cycle9_paid_on_time_pct",
            "ptrs_latest_cycle_used",
            "ar_days_benchmark_source",
            "ap_days_benchmark_source",
        ]
    ].copy()
    benchmark["benchmark_origin"] = (
        "ebitda margin from ABS Australian Industry; "
        "AR and AP days from PTRS official public payment-times proxy when available, otherwise fallback proxy formula; "
        "inventory days from ABS quarterly inventories/sales ratios when available, otherwise fallback public-signal estimate; "
        "other benchmarks estimated from public industry signals using deterministic proxy rules"
    )

    save_csv(benchmark, processed_dir / "industry_generated_benchmarks.csv")
    return benchmark
