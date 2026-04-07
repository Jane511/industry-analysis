import pandas as pd
from pathlib import Path

import src.build_benchmarks as build_benchmarks_module
import src.build_bottom_up as build_bottom_up_module
from src.build_portfolio import build_portfolio_proxy


def _make_public_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "sector_key": "retail trade",
                "industry": "Retail Trade",
                "ebitda_margin_pct_latest": 7.8,
                "gross_operating_profit_to_sales_ratio_latest": 0.07,
                "inventories_to_sales_ratio_latest": 0.31,
                "inventory_days_est": 30.5,
                "inventory_days_yoy_change": -1.2,
                "inventory_stock_build_risk": "Low",
                "inventory_days_est_source": "ABS quarterly inventories/sales ratio converted to estimated inventory days",
                "wages_to_sales_pct_latest": 10.2,
                "classification_risk_score": 4.0,
                "macro_risk_score": 3.4,
                "demand_yoy_growth_pct": 10.0,
            },
            {
                "sector_key": "professional scientific and technical services",
                "industry": "Professional, Scientific and Technical Services",
                "ebitda_margin_pct_latest": 13.0,
                "gross_operating_profit_to_sales_ratio_latest": 0.13,
                "inventories_to_sales_ratio_latest": None,
                "inventory_days_est": 8.0,
                "inventory_days_yoy_change": None,
                "inventory_stock_build_risk": "Low",
                "inventory_days_est_source": "Fallback inventory-days estimate derived from public margin, sales, demand, and sector inventory profile",
                "wages_to_sales_pct_latest": 35.0,
                "classification_risk_score": 2.5,
                "macro_risk_score": 3.2,
                "demand_yoy_growth_pct": -12.0,
            },
        ]
    )


def test_build_industry_benchmarks_preserves_public_margin(monkeypatch):
    public_df = _make_public_df()
    monkeypatch.setattr(build_benchmarks_module, "save_csv", lambda df, path: None)

    result = build_benchmarks_module.build_industry_benchmarks(public_df, Path("."))

    retail = result[result["sector_key"] == "retail trade"].iloc[0]
    assert retail["ebitda_margin_pct_latest"] == 7.8
    assert retail["inventory_days_benchmark"] == 30.5
    assert retail["inventory_days_benchmark_source"] == "ABS quarterly inventories/sales ratio converted to estimated inventory days"
    assert retail["benchmark_origin"].startswith("ebitda margin from ABS Australian Industry")


def test_build_industry_benchmarks_generates_missing_inventory_sectors(monkeypatch):
    public_df = _make_public_df()
    monkeypatch.setattr(build_benchmarks_module, "save_csv", lambda df, path: None)

    result = build_benchmarks_module.build_industry_benchmarks(public_df, Path("."))

    services = result[result["sector_key"] == "professional scientific and technical services"].iloc[0]
    assert services["inventory_days_benchmark"] == 8.0
    assert services["inventory_stock_build_risk"] == "Low"
    assert services["ar_days_benchmark"] > services["inventory_days_benchmark"]
    assert services["icr_benchmark"] >= 1.5


def test_build_industry_benchmarks_prefers_ptrs_ar_days_when_available(monkeypatch):
    public_df = _make_public_df()
    public_df["anzsic_division_code"] = ["G", "M"]
    monkeypatch.setattr(build_benchmarks_module, "save_csv", lambda df, path: None)
    monkeypatch.setattr(
        build_benchmarks_module,
        "_load_ptrs_ar_benchmarks",
        lambda ptrs_workbook_path=None: pd.DataFrame(
            [
                {
                    "anzsic_division_code": "G",
                    "ptrs_industry": "Retail Trade",
                    "ptrs_cycle8_avg_payment_days": 29.7,
                    "ptrs_cycle9_avg_payment_days": 28.7,
                    "ar_days_benchmark": 29.7,
                    "ar_days_stress_benchmark": 42.0,
                    "ar_days_severe_benchmark": 77.0,
                    "ap_days_benchmark": 29.7,
                    "ap_days_stress_benchmark": 42.0,
                    "ap_days_severe_benchmark": 77.0,
                    "ptrs_cycle8_paid_on_time_pct": 0.654,
                    "ptrs_cycle9_paid_on_time_pct": 0.675,
                    "ptrs_latest_cycle_used": "Cycle 9",
                    "ar_days_benchmark_source": "PTRS official public payment-times proxy",
                    "ap_days_benchmark_source": "PTRS official public payment-times proxy",
                }
            ]
        ),
    )

    result = build_benchmarks_module.build_industry_benchmarks(public_df, Path("."))

    retail = result[result["sector_key"] == "retail trade"].iloc[0]
    services = result[result["sector_key"] == "professional scientific and technical services"].iloc[0]
    assert retail["ar_days_benchmark"] == 29.7
    assert retail["ap_days_benchmark"] == 29.7
    assert retail["ar_days_benchmark_source"] == "PTRS official public payment-times proxy"
    assert retail["ap_days_benchmark_source"] == "PTRS official public payment-times proxy"
    assert services["ar_days_benchmark_source"] == "Derived from public industry signals using deterministic proxy formula"
    assert services["ap_days_benchmark_source"] == "Derived from public industry signals using deterministic proxy formula"


def test_build_bottom_up_uses_generated_benchmarks(monkeypatch):
    public_df = pd.DataFrame(
        [
            {
                "sector_key": "retail trade",
                "industry": "Retail Trade",
                "sales_m_latest": 643421,
                "ebitda_margin_pct_latest": 7.8,
                "classification_risk_score": 4.0,
                "macro_risk_score": 3.4,
            }
        ]
    )
    benchmark_df = pd.DataFrame(
        [
            {
                "sector_key": "retail trade",
                "industry": "Retail Trade",
                "ebitda_margin_pct_latest": 7.8,
                "debt_to_ebitda_benchmark": 2.4,
                "icr_benchmark": 3.0,
                "ar_days_benchmark": 10.0,
                "ap_days_benchmark": 35.0,
                "inventory_days_benchmark": 80.0,
                "benchmark_origin": "generated",
            }
        ]
    )
    monkeypatch.setattr(build_bottom_up_module, "save_csv", lambda df, path: None)

    result = build_bottom_up_module.build_bottom_up(public_df, benchmark_df, Path("."))

    row = result.iloc[0]
    assert row["benchmark_origin"] == "generated"
    assert row["debt_to_ebitda_benchmark"] == 2.4
    assert row["bottom_up_risk_score"] > 0


def test_build_portfolio_proxy_uses_public_weights(monkeypatch):
    macro_df = pd.DataFrame(
        [
            {"industry": "Retail Trade", "sales_m_latest": 600, "employment_000_latest": 100},
            {"industry": "Construction", "sales_m_latest": 400, "employment_000_latest": 100},
        ]
    )
    monkeypatch.setattr("src.build_portfolio.save_csv", lambda df, path: None)

    result = build_portfolio_proxy(macro_df, Path("."))

    retail = result[result["industry"] == "Retail Trade"].iloc[0]
    construction = result[result["industry"] == "Construction"].iloc[0]
    assert retail["current_exposure_pct"] > construction["current_exposure_pct"]
    assert round(result["current_exposure_pct"].sum(), 1) == 100.0
