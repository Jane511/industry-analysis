"""Pin the canonical score-to-multiplier ladder.

Every published `pd_multiplier` and `industry_base_risk_level` value in the
contract files is derived from this ladder. Calibration drift would silently
shift downstream PD adjustments, so these assertions hard-pin both the band
boundaries and the multipliers each band emits.
"""

from __future__ import annotations

import math

import pytest

from src.overlays.build_industry_risk_scores import (
    SCORE_TO_MULTIPLIER_LADDER,
    score_to_pd_multiplier,
    score_to_risk_level,
)


@pytest.mark.parametrize(
    "score,expected_label,expected_multiplier",
    [
        (0.50, "Low", 0.90),
        (1.59, "Low", 0.90),
        (1.60, "Moderate-low", 0.95),
        (1.99, "Moderate-low", 0.95),
        (2.00, "Medium", 1.00),
        (2.50, "Medium", 1.00),
        (2.79, "Medium", 1.00),
        (2.80, "Moderate-high", 1.10),
        (3.22, "Moderate-high", 1.10),
        (3.23, "Elevated", 1.15),
        (4.50, "Elevated", 1.15),
    ],
)
def test_ladder_label_and_multiplier_at_band_boundaries(score, expected_label, expected_multiplier):
    assert score_to_risk_level(score) == expected_label
    assert score_to_pd_multiplier(score) == expected_multiplier


def test_ladder_returns_neutral_for_nan():
    assert score_to_risk_level(float("nan")) == "Medium"
    assert score_to_pd_multiplier(float("nan")) == 1.00


def test_ladder_covers_all_real_numbers_with_no_overlap_or_gap():
    """Bands must tile (-inf, +inf) — every real score maps to exactly one band."""
    bands = list(SCORE_TO_MULTIPLIER_LADDER)
    assert bands[0][0] == -math.inf
    assert bands[-1][1] == math.inf
    for (_, upper_a, _, _), (lower_b, _, _, _) in zip(bands, bands[1:]):
        assert upper_a == lower_b, f"Gap or overlap between {upper_a} and {lower_b}"


def test_ladder_multipliers_are_monotonic_in_score():
    """Higher score must produce a higher (or equal) multiplier."""
    multipliers = [m for _, _, _, m in SCORE_TO_MULTIPLIER_LADDER]
    assert multipliers == sorted(multipliers)


def test_ladder_multipliers_are_within_published_range():
    """README pins multipliers to the closed interval [0.90, 1.15]."""
    for _, _, _, mult in SCORE_TO_MULTIPLIER_LADDER:
        assert 0.90 <= mult <= 1.15
