import pandas as pd
from pathlib import Path

from src.portfolio import (
    CONCENTRATION_LIMITS,
    build_concentration_limits,
    build_industry_credit_appetite_strategy,
    build_industry_stress_test_matrix,
    build_industry_esg_overlay,
    build_portfolio_proxy,
)


def _make_macro():
    return pd.DataFrame(
        [
            {
                "industry": "Construction",
                "sector_key": "construction",
                "industry_base_risk_level": "Elevated",
                "industry_base_risk_score": 3.4,
                "classification_risk_score": 3.5,
                "macro_risk_score": 3.3,
            },
            {
                "industry": "Health Care and Social Assistance",
                "sector_key": "health care and social assistance",
                "industry_base_risk_level": "Low",
                "industry_base_risk_score": 1.9,
                "classification_risk_score": 2.0,
                "macro_risk_score": 1.8,
            },
        ]
    )


def test_appetite_strategy_maps_risk_to_stance(monkeypatch):
    monkeypatch.setattr("src.portfolio.save_csv", lambda df, path: None)
    result = build_industry_credit_appetite_strategy(_make_macro(), Path("."))

    construction = result[result["industry"] == "Construction"].iloc[0]
    health = result[result["industry"] == "Health Care and Social Assistance"].iloc[0]
    assert construction["credit_appetite_stance"] == "Selective"
    assert health["credit_appetite_stance"] == "Grow"


def test_stress_test_matrix_has_four_scenarios(monkeypatch):
    monkeypatch.setattr("src.portfolio.save_csv", lambda df, path: None)
    result = build_industry_stress_test_matrix(_make_macro(), Path("."))

    assert result["scenario_name"].nunique() == 4
    assert (result["stressed_industry_risk_score"] >= result["base_industry_risk_score"]).all()


def test_esg_overlay_flags_sensitive_sectors(monkeypatch):
    monkeypatch.setattr("src.portfolio.save_csv", lambda df, path: None)
    result = build_industry_esg_overlay(_make_macro(), Path("."))

    construction = result[result["industry"] == "Construction"].iloc[0]
    health = result[result["industry"] == "Health Care and Social Assistance"].iloc[0]
    assert bool(construction["esg_sensitive_sector"]) is True
    assert bool(health["esg_sensitive_sector"]) is False


def test_portfolio_proxy_uses_public_weights(monkeypatch):
    macro_df = pd.DataFrame(
        [
            {"industry": "Retail Trade", "sales_m_latest": 600, "employment_000_latest": 100},
            {"industry": "Construction", "sales_m_latest": 400, "employment_000_latest": 100},
        ]
    )
    monkeypatch.setattr("src.portfolio.save_csv", lambda df, path: None)

    result = build_portfolio_proxy(macro_df, Path("."))

    retail = result[result["industry"] == "Retail Trade"].iloc[0]
    construction = result[result["industry"] == "Construction"].iloc[0]
    assert retail["current_exposure_pct"] > construction["current_exposure_pct"]
    assert round(result["current_exposure_pct"].sum(), 1) == 100.0


def test_concentration_limits_flag_breaches() -> None:
    macro = pd.DataFrame(
        [{"industry": "Construction", "industry_base_risk_score": 3.74, "industry_base_risk_level": "Elevated"}]
    )
    portfolio = pd.DataFrame([{"industry": "Construction", "current_exposure_pct": 20.0}])

    result = build_concentration_limits(macro, portfolio)

    assert bool(result.iloc[0]["breach"]) is True
    assert result.iloc[0]["concentration_limit_pct"] == CONCENTRATION_LIMITS["Elevated"]


def test_concentration_limits_calculate_headroom() -> None:
    macro = pd.DataFrame([{"industry": "Health Care", "industry_base_risk_score": 2.0, "industry_base_risk_level": "Low"}])
    portfolio = pd.DataFrame([{"industry": "Health Care", "current_exposure_pct": 10.0}])

    result = build_concentration_limits(macro, portfolio)

    assert bool(result.iloc[0]["breach"]) is False
    assert result.iloc[0]["headroom_pct"] == 15.0
