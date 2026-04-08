"""Tests for pricing and policy overlays."""

import pandas as pd
from src.credit import (
    build_pricing_grid,
    build_policy_overlay,
    PRICING_LOADING,
)


def _make_scorecard():
    return pd.DataFrame([
        {'borrower_name': 'LowCo', 'industry': 'Health Care', 'risk_level': 'Low',
         'final_industry_risk_score': 1.8, 'classification_risk_score': 2.0,
         'macro_risk_score': 1.5, 'bottom_up_risk_score': 1.8},
        {'borrower_name': 'MedCo', 'industry': 'Transport', 'risk_level': 'Medium',
         'final_industry_risk_score': 2.5, 'classification_risk_score': 3.0,
         'macro_risk_score': 2.5, 'bottom_up_risk_score': 2.0},
        {'borrower_name': 'ElevCo', 'industry': 'Construction', 'risk_level': 'Elevated',
         'final_industry_risk_score': 3.5, 'classification_risk_score': 4.0,
         'macro_risk_score': 3.0, 'bottom_up_risk_score': 3.5},
        {'borrower_name': 'HighCo', 'industry': 'Accommodation', 'risk_level': 'High',
         'final_industry_risk_score': 4.5, 'classification_risk_score': 5.0,
         'macro_risk_score': 4.0, 'bottom_up_risk_score': 4.5},
    ])


# ---------------------------------------------------------------------------
# Pricing grid
# ---------------------------------------------------------------------------
class TestPricingGrid:
    def test_loading_per_risk_level(self):
        scorecard = _make_scorecard()
        pricing = build_pricing_grid(scorecard, cash_rate=4.35)

        for _, row in pricing.iterrows():
            expected = PRICING_LOADING[row['risk_level']]
            assert row['industry_loading_pct'] == expected

    def test_all_in_rate(self):
        scorecard = _make_scorecard()
        pricing = build_pricing_grid(scorecard, cash_rate=4.35)

        for _, row in pricing.iterrows():
            expected = row['cash_rate_pct'] + row['base_margin_pct'] + row['industry_loading_pct']
            assert abs(row['all_in_rate_pct'] - expected) < 1e-9

    def test_low_risk_no_loading(self):
        scorecard = _make_scorecard()
        pricing = build_pricing_grid(scorecard, cash_rate=4.35)
        low = pricing[pricing['risk_level'] == 'Low'].iloc[0]
        assert low['industry_loading_pct'] == 0.0


# ---------------------------------------------------------------------------
# Policy overlay
# ---------------------------------------------------------------------------
class TestPolicyOverlay:
    def test_lvr_decreases_with_risk(self):
        scorecard = _make_scorecard()
        policy = build_policy_overlay(scorecard)

        lvr_by_level = policy.set_index('risk_level')['max_lvr_pct']
        assert lvr_by_level['Low'] > lvr_by_level['Medium']
        assert lvr_by_level['Medium'] > lvr_by_level['Elevated']
        assert lvr_by_level['Elevated'] > lvr_by_level['High']

    def test_high_risk_requires_committee(self):
        scorecard = _make_scorecard()
        policy = build_policy_overlay(scorecard)
        high = policy[policy['risk_level'] == 'High'].iloc[0]
        assert 'committee' in high['approval_authority'].lower()
