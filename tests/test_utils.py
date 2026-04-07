"""Tests for src.utils scoring functions."""

import math
import pytest
from src.utils import (
    normalise_text,
    risk_band,
    score_employment_growth,
    score_margin_level,
    score_margin_trend,
    score_inventory_ratio,
    score_demand_growth,
    score_gap_higher_is_worse,
    score_gap_lower_is_worse,
    score_icr,
)


# ---------------------------------------------------------------------------
# normalise_text
# ---------------------------------------------------------------------------
class TestNormaliseText:
    def test_basic(self):
        assert normalise_text("Retail Trade") == "retail trade"

    def test_special_chars(self):
        assert normalise_text("Agriculture, Forestry & Fishing") == "agriculture forestry fishing"

    def test_numeric(self):
        assert normalise_text("Division A1") == "division a1"


# ---------------------------------------------------------------------------
# risk_band
# ---------------------------------------------------------------------------
class TestRiskBand:
    def test_low_boundary(self):
        assert risk_band(2.0) == "Low"

    def test_medium_lower(self):
        assert risk_band(2.01) == "Medium"

    def test_medium_upper(self):
        assert risk_band(3.0) == "Medium"

    def test_elevated_lower(self):
        assert risk_band(3.01) == "Elevated"

    def test_elevated_upper(self):
        assert risk_band(4.0) == "Elevated"

    def test_high(self):
        assert risk_band(4.01) == "High"

    def test_extreme(self):
        assert risk_band(5.0) == "High"

    def test_very_low(self):
        assert risk_band(1.0) == "Low"


# ---------------------------------------------------------------------------
# score_employment_growth
# ---------------------------------------------------------------------------
class TestScoreEmploymentGrowth:
    def test_strong_growth(self):
        assert score_employment_growth(5.0) == 1

    def test_moderate_growth(self):
        assert score_employment_growth(3.0) == 2

    def test_low_growth(self):
        assert score_employment_growth(2.0) == 3

    def test_very_low_growth(self):
        assert score_employment_growth(0.5) == 4

    def test_decline(self):
        assert score_employment_growth(-1.0) == 5

    def test_nan(self):
        assert score_employment_growth(float('nan')) == 3


# ---------------------------------------------------------------------------
# score_margin_level
# ---------------------------------------------------------------------------
class TestScoreMarginLevel:
    def test_high_percentage(self):
        assert score_margin_level(30) == 1

    def test_low_percentage(self):
        assert score_margin_level(5) == 5

    def test_nan(self):
        assert score_margin_level(float('nan')) == 3


# ---------------------------------------------------------------------------
# score_margin_trend
# ---------------------------------------------------------------------------
class TestScoreMarginTrend:
    def test_improving(self):
        assert score_margin_trend(5) == 1

    def test_declining(self):
        assert score_margin_trend(-6) == 5

    def test_nan(self):
        assert score_margin_trend(float('nan')) == 3


# ---------------------------------------------------------------------------
# score_inventory_ratio
# ---------------------------------------------------------------------------
class TestScoreInventoryRatio:
    def test_low(self):
        assert score_inventory_ratio(0.10) == 1

    def test_high(self):
        assert score_inventory_ratio(0.80) == 5

    def test_nan(self):
        assert score_inventory_ratio(float('nan')) == 3


# ---------------------------------------------------------------------------
# score_demand_growth
# ---------------------------------------------------------------------------
class TestScoreDemandGrowth:
    def test_strong_growth(self):
        assert score_demand_growth(25) == 1

    def test_strong_decline(self):
        assert score_demand_growth(-25) == 5

    def test_nan(self):
        assert score_demand_growth(float('nan')) == 3


# ---------------------------------------------------------------------------
# score_gap_higher_is_worse
# ---------------------------------------------------------------------------
class TestScoreGapHigherIsWorse:
    def test_below_benchmark(self):
        assert score_gap_higher_is_worse(1.5, 2.5) == 1

    def test_above_benchmark(self):
        # gap = 1.5, benchmark * 0.60 = 1.5, so gap <= 0.60 * benchmark → score 4
        assert score_gap_higher_is_worse(4.0, 2.5) == 4

    def test_nan_actual(self):
        assert score_gap_higher_is_worse(float('nan'), 2.5) == 3

    def test_nan_benchmark(self):
        assert score_gap_higher_is_worse(2.0, float('nan')) == 3


# ---------------------------------------------------------------------------
# score_gap_lower_is_worse
# ---------------------------------------------------------------------------
class TestScoreGapLowerIsWorse:
    def test_well_above(self):
        assert score_gap_lower_is_worse(20, 10) == 1

    def test_well_below(self):
        assert score_gap_lower_is_worse(0, 15) == 5

    def test_nan(self):
        assert score_gap_lower_is_worse(float('nan'), 10) == 3


# ---------------------------------------------------------------------------
# score_icr
# ---------------------------------------------------------------------------
class TestScoreICR:
    def test_well_above_benchmark(self):
        assert score_icr(5.0, 3.0) == 1

    def test_at_benchmark(self):
        assert score_icr(3.0, 3.0) == 2

    def test_below_benchmark(self):
        assert score_icr(1.5, 3.0) == 5

    def test_nan(self):
        assert score_icr(float('nan'), 3.0) == 3
