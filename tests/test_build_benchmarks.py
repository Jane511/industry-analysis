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
    assert retail["inventory_days_benchmark"] > 0
    assert retail["benchmark_origin"].startswith("ebitda margin from ABS Australian Industry")


def test_build_industry_benchmarks_generates_missing_inventory_sectors(monkeypatch):
    public_df = _make_public_df()
    monkeypatch.setattr(build_benchmarks_module, "save_csv", lambda df, path: None)

    result = build_benchmarks_module.build_industry_benchmarks(public_df, Path("."))

    services = result[result["sector_key"] == "professional scientific and technical services"].iloc[0]
    assert services["inventory_days_benchmark"] >= 5
    assert services["ar_days_benchmark"] > services["inventory_days_benchmark"]
    assert services["icr_benchmark"] >= 1.5


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
