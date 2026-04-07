"""Credit application functions — pricing, policy overlays, and concentration limits."""

from pathlib import Path
import pandas as pd
from src.utils import risk_band
from src.output import save_csv


# ---------------------------------------------------------------------------
# Pricing grid
# ---------------------------------------------------------------------------
PRICING_LOADING = {
    'Low': 0.00,
    'Medium': 0.25,
    'Elevated': 0.50,
    'High': 1.00,
}

BASE_MARGIN_PCT = 2.50  # base margin above cash rate


def build_pricing_grid(scorecard_df: pd.DataFrame, cash_rate: float) -> pd.DataFrame:
    """Map each borrower's risk level to an indicative lending rate.

    Rate = cash_rate + base_margin + industry_risk_loading.
    """
    df = scorecard_df.copy()
    df['cash_rate_pct'] = cash_rate
    df['base_margin_pct'] = BASE_MARGIN_PCT
    df['industry_loading_pct'] = df['risk_level'].map(PRICING_LOADING)
    df['indicative_rate_pct'] = df['base_margin_pct'] + df['industry_loading_pct']
    df['all_in_rate_pct'] = df['cash_rate_pct'] + df['indicative_rate_pct']
    return df[['borrower_name', 'industry', 'risk_level', 'final_industry_risk_score',
               'cash_rate_pct', 'base_margin_pct', 'industry_loading_pct',
               'indicative_rate_pct', 'all_in_rate_pct']]


# ---------------------------------------------------------------------------
# Policy overlay
# ---------------------------------------------------------------------------
POLICY_RULES = {
    'Low': {
        'max_lvr_pct': 80,
        'review_frequency': 'Annual',
        'approval_authority': 'Standard delegated authority',
        'additional_conditions': 'None',
    },
    'Medium': {
        'max_lvr_pct': 75,
        'review_frequency': 'Annual',
        'approval_authority': 'Standard delegated authority',
        'additional_conditions': 'Industry section in credit memo required',
    },
    'Elevated': {
        'max_lvr_pct': 65,
        'review_frequency': 'Semi-annual',
        'approval_authority': 'Senior credit officer',
        'additional_conditions': 'Enhanced due diligence; stress-test cash flows',
    },
    'High': {
        'max_lvr_pct': 50,
        'review_frequency': 'Quarterly',
        'approval_authority': 'Credit committee',
        'additional_conditions': 'New lending subject to committee approval; mandatory collateral revaluation',
    },
}


def build_policy_overlay(scorecard_df: pd.DataFrame) -> pd.DataFrame:
    """Attach credit policy restrictions based on industry risk level."""
    rows = []
    for _, r in scorecard_df.iterrows():
        level = r['risk_level']
        rules = POLICY_RULES.get(level, POLICY_RULES['Medium'])
        rows.append({
            'borrower_name': r['borrower_name'],
            'industry': r['industry'],
            'risk_level': level,
            'final_industry_risk_score': r['final_industry_risk_score'],
            **rules,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Concentration limits
# ---------------------------------------------------------------------------
CONCENTRATION_LIMITS = {
    'Low': 25.0,
    'Medium': 20.0,
    'Elevated': 15.0,
    'High': 10.0,
}


def build_concentration_limits(macro_df: pd.DataFrame,
                               portfolio_df: pd.DataFrame) -> pd.DataFrame:
    """Compare current portfolio exposure to risk-based concentration limits."""
    base = macro_df[['industry', 'industry_base_risk_score', 'industry_base_risk_level']].copy()
    base = base.rename(columns={'industry_base_risk_level': 'risk_level'})
    base['concentration_limit_pct'] = base['risk_level'].map(CONCENTRATION_LIMITS)

    df = base.merge(portfolio_df, on='industry', how='left')
    df['current_exposure_pct'] = df['current_exposure_pct'].fillna(0)
    df['headroom_pct'] = df['concentration_limit_pct'] - df['current_exposure_pct']
    df['breach'] = df['current_exposure_pct'] > df['concentration_limit_pct']
    df['utilisation_pct'] = (df['current_exposure_pct'] / df['concentration_limit_pct'] * 100).round(1)

    return df[['industry', 'risk_level', 'industry_base_risk_score',
               'concentration_limit_pct', 'current_exposure_pct',
               'headroom_pct', 'breach', 'utilisation_pct']]
