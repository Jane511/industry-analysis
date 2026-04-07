from pathlib import Path
import shutil
from uuid import uuid4

import pandas as pd

from src.reporting import build_reporting_workbook, build_formal_chart_report


def _sample_foundation() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "sector_key": "construction",
                "cyclical_score": 4.0,
                "rate_sensitivity_score": 5.0,
                "demand_dependency_score": 4.0,
                "external_shock_score": 3.0,
            }
        ]
    )


def _sample_macro() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "sector_key": "construction",
                "industry": "Construction",
                "classification_risk_score": 4.0,
                "macro_risk_score": 3.2,
                "industry_base_risk_score": 3.64,
                "industry_base_risk_level": "Elevated",
                "sales_m_latest": 400.0,
                "employment_000_latest": 120.0,
                "employment_yoy_growth_pct": 1.2,
                "wages_to_sales_pct_latest": 14.5,
                "ebitda_margin_pct_latest": 10.5,
                "gross_operating_profit_to_sales_ratio_latest": 0.08,
                "inventories_to_sales_ratio_latest": 0.04,
                "inventory_days_est": 18.4,
                "inventory_days_yoy_change": 1.2,
                "inventory_stock_build_risk": "Moderate",
                "inventory_days_est_source": "ABS quarterly inventories/sales ratio converted to estimated inventory days",
                "demand_proxy_building_type": "Total Non-residential",
                "demand_yoy_growth_pct": 22.0,
                "cash_rate_latest_pct": 3.85,
                "cash_rate_change_1y_pctpts": -0.25,
            }
        ]
    )


def _sample_benchmark() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "sector_key": "construction",
                "industry": "Construction",
                "debt_to_ebitda_benchmark": 2.8,
                "icr_benchmark": 3.6,
                "ar_days_benchmark": 25.0,
                "ar_days_stress_benchmark": 33.0,
                "ar_days_severe_benchmark": 48.0,
                "ap_days_benchmark": 32.0,
                "ap_days_stress_benchmark": 36.0,
                "ap_days_severe_benchmark": 52.0,
                "inventory_days_benchmark": 18.4,
                "inventory_days_yoy_change": 1.2,
                "inventory_stock_build_risk": "Moderate",
                "inventory_days_benchmark_source": "ABS quarterly inventories/sales ratio converted to estimated inventory days",
                "ptrs_cycle8_avg_payment_days": 24.0,
                "ptrs_cycle9_avg_payment_days": 25.0,
                "ptrs_cycle8_paid_on_time_pct": 0.68,
                "ptrs_cycle9_paid_on_time_pct": 0.65,
                "ptrs_latest_cycle_used": "Cycle 9",
                "ar_days_benchmark_source": "PTRS official public payment-times proxy",
                "ap_days_benchmark_source": "PTRS official public payment-times proxy",
            }
        ]
    )


def _sample_borrower_compare() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "borrower_name": "Construction Archetype",
                "industry": "Construction",
                "sector_key": "construction",
                "revenue": 10000000,
                "ebitda": 900000,
                "total_debt": 2520000,
                "interest_expense": 250000,
                "accounts_receivable": 685000,
                "accounts_payable": 540000,
                "inventory": 420000,
                "cogs_or_purchases": 9100000,
                "ebitda_margin_pct": 9.0,
                "debt_to_ebitda": 2.8,
                "icr": 3.6,
                "ar_days": 25.0,
                "ap_days": 32.0,
                "inventory_days": 16.8,
                "borrower_profile_source": "generated archetype",
                "industry_public": "Construction",
                "ebitda_margin_pct_latest": 10.5,
                "classification_risk_score": 4.0,
                "macro_risk_score": 3.2,
                "debt_to_ebitda_benchmark": 2.8,
                "icr_benchmark": 3.6,
                "ar_days_benchmark": 25.0,
                "ap_days_benchmark": 32.0,
                "inventory_days_benchmark": 18.4,
                "benchmark_origin": "deterministic proxy benchmark",
                "ebitda_margin_score": 3,
                "debt_to_ebitda_score": 2,
                "icr_score": 3,
                "ar_days_score": 2,
                "ap_days_score": 2,
                "inventory_days_score": 2,
                "bottom_up_risk_score": 2.33,
            }
        ]
    )


def _sample_industry_working_capital() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "sector_key": "construction",
                "industry": "Construction",
                "ar_days_benchmark": 25.0,
                "ar_days_stress_benchmark": 33.0,
                "ar_days_severe_benchmark": 48.0,
                "ar_stress_uplift_days": 8.0,
                "ar_severe_uplift_days": 23.0,
                "ap_days_benchmark": 32.0,
                "ap_days_stress_benchmark": 36.0,
                "ap_days_severe_benchmark": 52.0,
                "ap_stress_uplift_days": 4.0,
                "ap_severe_uplift_days": 20.0,
                "ptrs_paid_on_time_pct_latest": 0.65,
                "inventory_days_benchmark": 18.4,
                "inventory_days_yoy_change": 1.2,
                "inventory_stock_build_risk": "Moderate",
                "cash_conversion_cycle_benchmark_days": 11.4,
                "cash_conversion_cycle_stress_days": 19.4,
                "cash_conversion_cycle_uplift_days": 8.0,
                "ar_collection_score": 2.33,
                "receivables_realisation_score": 3.33,
                "ap_supplier_stretch_score": 2.00,
                "inventory_liquidity_score": 2,
                "inventory_stock_build_score": 3,
                "cash_conversion_cycle_score": 2,
                "working_capital_scorecard_overlay_score": 2.08,
                "working_capital_scorecard_overlay_band": "Medium",
                "working_capital_pd_overlay_score": 2.80,
                "working_capital_pd_overlay_band": "Medium",
                "working_capital_lgd_overlay_score": 2.78,
                "working_capital_lgd_overlay_band": "Medium",
                "scorecard_primary_driver": "AR collection pressure",
                "pd_primary_driver": "Receivables realisation",
                "lgd_primary_driver": "Receivables realisation",
                "metric_origin": "test fixture",
            }
        ]
    )


def _sample_borrower_working_capital() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "borrower_name": "Construction Archetype",
                "industry": "Construction",
                "sector_key": "construction",
                "ar_days": 25.0,
                "ar_days_benchmark": 25.0,
                "ar_days_score": 2,
                "receivables_headroom_to_stress_days": 8.0,
                "ap_days": 32.0,
                "ap_days_benchmark": 32.0,
                "ap_days_score": 2,
                "payables_headroom_to_stress_days": 4.0,
                "inventory_days": 16.8,
                "inventory_days_benchmark": 18.4,
                "inventory_days_score": 2,
                "inventory_stock_build_risk": "Moderate",
                "cash_conversion_cycle_days": 9.8,
                "cash_conversion_cycle_benchmark_days": 11.4,
                "cash_conversion_cycle_gap_days": -1.6,
                "cash_conversion_cycle_score": 1,
                "receivables_realisation_score": 3,
                "supplier_stretch_score": 4,
                "working_capital_scorecard_overlay_score": 2.08,
                "working_capital_scorecard_metric_score": 1.75,
                "working_capital_scorecard_metric_band": "Low",
                "working_capital_pd_overlay_score": 2.80,
                "working_capital_pd_metric_score": 2.39,
                "working_capital_pd_metric_band": "Medium",
                "working_capital_lgd_overlay_score": 2.78,
                "working_capital_lgd_metric_score": 2.59,
                "working_capital_lgd_metric_band": "Medium",
                "metric_origin": "test fixture",
            }
        ]
    )


def _sample_scorecard() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "borrower_name": "Construction Archetype",
                "industry": "Construction",
                "classification_risk_score": 4.0,
                "macro_risk_score": 3.2,
                "bottom_up_risk_score": 3.1,
                "final_industry_risk_score": 3.46,
                "risk_level": "Elevated",
            }
        ]
    )


def _sample_pricing() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "borrower_name": "Construction Archetype",
                "industry": "Construction",
                "risk_level": "Elevated",
                "final_industry_risk_score": 3.46,
                "cash_rate_pct": 3.85,
                "base_margin_pct": 2.50,
                "industry_loading_pct": 0.50,
                "indicative_rate_pct": 3.00,
                "all_in_rate_pct": 6.85,
            }
        ]
    )


def _sample_policy() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "borrower_name": "Construction Archetype",
                "industry": "Construction",
                "risk_level": "Elevated",
                "final_industry_risk_score": 3.46,
                "max_lvr_pct": 65,
                "review_frequency": "Semi-annual",
                "approval_authority": "Senior credit officer",
                "additional_conditions": "Enhanced due diligence",
            }
        ]
    )


def _sample_concentration() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "industry": "Construction",
                "risk_level": "Elevated",
                "industry_base_risk_score": 3.64,
                "concentration_limit_pct": 15.0,
                "current_exposure_pct": 12.0,
                "headroom_pct": 3.0,
                "breach": False,
                "utilisation_pct": 80.0,
            }
        ]
    )


def _sample_watchlist() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "industry": "Construction",
                "trigger": "Elevated base risk score",
                "value": "Base score = 3.64",
                "recommended_action": "Escalate review",
            }
        ]
    )


def _sample_stress() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "industry": "Construction",
                "scenario_name": "Demand shock",
                "base_macro_risk_score": 3.2,
                "stressed_macro_risk_score": 3.7,
                "base_industry_risk_score": 3.64,
                "stressed_industry_risk_score": 3.87,
                "stress_delta": 0.23,
                "implied_monitoring_action": "Escalate sector review",
            }
        ]
    )


def test_reporting_workbook_and_pdf_generation() -> None:
    tmp_path = Path("tests") / ".tmp" / f"reporting-{uuid4().hex}"
    tmp_path.mkdir(parents=True, exist_ok=True)

    try:
        workbook_path = tmp_path / "industry_risk_reporting_workbook.xlsx"
        chart_table_path = tmp_path / "chart_table.csv"
        charts_dir = tmp_path / "charts"
        pdf_path = tmp_path / "industry_risk_formal_report.pdf"
        explanation_path = tmp_path / "chart_explanations.md"
        executive_summary_path = tmp_path / "executive_summary.md"

        build_reporting_workbook(
            _sample_foundation(),
            _sample_macro(),
            _sample_benchmark(),
            _sample_borrower_compare(),
            _sample_industry_working_capital(),
            _sample_borrower_working_capital(),
            _sample_scorecard(),
            _sample_pricing(),
            _sample_policy(),
            _sample_concentration(),
            _sample_watchlist(),
            _sample_stress(),
            workbook_path,
            chart_table_path,
            executive_summary_path,
        )

        assert workbook_path.exists()
        assert chart_table_path.exists()
        assert executive_summary_path.exists()

        build_formal_chart_report(workbook_path, charts_dir, pdf_path, explanation_path)

        assert pdf_path.exists()
        assert explanation_path.exists()
        assert list(charts_dir.glob("*.png")) == []
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)
