import pandas as pd
from pathlib import Path

from src.bank_practice import (
    build_industry_credit_appetite_strategy,
    build_industry_stress_test_matrix,
    build_industry_esg_overlay,
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
    monkeypatch.setattr("src.bank_practice.save_csv", lambda df, path: None)
    result = build_industry_credit_appetite_strategy(_make_macro(), Path("."))

    construction = result[result["industry"] == "Construction"].iloc[0]
    health = result[result["industry"] == "Health Care and Social Assistance"].iloc[0]
    assert construction["credit_appetite_stance"] == "Selective"
    assert health["credit_appetite_stance"] == "Grow"


def test_stress_test_matrix_has_four_scenarios(monkeypatch):
    monkeypatch.setattr("src.bank_practice.save_csv", lambda df, path: None)
    result = build_industry_stress_test_matrix(_make_macro(), Path("."))

    assert result["scenario_name"].nunique() == 4
    assert (result["stressed_industry_risk_score"] >= result["base_industry_risk_score"]).all()


def test_esg_overlay_flags_sensitive_sectors(monkeypatch):
    monkeypatch.setattr("src.bank_practice.save_csv", lambda df, path: None)
    result = build_industry_esg_overlay(_make_macro(), Path("."))

    construction = result[result["industry"] == "Construction"].iloc[0]
    health = result[result["industry"] == "Health Care and Social Assistance"].iloc[0]
    assert bool(construction["esg_sensitive_sector"]) is True
    assert bool(health["esg_sensitive_sector"]) is False
