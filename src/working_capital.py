"""Working-capital overlays for scorecard, PD, and LGD interpretation."""

from pathlib import Path

import numpy as np
import pandas as pd

from src.output import save_csv
from src.utils import risk_band, score_gap_higher_is_worse


def _round_score(values: list[float]) -> float:
    clean = [float(v) for v in values if pd.notna(v)]
    if not clean:
        return 3.0
    return round(float(np.mean(clean)), 2)


def _score_receivable_days(days_value: float) -> int:
    if pd.isna(days_value):
        return 3
    if days_value <= 20:
        return 1
    if days_value <= 25:
        return 2
    if days_value <= 30:
        return 3
    if days_value <= 35:
        return 4
    return 5


def _score_payable_days(days_value: float) -> int:
    if pd.isna(days_value):
        return 3
    if days_value <= 20:
        return 1
    if days_value <= 28:
        return 2
    if days_value <= 35:
        return 3
    if days_value <= 45:
        return 4
    return 5


def _score_inventory_days(days_value: float) -> int:
    if pd.isna(days_value):
        return 3
    if days_value <= 10:
        return 1
    if days_value <= 20:
        return 2
    if days_value <= 35:
        return 3
    if days_value <= 50:
        return 4
    return 5


def _score_uplift_days(days_value: float) -> int:
    if pd.isna(days_value):
        return 3
    if days_value <= 5:
        return 1
    if days_value <= 10:
        return 2
    if days_value <= 15:
        return 3
    if days_value <= 20:
        return 4
    return 5


def _score_paid_on_time(pct_value: float) -> int:
    if pd.isna(pct_value):
        return 3
    pct_value = float(pct_value)
    if pct_value <= 1:
        pct_value *= 100
    if pct_value >= 75:
        return 1
    if pct_value >= 68:
        return 2
    if pct_value >= 62:
        return 3
    if pct_value >= 55:
        return 4
    return 5


def _score_stock_build(flag: str) -> int:
    return {
        "Low": 1,
        "Moderate": 3,
        "Elevated": 4,
        "High": 5,
    }.get(flag, 3)


def _score_cash_conversion(days_value: float) -> int:
    if pd.isna(days_value):
        return 3
    if days_value <= 5:
        return 1
    if days_value <= 15:
        return 2
    if days_value <= 30:
        return 3
    if days_value <= 45:
        return 4
    return 5


def _score_stress_headroom(days_value: float) -> int:
    if pd.isna(days_value):
        return 3
    if days_value >= 15:
        return 1
    if days_value >= 10:
        return 2
    if days_value >= 5:
        return 3
    if days_value >= 0:
        return 4
    return 5


def _dominant_driver(row: pd.Series, columns: dict[str, str]) -> str:
    available = {label: row.get(column, np.nan) for label, column in columns.items()}
    available = {label: float(value) for label, value in available.items() if pd.notna(value)}
    if not available:
        return "Mixed"
    return max(available, key=available.get)


def build_working_capital_metrics(
    benchmark_df: pd.DataFrame,
    borrower_compare_df: pd.DataFrame,
    processed_dir: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    industry = benchmark_df.copy()
    industry["ptrs_paid_on_time_pct_latest"] = industry["ptrs_cycle9_paid_on_time_pct"].combine_first(
        industry["ptrs_cycle8_paid_on_time_pct"]
    )
    industry["ar_stress_uplift_days"] = (
        industry["ar_days_stress_benchmark"] - industry["ar_days_benchmark"]
    ).round(1)
    industry["ar_severe_uplift_days"] = (
        industry["ar_days_severe_benchmark"] - industry["ar_days_benchmark"]
    ).round(1)
    industry["ap_stress_uplift_days"] = (
        industry["ap_days_stress_benchmark"] - industry["ap_days_benchmark"]
    ).round(1)
    industry["ap_severe_uplift_days"] = (
        industry["ap_days_severe_benchmark"] - industry["ap_days_benchmark"]
    ).round(1)
    industry["cash_conversion_cycle_benchmark_days"] = (
        industry["ar_days_benchmark"] + industry["inventory_days_benchmark"] - industry["ap_days_benchmark"]
    ).round(1)
    industry["cash_conversion_cycle_stress_days"] = (
        industry["ar_days_stress_benchmark"].combine_first(industry["ar_days_benchmark"])
        + industry["inventory_days_benchmark"]
        - industry["ap_days_benchmark"]
    ).round(1)
    industry["cash_conversion_cycle_uplift_days"] = (
        industry["cash_conversion_cycle_stress_days"] - industry["cash_conversion_cycle_benchmark_days"]
    ).round(1)

    industry["ar_collection_score"] = industry.apply(
        lambda row: _round_score(
            [
                _score_receivable_days(row.get("ar_days_benchmark")),
                _score_uplift_days(row.get("ar_stress_uplift_days")),
                _score_paid_on_time(row.get("ptrs_paid_on_time_pct_latest")),
            ]
        ),
        axis=1,
    )
    industry["receivables_realisation_score"] = industry.apply(
        lambda row: _round_score(
            [
                _score_uplift_days(row.get("ar_stress_uplift_days")),
                _score_uplift_days(row.get("ar_severe_uplift_days")),
                _score_paid_on_time(row.get("ptrs_paid_on_time_pct_latest")),
            ]
        ),
        axis=1,
    )
    industry["ap_supplier_stretch_score"] = industry.apply(
        lambda row: _round_score(
            [
                _score_payable_days(row.get("ap_days_benchmark")),
                _score_uplift_days(row.get("ap_stress_uplift_days")),
                _score_paid_on_time(row.get("ptrs_paid_on_time_pct_latest")),
            ]
        ),
        axis=1,
    )
    industry["inventory_liquidity_score"] = industry["inventory_days_benchmark"].apply(_score_inventory_days)
    industry["inventory_stock_build_score"] = industry["inventory_stock_build_risk"].apply(_score_stock_build)
    industry["cash_conversion_cycle_score"] = industry["cash_conversion_cycle_benchmark_days"].apply(
        _score_cash_conversion
    )

    industry["working_capital_scorecard_overlay_score"] = industry.apply(
        lambda row: _round_score(
            [
                row.get("ar_collection_score"),
                row.get("ap_supplier_stretch_score"),
                row.get("inventory_liquidity_score"),
                row.get("cash_conversion_cycle_score"),
            ]
        ),
        axis=1,
    )
    industry["working_capital_pd_overlay_score"] = industry.apply(
        lambda row: _round_score(
            [
                row.get("working_capital_scorecard_overlay_score"),
                row.get("inventory_stock_build_score"),
                row.get("receivables_realisation_score"),
            ]
        ),
        axis=1,
    )
    industry["working_capital_lgd_overlay_score"] = industry.apply(
        lambda row: _round_score(
            [
                row.get("receivables_realisation_score"),
                row.get("inventory_liquidity_score"),
                row.get("inventory_stock_build_score"),
            ]
        ),
        axis=1,
    )
    industry["working_capital_scorecard_overlay_band"] = industry[
        "working_capital_scorecard_overlay_score"
    ].apply(risk_band)
    industry["working_capital_pd_overlay_band"] = industry["working_capital_pd_overlay_score"].apply(risk_band)
    industry["working_capital_lgd_overlay_band"] = industry["working_capital_lgd_overlay_score"].apply(risk_band)
    industry["scorecard_primary_driver"] = industry.apply(
        lambda row: _dominant_driver(
            row,
            {
                "AR collection pressure": "ar_collection_score",
                "AP supplier stretch": "ap_supplier_stretch_score",
                "Inventory liquidity": "inventory_liquidity_score",
                "Cash conversion cycle": "cash_conversion_cycle_score",
            },
        ),
        axis=1,
    )
    industry["pd_primary_driver"] = industry.apply(
        lambda row: _dominant_driver(
            row,
            {
                "Receivables realisation": "receivables_realisation_score",
                "Inventory stock build": "inventory_stock_build_score",
                "Cash conversion cycle": "cash_conversion_cycle_score",
            },
        ),
        axis=1,
    )
    industry["lgd_primary_driver"] = industry.apply(
        lambda row: _dominant_driver(
            row,
            {
                "Receivables realisation": "receivables_realisation_score",
                "Inventory liquidity": "inventory_liquidity_score",
                "Inventory stock build": "inventory_stock_build_score",
            },
        ),
        axis=1,
    )
    industry["metric_origin"] = (
        "AR/AP from reconstructed PTRS public payment-times tables when available; "
        "inventory from ABS quarterly inventories/sales ratio estimate; overlay scores are deterministic public-data-derived rules"
    )

    industry_out = industry[
        [
            "sector_key",
            "industry",
            "ar_days_benchmark",
            "ar_days_stress_benchmark",
            "ar_days_severe_benchmark",
            "ar_stress_uplift_days",
            "ar_severe_uplift_days",
            "ap_days_benchmark",
            "ap_days_stress_benchmark",
            "ap_days_severe_benchmark",
            "ap_stress_uplift_days",
            "ap_severe_uplift_days",
            "ptrs_paid_on_time_pct_latest",
            "inventory_days_benchmark",
            "inventory_days_yoy_change",
            "inventory_stock_build_risk",
            "cash_conversion_cycle_benchmark_days",
            "cash_conversion_cycle_stress_days",
            "cash_conversion_cycle_uplift_days",
            "ar_collection_score",
            "receivables_realisation_score",
            "ap_supplier_stretch_score",
            "inventory_liquidity_score",
            "inventory_stock_build_score",
            "cash_conversion_cycle_score",
            "working_capital_scorecard_overlay_score",
            "working_capital_scorecard_overlay_band",
            "working_capital_pd_overlay_score",
            "working_capital_pd_overlay_band",
            "working_capital_lgd_overlay_score",
            "working_capital_lgd_overlay_band",
            "scorecard_primary_driver",
            "pd_primary_driver",
            "lgd_primary_driver",
            "metric_origin",
        ]
    ].sort_values(["working_capital_pd_overlay_score", "industry"], ascending=[False, True])

    borrower = borrower_compare_df.copy()
    borrower["cash_conversion_cycle_days"] = (
        borrower["ar_days"] + borrower["inventory_days"] - borrower["ap_days"]
    ).round(1)
    borrower["cash_conversion_cycle_benchmark_days"] = (
        borrower["ar_days_benchmark"] + borrower["inventory_days_benchmark"] - borrower["ap_days_benchmark"]
    ).round(1)
    borrower["cash_conversion_cycle_gap_days"] = (
        borrower["cash_conversion_cycle_days"] - borrower["cash_conversion_cycle_benchmark_days"]
    ).round(1)
    borrower["cash_conversion_cycle_score"] = borrower.apply(
        lambda row: score_gap_higher_is_worse(
            max(float(row.get("cash_conversion_cycle_days", 0.0)), 0.0),
            max(float(row.get("cash_conversion_cycle_benchmark_days", 0.0)), 1.0),
        ),
        axis=1,
    )
    borrower = borrower.merge(
        industry_out[
            [
                "sector_key",
                "ar_days_stress_benchmark",
                "ap_days_stress_benchmark",
                "inventory_stock_build_risk",
                "inventory_stock_build_score",
                "working_capital_scorecard_overlay_score",
                "working_capital_pd_overlay_score",
                "working_capital_lgd_overlay_score",
            ]
        ],
        on="sector_key",
        how="left",
        suffixes=("", "_industry"),
    )
    borrower["receivables_headroom_to_stress_days"] = (
        borrower["ar_days_stress_benchmark"] - borrower["ar_days"]
    ).round(1)
    borrower["payables_headroom_to_stress_days"] = (
        borrower["ap_days_stress_benchmark"] - borrower["ap_days"]
    ).round(1)
    borrower["receivables_realisation_score"] = borrower["receivables_headroom_to_stress_days"].apply(
        _score_stress_headroom
    )
    borrower["supplier_stretch_score"] = borrower["payables_headroom_to_stress_days"].apply(_score_stress_headroom)
    borrower["working_capital_scorecard_metric_score"] = borrower.apply(
        lambda row: _round_score(
            [
                row.get("ar_days_score"),
                row.get("ap_days_score"),
                row.get("inventory_days_score"),
                row.get("cash_conversion_cycle_score"),
            ]
        ),
        axis=1,
    )
    borrower["working_capital_pd_metric_score"] = borrower.apply(
        lambda row: _round_score(
            [
                row.get("working_capital_scorecard_metric_score"),
                row.get("working_capital_pd_overlay_score"),
                row.get("receivables_realisation_score"),
                row.get("inventory_stock_build_score"),
            ]
        ),
        axis=1,
    )
    borrower["working_capital_lgd_metric_score"] = borrower.apply(
        lambda row: _round_score(
            [
                row.get("receivables_realisation_score"),
                row.get("inventory_days_score"),
                row.get("working_capital_lgd_overlay_score"),
            ]
        ),
        axis=1,
    )
    borrower["working_capital_scorecard_metric_band"] = borrower[
        "working_capital_scorecard_metric_score"
    ].apply(risk_band)
    borrower["working_capital_pd_metric_band"] = borrower["working_capital_pd_metric_score"].apply(risk_band)
    borrower["working_capital_lgd_metric_band"] = borrower["working_capital_lgd_metric_score"].apply(risk_band)
    borrower["metric_origin"] = (
        "Borrower rows are synthetic archetypes; AR/AP/inventory comparisons and overlay scores are deterministic comparisons against public-data-derived sector benchmarks"
    )

    borrower_out = borrower[
        [
            "borrower_name",
            "industry",
            "sector_key",
            "ar_days",
            "ar_days_benchmark",
            "ar_days_score",
            "receivables_headroom_to_stress_days",
            "ap_days",
            "ap_days_benchmark",
            "ap_days_score",
            "payables_headroom_to_stress_days",
            "inventory_days",
            "inventory_days_benchmark",
            "inventory_days_score",
            "inventory_stock_build_risk",
            "cash_conversion_cycle_days",
            "cash_conversion_cycle_benchmark_days",
            "cash_conversion_cycle_gap_days",
            "cash_conversion_cycle_score",
            "receivables_realisation_score",
            "supplier_stretch_score",
            "working_capital_scorecard_overlay_score",
            "working_capital_scorecard_metric_score",
            "working_capital_scorecard_metric_band",
            "working_capital_pd_overlay_score",
            "working_capital_pd_metric_score",
            "working_capital_pd_metric_band",
            "working_capital_lgd_overlay_score",
            "working_capital_lgd_metric_score",
            "working_capital_lgd_metric_band",
            "metric_origin",
        ]
    ].sort_values(["working_capital_pd_metric_score", "borrower_name"], ascending=[False, True])

    save_csv(industry_out, processed_dir / "industry_working_capital_risk_metrics.csv")
    save_csv(borrower_out, processed_dir / "borrower_working_capital_risk_metrics.csv")
    return industry_out, borrower_out
