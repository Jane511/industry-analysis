import pandas as pd

from src.build_foundation import (
    _score_demand_dependency,
    _score_external_shock,
    _score_rate_sensitivity,
)
from src.build_macro_view import (
    DEMAND_PROXY_MAP,
    LOW_RELIABILITY_DEMAND_PROXY_SECTORS,
    _estimate_inventory_days_from_ratio,
    _inventory_stock_build_risk,
)
from src.utils import score_demand_growth


def test_defensive_service_sectors_are_not_penalised_for_labour_intensity() -> None:
    health_rate = _score_rate_sensitivity(16.7, "health care and social assistance")
    professional_rate = _score_rate_sensitivity(13.0, "professional scientific and technical services")

    assert health_rate <= 2
    assert professional_rate <= 2


def test_cyclical_sectors_keep_higher_structural_demand_dependency() -> None:
    construction_score = _score_demand_dependency(10.5, "construction")
    health_score = _score_demand_dependency(7.5, "health care and social assistance")

    assert construction_score > health_score


def test_external_shock_no_longer_uses_sector_size_as_risk_driver() -> None:
    health_score = _score_external_shock(16.7, 7.5, "health care and social assistance")
    agriculture_score = _score_external_shock(14.6, -11.0, "agriculture forestry and fishing")

    assert health_score < agriculture_score


def test_low_reliability_demand_proxy_sectors_score_neutral_when_proxy_is_missing() -> None:
    assert "health care and social assistance" in LOW_RELIABILITY_DEMAND_PROXY_SECTORS
    assert "professional scientific and technical services" in LOW_RELIABILITY_DEMAND_PROXY_SECTORS
    assert DEMAND_PROXY_MAP["health care and social assistance"] == "Health buildings"
    assert DEMAND_PROXY_MAP["professional scientific and technical services"] == "Offices"

    demand_series = pd.Series([None, None], dtype="float64")
    scores = demand_series.apply(score_demand_growth).tolist()
    assert scores == [3, 3]


def test_inventory_days_estimation_uses_quarterly_ratio_basis() -> None:
    estimated_days = _estimate_inventory_days_from_ratio(0.52, 0.10)

    assert round(estimated_days, 1) == 52.7
    assert estimated_days < 60


def test_inventory_stock_build_risk_flags_rising_stock_into_weaker_conditions() -> None:
    row = pd.Series(
        {
            "sector_key": "manufacturing",
            "inventory_days_est": 58.0,
            "inventory_days_yoy_change": 14.0,
            "inventories_to_sales_ratio_yoy_change": 0.06,
            "sales_growth_pct": -3.5,
            "demand_yoy_growth_pct": -8.0,
            "gross_operating_profit_to_sales_ratio_yoy_change": -0.02,
        }
    )

    assert _inventory_stock_build_risk(row) == "High"
